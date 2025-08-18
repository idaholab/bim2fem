# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

from shapely.geometry import Polygon, Point
import ifcopenshell.util.placement
import numpy as np
import inlbim.util.geometry
from typing import Literal
import math


PRESET_SHAPE_MATRICES = {
    "C_SHAPE": [
        [1, 1, 1],
        [1, 0, 0],
        [1, 1, 1],
    ],
    "H_CIRCLE_OR_H_RECT": [
        [1, 1, 1],
        [1, 0, 1],
        [1, 1, 1],
    ],
    "I_SHAPE": [
        [1, 1, 1],
        [0, 1, 0],
        [1, 1, 1],
    ],
    "L_SHAPE": [
        [1, 0, 0],
        [1, 0, 0],
        [1, 1, 1],
    ],
    "CIRCLE_OR_RECT": [
        [1, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ],
    "T_SHAPE": [
        [1, 1, 1],
        [0, 1, 0],
        [0, 1, 0],
    ],
    "Z_SHAPE": [
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
    ],
}

PRESET_SHAPE_LABEL = Literal[
    "C_SHAPE",
    "H_CIRCLE_OR_H_RECT",
    "I_SHAPE",
    "L_SHAPE",
    "CIRCLE_OR_RECT",
    "T_SHAPE",
    "Z_SHAPE",
]


def classify_shape_and_determine_orientation_of_faces(
    local_z_axis_in_global_coordinates: tuple[float, float, float],
    assumed_local_y_axis_in_global_coordinates: tuple[float, float, float],
    faces_defined_by_vertex_coordinates: list[list[tuple[float, float, float]]],
) -> dict:

    # inlbim.util.geometry.TriangularMesh.plot_faces_3d(
    #     faces_as_tuples_with_coordinates=faces_defined_by_vertex_coordinates
    # )

    # Calculate centroid
    areas_of_faces = []
    centroids_of_faces = []
    for face in faces_defined_by_vertex_coordinates:
        p1 = face[0]
        p2 = face[1]
        p3 = face[2]
        vec1 = tuple(np.array(p2) - np.array(p1))
        vec2 = tuple(np.array(p3) - np.array(p1))
        cross_product = inlbim.util.geometry.calculate_cross_product_of_two_vectors(
            vector1=vec1,
            vector2=vec2,
            unit_normalize=False,
        )
        areas_of_faces.append(float(0.5 * np.linalg.norm(cross_product)))
        centroids_of_faces.append((np.array(p1) + np.array(p2) + np.array(p3)) / 3.0)
    centroid_in_global_coordinates = sum(
        [
            area_of_face * centroid_of_face
            for area_of_face, centroid_of_face in zip(
                areas_of_faces, centroids_of_faces
            )
            if isinstance(centroid_of_face, np.ndarray)
        ]
    )
    assert isinstance(centroid_in_global_coordinates, np.ndarray)
    centroid_in_global_coordinates = tuple(
        [float(val) for val in centroid_in_global_coordinates]
    )

    # Get assumed x-axis in global coordinates
    assumed_local_x_axis_in_global_coordinates = (
        inlbim.util.geometry.calculate_cross_product_of_two_vectors(
            vector1=assumed_local_y_axis_in_global_coordinates,
            vector2=local_z_axis_in_global_coordinates,
        )
    )

    # Transformation Matrix (local to global)
    transformation_matrix = ifcopenshell.util.placement.a2p(
        o=centroid_in_global_coordinates,
        z=local_z_axis_in_global_coordinates,
        x=assumed_local_x_axis_in_global_coordinates,
    )

    # transformation_matrix_v2_global_to_local = create_transformation_matrix(
    #     direction_ratios_of_z_axis=local_z_axis_in_global_coordinates,
    #     direction_ratios_of_x_axis=assumed_local_x_axis_in_global_coordinates,
    # )

    transformed_faces_defined_by_vertex_coordinates = []
    xs = []
    ys = []
    zs = []
    for face in faces_defined_by_vertex_coordinates:
        p1 = face[0]
        p2 = face[1]
        p3 = face[2]
        transformed_p1 = transformation_matrix.transpose() @ np.array(list(p1) + [1.0])
        transformed_p2 = transformation_matrix.transpose() @ np.array(list(p2) + [1.0])
        transformed_p3 = transformation_matrix.transpose() @ np.array(list(p3) + [1.0])
        xs += [transformed_p1[0], transformed_p2[0], transformed_p3[0]]
        ys += [transformed_p1[1], transformed_p2[1], transformed_p3[1]]
        zs += [transformed_p1[2], transformed_p2[2], transformed_p3[2]]
        transformed_face_defined_by_vertex_coordinates = [
            [float(val) for val in transformed_p1[0:2]],
            [float(val) for val in transformed_p2[0:2]],
            [float(val) for val in transformed_p3[0:2]],
        ]
        transformed_faces_defined_by_vertex_coordinates.append(
            transformed_face_defined_by_vertex_coordinates
        )

    x_min, x_max, y_min, y_max = min(xs), max(xs), min(ys), max(ys)

    squares = [
        [],
        [],
        [],
    ]
    x_delta = (x_max - x_min) / 3.0
    y_delta = (y_max - y_min) / 3.0
    for col in range(3):
        x_start = x_min + col * x_delta
        for row in range(3):
            y_start = y_max - row * y_delta
            square = [
                (x_start, y_start),
                (x_start, y_start - y_delta),
                (x_start + x_delta, y_start - y_delta),
                (x_start + x_delta, y_start),
            ]
            squares[row].append(square)

    shape_matrix = [
        [0, 0, 0],
        [0, 0, 0],
        [0, 0, 0],
    ]
    for row in range(3):
        for col in range(3):
            grid_cell_activated = False
            square = squares[row][col]
            for triangle in transformed_faces_defined_by_vertex_coordinates:
                if triangle_overlaps_square(
                    triangle_coords=tuple(triangle), square_coords=tuple(square)
                ):
                    grid_cell_activated = True
                    break
            if grid_cell_activated:
                shape_matrix[row][col] = 1

    matching_shape = None
    actual_local_x_axis_in_global_coordinates = None
    trial_local_x_axis_in_global_coordinates = (
        assumed_local_x_axis_in_global_coordinates
    )
    trial_shape_matrix = shape_matrix
    trial_number = 0
    for _ in range(4):
        trial_number += 1
        for preset_shape_name, preset_shape_matrix in PRESET_SHAPE_MATRICES.items():
            shapes_match = (
                calculate_l2_norm(
                    array1=flatten_matrix(trial_shape_matrix),
                    array2=flatten_matrix(preset_shape_matrix),
                )
                == 0.0
            )
            if shapes_match:
                actual_local_x_axis_in_global_coordinates = (
                    trial_local_x_axis_in_global_coordinates
                )
                matching_shape = preset_shape_name
                break
        if shapes_match:
            break
        trial_local_x_axis_in_global_coordinates = (
            inlbim.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=local_z_axis_in_global_coordinates,
                vector2=trial_local_x_axis_in_global_coordinates,
            )
        )
        trial_shape_matrix = rotate_matrix_90_clockwise(matrix=trial_shape_matrix)

    return {
        "matching_shape": matching_shape,
        "local_x_axis_in_global_coordinates": actual_local_x_axis_in_global_coordinates,
    }
    # return matching_shape, actual_local_x_axis_in_global_coordinates


