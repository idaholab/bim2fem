# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import numpy as np
import ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcplus.api.geometry
import ifcopenshell.util.element
import ifcplus.merge_projects
import ifcplus.util.geometry
import ifcplus.util.structural
import ifcopenshell
import ifcopenshell.api.root
import ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcplus.api.geometry
import ifcopenshell.api.spatial
import ifcopenshell.api.root
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcplus.api.geometry
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import ifcplus.api.geometry
from typing import Literal
import ifcplus.api.profile
import ifcplus
import ifcopenshell.util.placement
import ifcplus.util.material
import ifcplus.api.style
import ifcplus.api.placement
import ifcopenshell.util.representation

VIEW_OPTION = Literal["Extruded", "Wireframe_3D"]


def recreate_ifc4_sav_with_3d_body_shape_representation(
    ifc4_sav_file: ifcopenshell.file,
    view_option: VIEW_OPTION = "Extruded",
    thickness_of_flat_shells: float = 0.1 / 2.0 / 2.0 / 2.0,
    size_of_wireframe_bodies: float = 0.1 / 2.0 / 2.0 / 2.0,
    size_of_node_bodies: float = 0.1 / 2.0,
) -> ifcopenshell.file:

    # Create New File
    ifc4_arch_file = ifcopenshell.file(schema=ifc4_sav_file.schema)
    ifcopenshell.api.root.create_entity(file=ifc4_arch_file, ifc_class="IfcProject")

    # Merge Projects
    ifcplus.merge_projects.merge_projects(
        destination_ifc4_file=ifc4_arch_file,
        source_ifc4_files=[ifc4_sav_file],
    )
    project_in_source_file = ifc4_sav_file.by_type(type="IfcProject")[0]
    project_in_destination_file = ifc4_arch_file.by_type(type="IfcProject")[0]
    project_in_destination_file.Name = (
        project_in_source_file.Name
        + " (recreated with architectural body shape representation)"
    )
    project_in_destination_file.OwnerHistory = ifc4_arch_file.by_type(
        type="IfcOwnerHistory"
    )[0]
    project_in_destination_file.RepresentationContexts = [
        ifc4_arch_file.by_type(type="IfcGeometricRepresentationContext")[0]
    ]
    project_in_destination_file.UnitsInContext = ifc4_arch_file.by_type(
        type="IfcUnitAssignment"
    )[0]

    # Recreate IfcStructuralSurfaceMembers
    ifc4_arch_file = recreate_structural_surface_members(
        ifc4_arch_file=ifc4_arch_file,
        view_option=view_option,
        thickness_of_flat_shells=thickness_of_flat_shells,
    )

    # Recreate IfcStructuralCurveMembers
    ifc4_arch_file = recreate_linear_structural_curve_members(
        ifc4_arch_file=ifc4_arch_file,
        view_option=view_option,
        size_of_wireframe_bodies=size_of_wireframe_bodies,
    )

    # Recreate IfcStructuralPointConnections
    ifc4_arch_file = recreate_structural_point_connections(
        ifc4_arch_file=ifc4_arch_file,
        view_option=view_option,
        size_of_node_bodies=size_of_node_bodies,
    )

    # Remove StructuralItems and other structural products
    for structural_item in ifc4_arch_file.by_type(
        type="IfcStructuralItem", include_subtypes=True
    ):
        ifcopenshell.api.root.remove_product(
            file=ifc4_arch_file,
            product=structural_item,
        )
    for rel in ifc4_arch_file.by_type(type="IfcRelConnectsStructuralMember"):
        ifcopenshell.api.root.remove_product(
            file=ifc4_arch_file,
            product=rel,
        )
    structural_analysis_model = ifc4_arch_file.by_type(
        type="IfcStructuralAnalysisModel"
    )[0]
    for structural_analysis_model in ifc4_arch_file.by_type(
        type="IfcStructuralAnalysisModel"
    ):
        ifcopenshell.api.root.remove_product(
            file=ifc4_arch_file,
            product=structural_analysis_model,
        )

    # Remove Unreferenced Resource Entities
    for ifc_class_for_placement_related_entity in [
        "IfcLocalPlacement",
        "IfcAxis2Placement3D",
        "IfcCartesianPoint",
        "IfcDirection",
    ]:
        for entity in ifc4_arch_file.by_type(
            type=ifc_class_for_placement_related_entity,
            include_subtypes=False,
        ):
            num_inverses = ifc4_arch_file.get_total_inverses(entity)
            if num_inverses == 0:
                ifc4_arch_file.remove(entity)

    return ifc4_arch_file


