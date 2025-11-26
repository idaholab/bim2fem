# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import bim2fem.ifcplus.util.geometry
import bim2fem.ifcplus.util.material
import bim2fem.ifcplus.api.material
from bim2fem.ifcplus import REGION
import bim2fem.ifcplus.util.profile
import ifcopenshell.api.root
import bim2fem.ifcplus.api.profile
import bim2fem.ifcplus.api.structural
import ifcopenshell.util.representation
import ifcopenshell.util.placement
import numpy as np
import bim2fem.ifcplus.util.representation
from bim2fem.ifcplus.util.geometry import TriangularMesh
import bim2fem.core.convert.classify_beam_shape
import ifcopenshell.util.unit
import bim2fem.ifcplus.api.element_type
import ifcopenshell.api.type
import ifcopenshell.api.spatial
import bim2fem.ifcplus.util.project
from typing import cast


def convert_linear_frame_member_to_linear_structural_curve_member(
    linear_frame_member_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    building_element_copied_to_destination_file = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class=linear_frame_member_from_source_file.is_a(),
        name=linear_frame_member_from_source_file.Name,
    )
    building_element_copied_to_destination_file.GlobalId = (
        linear_frame_member_from_source_file.GlobalId
    )

    site = ifc4_destination_file.by_type(type="IfcSite", include_subtypes=False)[0]
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_destination_file,
        products=[building_element_copied_to_destination_file],
        relating_structure=site,
    )

    material_names_from_destination_file = list(
        {
            material.Name
            for material in ifc4_destination_file.by_type(
                type="IfcMaterial",
                include_subtypes=False,
            )
        }
    )
    standard_material_name = bim2fem.ifcplus.util.material.get_best_matching_standard_material_from_element_metadata(
        element=linear_frame_member_from_source_file,
        region=region,
        other_material_names=material_names_from_destination_file,
    )
    if standard_material_name is None:
        if region == "Europe":
            standard_material_name = "S355"
        elif region == "UnitedStates":
            standard_material_name = "A36"
        else:
            standard_material_name = "S355"

    profile_names_from_destination_file = list(
        {
            profile.ProfileName
            for profile in ifc4_destination_file.by_type(
                type="IfcProfileDef",
                include_subtypes=True,
            )
        }
    )
    standard_profile_name = bim2fem.ifcplus.util.profile.get_best_matching_standard_profile_from_element_metadata(
        element=linear_frame_member_from_source_file,
        region=region,
        other_standard_profile_names=profile_names_from_destination_file,
    )

    extruded_area_solid = bim2fem.ifcplus.util.representation.get_single_extruded_area_solid_representation(
        element=linear_frame_member_from_source_file
    )

    if extruded_area_solid and standard_profile_name:
        structural_curve_member = convert_frame_member_to_fem_for_case_1(
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            standard_material_name=standard_material_name,
            standard_profile_name=standard_profile_name,
            structural_analysis_model=structural_analysis_model,
            frame_member_from_source_file=linear_frame_member_from_source_file,
            frame_member_copied_to_destination_file=building_element_copied_to_destination_file,
            extruded_area_solid=extruded_area_solid,
        )
    else:
        structural_curve_member = convert_frame_member_to_fem_for_case_2(
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            standard_material_name=standard_material_name,
            standard_profile_name=standard_profile_name,
            structural_analysis_model=structural_analysis_model,
            frame_member_from_source_file=linear_frame_member_from_source_file,
            frame_member_copied_to_destination_file=building_element_copied_to_destination_file,
        )

    return structural_curve_member


