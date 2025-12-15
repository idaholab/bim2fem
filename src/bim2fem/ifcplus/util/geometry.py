# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.geom
import ifcopenshell
import ifcopenshell.geom
import numpy as np
from ifcopenshell.ifcopenshell_wrapper import TriangulationElement
from dataclasses import dataclass
from typing import cast
import ifcopenshell.util.placement
import bim2fem.ifcplus.util.geometry


def get_location_in_global_coordinates(
    product: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:
    local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=product.ObjectPlacement
        )
    )
    x_val = float(local_placement_in_global_coordinates[0][3])
    y_val = float(local_placement_in_global_coordinates[1][3])
    z_val = float(local_placement_in_global_coordinates[2][3])

    return x_val, y_val, z_val


def get_z_axis_in_global_coordinates(
    product: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:

    local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=product.ObjectPlacement
        )
    )
    val_1 = float(local_placement_in_global_coordinates[0][2])
    val_2 = float(local_placement_in_global_coordinates[1][2])
    val_3 = float(local_placement_in_global_coordinates[2][2])

    local_z_axis_in_global_coordinates = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(
            vector=(val_1, val_2, val_3)
        )
    )

    return local_z_axis_in_global_coordinates


def get_object_x_axis_in_global_coordinates(
    product: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:

    local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=product.ObjectPlacement
        )
    )
    val_1 = float(local_placement_in_global_coordinates[0][0])
    val_2 = float(local_placement_in_global_coordinates[1][0])
    val_3 = float(local_placement_in_global_coordinates[2][0])

    local_x_axis_in_global_coordinates = (
        bim2fem.ifcplus.util.geometry.unit_normalize_vector(
            vector=(val_1, val_2, val_3)
        )
    )

    return local_x_axis_in_global_coordinates


def get_coordinates_of_vertex_point(
    vertex_point: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:

    coordinates_of_vertex_point = vertex_point.VertexGeometry.Coordinates

    return coordinates_of_vertex_point


@dataclass
class BoundingBox:
    xmin: float
    ymin: float
    zmin: float
    xmax: float
    ymax: float
    zmax: float

    @classmethod
    def from_points(cls, points: np.ndarray) -> "BoundingBox":
        """Create from point cloud"""
        min_coords = points.min(axis=0)
        max_coords = points.max(axis=0)
        return cls(*min_coords, *max_coords)

    @classmethod
    def from_ifc_product(cls, product: ifcopenshell.entity_instance) -> "BoundingBox":
        """Create directly from IfcProduct"""
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)

        shape = cast(
            typ=TriangulationElement,
            val=ifcopenshell.geom.create_shape(settings, product),
        )

        geometry = shape.geometry

        verts = np.array(geometry.verts).reshape(-1, 3)

        xmin = float(verts.min(axis=0)[0])
        ymin = float(verts.min(axis=0)[1])
        zmin = float(verts.min(axis=0)[2])

        xmax = float(verts.max(axis=0)[0])
        ymax = float(verts.max(axis=0)[1])
        zmax = float(verts.max(axis=0)[2])

        return cls(xmin, ymin, zmin, xmax, ymax, zmax)

    @classmethod
    def from_multiple(cls, boxes: list["BoundingBox"]) -> "BoundingBox":
        """Create a bounding box that encompasses all input boxes."""

        return cls(
            xmin=min(box.xmin for box in boxes),
            ymin=min(box.ymin for box in boxes),
            zmin=min(box.zmin for box in boxes),
            xmax=max(box.xmax for box in boxes),
            ymax=max(box.ymax for box in boxes),
            zmax=max(box.zmax for box in boxes),
        )

    def contains_point(self, point: tuple[float, float, float]) -> bool:
        """Check if point is inside bounding box"""
        return (
            self.xmin <= point[0] <= self.xmax
            and self.ymin <= point[1] <= self.ymax
            and self.zmin <= point[2] <= self.zmax
        )

    def intersects(self, other: "BoundingBox") -> bool:
        """Check intersection with another bounding box"""
        return not (
            self.xmax < other.xmin
            or self.xmin > other.xmax
            or self.ymax < other.ymin
            or self.ymin > other.ymax
            or self.zmax < other.zmin
            or self.zmin > other.zmax
        )

    def union(self, other: "BoundingBox") -> "BoundingBox":
        """Compute union of two bounding boxes"""
        return BoundingBox(
            min(self.xmin, other.xmin),
            min(self.ymin, other.ymin),
            min(self.zmin, other.zmin),
            max(self.xmax, other.xmax),
            max(self.ymax, other.ymax),
            max(self.zmax, other.zmax),
        )

    def to_dict(self) -> dict:
        """For serialization"""
        return {
            "min": (self.xmin, self.ymin, self.zmin),
            "max": (self.xmax, self.ymax, self.zmax),
        }

    @property
    def corners(self) -> np.ndarray:
        """Get all 8 corners of the bounding box"""
        return np.array(
            [
                [self.xmin, self.ymin, self.zmin],
                [self.xmax, self.ymin, self.zmin],
                [self.xmax, self.ymax, self.zmin],
                [self.xmin, self.ymax, self.zmin],
                [self.xmin, self.ymin, self.zmax],
                [self.xmax, self.ymin, self.zmax],
                [self.xmax, self.ymax, self.zmax],
                [self.xmin, self.ymax, self.zmax],
            ]
        )

    @property
    def dimensions(self) -> tuple[float, float, float]:
        return (
            self.xmax - self.xmin,
            self.ymax - self.ymin,
            self.zmax - self.zmin,
        )