def recreate_structural_surface_members(
    ifc4_arch_file: ifcopenshell.file,
    view_option: VIEW_OPTION = "Extruded",
    thickness_of_flat_shells: float = 0.1,
) -> ifcopenshell.file:

    structural_surface_members = ifc4_arch_file.by_type(
        type="IfcStructuralSurfaceMember",
        include_subtypes=False,
    )

    for structural_surface_member in structural_surface_members:

        # Get assigned product
        assigned_product = (
            ifcplus.util.structural.get_assigned_product_of_structural_item(
                structural_item=structural_surface_member
            )
        )
        assert assigned_product

        # Create Element
        decomposing_element_of_assigned_product = ifcopenshell.api.root.create_entity(
            file=ifc4_arch_file,
            ifc_class=assigned_product.is_a(),
            name=structural_surface_member.Name,
            predefined_type=None,
        )
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_arch_file,
            products=[decomposing_element_of_assigned_product],
            relating_object=assigned_product,
        )
        ifcplus.api.placement.edit_object_placement(
            product=decomposing_element_of_assigned_product,
            place_object_relative_to_parent=True,
        )

        # Get coordinates of outer bound vertices
        points_3d = ifcplus.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
            triangular_structural_surface_member=structural_surface_member
        )

        # Transform coordinates of vertices to 2D
        v12 = tuple((np.array(points_3d[1]) - np.array(points_3d[0])).tolist())
        v23 = tuple((np.array(points_3d[2]) - np.array(points_3d[1])).tolist())
        local_z_axis_in_global_coordinates = (
            ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=v12, vector2=v23
            )
        )
        local_x_axis_in_global_coordinates = (
            ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
                p1=points_3d[0], p2=points_3d[1]
            )
        )
        transformation_matrix = ifcopenshell.util.placement.a2p(
            o=points_3d[0],
            z=local_z_axis_in_global_coordinates,
            x=local_x_axis_in_global_coordinates,
        )

        # temp1 = transformation_matrix.transpose()
        # temp2 = transformation_matrix.transpose()[:3][:3]
        # temp1[3] = temp1[3] * np.array([-1.0, -1.0, -1.0, 1])

        points_2d = []
        for point_3d in points_3d:
            point_2d = (
                transformation_matrix.transpose() @ np.array(list(point_3d) + [1])
            ).tolist()[0:-2]
            points_2d.append(tuple(point_2d))
        points_2d += [points_2d[0]]

        first_point_2d = np.array(points_2d[0])
        points_2d_relative = []
        for point_2d in points_2d:
            point_2d_relative = tuple((np.array(point_2d) - first_point_2d).tolist())
            points_2d_relative.append(point_2d_relative)

        material_layer_set = ifcopenshell.util.element.get_material(
            element=assigned_product,
            should_skip_usage=True,
        )
        assert material_layer_set

        # Calculate thickness
        if view_option == "Extruded":
            thickness = ifcplus.util.material.sum_material_layer_thicknesses(
                material_layer_set=material_layer_set
            )
        else:
            thickness = thickness_of_flat_shells

        # Add and assign representation
        representation_item = ifcplus.api.geometry.add_extruded_area_solid(
            ifc4_file=ifc4_arch_file,
            swept_area=ifcplus.api.profile.add_arbitrary_profile_with_or_without_voids(
                file=ifc4_arch_file,
                outer_profile=points_2d_relative,
                inner_profiles=[],
                name=None,
            ),
            repositioned_origin=(0.0, 0.0, -thickness / 2),
            depth=thickness,
        )
        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_arch_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type="SweptSolid",
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[representation_item],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_arch_file,
            product=decomposing_element_of_assigned_product,
            representation=shape_model,
        )

        # Edit Placement
        ifcplus.api.placement.edit_object_placement(
            product=decomposing_element_of_assigned_product,
            repositioned_origin=points_3d[0],
            repositioned_z_axis=local_z_axis_in_global_coordinates,
            repositioned_x_axis=local_x_axis_in_global_coordinates,
            place_object_relative_to_parent=False,
        )

    return ifc4_arch_file