def convert_frame_member_to_fem_for_case_1(
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    standard_material_name: str,
    standard_profile_name: str,
    structural_analysis_model: ifcopenshell.entity_instance,
    frame_member_from_source_file: ifcopenshell.entity_instance,
    frame_member_copied_to_destination_file: ifcopenshell.entity_instance,
    extruded_area_solid: ifcopenshell.entity_instance,
    plot_each_step: bool = False,
) -> ifcopenshell.entity_instance | None:
    """Case 1: Standard Profile Name is identified and RepresentationItem is IfcExtrudedAreaSolid"""

    material = bim2fem.ifcplus.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    material = cast(ifcopenshell.entity_instance, material)

    profile_def = bim2fem.ifcplus.api.profile.add_profile_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        profile_name=standard_profile_name,
        check_for_duplicate=True,
    )
    profile_def = cast(ifcopenshell.entity_instance, profile_def)

    material_profile_set = bim2fem.ifcplus.api.material.add_material_profile_set_with_single_material_profile(
        material=material,
        profile=profile_def,
        name=None,
        check_for_duplicate=True,
    )
    element_type = (
        bim2fem.ifcplus.api.element_type.add_element_type_for_material_profile_set(
            ifc_class=frame_member_copied_to_destination_file.is_a() + "Type",
            material_profile_set=material_profile_set,
            name=material_profile_set.Name,
            check_for_duplicate=True,
        )
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[frame_member_copied_to_destination_file],
        relating_type=element_type,
    )

    transformation_matrix = ifcopenshell.util.placement.get_local_placement(
        placement=frame_member_from_source_file.ObjectPlacement
    )

    body_representation = ifcopenshell.util.representation.get_representation(
        element=frame_member_from_source_file,
        context="Model",
        subcontext="Body",
        target_view="MODEL_VIEW",
    )
    body_representation = cast(ifcopenshell.entity_instance, body_representation)
    if body_representation.RepresentationType == "MappedRepresentation":
        mapped_item = body_representation.Items[0]
        mappeditem_transformation_matrix = (
            ifcopenshell.util.placement.get_mappeditem_transformation(item=mapped_item)
        )
        transformation_matrix = transformation_matrix @ mappeditem_transformation_matrix
        body_representation = ifcopenshell.util.representation.resolve_representation(
            representation=body_representation
        )

    (
        local_origin_of_extruded_area_solid,
        local_z_axis_of_extruded_area_solid,
        local_x_axis_of_extruded_area_solid,
    ) = bim2fem.ifcplus.util.representation.get_local_origin_and_axes_of_extruded_area_solid(
        extruded_area_solid=extruded_area_solid
    )
    extruded_area_solid_transformation_matrix = ifcopenshell.util.placement.a2p(
        o=local_origin_of_extruded_area_solid,
        z=local_z_axis_of_extruded_area_solid,
        x=local_x_axis_of_extruded_area_solid,
    )
    transformation_matrix = (
        transformation_matrix @ extruded_area_solid_transformation_matrix
    )

    extrusion_direction_in_local_coordinates = (
        extruded_area_solid.ExtrudedDirection.DirectionRatios
    )
    extrusion_direction_in_global_coordinates = tuple(
        transformation_matrix[:3, :3]
        @ np.array(extrusion_direction_in_local_coordinates)
    )

    if extruded_area_solid.SweptArea.is_a("IfcParameterizedProfileDef"):
        # print("\tCase 1a: SweptArea is an IfcParameterizedProfileDef")
        local_origin_of_swept_area, local_x_axis_of_swept_area = (
            bim2fem.ifcplus.util.profile.get_local_origin_and_x_axis_of_parameterized_profile_def(
                parameterized_profile_def=extruded_area_solid.SweptArea
            )
        )
        origin_in_global_coordinates = tuple(
            (
                transformation_matrix
                @ np.array(list(local_origin_of_swept_area) + [0.0, 1.0])
            )[:3].tolist()
        )
        local_x_axis_in_global_coordinates = tuple(
            transformation_matrix[:3, :3]
            @ np.array(list(local_x_axis_of_swept_area) + [0.0])
        )
        local_y_axis_in_global_coordinates = np.array(
            bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=extrusion_direction_in_global_coordinates,
                vector2=local_x_axis_in_global_coordinates,
            )
        )

    # Case 1b
    else:
        # print("\tCase 1b: SweptArea is not an IfcParameterizedProfileDef")
        triangular_mesh = TriangularMesh.from_ifc_element(
            element=frame_member_from_source_file
        )
        if plot_each_step:
            triangular_mesh.plot_all()
        indices_of_faces_with_normals_acute_to_extrusion_direction = []
        for index_of_face, _ in enumerate(triangular_mesh.faces):
            face_normal_vector = triangular_mesh.calculate_normal_vector_of_face(
                face_index=index_of_face
            )
            angle = bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
                vector1=extrusion_direction_in_global_coordinates,
                vector2=face_normal_vector,
            )
            if 0.0 <= angle < np.pi / 2:
                indices_of_faces_with_normals_acute_to_extrusion_direction.append(
                    index_of_face
                )
        external_edges = triangular_mesh.get_boundary_edges_from_group_of_contiguous_planar_faces(
            indices_of_contiguous_planar_faces=indices_of_faces_with_normals_acute_to_extrusion_direction
        )
        longest_edge = triangular_mesh.get_longest_edge_from_given_edges(
            edges=external_edges
        )
        assumed_local_y_axis_in_global_coordinates = (
            triangular_mesh.calculate_unit_normalized_direction_vector_of_edge(
                edge=longest_edge
            )
        )
        assumed_local_y_axis_is_global_negative_z_direction = (
            np.linalg.norm(
                np.array([0.0, 0.0, -1.0])
                - np.array(assumed_local_y_axis_in_global_coordinates)
            )
            == 0.0
        )
        if (
            frame_member_from_source_file.is_a("IfcBeam")
            and assumed_local_y_axis_is_global_negative_z_direction
        ):
            assumed_local_y_axis_in_global_coordinates = (0.0, 0.0, 1.0)
        result = bim2fem.core.convert.classify_beam_shape.classify_shape_and_determine_orientation_of_faces(
            local_z_axis_in_global_coordinates=extrusion_direction_in_global_coordinates,
            assumed_local_y_axis_in_global_coordinates=assumed_local_y_axis_in_global_coordinates,
            faces_defined_by_vertex_coordinates=triangular_mesh.get_coordinates_of_faces(
                indices_of_faces=indices_of_faces_with_normals_acute_to_extrusion_direction
            ),
        )
        matching_shape, local_x_axis_in_global_coordinates = (
            result["matching_shape"],
            result["local_x_axis_in_global_coordinates"],
        )
        if not matching_shape and not local_x_axis_in_global_coordinates:
            print(
                " ".join(
                    [
                        "\tWarning: Failed Conversion for",
                        f"{frame_member_from_source_file}.",
                        "Could not determine orientation for Case 1b",
                    ]
                )
            )
            return None
        origin_in_global_coordinates = tuple(transformation_matrix[:3, 3].tolist())
        local_y_axis_in_global_coordinates = (
            bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=extrusion_direction_in_global_coordinates,
                vector2=local_x_axis_in_global_coordinates,
            )
        )

    start_point = origin_in_global_coordinates

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(
        ifc_file=frame_member_from_source_file.file
    )

    length_of_frame_member_in_meters = unit_scale * extruded_area_solid.Depth

    end_point = tuple(
        (
            np.array(origin_in_global_coordinates)
            + np.array(extrusion_direction_in_global_coordinates)
            * length_of_frame_member_in_meters
        ).tolist()
    )

    orientation_point = tuple(
        (np.array(start_point) + np.array(local_y_axis_in_global_coordinates)).tolist()
    )

    structural_curve_member = (
        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=start_point,
            end_point=end_point,
            orientation_point=orientation_point,
            profile=profile_def,
            material=material,
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=frame_member_copied_to_destination_file,
        )
    )

    return structural_curve_member


