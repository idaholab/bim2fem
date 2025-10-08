# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.util.representation
from typing import Literal
import numpy as np
import bim2fem.ifcplus.api.profile
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.util.representation
from ifcopenshell.util.representation import (
    REPRESENTATION_IDENTIFIER,
    CONTEXT_TYPE,
    TARGET_VIEW,
)
import bim2fem.ifcplus.util.geometry


FACE_BOUND_CLASS = Literal["IfcFaceOuterBound", "IfcFaceBound"]

SHAPE_MODEL_CLASS = Literal["IfcShapeRepresentation", "IfcTopologyRepresentation"]

BOOLEAN_OPERATOR = Literal["DIFFERENCE", "INTERSECTION", "UNION"]


def add_shape_model(
    ifc4_file: ifcopenshell.file,
    shape_model_class: SHAPE_MODEL_CLASS,
    representation_identifier: REPRESENTATION_IDENTIFIER,
    representation_type: str,
    context_type: CONTEXT_TYPE = "Model",
    target_view: TARGET_VIEW = "MODEL_VIEW",
    items=[ifcopenshell.entity_instance],
):
    """Add an IfcShapeModel. The IfcShapeModel may either be an IfcShapeRepresentation
    or an IfcTopologyRepresentation.
    """

    subcontext = ifcopenshell.util.representation.get_context(
        ifc_file=ifc4_file,
        subcontext=representation_identifier,
        context=context_type,
        target_view=target_view,
    )
    if subcontext is None:
        model3d_context = ifcopenshell.util.representation.get_context(
            ifc_file=ifc4_file,
            subcontext=None,
            context=context_type,
            target_view=None,
        )
        subcontext = ifcopenshell.api.context.add_context(
            file=ifc4_file,
            context_identifier=representation_identifier,
            context_type=context_type,
            target_view=target_view,
            parent=model3d_context,
        )

    if shape_model_class == "IfcShapeRepresentation":
        shape_model = ifc4_file.createIfcShapeRepresentation(
            subcontext,
            subcontext.ContextIdentifier,  # i.e, Box
            representation_type,  # i.e, BoundingBox
            items,
        )
    else:
        shape_model = ifc4_file.createIfcTopologyRepresentation(
            subcontext,
            subcontext.ContextIdentifier,  # i.e., Reference
            representation_type,  # i.e, FaceSurface
            items,
        )

    return shape_model