# def create_transformation_matrix(
#     direction_ratios_of_z_axis: tuple[float, float, float],
#     direction_ratios_of_x_axis: tuple[float, float, float],
# ) -> np.ndarray:
#     """Create Transformation Matrix (Global to Local)"""

#     # Get Local Basis Vectors in Global Coordinates
#     local_z_axis_vector = (
#         np.array(direction_ratios_of_z_axis)
#         * 1
#         / np.linalg.norm(np.array(direction_ratios_of_z_axis))
#     )

#     local_x_axis_vector = (
#         np.array(direction_ratios_of_x_axis)
#         * 1
#         / np.linalg.norm(np.array(direction_ratios_of_x_axis))
#     )

#     local_y_axis_vector = np.cross(local_z_axis_vector, local_x_axis_vector)
#     local_y_axis_vector = local_y_axis_vector * 1 / np.linalg.norm(local_y_axis_vector)

#     # Get Matrices for Change of Basis
#     list_of_new_basis_vectors_in_global_coordinate_system = [
#         local_x_axis_vector,
#         local_y_axis_vector,
#         local_z_axis_vector,
#     ]
#     transformation_matrix = np.array(
#         list_of_new_basis_vectors_in_global_coordinate_system
#     )

#     return transformation_matrix


def flatten_matrix(matrix: list[list[int]]) -> list[int]:
    return [element for row in matrix for element in row]