def convert_frame_member_to_fem_for_case_2(
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    standard_material_name: str,
    standard_profile_name: str | None,
    structural_analysis_model: ifcopenshell.entity_instance,
    frame_member_from_source_file: ifcopenshell.entity_instance,
    frame_member_copied_to_destination_file: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:
    """Case 2: Standard Profile Name is None or
    RepresentationItem is not a single IfcExtrudedAreaSolid"""

    material = bim2fem.ifcplus.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    material = cast(ifcopenshell.entity_instance, material)

    triangular_mesh = TriangularMesh.from_ifc_element(
        element=frame_member_from_source_file
    )

    centroid_of_triangular_mesh = (
        triangular_mesh.calculate_centroid_of_triangular_mesh()
    )

    distances_from_centroid_to_faces = []
    for index_of_face in range(len(triangular_mesh.faces)):
        centroid_of_face = triangular_mesh.calculate_centroid_of_face(
            index_of_face=index_of_face
        )
        distance = float(
            np.linalg.norm(
                np.array(centroid_of_face) - np.array(centroid_of_triangular_mesh)
            )
        )
        distances_from_centroid_to_faces.append(distance)

    furthest_distance = max(distances_from_centroid_to_faces)
    index_of_furthest_face = distances_from_centroid_to_faces.index(furthest_distance)

    indices_of_faces_near_endpoints_of_frame_member = []
    for face_index, distance_from_centroid_to_face in enumerate(
        distances_from_centroid_to_faces
    ):
        if (
            0.75 * furthest_distance
            <= distance_from_centroid_to_face
            <= 1.25 * furthest_distance
        ):
            indices_of_faces_near_endpoints_of_frame_member.append(face_index)

    rough_estimate_of_length_of_frame_member = 2.0 * furthest_distance
    indices_of_faces_at_first_endpoint = []
    indices_of_faces_at_second_endpoint = []
    centroid_of_furthest_face = triangular_mesh.calculate_centroid_of_face(
        index_of_face=index_of_furthest_face
    )
    for index_of_trial_face in indices_of_faces_near_endpoints_of_frame_member:
        centroid_of_trial_face = triangular_mesh.calculate_centroid_of_face(
            index_of_face=index_of_trial_face
        )
        distance_from_trial_face_to_furthest_face = np.linalg.norm(
            np.array(centroid_of_trial_face) - np.array(centroid_of_furthest_face)
        )
        if (
            distance_from_trial_face_to_furthest_face
            <= rough_estimate_of_length_of_frame_member * 0.50
        ):
            indices_of_faces_at_first_endpoint.append(index_of_trial_face)
        else:
            indices_of_faces_at_second_endpoint.append(index_of_trial_face)

    origin_in_global_coordinates = triangular_mesh.calculate_centroid_of_given_faces(
        indices_of_faces=indices_of_faces_at_first_endpoint
    )
    terminus_in_global_coordinates = triangular_mesh.calculate_centroid_of_given_faces(
        indices_of_faces=indices_of_faces_at_second_endpoint
    )

    extrusion_direction_in_global_coordinates = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
        p1=origin_in_global_coordinates,
        p2=terminus_in_global_coordinates,
    )

    length_of_frame_member = float(
        np.linalg.norm(
            np.array(terminus_in_global_coordinates)
            - np.array(origin_in_global_coordinates)
        )
    )

    external_edges = (
        triangular_mesh.get_boundary_edges_from_group_of_contiguous_planar_faces(
            indices_of_contiguous_planar_faces=indices_of_faces_at_second_endpoint
        )
    )
    longest_edge = triangular_mesh.get_longest_edge_from_given_edges(
        edges=external_edges
    )
    assumed_local_y_axis_in_global_coordinates = (
        triangular_mesh.calculate_unit_normalized_direction_vector_of_edge(
            edge=longest_edge
        )
    )
    assumed_local_y_axis_is_global_negative_z_direction = (
        np.linalg.norm(
            np.array([0.0, 0.0, -1.0])
            - np.array(assumed_local_y_axis_in_global_coordinates)
        )
        == 0.0
    )
    if (
        frame_member_from_source_file.is_a("IfcBeam")
        and assumed_local_y_axis_is_global_negative_z_direction
    ):
        assumed_local_y_axis_in_global_coordinates = (0.0, 0.0, 1.0)
    result_for_beam_shape_classification = bim2fem.core.convert.classify_beam_shape.classify_shape_and_determine_orientation_of_faces(
        local_z_axis_in_global_coordinates=extrusion_direction_in_global_coordinates,
        assumed_local_y_axis_in_global_coordinates=assumed_local_y_axis_in_global_coordinates,
        faces_defined_by_vertex_coordinates=triangular_mesh.get_coordinates_of_faces(
            indices_of_faces=indices_of_faces_at_second_endpoint
        ),
    )
    matching_shape, local_x_axis_in_global_coordinates = (
        result_for_beam_shape_classification["matching_shape"],
        result_for_beam_shape_classification["local_x_axis_in_global_coordinates"],
    )
    if not matching_shape and not local_x_axis_in_global_coordinates:
        print(
            " ".join(
                [
                    "\tWarning: Failed Conversion for",
                    f"{frame_member_from_source_file}.",
                    "Could not determine orientation for Case 1b",
                ]
            )
        )
        return None
    local_y_axis_in_global_coordinates = (
        bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
            vector1=extrusion_direction_in_global_coordinates,
            vector2=local_x_axis_in_global_coordinates,
        )
    )

    if not standard_profile_name:
        print("\tCase 2a: Standard Profile Name is not Known from Metadata")
        numeric_scale = bim2fem.ifcplus.util.project.get_numeric_scale_of_project(
            ifc4_file=ifc4_destination_file
        )
        result_for_beam_shape_measurement = bim2fem.core.convert.classify_beam_shape.measure_dimensions_of_classified_shape_of_faces(
            local_z_axis_in_global_coordinates=extrusion_direction_in_global_coordinates,
            local_x_axis_in_global_coordinates=local_x_axis_in_global_coordinates,
            faces_defined_by_vertex_coordinates=triangular_mesh.get_coordinates_of_faces(
                indices_of_faces=indices_of_faces_at_second_endpoint
            ),
            preset_beam_shape_classification=matching_shape,
            numeric_scale=numeric_scale,
        )
        parameterized_profile_class, dimensions = (
            result_for_beam_shape_measurement["parameterized_profile_class"],
            result_for_beam_shape_measurement["dimensions"],
        )
        if not parameterized_profile_class and not dimensions:
            print(
                " ".join(
                    [
                        "\tWarning: Failed Conversion for",
                        f"{frame_member_from_source_file}. ",
                        "Could not determine profile nor measure dimensions.",
                    ]
                )
            )
            return None
        profile_def = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_destination_file,
            profile_class=parameterized_profile_class,
            dimensions=dimensions,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

    else:
        print("\tCase 2b: Standard Profile Name is Known from Metadata")
        profile_def = bim2fem.ifcplus.api.profile.add_profile_from_standard_library(
            ifc4_file=ifc4_destination_file,
            region=region,
            profile_name=standard_profile_name,
            check_for_duplicate=True,
        )
        profile_def = cast(ifcopenshell.entity_instance, profile_def)

    material_profile_set = bim2fem.ifcplus.api.material.add_material_profile_set_with_single_material_profile(
        material=material,
        profile=profile_def,
        name=None,
        check_for_duplicate=True,
    )
    element_type = (
        bim2fem.ifcplus.api.element_type.add_element_type_for_material_profile_set(
            ifc_class=frame_member_copied_to_destination_file.is_a() + "Type",
            material_profile_set=material_profile_set,
            name=material_profile_set.Name,
            check_for_duplicate=True,
        )
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[frame_member_copied_to_destination_file],
        relating_type=element_type,
    )

    start_point = origin_in_global_coordinates

    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(
        ifc_file=frame_member_from_source_file.file
    )

    length_of_frame_member_in_meters = unit_scale * length_of_frame_member

    end_point = tuple(
        (
            np.array(origin_in_global_coordinates)
            + np.array(extrusion_direction_in_global_coordinates)
            * length_of_frame_member_in_meters
        ).tolist()
    )

    orientation_point = tuple(
        (np.array(start_point) + np.array(local_y_axis_in_global_coordinates)).tolist()
    )

    structural_curve_member = (
        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=start_point,
            end_point=end_point,
            orientation_point=orientation_point,
            profile=profile_def,
            material=material,
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=frame_member_copied_to_destination_file,
        )
    )

    return structural_curve_member
