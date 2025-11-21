# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.material
import ifcopenshell.api.structural
import ifcplus.api.geometry
import ifcplus.util.geometry
import ifcplus.util.structural
import ifcplus.util.project
import ifcopenshell.api.project
import ifcplus.api.material
import math
import numpy as np
import ifcplus.api.structural
import ifcopenshell.util.element
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell
import ifcopenshell.api.owner
import ifcopenshell.guid


def assign_structural_items_to_product(
    file: ifcopenshell.file,
    structural_items: list[ifcopenshell.entity_instance],
    product: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:
    """Assigns IfcStructuralItems to an IfcProduct

    If an object is already assigned to the product, it will not be assigned
    twice.

    :param objects: A list of IfcObjects to assign to the product
    :param product: The IfcProduct to assign the objects to
    :return: The IfcRelAssignsToProduct relationship
        or `None` if `objects` was empty list.

    Example:

    .. code:: python

        product = ifcopenshell.api.root.create_entity(file, "IfcBeam")
        ifcopenshell.api.product.assign_product(file,
            objects=model.by_type("IfcStructuralCurveMember"), product=product)
    """
    if not structural_items:
        return

    referenced_by: tuple[ifcopenshell.entity_instance, ...]
    if not (referenced_by := product.ReferencedBy):
        return file.create_entity(
            "IfcRelAssignsToProduct",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": structural_items,
                "RelatingProduct": product,
            },
        )
    rel = referenced_by[0]
    related_objects = set(rel.RelatedObjects) or set()
    objects_set = set(structural_items)
    if objects_set.issubset(related_objects):
        return rel
    rel.RelatedObjects = list(related_objects | objects_set)
    ifcopenshell.api.owner.update_owner_history(file=file, element=rel)
    return rel


def add_structural_analysis_model(
    ifc4_file: ifcopenshell.file,
    name: str | None = None,
    predefined_type: str | None = "LOADING_3D",
):
    """Create IfcStructuralAnalysisModel"""

    structural_analysis_model = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcStructuralAnalysisModel",
        name=name,
        predefined_type=predefined_type,
    )

    shared_placement = ifc4_file.createIfcLocalPlacement()

    shared_placement.RelativePlacement = ifc4_file.createIfcAxis2Placement3D(
        ifc4_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
        ifc4_file.createIfcDirection((0.0, 0.0, 1.0)),
        ifc4_file.createIfcDirection((1.0, 0.0, 0.0)),
    )

    structural_analysis_model.SharedPlacement = shared_placement

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[structural_analysis_model],
        relating_context=project,
    )

    return structural_analysis_model


def create_linear_structural_curve_member(
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    orientation_point: tuple[float, float, float],
    profile: ifcopenshell.entity_instance,
    material: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    structural_curve_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    product_to_be_assigned_to: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:
    """Create Linear IfcStructuralCurveMember"""

    ifc4_file = profile.file

    if structural_curve_member is None:
        structural_curve_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStructuralCurveMember",
            name=name,
            predefined_type="NOTDEFINED",
        )
        if name is None:
            name = f"StructuralCurveMember-{structural_curve_member.id()}"
            structural_curve_member.Name = name

    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_curve_member],
        structural_analysis_model=structural_analysis_model,
    )

    structural_curve_member.ObjectPlacement = structural_analysis_model.SharedPlacement

    material_profile_set = (
        ifcplus.api.material.add_material_profile_set_with_single_material_profile(
            material=material,
            profile=profile,
            check_for_duplicate=True,
        )
    )

    material_profile_set_usage = ifc4_file.create_entity(
        type="IfcMaterialProfileSetUsage",
        ForProfileSet=material_profile_set,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[structural_curve_member],
        material=material_profile_set_usage,
    )

    x_axis = tuple((np.array(end_point) - np.array(start_point)).tolist())

    vector_from_start_point_to_orientation_point = tuple(
        (np.array(orientation_point) - np.array(start_point)).tolist()
    )

    y_axis = tuple(
        np.cross(
            vector_from_start_point_to_orientation_point,
            x_axis,
        ).tolist()
    )

    z_axis = ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
        vector1=x_axis,
        vector2=y_axis,
        unit_normalize=True,
    )

    structural_curve_member.Axis = ifc4_file.createIfcDirection(z_axis)

    vertex_points = []
    for point in [start_point, end_point]:
        vertex_points.append(
            ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=point,
            )
        )

    edge = ifcplus.api.geometry.add_edge(
        edge_start_as_vertex_point=vertex_points[0],
        edge_end_as_vertex_point=vertex_points[1],
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[edge]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[edge],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_curve_member,
        representation=shape_representation,
    )

    for vertex_point in vertex_points:
        structural_point_connection = create_structural_point_connection(
            vertex_point=vertex_point,
            structural_analysis_model=structural_analysis_model,
            name=None,
        )
        ifcopenshell.api.structural.add_structural_member_connection(
            file=ifc4_file,
            relating_structural_member=structural_curve_member,
            related_structural_connection=structural_point_connection,
        )

    if product_to_be_assigned_to:
        assign_structural_items_to_product(
            file=ifc4_file,
            structural_items=[structural_curve_member],
            product=product_to_be_assigned_to,
        )

    return structural_curve_member