def recreate_linear_structural_curve_members(
    ifc4_arch_file: ifcopenshell.file,
    view_option: VIEW_OPTION = "Extruded",
    size_of_wireframe_bodies: float = 0.1,
) -> ifcopenshell.file:

    structural_curve_members = ifc4_arch_file.by_type(
        type="IfcStructuralCurveMember",
        include_subtypes=False,
    )

    for structural_curve_member in structural_curve_members:

        # Get assigned product
        assigned_product = (
            ifcplus.util.structural.get_assigned_product_of_structural_item(
                structural_item=structural_curve_member
            )
        )
        assert assigned_product

        # Create Element
        decomposing_element_of_assigned_product = ifcopenshell.api.root.create_entity(
            file=ifc4_arch_file,
            ifc_class=assigned_product.is_a(),
            name=structural_curve_member.Name,
            predefined_type=None,
        )
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_arch_file,
            products=[decomposing_element_of_assigned_product],
            relating_object=assigned_product,
        )
        ifcplus.api.placement.edit_object_placement(
            product=decomposing_element_of_assigned_product,
            place_object_relative_to_parent=True,
        )

        # Get points
        p1, p2, p3 = (
            ifcplus.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
                linear_structural_curve_member=structural_curve_member
            )
        )

        # Calculate Axes
        z_axis = np.array(p2) - np.array(p1)
        y_axis = np.array(p3) - np.array(p1)
        x_axis = np.cross(y_axis, z_axis)

        # Calculate length
        length = float(np.linalg.norm(z_axis))

        # Get ProfileDef
        if view_option == "Extruded":
            material_profile_set = ifcopenshell.util.element.get_material(
                element=assigned_product,
                should_skip_usage=True,
            )
            assert isinstance(material_profile_set, ifcopenshell.entity_instance)
            profile_def = material_profile_set.MaterialProfiles[0].Profile
        else:
            profile_def = ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_arch_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[size_of_wireframe_bodies, size_of_wireframe_bodies],
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            )

        # Add and assign representation
        representation_item = ifcplus.api.geometry.add_extruded_area_solid(
            ifc4_file=ifc4_arch_file,
            swept_area=profile_def,
            depth=length,
        )
        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_arch_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type="SweptSolid",
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[representation_item],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_arch_file,
            product=decomposing_element_of_assigned_product,
            representation=shape_model,
        )

        # Edit Placement
        ifcplus.api.placement.edit_object_placement(
            product=decomposing_element_of_assigned_product,
            repositioned_origin=p1,
            repositioned_z_axis=tuple(z_axis.tolist()),
            repositioned_x_axis=tuple(x_axis.tolist()),
            place_object_relative_to_parent=True,
        )

    return ifc4_arch_file


def recreate_structural_point_connections(
    ifc4_arch_file: ifcopenshell.file,
    view_option: VIEW_OPTION = "Extruded",
    size_of_node_bodies: float = 0.1,
) -> ifcopenshell.file:

    # Add Body Representation for each IfcStructuralPointConnection
    structural_point_connections = ifc4_arch_file.by_type(
        type="IfcStructuralPointConnection", include_subtypes=False
    )
    for structural_point_connection in structural_point_connections:
        if view_option == "Extruded":
            pass
        elif view_option == "Wireframe_3D":

            # Create Element
            proxy_element_for_node = ifcopenshell.api.root.create_entity(
                file=ifc4_arch_file,
                ifc_class="IfcBuildingElementProxy",
                name=structural_point_connection.Name,
                predefined_type=None,
            )
            site = ifc4_arch_file.by_type(type="IfcSite", include_subtypes=False)[0]
            ifcopenshell.api.spatial.assign_container(
                file=ifc4_arch_file,
                products=[proxy_element_for_node],
                relating_structure=site,
            )
            ifcplus.api.placement.edit_object_placement(
                product=proxy_element_for_node,
                place_object_relative_to_parent=True,
            )

            # Get point
            coordinates_of_node = (
                ifcplus.util.structural.get_coordinates_of_structural_point_connection(
                    structural_point_connection=structural_point_connection
                )
            )

            # Add and assign representation
            block = ifcplus.api.geometry.add_block(  # Block
                ifc4_file=ifc4_arch_file,
                length=size_of_node_bodies,
                width=size_of_node_bodies,
                height=size_of_node_bodies,
                repositioned_origin=(
                    -size_of_node_bodies / 2.0,
                    -size_of_node_bodies / 2.0,
                    -size_of_node_bodies / 2.0,
                ),
            )

            csg_solid = ifcplus.api.geometry.add_csg_solid(
                boolean_result_or_primitive=block,
            )

            representation_type = ifcopenshell.util.representation.guess_type(
                items=[csg_solid]
            )
            assert isinstance(representation_type, str)

            shape_model = ifcplus.api.geometry.add_shape_model(
                ifc4_file=ifc4_arch_file,
                shape_model_class="IfcShapeRepresentation",
                representation_identifier="Body",
                representation_type=representation_type,
                items=[csg_solid],
            )
            ifcopenshell.api.geometry.assign_representation(
                file=ifc4_arch_file,
                product=proxy_element_for_node,
                representation=shape_model,
            )

            # Edit Element Placement
            ifcplus.api.placement.edit_object_placement(
                product=proxy_element_for_node,
                repositioned_origin=coordinates_of_node,
                place_object_relative_to_parent=True,
            )

            # Add Color
            ifcplus.api.style.assign_color_to_element(
                element=proxy_element_for_node,
                rgb_triplet=(0.0, 0.0, 0.0),
            )

    return ifc4_arch_file