def calculate_l2_norm(array1: list[int], array2: list[int]) -> float:
    if len(array1) != len(array2):
        raise ValueError("Arrays must have the same length")

    # Convert lists to numpy arrays
    np_array1 = np.array(array1)
    np_array2 = np.array(array2)

    # Calculate the L2 norm (Euclidean distance) between the two arrays
    l2_norm = float(np.linalg.norm(np_array1 - np_array2))

    return l2_norm


def rotate_matrix_90_clockwise(matrix: list[list[int]]) -> list[list[int]]:
    # Ensure the matrix is 3x3
    if len(matrix) != 3 or any(len(row) != 3 for row in matrix):
        raise ValueError("The matrix must be 3x3")

    # Transpose the matrix
    transposed_matrix = [[matrix[j][i] for j in range(3)] for i in range(3)]

    # Reverse the rows of the transposed matrix
    rotated_matrix = [row[::-1] for row in transposed_matrix]

    return rotated_matrix


def is_point_in_polygon(point, polygon):
    return polygon.contains(point)


def do_edges_intersect(polygon1, polygon2):
    return polygon1.intersects(polygon2)


def triangle_overlaps_square(
    triangle_coords: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
    ],
    square_coords: tuple[
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
        tuple[float, float],
    ],
):
    # Create Polygon objects for the triangle and the square
    triangle = Polygon(triangle_coords)
    square = Polygon(square_coords)

    # Check if any triangle's vertex is inside the square
    for vertex in triangle_coords:
        if is_point_in_polygon(Point(vertex), square):
            return True

    # Check if any square's vertex is inside the triangle
    for vertex in square_coords:
        if is_point_in_polygon(Point(vertex), triangle):
            return True

    # Check if any edges of the triangle intersect with any edges of the square
    if do_edges_intersect(triangle, square):
        return True

    return False


def is_point_in_circle(
    point: tuple[float, float],
    center: tuple[float, float],
    radius: float,
):
    """
    Determine if a point is within a circle.

    :param point: A tuple (x, y) representing the coordinates of the point.
    :param center: A tuple (cx, cy) representing the coordinates of the circle's center.
    :param radius: The radius of the circle.
    :return: True if the point is within the circle, False otherwise.
    """
    x, y = point
    cx, cy = center

    # Calculate the distance between the point and the center of the circle
    distance = math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy))

    # Check if the distance is less than or equal to the radius
    return distance <= radius