def create_curved_structural_curve_member(
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    orientation_point: tuple[float, float, float],
    point_defining_plane_of_arc_and_center_of_curvature_side: tuple[
        float, float, float
    ],
    radius_of_curvature: float,
    profile: ifcopenshell.entity_instance,
    material: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    structural_curve_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    product_to_be_assigned_to: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:
    """Create Curved IfcStructuralCurveMember"""

    ifc4_file = profile.file

    if structural_curve_member is None:
        structural_curve_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStructuralCurveMember",
            name=name,
            predefined_type="NOTDEFINED",
        )
        if name is None:
            name = f"StructuralCurveMember-{structural_curve_member.id()}"
            structural_curve_member.Name = name

    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_curve_member],
        structural_analysis_model=structural_analysis_model,
    )

    structural_curve_member.ObjectPlacement = structural_analysis_model.SharedPlacement

    material_profile_set = (
        ifcplus.api.material.add_material_profile_set_with_single_material_profile(
            material=material,
            profile=profile,
            check_for_duplicate=True,
        )
    )

    material_profile_set_usage = ifc4_file.create_entity(
        type="IfcMaterialProfileSetUsage",
        ForProfileSet=material_profile_set,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[structural_curve_member],
        material=material_profile_set_usage,
    )

    horizontal_curve = ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_on_center_of_curvature_side=point_defining_plane_of_arc_and_center_of_curvature_side,
        point_of_curvature=start_point,
        point_of_tangency=end_point,
        radius_of_curvature=radius_of_curvature,
    )

    x_axis = tuple((np.array(end_point) - np.array(start_point)).tolist())

    vector_from_start_point_to_orientation_point = tuple(
        (np.array(orientation_point) - np.array(start_point)).tolist()
    )

    y_axis = tuple(
        np.cross(
            vector_from_start_point_to_orientation_point,
            x_axis,
        ).tolist()
    )

    z_axis = ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
        vector1=x_axis,
        vector2=y_axis,
        unit_normalize=True,
    )

    structural_curve_member.Axis = ifc4_file.createIfcDirection(z_axis)

    vertex_points = []
    for point in [
        horizontal_curve.point_of_curvature,
        horizontal_curve.point_of_tangency,
    ]:
        vertex_points.append(
            ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file, point_coordinates=point
            )
        )

    edge_curve = ifcplus.api.geometry.add_edge_curve(
        point_of_curvature_as_vertex_point=vertex_points[0],
        point_of_tangency_as_vertex_point=vertex_points[1],
        point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve.center_of_curvature,
        radius_of_curvature=horizontal_curve.radius_of_curvature,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[edge_curve]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[edge_curve],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_curve_member,
        representation=shape_representation,
    )

    for vertex_point in vertex_points:
        structural_point_connection = create_structural_point_connection(
            vertex_point=vertex_point,
            structural_analysis_model=structural_analysis_model,
            name=None,
        )
        ifcopenshell.api.structural.add_structural_member_connection(
            file=ifc4_file,
            relating_structural_member=structural_curve_member,
            related_structural_connection=structural_point_connection,
        )

    if product_to_be_assigned_to:
        assign_structural_items_to_product(
            file=ifc4_file,
            structural_items=[structural_curve_member],
            product=product_to_be_assigned_to,
        )

    return structural_curve_member