def calculate_angle_between_two_vectors(
    vector1: tuple[float, float, float],
    vector2: tuple[float, float, float],
) -> float:

    cos_theta = (
        np.dot(vector1, vector2)
        * 1
        / np.linalg.norm(vector1)
        * 1
        / np.linalg.norm(vector2)
    )

    theta = float(np.arccos(cos_theta))

    return theta


def calculate_unit_direction_vector_between_two_points(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
) -> tuple[float, float, float]:

    vector = tuple((np.array(p2) - np.array(p1)).tolist())
    vector_normalized = unit_normalize_vector(vector=vector)

    return vector_normalized


def calculate_cross_product_of_two_vectors(
    vector1: tuple[float, float, float],
    vector2: tuple[float, float, float],
    unit_normalize: bool = True,
) -> tuple[float, float, float]:

    cross_prod = tuple(np.cross(np.array(vector1), np.array(vector2)).tolist())

    if unit_normalize:
        cross_prod = unit_normalize_vector(vector=cross_prod)

    return cross_prod


def unit_normalize_vector(
    vector: tuple[float, float, float],
) -> tuple[float, float, float]:

    return tuple((np.array(vector) / np.linalg.norm(vector)).tolist())


class HorizontalCurve:
    def __init__(
        self,
        point_of_intersection: tuple[float, float, float],
        central_angle: float,
        radius_of_curvature: float,
        direction_of_axis_of_rotation: tuple[float, float, float],
        point_of_curvature: tuple[float, float, float],
        point_of_tangency: tuple[float, float, float],
        center_of_curvature: tuple[float, float, float],
    ):
        self.point_of_intersection = point_of_intersection
        self.central_angle = central_angle
        self.radius_of_curvature = radius_of_curvature
        self.direction_of_axis_of_rotation = direction_of_axis_of_rotation
        self.point_of_curvature = point_of_curvature
        self.point_of_tangency = point_of_tangency
        self.center_of_curvature = center_of_curvature

        self.length_of_curve = self.radius_of_curvature * self.central_angle
        self.long_chord = float(
            2 * self.radius_of_curvature * np.sin(self.central_angle / 2.0)
        )
        self.tangent_length = float(
            self.radius_of_curvature * np.tan(self.central_angle / 2.0)
        )
        self.external_distance = float(
            self.radius_of_curvature * (1 / np.cos(self.central_angle / 2.0) - 1.0)
        )
        self.middle_ordinate_distance = float(
            self.radius_of_curvature * (1 - np.cos(self.central_angle / 2.0))
        )

        unit_vector_from_CC_to_PI = calculate_unit_direction_vector_between_two_points(
            p1=self.center_of_curvature,
            p2=self.point_of_intersection,
        )
        self.point_at_midpoint_of_curve = tuple(
            (
                np.array(self.center_of_curvature)
                + np.array(unit_vector_from_CC_to_PI) * self.radius_of_curvature
            ).tolist()
        )

    @classmethod
    def from_3pt_polyline(
        cls,
        first_point: tuple[float, float, float],
        second_point: tuple[float, float, float],
        third_point: tuple[float, float, float],
        radius_of_curvature: float,
    ):

        point_of_intersection = second_point

        unit_vector_from_PC_to_PI = calculate_unit_direction_vector_between_two_points(
            p1=first_point,
            p2=point_of_intersection,
        )

        unit_vector_from_PI_to_PT = calculate_unit_direction_vector_between_two_points(
            p1=point_of_intersection,
            p2=third_point,
        )

        central_angle = calculate_angle_between_two_vectors(
            vector1=unit_vector_from_PI_to_PT,
            vector2=unit_vector_from_PC_to_PI,
        )

        axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=unit_vector_from_PC_to_PI,
            vector2=unit_vector_from_PI_to_PT,
            unit_normalize=True,
        )

        tangent_length = radius_of_curvature * np.tan(central_angle / 2)

        point_of_curvature = (
            np.array(point_of_intersection)
            - np.array(unit_vector_from_PC_to_PI) * tangent_length
        )

        point_of_tangency = (
            np.array(point_of_intersection)
            + np.array(unit_vector_from_PI_to_PT) * tangent_length
        )

        unit_vector_from_PC_to_CC = calculate_cross_product_of_two_vectors(
            vector1=axis_of_rotation,
            vector2=unit_vector_from_PC_to_PI,
        )

        center_of_curvature = (
            np.array(point_of_curvature)
            + np.array(unit_vector_from_PC_to_CC) * radius_of_curvature
        )

        return cls(
            point_of_intersection=point_of_intersection,
            central_angle=float(central_angle),
            radius_of_curvature=float(radius_of_curvature),
            direction_of_axis_of_rotation=axis_of_rotation,
            point_of_curvature=tuple(point_of_curvature.tolist()),
            point_of_tangency=tuple(point_of_tangency.tolist()),
            center_of_curvature=tuple(center_of_curvature.tolist()),
        )

    @classmethod
    def from_PC_and_PT_and_PI(
        cls,
        point_of_curvature: tuple[float, float, float],
        point_of_intersection: tuple[float, float, float],
        point_of_tangency: tuple[float, float, float],
    ):

        unit_vector_from_PC_to_PI = calculate_unit_direction_vector_between_two_points(
            p1=point_of_curvature,
            p2=point_of_intersection,
        )

        unit_vector_from_PI_to_PT = calculate_unit_direction_vector_between_two_points(
            p1=point_of_intersection,
            p2=point_of_tangency,
        )

        central_angle_of_curvature = calculate_angle_between_two_vectors(
            vector1=unit_vector_from_PI_to_PT,
            vector2=unit_vector_from_PC_to_PI,
        )

        axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=unit_vector_from_PC_to_PI,
            vector2=unit_vector_from_PI_to_PT,
            unit_normalize=True,
        )

        tangent_length = np.linalg.norm(
            np.array(point_of_intersection) - np.array(point_of_curvature)
        )

        radius_of_curvature = float(
            tangent_length * 1 / np.tan(central_angle_of_curvature / 2)
        )

        unit_vector_from_PC_to_CC = calculate_cross_product_of_two_vectors(
            vector1=axis_of_rotation,
            vector2=unit_vector_from_PC_to_PI,
            unit_normalize=True,
        )

        center_of_curvature = (
            np.array(point_of_curvature)
            + np.array(unit_vector_from_PC_to_CC) * radius_of_curvature
        )

        return cls(
            point_of_intersection=point_of_intersection,
            central_angle=float(central_angle_of_curvature),
            radius_of_curvature=float(radius_of_curvature),
            direction_of_axis_of_rotation=axis_of_rotation,
            point_of_curvature=point_of_curvature,
            point_of_tangency=point_of_tangency,
            center_of_curvature=tuple(center_of_curvature.tolist()),
        )

    @classmethod
    def from_PC_and_PT_and_CC(
        cls,
        point_of_curvature: tuple[float, float, float],
        point_on_center_of_curvature_side: tuple[float, float, float],
        point_of_tangency: tuple[float, float, float],
        radius_of_curvature: float,
    ):

        long_chord_length = np.linalg.norm(
            np.array(point_of_tangency) - np.array(point_of_curvature),
        )

        central_angle = 2 * np.arcsin(long_chord_length / 2 / radius_of_curvature)

        unit_vector_from_PC_to_PT = calculate_unit_direction_vector_between_two_points(
            p1=point_of_curvature,
            p2=point_of_tangency,
        )

        unit_vector_from_PC_to_point_on_CC_side = (
            calculate_unit_direction_vector_between_two_points(
                p1=point_of_curvature,
                p2=point_on_center_of_curvature_side,
            )
        )

        axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=unit_vector_from_PC_to_PT,
            vector2=unit_vector_from_PC_to_point_on_CC_side,
            unit_normalize=True,
        )

        unit_vector_from_from_CC_to_PI = calculate_cross_product_of_two_vectors(
            vector1=unit_vector_from_PC_to_PT,
            vector2=axis_of_rotation,
        )

        middle_ordinate_distance = radius_of_curvature * (
            1.0 - np.cos(central_angle / 2)
        )

        external_distance = radius_of_curvature * (1 / np.cos(central_angle / 2) - 1.0)

        point_of_intersection = (
            np.array(point_of_curvature)
            + long_chord_length / 2 * np.array(unit_vector_from_PC_to_PT)
            + (middle_ordinate_distance + external_distance)
            * np.array(unit_vector_from_from_CC_to_PI)
        )

        return cls.from_PC_and_PT_and_PI(
            point_of_curvature=point_of_curvature,
            point_of_tangency=point_of_tangency,
            point_of_intersection=tuple(point_of_intersection.tolist()),
        )

    @classmethod
    def from_PC_and_CC_and_angle(
        cls,
        point_of_curvature: tuple[float, float, float],
        point_of_center_of_curvature: tuple[float, float, float],
        central_angle_of_curvature: float,
    ):

        radius_of_curvature = float(
            np.linalg.norm(
                np.array(point_of_center_of_curvature) - np.array(point_of_curvature)
            )
        )

        vector_rotating = calculate_unit_direction_vector_between_two_points(
            p1=point_of_center_of_curvature,
            p2=point_of_curvature,
        )

        axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=point_of_curvature,
            vector2=point_of_center_of_curvature,
            unit_normalize=True,
        )

        rotated_vector = rotate_vector_about_axis(
            vector=vector_rotating,
            axis=axis_of_rotation,
            angle=central_angle_of_curvature,
        )

        point_of_tangency = np.array(point_of_center_of_curvature) + np.array(
            rotated_vector
        )

        return cls.from_PC_and_PT_and_CC(
            point_of_curvature=point_of_curvature,
            point_of_tangency=tuple(point_of_tangency.tolist()),
            point_on_center_of_curvature_side=point_of_center_of_curvature,
            radius_of_curvature=radius_of_curvature,
        )

    def __repr__(self):
        return "".join(
            [
                "HorizontalCurve(",
                f"point_of_intersection={self.point_of_intersection}, ",
                f"central_angle={self.central_angle}, ",
                f"central_angle_in_degrees={self.central_angle*180/np.pi}, ",
                f"radius_of_curvature={self.radius_of_curvature}, ",
                f"direction_of_axis_of_rotation={self.direction_of_axis_of_rotation}, ",
                f"point_of_curvature={self.point_of_curvature}, ",
                f"point_of_tangency={self.point_of_tangency}, ",
                f"center_of_curvature={self.center_of_curvature})",
            ]
        )