def add_csg_solid(
    boolean_result_or_primitive: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Adds an IfcCsgSolid"""

    ifc4_file = boolean_result_or_primitive.file

    csg_solid = ifc4_file.createIfcCsgSolid(boolean_result_or_primitive)

    return csg_solid


def add_block(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Adds an IfcBlock"""

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    block = ifc4_file.createIfcBlock(
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        length,
        width,
        height,
    )

    return block


def add_rectangular_pyramid(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    rect_pyramid = ifc4_file.createIfcRectangularPyramid(
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        length,
        width,
        height,
    )

    return rect_pyramid


def add_cylindrical_extruded_area_solid(
    ifc4_file: ifcopenshell.file,
    radius: float,
    extrusion_depth: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Add cylindrical IfcExtrudedAreaSolid"""

    profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
        ifc4_file=ifc4_file,
        profile_class="IfcCircleProfileDef",
        dimensions=[radius],
        check_for_duplicate=True,
    )

    extruded_area_solid = add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile,
        extrusion_depth=extrusion_depth,
        repositioned_origin=repositioned_origin,
        repositioned_z_axis=repositioned_z_axis,
        repositioned_x_axis=repositioned_x_axis,
    )

    return extruded_area_solid


def add_sphere(
    ifc4_file: ifcopenshell.file,
    radius: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Add an IfcSphere"""

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    sphere = ifc4_file.createIfcSphere(
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        radius,
    )

    return sphere


def add_bounding_box(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    corner_coordinates: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Add an IfcBoundingBox"""

    bounding_box = ifc4_file.createIfcBoundingBox(
        ifc4_file.createIfcCartesianPoint(corner_coordinates),
        length,
        width,
        height,
    )

    return bounding_box


def add_extruded_area_solid_tapered(
    ifc4_file: ifcopenshell.file,
    profile_start: ifcopenshell.entity_instance,
    profile_end: ifcopenshell.entity_instance,
    extrusion_depth: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
    extruded_direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> ifcopenshell.entity_instance:
    """Add an IfcExtrudedAreaSolidTapered"""

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    extruded_area_solid = ifc4_file.createIfcExtrudedAreaSolidTapered(
        profile_start,
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        ifc4_file.createIfcDirection(extruded_direction),
        extrusion_depth,
        profile_end,
    )

    return extruded_area_solid


def add_extruded_area_solid(
    ifc4_file: ifcopenshell.file,
    profile: ifcopenshell.entity_instance,
    extrusion_depth: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
    extruded_direction: tuple[float, float, float] = (0.0, 0.0, 1.0),
) -> ifcopenshell.entity_instance:
    """Add an IfcExtrudedAreaSolid"""

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    extruded_area_solid = ifc4_file.createIfcExtrudedAreaSolid(
        profile,
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        ifc4_file.createIfcDirection(extruded_direction),
        extrusion_depth,
    )

    return extruded_area_solid


def add_revolved_area_solid(
    ifc4_file: ifcopenshell.file,
    profile: ifcopenshell.entity_instance,
    central_angle_of_curvature: float,
    center_of_curvature_in_object_xy_plane: tuple[float, float],
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Add an IfcRevolvedAreaSolid"""

    center_of_curvature_in_object_xyz_coordinates = (
        center_of_curvature_in_object_xy_plane[0],
        center_of_curvature_in_object_xy_plane[1],
        0.0,
    )

    object_z_axis = (0.0, 0.0, 1.0)

    direction_of_axis_of_rotation = (
        bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
            vector1=object_z_axis, vector2=center_of_curvature_in_object_xyz_coordinates
        )
    )

    repositioned_z_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_z_axis)
    )
    repositioned_x_axis_normalized = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(vector=repositioned_x_axis)
    )

    revolved_area_solid = ifc4_file.createIfcRevolvedAreaSolid(
        profile,
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(repositioned_origin),
            ifc4_file.createIfcDirection(repositioned_z_axis_normalized),
            ifc4_file.createIfcDirection(repositioned_x_axis_normalized),
        ),
        ifc4_file.createIfcAxis1Placement(
            ifc4_file.createIfcCartesianPoint(
                center_of_curvature_in_object_xyz_coordinates
            ),
            ifc4_file.createIfcDirection(direction_of_axis_of_rotation),
        ),
        central_angle_of_curvature,
    )

    return revolved_area_solid


def add_faceted_brep(
    ifc4_file: ifcopenshell.file,
    points: list[tuple[float, float, float]],
    triangles: list[list[int]],
) -> ifcopenshell.entity_instance:
    """Add faceted brep representation."""

    ifc_cartesian_points = [
        ifc4_file.createIfcCartesianPoint(point) for point in points
    ]

    ifc_faces = [
        ifc4_file.createIfcFace(
            [
                ifc4_file.createIfcFaceOuterBound(
                    ifc4_file.createIfcPolyLoop(
                        [ifc_cartesian_points[index] for index in triangle]
                    ),
                    True,
                )
            ]
        )
        for triangle in triangles
    ]

    faceted_brep = ifc4_file.createIfcFacetedBrep(
        ifc4_file.createIfcClosedShell(ifc_faces)
    )

    return faceted_brep


def add_vertex_point(
    ifc4_file: ifcopenshell.file,
    point_coordinates: tuple[float, float, float],
) -> ifcopenshell.entity_instance:
    """Add an IfcVertexPoint"""

    vertex_point = ifc4_file.createIfcVertexPoint(
        ifc4_file.createIfcCartesianPoint(point_coordinates)
    )

    return vertex_point