def create_structural_surface_member(
    outer_profile: list[tuple[float, float, float]],
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    structural_analysis_model: ifcopenshell.entity_instance,
    inner_profiles: list[list[tuple[float, float, float]]] = [],
    structural_surface_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    corresponding_product: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:
    """Create IfcStructuralSurfaceMember"""

    ifc4_file = materials[0].file

    if structural_surface_member is None:
        structural_surface_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStructuralSurfaceMember",
            name=name,
            predefined_type="NOTDEFINED",
        )
    if name is None and structural_surface_member.Name is None:
        name = f"StructuralSurfaceMember-{structural_surface_member.id()}"
        structural_surface_member.Name = name

    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_surface_member],
        structural_analysis_model=structural_analysis_model,
    )

    structural_surface_member.ObjectPlacement = (
        structural_analysis_model.SharedPlacement
    )

    material_layer_set = ifcplus.api.material.add_material_layer_set(
        materials=materials,
        thicknesses=thicknesses,
        check_for_duplicate=True,
    )

    total_thickness = 0.0
    for material_layer in material_layer_set.MaterialLayers:
        total_thickness += material_layer.LayerThickness

    material_layer_set_usage = ifc4_file.create_entity(
        type="IfcMaterialLayerSetUsage",
        ForLayerSet=material_layer_set,
        LayerSetDirection="AXIS3",
        DirectionSense="POSITIVE",
        OffsetFromReferenceLine=-total_thickness / 2,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[structural_surface_member],
        material=material_layer_set_usage,
    )

    structural_surface_member.Thickness = total_thickness

    vertex_points_of_outer_profile = []
    for point in outer_profile:
        vertex_points_of_outer_profile.append(
            ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=point,
            )
        )

    vertex_points_of_inner_profiles = []
    for inner_profile in inner_profiles:
        vertex_points_of_inner_profile = []
        for point in inner_profile:
            vertex_points_of_inner_profile.append(
                ifcplus.api.geometry.add_vertex_point(
                    ifc4_file=ifc4_file,
                    point_coordinates=point,
                )
            )
        vertex_points_of_inner_profiles.append(vertex_points_of_inner_profile)

    face_surface = ifcplus.api.geometry.add_face_surface(
        vertex_points_of_outer_bound=vertex_points_of_outer_profile,
        vertex_points_of_inner_bounds=vertex_points_of_inner_profiles,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[face_surface]),
        ),  # Face
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[face_surface],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_surface_member,
        representation=shape_representation,
    )

    for vertex_point in vertex_points_of_outer_profile:
        structural_point_connection = create_structural_point_connection(
            vertex_point=vertex_point,
            structural_analysis_model=structural_analysis_model,
            name=None,
        )
        ifcopenshell.api.structural.add_structural_member_connection(
            file=ifc4_file,
            relating_structural_member=structural_surface_member,
            related_structural_connection=structural_point_connection,
        )
    for vertex_points_of_inner_profile in vertex_points_of_inner_profiles:
        for vertex_point in vertex_points_of_inner_profile:
            structural_point_connection = create_structural_point_connection(
                vertex_point=vertex_point,
                structural_analysis_model=structural_analysis_model,
                name=None,
            )
            ifcopenshell.api.structural.add_structural_member_connection(
                file=ifc4_file,
                relating_structural_member=structural_surface_member,
                related_structural_connection=structural_point_connection,
            )

    if corresponding_product:
        assign_structural_items_to_product(
            file=ifc4_file,
            structural_items=[structural_surface_member],
            product=corresponding_product,
        )

    return structural_surface_member