def rotate_vector_about_axis(
    vector: tuple[float, float, float],
    axis: tuple[float, float, float],
    angle: float,
):
    """
    Rotate vector vector about axis axis by angle (in radians).

    Args:
        vector: array-like - vector to rotate
        axis: array-like - axis of rotation (unit vector)
        angle: float - rotation angle in radians

    Returns:
        numpy array - rotated vector v3
    """
    v = np.array(vector)
    k = np.array(axis)  # axis unit vector

    cos_angle = np.cos(angle)
    sin_angle = np.sin(angle)

    # Rodrigues' rotation formula
    rotated_vector = (
        v * cos_angle + np.cross(k, v) * sin_angle + k * np.dot(k, v) * (1 - cos_angle)
    )

    return tuple(rotated_vector.tolist())


def filter_out_colinear_points_from_polyline(
    polyline: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:
    """Filter out colinear points from 3D polyline"""

    def remove_items_by_indices(lst: list, indices: list) -> list:
        indices_set = set(indices)
        return [item for idx, item in enumerate(lst) if idx not in indices_set]

    if len(polyline) < 3:
        return polyline

    indices_of_points_to_remove = []

    for index in range(len(polyline)):

        if index == len(polyline) - 2:
            break

        p1 = polyline[index]
        p2 = polyline[index + 1]
        p3 = polyline[index + 2]

        v12 = calculate_unit_direction_vector_between_two_points(
            p1=p1,
            p2=p2,
        )

        v23 = calculate_unit_direction_vector_between_two_points(
            p1=p2,
            p2=p3,
        )

        angle = calculate_angle_between_two_vectors(vector1=v12, vector2=v23)

        if angle == 0.0:
            indices_of_points_to_remove.append(index + 1)

        new_polyline = remove_items_by_indices(
            lst=polyline, indices=indices_of_points_to_remove
        )

    return new_polyline


def transform_point(
    four_by_four_transformation_matrix: np.ndarray,
    point: tuple[float, float, float],
) -> tuple[float, float, float]:

    vector_3d = np.array(point)

    vector_in_homogeneous_coordinates = np.append(vector_3d, 1)

    result = np.dot(
        four_by_four_transformation_matrix, vector_in_homogeneous_coordinates
    )

    result_3d = result[:3] / result[3]

    return tuple(result_3d.tolist())


def transform_direction_vector(
    four_by_four_transformation_matrix: np.ndarray,
    point: tuple[float, float, float],
) -> tuple[float, float, float]:

    vector_3d = np.array(point)

    vector_in_homogeneous_coordinates = np.append(vector_3d, 0)

    result = np.dot(
        four_by_four_transformation_matrix, vector_in_homogeneous_coordinates
    )

    result_3d = result[:3]

    return tuple(result_3d.tolist())
