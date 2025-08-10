# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import inlbim.util.geometry
import numpy as np
import ifcopenshell.util.representation


def get_structural_items_assigned_to_specified_element_class(
    ifc4_sav_file: ifcopenshell.file,
    ifc_element_class: str,
) -> list[ifcopenshell.entity_instance]:

    strucutral_members = []

    for structural_member in ifc4_sav_file.by_type(
        type="IfcStructuralMember",
        include_subtypes=True,
    ):
        assigned_product = get_assigned_product_of_structural_item(
            structural_item=structural_member,
        )
        if not isinstance(assigned_product, ifcopenshell.entity_instance):
            continue
        if assigned_product.is_a(ifc_element_class):
            strucutral_members.append(structural_member)

    return strucutral_members


def get_assigned_product_of_structural_item(
    structural_item: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    assigned_product = None
    for assignment in structural_item.HasAssignments:
        if assignment.is_a("IfcRelAssignsToProduct"):
            assigned_product = assignment.RelatingProduct
            break

    return assigned_product


def get_structural_analysis_model_of_structural_item(
    structural_item: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    structural_analysis_model = None
    for assignment in structural_item.HasAssignments:
        if assignment.is_a("IfcRelAssignsToGroup"):
            relating_group = assignment.RelatingGroup
            if isinstance(relating_group, ifcopenshell.entity_instance):
                if relating_group.is_a("IfcStructuralAnalysisModel"):
                    structural_analysis_model = relating_group
                    break

    return structural_analysis_model


def get_vertex_point_of_structural_point_connection(
    structural_point_connection: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Get VertexPoint of StructuralPointConnection

    Args:
        structural_point_connection (ifcopenshell.entity_instance):
        IfcStructuralPointConnection
    """

    vertex_point = structural_point_connection.Representation.Representations[0].Items[
        0
    ]

    return vertex_point


def get_coordinates_of_structural_point_connection(
    structural_point_connection: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:

    # Get VertexPoint of StructuralPointConnection
    vertex_point = get_vertex_point_of_structural_point_connection(
        structural_point_connection=structural_point_connection,
    )

    # Get coordinates of VertexPoint of StructuralPointConnection
    coordinates_of_vertex_point = inlbim.util.geometry.get_coordinates_of_vertex_point(
        vertex_point=vertex_point,
    )

    return coordinates_of_vertex_point


def two_structural_point_connections_are_coincident(
    structural_point_connection_1: ifcopenshell.entity_instance,
    structural_point_connection_2: ifcopenshell.entity_instance,
    tolerance: float,
) -> bool:

    coordinates_of_node_1 = get_coordinates_of_structural_point_connection(
        structural_point_connection=structural_point_connection_1,
    )
    coordinates_of_node_2 = get_coordinates_of_structural_point_connection(
        structural_point_connection=structural_point_connection_2,
    )
    distance = np.linalg.norm(
        np.array(coordinates_of_node_1) - np.array(coordinates_of_node_2)
    )

    if distance <= tolerance:
        return True
    else:
        return False


def get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
    triangular_structural_surface_member: ifcopenshell.entity_instance,
) -> list[tuple[float, float, float]]:

    topology_representation = ifcopenshell.util.representation.get_representation(
        element=triangular_structural_surface_member,
        context="Model",
        subcontext="Reference",
        target_view="MODEL_VIEW",
    )
    assert topology_representation

    face_surface = topology_representation.Items[0]

    face_outer_bound = face_surface.Bounds[0]

    edge_list = face_outer_bound.Bound.EdgeList

    points = []
    for oriented_edge in edge_list:
        point = oriented_edge.EdgeStart.VertexGeometry.Coordinates
        points.append(point)

    return points


def get_coordinates_of_points_of_linear_structural_curve_member(
    linear_structural_curve_member: ifcopenshell.entity_instance,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:

    topology_representation = ifcopenshell.util.representation.get_representation(
        element=linear_structural_curve_member,
        context="Model",
        subcontext="Reference",
        target_view="MODEL_VIEW",
    )
    assert topology_representation

    edge = topology_representation.Items[0]

    axis = linear_structural_curve_member.Axis.DirectionRatios

    p1 = edge.EdgeStart.VertexGeometry.Coordinates
    p2 = edge.EdgeEnd.VertexGeometry.Coordinates

    p3 = tuple(float(val) for val in (np.array(p1) + np.array(axis) * 1.0).tolist())
    assert len(p3) == 3

    return p1, p2, p3


def get_ordered_structural_point_connections_of_linear_structural_curve_member(
    linear_structural_curve_member: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance]:

    topology_representation = ifcopenshell.util.representation.get_representation(
        element=linear_structural_curve_member,
        context="Model",
        subcontext="Reference",
        target_view="MODEL_VIEW",
    )
    assert topology_representation

    edge = topology_representation.Items[0]
    vertex_points = [edge.EdgeStart, edge.EdgeEnd]

    # ifc4_sav_file = linear_structural_curve_member.file
    structural_points_connections = []
    for vertex_point in vertex_points:
        # references = ifc4_sav_file.get_inverse(inst=vertex_point)
        # topology_representation = None
        # for reference in references:
        #     if reference.is_a("IfcTopologyRepresentation"):
        #         topology_representation = reference
        # assert isinstance(topology_representation, ifcopenshell.entity_instance)
        # product_definition_shape = topology_representation.OfProductRepresentation[0]
        # structural_point_connection = product_definition_shape.ShapeOfProduct[0]
        structural_point_connection = get_structural_point_connection_of_vertex_point(
            vertex_point=vertex_point
        )
        structural_points_connections.append(structural_point_connection)

    return structural_points_connections


def get_ordered_structural_point_connections_of_triangular_structural_surface_member(
    triangular_structural_surface_member: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance]:

    topology_representation = ifcopenshell.util.representation.get_representation(
        element=triangular_structural_surface_member,
        context="Model",
        subcontext="Reference",
        target_view="MODEL_VIEW",
    )
    assert topology_representation

    face_surface = topology_representation.Items[0]
    face_outer_bound = face_surface.Bounds[0]
    edge_list = face_outer_bound.Bound.EdgeList
    vertex_points = []
    for oriented_edge in edge_list:
        vertex_point = oriented_edge.EdgeStart
        vertex_points.append(vertex_point)

    # ifc4_sav_file = triangular_structural_surface_member.file
    structural_points_connections = []
    for vertex_point in vertex_points:
        # references = ifc4_sav_file.get_inverse(inst=vertex_point)
        # topology_representation = None
        # for reference in references:
        #     if reference.is_a("IfcTopologyRepresentation"):
        #         topology_representation = reference
        # assert isinstance(topology_representation, ifcopenshell.entity_instance)
        # product_definition_shape = topology_representation.OfProductRepresentation[0]
        # structural_point_connection = product_definition_shape.ShapeOfProduct[0]
        structural_point_connection = get_structural_point_connection_of_vertex_point(
            vertex_point=vertex_point
        )
        structural_points_connections.append(structural_point_connection)

    return structural_points_connections


def get_structural_point_connection_of_vertex_point(
    vertex_point: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    ifc4_sav_file = vertex_point.file
    references = ifc4_sav_file.get_inverse(inst=vertex_point)
    topology_representation = None
    for reference in references:
        if reference.is_a("IfcTopologyRepresentation"):
            topology_representation = reference
    assert isinstance(topology_representation, ifcopenshell.entity_instance)
    product_definition_shape = topology_representation.OfProductRepresentation[0]
    structural_point_connection = product_definition_shape.ShapeOfProduct[0]

    return structural_point_connection


def select_structural_point_connections(
    ifc4_sav_file: ifcopenshell.file,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    z_min: float,
    z_max: float,
) -> list[ifcopenshell.entity_instance]:

    selected_structural_point_connections = []

    for structural_point_connection in ifc4_sav_file.by_type(
        type="IfcStructuralPointConnection",
        include_subtypes=False,
    ):
        coordinates_of_structural_point_connection = (
            get_coordinates_of_structural_point_connection(
                structural_point_connection=structural_point_connection
            )
        )
        x_val, y_val, z_val = coordinates_of_structural_point_connection
        if not x_min <= x_val <= x_max:
            continue
        if not y_min <= y_val <= y_max:
            continue
        if not z_min <= z_val <= z_max:
            continue
        selected_structural_point_connections.append(structural_point_connection)

    return selected_structural_point_connections