def create_structural_point_connection(
    vertex_point: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    name: str | None = None,
) -> ifcopenshell.entity_instance:
    """Create IfcStructuralPointConnection"""

    ifc4_file = vertex_point.file

    structural_point_connection = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcStructuralPointConnection",
        name=name,
    )
    if name is None:
        name = f"Node-{structural_point_connection.id()}"
        structural_point_connection.Name = name

    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_point_connection],
        structural_analysis_model=structural_analysis_model,
    )

    structural_point_connection.ObjectPlacement = (
        structural_analysis_model.SharedPlacement
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[vertex_point]),
        ),  # Vertex
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[vertex_point],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_point_connection,
        representation=shape_representation,
    )

    return structural_point_connection


def merge_all_coincident_structural_point_connections(
    ifc4sav_file: ifcopenshell.file,
) -> ifcopenshell.file:

    model_precision = ifcplus.util.project.get_precision_of_project(
        ifc4_file=ifc4sav_file
    )

    node_groups = {}
    num_x_divisions = 8
    num_y_divisions = 8
    num_z_divisions = 8
    for x_group_num in range(num_x_divisions):
        for y_group_num in range(num_y_divisions):
            for z_group_num in range(num_z_divisions):
                group_key = f"{x_group_num}{y_group_num}{z_group_num}"
                node_groups[group_key] = []
    all_nodes = ifc4sav_file.by_type(
        type="IfcStructuralPointConnection", include_subtypes=False
    )

    x_vals = set()
    y_vals = set()
    z_vals = set()
    for node in all_nodes:
        coordinates_of_node = (
            ifcplus.util.structural.get_coordinates_of_structural_point_connection(
                structural_point_connection=node,
            )
        )
        x_vals.add(coordinates_of_node[0])
        y_vals.add(coordinates_of_node[1])
        z_vals.add(coordinates_of_node[2])
    x_val_min = min(x_vals) - 1
    x_val_max = max(x_vals) + 1
    slope_for_x = num_x_divisions / (x_val_max - x_val_min)
    y_val_min = min(y_vals) - 1
    y_val_max = max(y_vals) + 1
    slope_for_y = num_y_divisions / (y_val_max - y_val_min)
    z_val_min = min(z_vals) - 1
    z_val_max = max(z_vals) + 1
    slope_for_z = num_z_divisions / (z_val_max - z_val_min)

    for node in all_nodes:
        coordinates_of_node = (
            ifcplus.util.structural.get_coordinates_of_structural_point_connection(
                structural_point_connection=node,
            )
        )
        x_val = coordinates_of_node[0]
        x_group_num = math.floor(slope_for_x * x_val + -slope_for_x * x_val_min)
        y_val = coordinates_of_node[1]
        y_group_num = math.floor(slope_for_y * y_val + -slope_for_y * y_val_min)
        z_val = coordinates_of_node[2]
        z_group_num = math.floor(slope_for_z * z_val + -slope_for_z * z_val_min)
        group_key = f"{x_group_num}{y_group_num}{z_group_num}"
        node_groups[group_key].append(node)

    count_of_nodes_in_groups = 0
    for node_group in node_groups.values():
        count_of_nodes_in_groups += len(node_group)
    if count_of_nodes_in_groups != len(all_nodes):
        return ifc4sav_file

    all_merged_nodes = []
    for node_group in node_groups.values():
        trial_nodes = node_group
        merged_nodes = []
        for trial_node in trial_nodes:
            trial_node_is_unique = True
            for merged_node in merged_nodes:
                nodes_are_coincident = ifcplus.util.structural.two_structural_point_connections_are_coincident(
                    structural_point_connection_1=merged_node,
                    structural_point_connection_2=trial_node,
                    tolerance=model_precision,
                )
                if nodes_are_coincident:
                    trial_node_is_unique = False
                    merge_two_structural_point_connections_together(
                        replacing_structural_point_connection=merged_node,
                        replaced_structural_point_connection=trial_node,
                    )
                    break
            if trial_node_is_unique:
                merged_nodes.append(trial_node)
                all_merged_nodes.append(trial_node)

    return ifc4sav_file