def measure_dimensions_of_classified_shape_of_faces(
    local_z_axis_in_global_coordinates: tuple[float, float, float],
    local_x_axis_in_global_coordinates: tuple[float, float, float],
    faces_defined_by_vertex_coordinates: list[list[tuple[float, float, float]]],
    preset_beam_shape_classification: PRESET_SHAPE_LABEL,
    numeric_scale: int = 4,
) -> dict:

    # Transformation Matrix (local to global)
    transformation_matrix = ifcopenshell.util.placement.a2p(
        o=(0.0, 0.0, 0.0),
        z=local_z_axis_in_global_coordinates,
        x=local_x_axis_in_global_coordinates,
    )

    # Transform 3D faces to 2D
    transformed_faces_defined_by_vertex_coordinates = []
    xs = []
    ys = []
    zs = []
    for face in faces_defined_by_vertex_coordinates:
        p1 = face[0]
        p2 = face[1]
        p3 = face[2]
        transformed_p1 = transformation_matrix.transpose() @ np.array(list(p1) + [1.0])
        transformed_p2 = transformation_matrix.transpose() @ np.array(list(p2) + [1.0])
        transformed_p3 = transformation_matrix.transpose() @ np.array(list(p3) + [1.0])
        xs += [transformed_p1[0], transformed_p2[0], transformed_p3[0]]
        ys += [transformed_p1[1], transformed_p2[1], transformed_p3[1]]
        zs += [transformed_p1[2], transformed_p2[2], transformed_p3[2]]
        transformed_face_defined_by_vertex_coordinates = [
            [float(val) for val in transformed_p1[0:2]],
            [float(val) for val in transformed_p2[0:2]],
            [float(val) for val in transformed_p3[0:2]],
        ]
        transformed_faces_defined_by_vertex_coordinates.append(
            transformed_face_defined_by_vertex_coordinates
        )

    parameterized_profile_class = None
    dimensions = None

    if preset_beam_shape_classification == "C_SHAPE":
        parameterized_profile_class = "IfcUShapeProfileDef"
        dimensions = get_dims_for_u_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )

    elif preset_beam_shape_classification == "H_CIRCLE_OR_H_RECT":
        # Get dims for rectangle and circle
        rect_dims = get_dims_for_rectangle_hollow_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )
        xdim, ydim, wall_thickness_for_rectangle = (
            rect_dims[0],
            rect_dims[1],
            rect_dims[2],
        )
        circ_dims = get_dims_for_circle_hollow_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )
        radius, wall_thickness_for_circle = circ_dims[0], circ_dims[1]

        # Rect Case 1: one dimension is larger than the other
        if max([xdim, ydim]) > 1.1 * min([xdim, ydim]):
            shape_is_rectangular = True

        # Rect Case 2: Check whether some point lies outside a hypothetical circle
        else:
            x_vals, y_vals = get_x_vals_and_y_vals(
                face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
                numeric_scale=numeric_scale,
                recenter_about_bounding_box=True,
            )
            x_pos_bb_center = (min(x_vals) + max(x_vals)) / 2
            y_pos_bb_center = (min(y_vals) + max(y_vals)) / 2
            some_point_lies_outside_a_hypothetical_circular_shape = False
            for face in transformed_faces_defined_by_vertex_coordinates:
                for vertex_of_face in face:
                    point_is_in_circle = is_point_in_circle(
                        point=vertex_of_face,
                        center=(x_pos_bb_center, y_pos_bb_center),
                        radius=1.1 * radius,
                    )
                    if not point_is_in_circle:
                        some_point_lies_outside_a_hypothetical_circular_shape = True
                        break
                if some_point_lies_outside_a_hypothetical_circular_shape:
                    break
            if some_point_lies_outside_a_hypothetical_circular_shape:
                shape_is_rectangular = True
            else:
                shape_is_rectangular = False

        # Narrow the classification and set dims
        if shape_is_rectangular:
            parameterized_profile_class = "IfcRectangleHollowProfileDef"
            dimensions = [xdim, ydim, wall_thickness_for_rectangle, None, None]
        else:
            parameterized_profile_class = "IfcCircleHollowProfileDef"
            dimensions = [radius, wall_thickness_for_circle]

    elif preset_beam_shape_classification == "I_SHAPE":
        parameterized_profile_class = "IfcIShapeProfileDef"
        dimensions = get_dims_for_i_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )

    elif preset_beam_shape_classification == "L_SHAPE":
        parameterized_profile_class = "IfcLShapeProfileDef"
        dimensions = get_dims_for_l_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )

    elif preset_beam_shape_classification == "CIRCLE_OR_RECT":
        # Get dims for rectangle and circle
        rect_dims = get_dims_for_rectangle_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )
        xdim, ydim = (rect_dims[0], rect_dims[1])
        circ_dims = get_dims_for_circle_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )
        radius = circ_dims[0]

        # Rect Case 1: one dimension is larger than the other
        if max([xdim, ydim]) > 1.1 * min([xdim, ydim]):
            shape_is_rectangular = True

        # Rect Case 2: Check whether some point lies outside a hypothetical circle
        else:
            x_vals, y_vals = get_x_vals_and_y_vals(
                face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
                numeric_scale=numeric_scale,
                recenter_about_bounding_box=True,
            )
            x_pos_bb_center = (min(x_vals) + max(x_vals)) / 2
            y_pos_bb_center = (min(y_vals) + max(y_vals)) / 2
            some_point_lies_outside_a_hypothetical_circular_shape = False
            for face in transformed_faces_defined_by_vertex_coordinates:
                for vertex_of_face in face:
                    point_is_in_circle = is_point_in_circle(
                        point=vertex_of_face,
                        center=(x_pos_bb_center, y_pos_bb_center),
                        radius=1.1 * radius,
                    )
                    if not point_is_in_circle:
                        some_point_lies_outside_a_hypothetical_circular_shape = True
                        break
                if some_point_lies_outside_a_hypothetical_circular_shape:
                    break
            if some_point_lies_outside_a_hypothetical_circular_shape:
                shape_is_rectangular = True
            else:
                shape_is_rectangular = False

        # Narrow the classification and set dims
        if shape_is_rectangular:
            parameterized_profile_class = "IfcRectangleProfileDef"
            dimensions = [xdim, ydim]
        else:
            parameterized_profile_class = "IfcCircleProfileDef"
            dimensions = [radius]

    elif preset_beam_shape_classification == "T_SHAPE":
        parameterized_profile_class = "IfcTShapeProfileDef"
        dimensions = get_dims_for_t_shape(
            face_surfaces_defined_by_2D_vertex_coordinates=transformed_faces_defined_by_vertex_coordinates,
            numeric_scale=numeric_scale,
        )

    result = {
        "parameterized_profile_class": parameterized_profile_class,
        "dimensions": dimensions,
    }

    return result