def add_edge(
    edge_start: ifcopenshell.entity_instance,
    edge_end: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Add an IfcEdge"""

    assert edge_start.is_a("IfcVertexPoint")
    assert edge_end.is_a("IfcVertexPoint")

    ifc4_file = edge_start.file

    edge = ifc4_file.createIfcEdge(edge_start, edge_end)

    return edge


def add_curved_edge(
    vertex_point_at_point_of_curvature: ifcopenshell.entity_instance,
    vertex_point_at_point_of_tangency: ifcopenshell.entity_instance,
    center_of_curvature: tuple[float, float, float],
) -> ifcopenshell.entity_instance:
    """Add an IfcEdgeCurve"""

    assert vertex_point_at_point_of_curvature.is_a("IfcVertexPoint")
    assert vertex_point_at_point_of_tangency.is_a("IfcVertexPoint")

    ifc4_file = vertex_point_at_point_of_curvature.file

    point_of_curvature = vertex_point_at_point_of_curvature.VertexGeometry.Coordinates
    point_of_tangency = vertex_point_at_point_of_tangency.VertexGeometry.Coordinates

    radius_of_curvature = float(
        np.linalg.norm(np.array(point_of_curvature) - np.array(center_of_curvature))
    )

    horizontal_curve = (
        bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
            point_of_curvature=point_of_curvature,
            point_on_center_of_curvature_side=center_of_curvature,
            point_of_tangency=point_of_tangency,
            radius_of_curvature=radius_of_curvature,
        )
    )

    z_axis = horizontal_curve.direction_of_axis_of_rotation

    x_axis = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
        p1=horizontal_curve.point_of_curvature,
        p2=horizontal_curve.point_of_tangency,
    )

    position = ifc4_file.createIfcAxis2Placement3D(
        ifc4_file.createIfcCartesianPoint(center_of_curvature),
        ifc4_file.createIfcDirection(z_axis),
        ifc4_file.createIfcDirection(x_axis),
    )

    edge_geometry = ifc4_file.createIfcCircle(
        position,
        radius_of_curvature,
    )

    same_sense = True

    edge_curve = ifc4_file.createIfcEdgeCurve(
        vertex_point_at_point_of_curvature,
        vertex_point_at_point_of_tangency,
        edge_geometry,
        same_sense,
    )

    return edge_curve


def add_face_bound(
    face_bound_class: FACE_BOUND_CLASS,
    vertex_points_of_bound: list[ifcopenshell.entity_instance],
) -> ifcopenshell.entity_instance:
    """Add an IfcFaceBound"""

    ifc4_file = vertex_points_of_bound[0].file

    edge_list = []
    for index in range(len(vertex_points_of_bound)):
        v1 = vertex_points_of_bound[index]
        if index + 1 == len(vertex_points_of_bound):
            v2 = vertex_points_of_bound[0]
        else:
            v2 = vertex_points_of_bound[index + 1]
        edge = add_edge(edge_start=v1, edge_end=v2)
        oriented_edge = ifc4_file.create_entity(
            type="IfcOrientedEdge",
            EdgeElement=edge,
            Orientation=True,
        )
        edge_list.append(oriented_edge)
    edge_loop = ifc4_file.create_entity(
        type="IfcEdgeLoop",
        EdgeList=edge_list,
    )

    face_bound = ifc4_file.create_entity(
        type=face_bound_class,
        Bound=edge_loop,
        Orientation=True,
    )

    return face_bound


def add_face_surface(
    vertex_points_of_outer_bound: list[ifcopenshell.entity_instance],
    vertex_points_of_inner_bounds: list[list[ifcopenshell.entity_instance]],
) -> ifcopenshell.entity_instance:
    """Add an IfcFaceSurface"""

    ifc4_file = vertex_points_of_outer_bound[0].file

    p1 = vertex_points_of_outer_bound[0].VertexGeometry.Coordinates
    p2 = vertex_points_of_outer_bound[1].VertexGeometry.Coordinates
    p3 = vertex_points_of_outer_bound[2].VertexGeometry.Coordinates

    v12 = np.array(p2) - np.array(p1)
    v23 = np.array(p3) - np.array(p2)
    if np.linalg.norm(np.cross(v12, v23)) == 0:
        exit("Warning: zero area during FaceSurface creation. Aborted.")
    z_axis_of_plane = np.cross(v12, v23) * 1 / np.linalg.norm(np.cross(v12, v23))
    x_axis_of_plane = v12 * 1 / np.linalg.norm(v12)

    position_of_plane = ifc4_file.createIfcAxis2Placement3D(
        ifc4_file.createIfcCartesianPoint(p1),
        ifc4_file.createIfcDirection(z_axis_of_plane.tolist()),
        ifc4_file.createIfcDirection(x_axis_of_plane.tolist()),
    )

    plane = ifc4_file.create_entity(
        type="IfcPlane",
        Position=position_of_plane,
    )

    face_outer_bound = add_face_bound(
        face_bound_class="IfcFaceOuterBound",
        vertex_points_of_bound=vertex_points_of_outer_bound,
    )

    face_inner_bounds = []
    for vertex_points_of_inner_bound in vertex_points_of_inner_bounds:
        face_bound = add_face_bound(
            face_bound_class="IfcFaceBound",
            vertex_points_of_bound=vertex_points_of_inner_bound,
        )
        face_inner_bounds.append(face_bound)

    face_surface = ifc4_file.create_entity(
        type="IfcFaceSurface",
        Bounds=[face_outer_bound] + face_inner_bounds,
        FaceSurface=plane,
        SameSense=True,
    )

    return face_surface