def merge_two_structural_point_connections_together(
    replacing_structural_point_connection: ifcopenshell.entity_instance,
    replaced_structural_point_connection: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:

    ifc4sav_file = replacing_structural_point_connection.file

    for (
        rel_connects_structural_member
    ) in replaced_structural_point_connection.ConnectsStructuralMembers:
        rel_connects_structural_member.RelatedStructuralConnection = (
            replacing_structural_point_connection
        )

    replacing_vertex_point = (
        ifcplus.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=replacing_structural_point_connection,
        )
    )

    replaced_vertex_point = (
        ifcplus.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=replaced_structural_point_connection,
        )
    )

    entities_referencing_replaced_vertex_point = ifc4sav_file.get_inverse(
        inst=replaced_vertex_point
    )
    for entity in entities_referencing_replaced_vertex_point:
        if not isinstance(entity, ifcopenshell.entity_instance):
            continue
        elif entity.is_a() == "IfcEdge":
            if entity.EdgeStart == replaced_vertex_point:
                entity.EdgeStart = replacing_vertex_point
                continue
            elif entity.EdgeEnd == replaced_vertex_point:
                entity.EdgeEnd = replacing_vertex_point
                continue
        elif entity.is_a() == "IfcEdgeCurve":
            if entity.EdgeStart == replaced_vertex_point:
                entity.EdgeStart = replacing_vertex_point
                continue
            elif entity.EdgeEnd == replaced_vertex_point:
                entity.EdgeEnd = replacing_vertex_point
                continue

    replaced_cartesian_point = replaced_vertex_point.VertexGeometry

    replaced_product_definition_shape = (
        replaced_structural_point_connection.Representation
    )

    replaced_topology_representation = (
        replaced_product_definition_shape.Representations[0]
    )

    ifc4_file = replaced_structural_point_connection.file
    owner_history_of_replaced_structural_point_connection = (
        replaced_structural_point_connection.OwnerHistory
    )
    total_inverses_for_owner_history_of_replaced_structural_point_connection = (
        ifc4_file.get_total_inverses(
            inst=owner_history_of_replaced_structural_point_connection
        )
    )
    if total_inverses_for_owner_history_of_replaced_structural_point_connection == 1:
        replaced_owner_history = owner_history_of_replaced_structural_point_connection
    else:
        replaced_owner_history = None

    for replaced_entity in [
        replaced_cartesian_point,
        replaced_vertex_point,
        replaced_topology_representation,
        replaced_product_definition_shape,
        replaced_owner_history,
        replaced_structural_point_connection,
    ]:
        if isinstance(replaced_entity, ifcopenshell.entity_instance):
            ifc4sav_file.remove(inst=replaced_entity)

    return replacing_structural_point_connection


def translate_structural_point_connection(
    structural_point_connection: ifcopenshell.entity_instance,
    translation: tuple[float, float, float],
):

    vertex_point = (
        ifcplus.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=structural_point_connection
        )
    )

    old_coordinates = (
        ifcplus.util.structural.get_coordinates_of_structural_point_connection(
            structural_point_connection=structural_point_connection
        )
    )

    new_coordinates = (
        old_coordinates[0] + translation[0],
        old_coordinates[1] + translation[1],
        old_coordinates[2] + translation[2],
    )

    old_cartesian_point = vertex_point.VertexGeometry

    ifc4_sav_file = structural_point_connection.file

    count_of_references_to_old_cartesian_point = ifc4_sav_file.get_total_inverses(
        inst=old_cartesian_point
    )

    safe_to_edit_old_cartesian_point = count_of_references_to_old_cartesian_point == 1

    if safe_to_edit_old_cartesian_point:
        old_cartesian_point.Coordinates = new_coordinates

    else:
        new_cartesian_point = ifc4_sav_file.createIfcCartesianPoint(new_coordinates)
        vertex_point.VertexGeometry = new_cartesian_point


