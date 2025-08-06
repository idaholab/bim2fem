# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import inlbim.util.geometry
import numpy as np
import ifcopenshell.util.representation


def get_assigned_product_of_structural_item(
    structural_item: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    assigned_product = None
    for assignment in structural_item.HasAssignments:
        if assignment.is_a("IfcRelAssignsToProduct"):
            assigned_product = assignment.RelatingProduct
            break

    return assigned_product


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


def get_outer_bound_points_of_structural_surface_member(
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


def get_three_points_of_linear_structural_curve_member(
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