def get_x_vals_and_y_vals(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
    recenter_about_bounding_box: bool = False,
) -> tuple[list[float], list[float]]:

    # Get all X-values and Y-values
    x_vals, y_vals = [], []
    for face in face_surfaces_defined_by_2D_vertex_coordinates:
        for vertex_coordinates in face:
            x_vals.append(vertex_coordinates[0])
            y_vals.append(vertex_coordinates[1])

    # Recenter about bounding box
    if recenter_about_bounding_box:
        dx = np.round((max(x_vals) - min(x_vals)) / 3, numeric_scale)
        dy = np.round((max(y_vals) - min(y_vals)) / 3, numeric_scale)
        x_val_bb_center = min(x_vals) + 1.5 * dx
        y_val_bb_center = min(y_vals) + 1.5 * dy
        x_vals = [x_val - x_val_bb_center for x_val in x_vals]
        y_vals = [y_val - y_val_bb_center for y_val in y_vals]

    return x_vals, y_vals


def get_dims_for_i_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    overal_width = max(x_vals) - min(x_vals)
    overal_depth = max(y_vals) - min(y_vals)

    dx = (max(x_vals) - min(x_vals)) / 3
    dy = (max(y_vals) - min(y_vals)) / 3

    pos_x_vals = [val for val in x_vals if val > min(x_vals) + 1.5 * dx]
    web_thickness = min(pos_x_vals) * 2

    top_right_y_vals = [
        y_val
        for x_val, y_val in zip(x_vals, y_vals)
        if x_val > max(x_vals) - dx and y_val > max(y_vals) - dy
    ]
    flange_thickness = max(top_right_y_vals) - min(top_right_y_vals)

    dimensions = [
        float(np.round(overal_width, numeric_scale)),
        float(np.round(overal_depth, numeric_scale)),
        float(np.round(web_thickness, numeric_scale)),
        float(np.round(flange_thickness, numeric_scale)),
        None,
        None,
        None,
    ]

    return dimensions


