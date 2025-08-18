# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import inlbim.util.geometry
import inlbim.util.material
import inlbim.api.material
from inlbim import REGION
import inlbim.util.profile
import ifcopenshell.api.root
import inlbim.api.profile
import inlbim.api.structural
import ifcopenshell.util.representation
import ifcopenshell.util.placement
import numpy as np
import inlbim.util.representation
from inlbim.util.geometry import TriangularMesh
import bim2fem.helpers.beam_shape_classification
import ifcopenshell.util.unit
import inlbim.api.element_type
import ifcopenshell.api.type
import ifcopenshell.api.spatial
import inlbim.util.file
import ifcopenshell.api.project


def convert_linear_frame_member_to_structural_item(
    frame_member_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    print("\tconvert_frame_member_to_structural_item()")
    print(f"\tframe_member_from_source_file: {frame_member_from_source_file}")
    print(f"\tregion: {region}")
    print(f"\tstructural_analysis_model: {structural_analysis_model}")

    # Add Beam/Column/Member to destination file with the original IfcGlobalId
    if frame_member_from_source_file.is_a("IfcBeam"):
        element_class = "IfcBeam"
    elif frame_member_from_source_file.is_a("IfcColumn"):
        element_class = "IfcColumn"
    elif frame_member_from_source_file.is_a("IfcColumn"):
        element_class = "IfcMember"
    else:
        return None
    frame_member_copied_to_destination_file = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class=element_class,
        name=frame_member_from_source_file.Name,
    )
    site = ifc4_destination_file.by_type(type="IfcSite", include_subtypes=False)[0]
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_destination_file,
        products=[frame_member_copied_to_destination_file],
        relating_structure=site,
    )

    # Get best matching standard material name, if it exists
    material_names_from_destination_file = list(
        {
            material.Name
            for material in ifc4_destination_file.by_type(
                type="IfcMaterial",
                include_subtypes=False,
            )
        }
    )
    standard_material_name = (
        inlbim.util.material.get_best_matching_standard_material_from_element_metadata(
            element=frame_member_from_source_file,
            region=region,
            other_material_names=material_names_from_destination_file,
        )
    )
    if standard_material_name is None:
        if region == "Europe":
            standard_material_name = "S355"
        elif region == "UnitedStates":
            standard_material_name = "A36"
        else:
            standard_material_name = "S355"
    print(f"\tstandard_material_name: {standard_material_name}")

    # Get best matching standard profile name, if it exists
    profile_names_from_destination_file = list(
        {
            profile.ProfileName
            for profile in ifc4_destination_file.by_type(
                type="IfcProfileDef",
                include_subtypes=True,
            )
        }
    )
    standard_profile_name = (
        inlbim.util.profile.get_best_matching_standard_profile_from_element_metadata(
            element=frame_member_from_source_file,
            region=region,
            other_standard_profile_names=profile_names_from_destination_file,
        )
    )
    print(f"\tstandard_profile_name: {standard_profile_name}")

    # Get the IfcExtrudedAreaSolid, if it exists
    extruded_area_solid = (
        inlbim.util.representation.get_single_extruded_area_solid_representation(
            element=frame_member_from_source_file
        )
    )
    print(f"\textruded_area_solid: {extruded_area_solid}")

    # Create the StructuralItem
    if standard_profile_name and extruded_area_solid:
        structural_curve_member = convert_frame_member_to_fem_for_case_1(
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            standard_material_name=standard_material_name,
            standard_profile_name=standard_profile_name,
            structural_analysis_model=structural_analysis_model,
            frame_member_from_source_file=frame_member_from_source_file,
            frame_member_copied_to_destination_file=frame_member_copied_to_destination_file,
            extruded_area_solid=extruded_area_solid,
        )
    elif not extruded_area_solid:
        structural_curve_member = convert_frame_member_to_fem_for_case_2(
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            standard_material_name=standard_material_name,
            standard_profile_name=standard_profile_name,
            structural_analysis_model=structural_analysis_model,
            frame_member_from_source_file=frame_member_from_source_file,
            frame_member_copied_to_destination_file=frame_member_copied_to_destination_file,
        )
    else:
        structural_curve_member = None
    print(f"\tstructural_curve_member: {structural_curve_member}")

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
) -> ifcopenshell.entity_instance | None:
    """Case 1: Standard Profile Name is identified and RepresentationItem is IfcExtrudedAreaSolid"""

    print(
        "\tCase 1: Standard Profile Name is identified and RepresentationItem is IfcExtrudedAreaSolid"
    )

    # Create the standard material
    material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    assert isinstance(material, ifcopenshell.entity_instance)

    # Create the profile
    profile_def = inlbim.api.profile.add_profile_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        profile_name=standard_profile_name,
        check_for_duplicate=True,
    )
    assert isinstance(profile_def, ifcopenshell.entity_instance)

    # Add and assign Type
    if frame_member_copied_to_destination_file.is_a("IfcBeam"):
        element_type_class = "IfcBeamType"
    elif frame_member_copied_to_destination_file.is_a("IfcColumn"):
        element_type_class = "IfcColumnType"
    else:
        element_type_class = "IfcMemberType"
    element_type = inlbim.api.element_type.add_beam_or_column_or_member_type(
        ifc_class=element_type_class,
        material=material,
        profile=profile_def,
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[frame_member_copied_to_destination_file],
        relating_type=element_type,
    )

    # Declare Type on Project
    project = ifc4_destination_file.by_type(type="IfcProject", include_subtypes=False)[
        0
    ]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_destination_file,
        definitions=[element_type],
        relating_context=project,
    )

    # Object Placement Transformation
    transformation_matrix = ifcopenshell.util.placement.get_local_placement(
        placement=frame_member_from_source_file.ObjectPlacement
    )

    # MappedItem Transformation
    body_representation = ifcopenshell.util.representation.get_representation(
        element=frame_member_from_source_file,
        context="Model",
        subcontext="Body",
        target_view="MODEL_VIEW",
    )
    assert body_representation
    if body_representation.RepresentationType == "MappedRepresentation":
        mapped_item = body_representation.Items[0]
        mappeditem_transformation_matrix = (
            ifcopenshell.util.placement.get_mappeditem_transformation(item=mapped_item)
        )
        transformation_matrix = transformation_matrix @ mappeditem_transformation_matrix
        body_representation = ifcopenshell.util.representation.resolve_representation(
            representation=body_representation
        )

    # ExtrudedAreaSolid Transformation
    (
        local_origin_of_extruded_area_solid,
        local_z_axis_of_extruded_area_solid,
        local_x_axis_of_extruded_area_solid,
    ) = inlbim.util.representation.get_local_origin_and_axes_of_extruded_area_solid(
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

    # Global Extrusion Direction
    extrusion_direction_in_local_coordinates = (
        extruded_area_solid.ExtrudedDirection.DirectionRatios
    )
    extrusion_direction_in_global_coordinates = tuple(
        transformation_matrix[:3, :3]
        @ np.array(extrusion_direction_in_local_coordinates)
    )

    # Case 1a
    if extruded_area_solid.SweptArea.is_a("IfcParameterizedProfileDef"):
        print("\tCase 1a: SweptArea is an IfcParameterizedProfileDef")
        local_origin_of_swept_area, local_x_axis_of_swept_area = (
            inlbim.util.profile.get_local_origin_and_x_axis_of_parameterized_profile_def(
                parameterized_profile_def=extruded_area_solid.SweptArea
            )
        )
        origin_in_global_coordinates = (
            transformation_matrix
            @ np.array(list(local_origin_of_swept_area) + [0.0, 1.0])
        )[:3]
        local_x_axis_in_global_coordinates = tuple(
            transformation_matrix[:3, :3]
            @ np.array(list(local_x_axis_of_swept_area) + [0.0])
        )
        local_y_axis_in_global_coordinates = np.array(
            inlbim.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=extrusion_direction_in_global_coordinates,
                vector2=local_x_axis_in_global_coordinates,
            )
        )

    # Case 1b
    else:
        print("\tCase 1b: SweptArea is not an IfcParameterizedProfileDef")
        triangular_mesh = TriangularMesh.from_ifc_element(
            element=frame_member_from_source_file
        )
        # triangular_mesh.plot_all()
        indices_of_faces_with_normals_acute_to_extrusion_direction = []
        for index_of_face, _ in enumerate(triangular_mesh.faces):
            face_normal_vector = triangular_mesh.calculate_normal_vector_of_face(
                face_index=index_of_face
            )
            angle = inlbim.util.geometry.calculate_angle_between_two_vectors(
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
        result = bim2fem.helpers.beam_shape_classification.classify_shape_and_determine_orientation_of_faces(
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
            # print(
            #     " ".join(
            #         [
            #             "\tWarning: Failed Conversion for",
            #             f"{frame_member_from_source_file}.",
            #             "Could not determine orientation for Case 1b",
            #         ]
            #     )
            # )
            return None
        origin_in_global_coordinates = tuple(
            [float(val) for val in transformation_matrix[:3, 3]]
        )
        local_y_axis_in_global_coordinates = (
            inlbim.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=extrusion_direction_in_global_coordinates,
                vector2=local_x_axis_in_global_coordinates,
            )
        )

    # Calculate points for StructuralCurveMember
    p1 = tuple(float(val) for val in origin_in_global_coordinates)
    assert len(p1) == 3
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(
        ifc_file=frame_member_from_source_file.file
    )
    p2 = tuple(
        float(val)
        for val in (
            np.array(origin_in_global_coordinates)
            + np.array(extrusion_direction_in_global_coordinates)
            * unit_scale
            * extruded_area_solid.Depth
        ).tolist()
    )
    assert len(p2) == 3
    p3 = tuple(
        float(val)
        for val in (
            np.array(p1) + np.array(local_y_axis_in_global_coordinates) * 1.0
        ).tolist()
    )
    assert len(p3) == 3

    # Create StructuralItem
    structural_curve_member = inlbim.api.structural.create_3pt_structural_curve_member(
        p1=p1,
        p2=p2,
        p3=p3,
        profile_def=profile_def,
        material=material,
        structural_analysis_model=structural_analysis_model,
        corresponding_product=frame_member_copied_to_destination_file,
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
    """Case 2: Standard Profile Name is either identified or not and
    RepresentationItem is not a single IfcExtrudedAreaSolid"""

    print("\tCase 2: RepresentationItem is not a single IfcExtrudedAreaSolid")

    # Create the standard material
    material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    assert isinstance(material, ifcopenshell.entity_instance)

    # Triangular Mesh
    triangular_mesh = TriangularMesh.from_ifc_element(
        element=frame_member_from_source_file
    )
    # triangular_mesh.plot_all()

    # Calculate Centroid
    centroid_of_triangular_mesh = (
        triangular_mesh.calculate_centroid_of_triangular_mesh()
    )

    # Get distances of faces to centroid
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

    # Get furthest face from centroid
    furthest_distance = max(distances_from_centroid_to_faces)
    index_of_furthest_face = distances_from_centroid_to_faces.index(furthest_distance)

    # Get faces that are near the endpoints of the frame member
    rough_estimate_of_length_of_frame_member = furthest_distance * 2.0
    indices_of_faces_near_endpoints_of_frame_member = []
    coordinates_of_faces = triangular_mesh.get_coordinates_of_faces(
        indices_of_faces=[_ for _ in range(len(triangular_mesh.faces))]
    )
    for index_of_face, coordinates_of_face in enumerate(coordinates_of_faces):
        face_is_within_specified_bounds_around_endpoints = True
        for coordinate_of_face in coordinates_of_face:
            distance_from_centroid_of_triangular_mesh_to_coordinate = np.linalg.norm(
                np.array(coordinate_of_face) - np.array(centroid_of_triangular_mesh)
            )
            if not (
                rough_estimate_of_length_of_frame_member * 0.25
                <= distance_from_centroid_of_triangular_mesh_to_coordinate
                <= rough_estimate_of_length_of_frame_member * 0.75
            ):
                face_is_within_specified_bounds_around_endpoints = False
                break
        if face_is_within_specified_bounds_around_endpoints:
            indices_of_faces_near_endpoints_of_frame_member.append(index_of_face)
    # triangular_mesh.plot_faces_3d(
    #     faces_as_tuples_with_coordinates=triangular_mesh.get_coordinates_of_faces(
    #         indices_of_faces=indices_of_faces_near_endpoints_of_frame_member
    #     )
    # )

    # Separate faces into two groups of faces corresponding to the two endpoints
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
            <= rough_estimate_of_length_of_frame_member * 0.25
        ):
            indices_of_faces_at_first_endpoint.append(index_of_trial_face)
        else:
            indices_of_faces_at_second_endpoint.append(index_of_trial_face)
    # triangular_mesh.plot_faces_3d(
    #     faces_as_tuples_with_coordinates=triangular_mesh.get_coordinates_of_faces(
    #         indices_of_faces=indices_of_faces_at_first_endpoint
    #     )
    # )
    # triangular_mesh.plot_faces_3d(
    #     faces_as_tuples_with_coordinates=triangular_mesh.get_coordinates_of_faces(
    #         indices_of_faces=indices_of_faces_at_second_endpoint
    #     )
    # )

    # Calculate endpoints
    origin_in_global_coordinates = triangular_mesh.calculate_centroid_of_given_faces(
        indices_of_faces=indices_of_faces_at_first_endpoint
    )
    terminus_in_global_coordinates = triangular_mesh.calculate_centroid_of_given_faces(
        indices_of_faces=indices_of_faces_at_second_endpoint
    )

    # Calculate extrusion direction
    extrusion_direction_in_global_coordinates = (
        inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=origin_in_global_coordinates,
            p2=terminus_in_global_coordinates,
        )
    )

    # Calculate length of frame member
    length_of_frame_member = float(
        np.linalg.norm(
            np.array(terminus_in_global_coordinates)
            - np.array(origin_in_global_coordinates)
        )
    )

    # Determine Shape Classification and Y-axis
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
    result_for_beam_shape_classification = bim2fem.helpers.beam_shape_classification.classify_shape_and_determine_orientation_of_faces(
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
        # print(
        #     " ".join(
        #         [
        #             "\tWarning: Failed Conversion for",
        #             f"{frame_member_from_source_file}.",
        #             "Could not determine orientation for Case 1b",
        #         ]
        #     )
        # )
        return None
    local_y_axis_in_global_coordinates = (
        inlbim.util.geometry.calculate_cross_product_of_two_vectors(
            vector1=extrusion_direction_in_global_coordinates,
            vector2=local_x_axis_in_global_coordinates,
        )
    )

    if not standard_profile_name:
        print("\tCase 2a: Standard Profile Name is not Known from Metadata")
        numeric_scale = inlbim.util.file.get_numeric_scale_of_project(
            ifc4_file=ifc4_destination_file
        )
        result_for_beam_shape_measurement = bim2fem.helpers.beam_shape_classification.measure_dimensions_of_classified_shape_of_faces(
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
            return None
        profile_def = inlbim.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_destination_file,
            profile_class=parameterized_profile_class,
            dimensions=dimensions,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

    else:
        print("\tCase 2b: Standard Profile Name is Known from Metadata")
        profile_def = inlbim.api.profile.add_profile_from_standard_library(
            ifc4_file=ifc4_destination_file,
            region=region,
            profile_name=standard_profile_name,
            check_for_duplicate=True,
        )
        assert isinstance(profile_def, ifcopenshell.entity_instance)

    # Add and assign Type
    if frame_member_copied_to_destination_file.is_a("IfcBeam"):
        element_type_class = "IfcBeamType"
    elif frame_member_copied_to_destination_file.is_a("IfcColumn"):
        element_type_class = "IfcColumnType"
    else:
        element_type_class = "IfcMemberType"
    element_type = inlbim.api.element_type.add_beam_or_column_or_member_type(
        ifc_class=element_type_class,
        material=material,
        profile=profile_def,
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[frame_member_copied_to_destination_file],
        relating_type=element_type,
    )

    # Declare Type on Project
    project = ifc4_destination_file.by_type(type="IfcProject", include_subtypes=False)[
        0
    ]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_destination_file,
        definitions=[element_type],
        relating_context=project,
    )

    # Calculate points for StructuralCurveMember
    p1 = tuple(float(val) for val in origin_in_global_coordinates)
    assert len(p1) == 3
    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(
        ifc_file=frame_member_from_source_file.file
    )
    p2 = tuple(
        float(val)
        for val in (
            np.array(origin_in_global_coordinates)
            + np.array(extrusion_direction_in_global_coordinates)
            * unit_scale
            * length_of_frame_member
        ).tolist()
    )
    assert len(p2) == 3
    p3 = tuple(
        float(val)
        for val in (
            np.array(p1) + np.array(local_y_axis_in_global_coordinates) * 1.0
        ).tolist()
    )
    assert len(p3) == 3

    # Create StructuralItem
    structural_curve_member = inlbim.api.structural.create_3pt_structural_curve_member(
        p1=p1,
        p2=p2,
        p3=p3,
        profile_def=profile_def,
        material=material,
        structural_analysis_model=structural_analysis_model,
        corresponding_product=frame_member_copied_to_destination_file,
    )

    return structural_curve_member