def divide_structural_curve_member(
    structural_curve_member: ifcopenshell.entity_instance,
    division_locations_as_proportions_of_length: list[float],
) -> list[ifcopenshell.entity_instance]:

    if len(division_locations_as_proportions_of_length) == 0:
        return [structural_curve_member]

    if all(0.0 < num < 1.0 for num in division_locations_as_proportions_of_length):
        division_locations_as_proportions_of_length = sorted(
            division_locations_as_proportions_of_length
        )
    else:
        raise ValueError(
            "All elements in the list must be between 0.0 and 1.0 (exclusive)"
        )

    original_start_point, original_end_point, original_orientation_point = (
        ifcplus.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
            linear_structural_curve_member=structural_curve_member
        )
    )

    length_of_original_member = float(
        np.linalg.norm(np.array(original_end_point) - np.array(original_start_point))
    )

    original_x_axis = (
        ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=original_start_point,
            p2=original_end_point,
        )
    )

    original_z_axis = (
        ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=original_start_point,
            p2=original_orientation_point,
        )
    )

    product_assigned_to = (
        ifcplus.util.structural.get_assigned_product_of_structural_item(
            structural_item=structural_curve_member
        )
    )

    material_profile_set = ifcopenshell.util.element.get_material(
        element=structural_curve_member,
        should_skip_usage=True,
    )
    material_profile_set = cast(ifcopenshell.entity_instance, material_profile_set)
    profile_def = material_profile_set.MaterialProfiles[0].Profile
    material = material_profile_set.MaterialProfiles[0].Material

    structural_analysis_model = (
        ifcplus.util.structural.get_structural_analysis_model_of_structural_item(
            structural_item=structural_curve_member
        )
    )

    structural_analysis_model = cast(
        ifcopenshell.entity_instance, structural_analysis_model
    )

    new_end_points = []
    for (
        division_location_as_proportion_of_length
    ) in division_locations_as_proportions_of_length + [1.0]:
        new_end_point = tuple(
            (
                np.array(original_start_point)
                + np.array(original_x_axis)
                * division_location_as_proportion_of_length
                * length_of_original_member
            ).tolist()
        )
        new_end_points.append(new_end_point)

    new_structural_curve_members = []
    new_start_point = original_start_point
    for index, new_end_point in enumerate(new_end_points):

        new_orientation_point = tuple(
            (np.array(new_start_point) + np.array(original_z_axis) * 1.0).tolist()
        )

        if index == 0:

            pass

        else:

            new_structural_curve_member = (
                ifcplus.api.structural.create_linear_structural_curve_member(
                    start_point=new_start_point,
                    end_point=new_end_point,
                    orientation_point=new_orientation_point,
                    profile=profile_def,
                    material=material,
                    structural_analysis_model=structural_analysis_model,
                    product_to_be_assigned_to=product_assigned_to,
                )
            )

            new_structural_curve_members.append(new_structural_curve_member)

        new_start_point = new_end_point

    _, original_end_node_of_whole_member = (
        ifcplus.util.structural.get_structural_point_connections_of_linear_structural_curve_member(
            linear_structural_curve_member=structural_curve_member,
        )
    )

    segment_1 = structural_curve_member

    edge_1 = segment_1.Representation.Representations[0].Items[0]

    segment_2 = new_structural_curve_members[0]

    edge_2 = segment_2.Representation.Representations[0].Items[0]

    edge_1.EdgeEnd = edge_2.EdgeStart

    start_node_of_segment_2 = (
        ifcplus.util.structural.get_structural_point_connection_of_vertex_point(
            vertex_point=edge_2.EdgeStart,
        )
    )

    for connection_relationship in segment_1.ConnectedBy:
        if not connection_relationship.is_a("IfcRelConnectsStructuralMember"):
            continue
        if (
            connection_relationship.RelatedStructuralConnection
            == original_end_node_of_whole_member
        ):
            connection_relationship.RelatedStructuralConnection = (
                start_node_of_segment_2
            )

    new_structural_curve_members = [segment_1] + new_structural_curve_members

    return new_structural_curve_members