def get_dims_for_u_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    depth = max(y_vals) - min(y_vals)
    flange_width = max(x_vals) - min(x_vals)

    neg_x_vals = [val for val in x_vals if val < 0]
    neg_x_vals = list(set(neg_x_vals))
    neg_x_vals.sort()
    web_thickness = neg_x_vals[1] - neg_x_vals[0]

    dx = np.round((max(x_vals) - min(x_vals)) / 3, numeric_scale)
    dy = np.round((max(y_vals) - min(y_vals)) / 3, numeric_scale)
    top_right_y_vals = [
        y_val
        for x_val, y_val in zip(x_vals, y_vals)
        if x_val > max(x_vals) - dx and y_val > max(y_vals) - dy
    ]
    flange_thickness = max(top_right_y_vals) - min(top_right_y_vals)

    dimensions = [
        float(np.round(depth, numeric_scale)),
        float(np.round(flange_width, numeric_scale)),
        float(np.round(web_thickness, numeric_scale)),
        float(np.round(flange_thickness, numeric_scale)),
        None,
        None,
        None,
    ]

    return dimensions


def get_dims_for_t_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    depth = max(y_vals) - min(y_vals)
    flange_width = max(x_vals) - min(x_vals)

    pos_x_vals = [val for val in x_vals if val > 0]
    web_thickness = min(pos_x_vals) * 2

    dx = np.round((max(x_vals) - min(x_vals)) / 3, numeric_scale)
    dy = np.round((max(y_vals) - min(y_vals)) / 3, numeric_scale)
    top_right_y_vals = [
        y_val
        for x_val, y_val in zip(x_vals, y_vals)
        if x_val > max(x_vals) - dx and y_val > max(y_vals) - dy
    ]
    flange_thickness = max(top_right_y_vals) - min(top_right_y_vals)

    dimensions = [
        float(np.round(depth, numeric_scale)),
        float(np.round(flange_width, numeric_scale)),
        float(np.round(web_thickness, numeric_scale)),
        float(np.round(flange_thickness, numeric_scale)),
        None,
        None,
        None,
        None,
        None,
    ]

    return dimensions


def get_dims_for_l_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    depth = max(y_vals) - min(y_vals)
    width = max(x_vals) - min(x_vals)

    right_half_y_vals = [y_val for x_val, y_val in zip(x_vals, y_vals) if x_val > 0]
    thickness = max(right_half_y_vals) - min(right_half_y_vals)

    dimensions = [
        float(np.round(depth, numeric_scale)),
        float(np.round(width, numeric_scale)),
        float(np.round(thickness, numeric_scale)),
        None,
        None,
        None,
    ]

    return dimensions


def get_dims_for_rectangle_hollow_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    xdim = max(x_vals) - min(x_vals)
    ydim = max(y_vals) - min(y_vals)

    pos_y_vals = [val for val in y_vals if val > 0]
    wall_thickness = max(pos_y_vals) - min(pos_y_vals)

    dimensions = [
        float(np.round(xdim, numeric_scale)),
        float(np.round(ydim, numeric_scale)),
        float(np.round(wall_thickness, numeric_scale)),
        None,
        None,
    ]

    return dimensions


def get_dims_for_circle_hollow_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    distances = [np.sqrt(x**2 + y**2) for x, y in zip(x_vals, y_vals)]
    radius = max(distances)
    wall_thickness = max(distances) - min(distances)

    dimensions = [
        float(np.round(radius, numeric_scale)),
        float(np.round(wall_thickness, numeric_scale)),
    ]

    return dimensions


def get_dims_for_rectangle_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    xdim = max(x_vals) - min(x_vals)
    ydim = max(y_vals) - min(y_vals)

    dimensions = [
        float(np.round(xdim, numeric_scale)),
        float(np.round(ydim, numeric_scale)),
    ]

    return dimensions


def get_dims_for_circle_shape(
    face_surfaces_defined_by_2D_vertex_coordinates: list[list[tuple[float, float]]],
    numeric_scale: int = 4,
) -> list:

    x_vals, y_vals = get_x_vals_and_y_vals(
        face_surfaces_defined_by_2D_vertex_coordinates=face_surfaces_defined_by_2D_vertex_coordinates,
        numeric_scale=numeric_scale,
        recenter_about_bounding_box=True,
    )

    distances = [np.sqrt(x**2 + y**2) for x, y in zip(x_vals, y_vals)]
    radius = max(distances)

    dimensions = [np.round(radius, numeric_scale)]

    return dimensions
