# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.geom
import multiprocessing
import ifcopenshell
import ifcopenshell.geom
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import Axes3D
import random


def get_coordinates_of_vertex_point(
    vertex_point: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:

    assert isinstance(vertex_point.VertexGeometry, ifcopenshell.entity_instance)
    assert isinstance(vertex_point.VertexGeometry.Coordinates, tuple)
    coordinates_of_vertex_point = vertex_point.VertexGeometry.Coordinates

    return coordinates_of_vertex_point


def group_in_threes(input_list: list[int | float]) -> list:
    # Check if the length of the input list is a multiple of 3
    if len(input_list) % 3 != 0:
        raise ValueError("The length of the list must be a multiple of 3.")

    # Create the list of lists
    grouped_list = [input_list[i : i + 3] for i in range(0, len(input_list), 3)]

    return grouped_list


class TriangularMesh:
    def __init__(
        self,
        verts: list[tuple[float, float, float]],
        faces: list[list[int]],
    ):
        self.verts = verts
        self.faces = faces

    def are_faces_coplanar(
        self,
        index_of_face1: int,
        index_of_face2: int,
    ):
        def normal_vector(v1, v2, v3):
            # Calculate the normal vector of the plane defined by three vertices
            vec1 = np.subtract(v2, v1)
            vec2 = np.subtract(v3, v1)
            return np.cross(vec1, vec2)

        def point_in_plane(point, plane_point, normal):
            # Check if a point lies in the plane defined by a point and a normal vector
            vec = np.subtract(point, plane_point)
            return np.round(np.dot(vec, normal), 4) == 0.0

        face1 = self.get_coordinates_of_faces(indices_of_faces=[index_of_face1])[0]
        face2 = self.get_coordinates_of_faces(indices_of_faces=[index_of_face2])[0]

        # Extract vertices from the faces
        v1, v2, v3 = face1
        v4, v5, v6 = face2

        # Calculate the normal vector of the first face
        normal = normal_vector(v1, v2, v3)

        # Check if all vertices of the second face lie in the plane of the first face
        return (
            point_in_plane(v4, v1, normal)
            and point_in_plane(v5, v1, normal)
            and point_in_plane(v6, v1, normal)
        )

    def calculate_centroid_of_face(
        self,
        index_of_face: int,
    ) -> tuple[float, float, float]:

        face = self.faces[index_of_face]

        p1 = self.verts[face[0]]
        p2 = self.verts[face[1]]
        p3 = self.verts[face[2]]

        average_array = tuple(
            [
                float(val)
                for val in np.mean(
                    np.stack((np.array(p1), np.array(p2), np.array(p3)), axis=0), axis=0
                ).tolist()
            ]
        )
        assert len(average_array) == 3

        return average_array

    def calculate_centroid_of_given_faces(
        self,
        indices_of_faces: list[int],
    ) -> tuple[float, float, float]:

        centroids_of_faces = [
            self.calculate_centroid_of_face(index_of_face=index_of_face)
            for index_of_face in indices_of_faces
        ]

        areas_of_faces = [
            self.calculate_area_of_face(face_index) for face_index in indices_of_faces
        ]

        total_area = sum(areas_of_faces)

        centroid = (
            sum(
                [
                    np.array(centroid_of_face) * area_of_face
                    for centroid_of_face, area_of_face in zip(
                        centroids_of_faces, areas_of_faces
                    )
                ]
            )
            * 1
            / total_area
        )
        assert isinstance(centroid, np.ndarray)

        centroid = tuple([float(val) for val in centroid.tolist()])
        assert len(centroid) == 3

        return centroid

    def calculate_centroid_of_triangular_mesh(self) -> tuple[float, float, float]:

        return self.calculate_centroid_of_given_faces(
            indices_of_faces=[_ for _ in range(len(self.faces))]
        )

    @classmethod
    def from_ifc_element(
        cls,
        element: ifcopenshell.entity_instance,
    ):

        ifc_file = element.file

        settings = ifcopenshell.geom.settings()
        settings.set("weld-vertices", True)
        settings.set(settings.BUILDING_LOCAL_PLACEMENT, False)
        settings.set(settings.SITE_LOCAL_PLACEMENT, True)
        settings.set(settings.USE_WORLD_COORDS, True)
        iterator = ifcopenshell.geom.iterator(
            settings, ifc_file, multiprocessing.cpu_count(), include=[element]
        )
        if iterator.initialize():
            while True:
                shape = iterator.get()
                # element = ifc_file.by_id(shape.id)
                # matrix = shape.transformation.matrix
                faces = group_in_threes(shape.geometry.faces)
                # edges = shape.geometry.edges
                verts = group_in_threes(shape.geometry.verts)
                # materials = shape.geometry.materials
                # material_ids = shape.geometry.material_ids
                # points = group_in_threes(verts)
                # triangles = group_in_threes(faces)
                # ... write code to process geometry here ...
                if not iterator.next():
                    break

        return cls(
            verts=verts,
            faces=faces,
        )

    def calculate_area_of_face(
        self,
        face_index: int,
    ) -> float:

        face = self.faces[face_index]

        p1 = self.verts[face[0]]
        p2 = self.verts[face[1]]
        p3 = self.verts[face[2]]

        # Calculate the vectors
        vec1 = tuple(np.array(p2) - np.array(p1))
        vec2 = tuple(np.array(p3) - np.array(p1))

        # Compute the cross product of vec1 and vec2
        cross_product = calculate_cross_product_of_two_vectors(
            vector1=vec1,
            vector2=vec2,
            unit_normalize=False,
        )

        # Calculate the area of the triangle
        area = float(0.5 * np.linalg.norm(cross_product))

        return area

    def calculate_normal_vector_of_face(
        self,
        face_index: int,
    ) -> tuple[float, float, float]:

        face = self.faces[face_index]

        p1 = self.verts[face[0]]
        p2 = self.verts[face[1]]
        p3 = self.verts[face[2]]

        # Calculate the vectors
        vec1 = tuple(np.array(p2) - np.array(p1))
        vec2 = tuple(np.array(p3) - np.array(p1))

        # Compute the normalized cross product of vec1 and vec2
        normal_vector = calculate_cross_product_of_two_vectors(
            vector1=vec1,
            vector2=vec2,
            unit_normalize=True,
        )

        return normal_vector

    def get_edges_of_face(self, index_of_face: int) -> list[tuple[int, int]]:
        face = self.faces[index_of_face]

        edges = [
            (face[0], face[1]),
            (face[1], face[2]),
            (face[2], face[0]),
        ]

        return edges

    def get_boundary_edges_from_group_of_contiguous_planar_faces(
        self,
        indices_of_contiguous_planar_faces: list[int],
    ) -> list[tuple[int, int]]:

        basket_for_boundary_edges = []

        basket_for_uncategorized_edges = []
        for index_of_face in indices_of_contiguous_planar_faces:
            edges_of_face = self.get_edges_of_face(index_of_face=index_of_face)
            basket_for_uncategorized_edges += edges_of_face

        cycle_number = 0
        while True:
            if len(basket_for_uncategorized_edges) == 1:
                basket_for_boundary_edges.append(basket_for_uncategorized_edges[0])
                basket_for_uncategorized_edges.pop(0)
            if len(basket_for_uncategorized_edges) == 0:
                break
            cycle_number += 1
            if cycle_number == 10000:
                exit("Problem!")
            edge_under_consideration = basket_for_uncategorized_edges[0]
            basket_for_uncategorized_edges.pop(0)
            edge_is_unique = True
            for index_of_other_edge, other_edge in enumerate(
                basket_for_uncategorized_edges
            ):
                if edge_under_consideration == other_edge[::-1]:
                    edge_is_unique = False
                    basket_for_uncategorized_edges.pop(index_of_other_edge)
                    break
            if edge_is_unique:
                basket_for_boundary_edges.append(edge_under_consideration)

        return basket_for_boundary_edges

    def get_longest_edge_from_given_edges(
        self,
        edges: list[tuple[int, int]],
    ) -> tuple[int, int]:

        lengths_of_edges = []
        for edge in edges:
            p1 = self.verts[edge[0]]
            p2 = self.verts[edge[1]]
            length_of_edge = float(np.linalg.norm(np.array(p2) - np.array(p1)))
            lengths_of_edges.append(length_of_edge)

        index_of_longest_edge = lengths_of_edges.index(max(lengths_of_edges))
        longest_edge = edges[index_of_longest_edge]

        return longest_edge

    def calculate_unit_normalized_direction_vector_of_edge(
        self,
        edge: tuple[int, int],
    ) -> tuple[float, float, float]:

        p1 = self.verts[edge[0]]
        p2 = self.verts[edge[1]]

        return calculate_unit_direction_vector_between_two_points(p1=p1, p2=p2)

    def get_coordinates_of_faces(
        self,
        indices_of_faces: list[int],
    ) -> list[list[tuple[float, float, float]]]:

        faces_as_tuples_with_coordinates = [
            [
                self.verts[face[0]],
                self.verts[face[1]],
                self.verts[face[2]],
            ]
            for face in [
                self.faces[index_of_face] for index_of_face in indices_of_faces
            ]
        ]

        return faces_as_tuples_with_coordinates

    def plot_all(self):
        self.plot_faces_3d(
            faces_as_tuples_with_coordinates=self.get_coordinates_of_faces(
                indices_of_faces=list(range(len(self.faces)))
            )
        )

    @classmethod
    def plot_faces_3d(
        cls,
        faces_as_tuples_with_coordinates: list[list[tuple[float, float, float]]],
    ):
        """
        Plots a list of triangular faces in 3D.

        Parameters:
        faces (list of tuple): Each face is a list of three (x, y, z) coordinate tuples.
                               Example: [[(0, 0, 0), (1, 0, 0), (0, 1, 0)], ...]
        """
        # faces = [self.faces[index_of_face] for index_of_face in indices_of_faces]

        # faces_as_tuples_with_coordinates = [
        #     (self.verts[face[0]], self.verts[face[1]], self.verts[face[2]])
        #     for face in faces
        # ]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        # Create a list of triangle vertex arrays for Poly3DCollection
        triangles = [list(face) for face in faces_as_tuples_with_coordinates]

        # Add the triangles to the plot
        poly3d = Poly3DCollection(
            triangles, facecolors="skyblue", edgecolors="k", alpha=0.6
        )
        ax.add_collection3d(poly3d)

        # Automatically scale axes to fit the mesh
        all_points = [pt for face in faces_as_tuples_with_coordinates for pt in face]
        xs, ys, zs = zip(*all_points)
        ax.set_xlim(min(xs), max(xs))
        ax.set_ylim(min(ys), max(ys))
        ax.set_zlim(min(zs), max(zs))

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.tight_layout()
        plt.show()

    def plot_edges_3d(
        self,
        edges_as_tuples_with_coordinates: list[list[tuple[float, float]]],
        node_size=20,
        seed=None,
    ):
        """
        Plots a list of 3D edges as lines with random colors, and black circular nodes at endpoints.

        Parameters:
        edges (list of tuple): Each edge is a list of two (x, y, z) coordinate tuples.
                               Example: [[(0, 0, 0), (1, 1, 1)], ...]
        node_size (int): Size of the scatter points used for edge endpoints.
        seed (int or None): Optional seed for reproducible colors.
        """

        # indices_of_vertices = set()
        # for edge in edges:
        #     index_of_vertex_1, index_of_vertex_2 = edge
        #     indices_of_vertices.add(index_of_vertex_1)
        #     indices_of_vertices.add(index_of_vertex_2)

        # edges_as_tuples_with_coordinates = [
        #     (self.verts[edge[0]], self.verts[edge[1]]) for edge in edges
        # ]

        if seed is not None:
            random.seed(seed)

        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")

        all_points = set()

        for edge in edges_as_tuples_with_coordinates:
            (x1, y1, z1), (x2, y2, z2) = edge
            color = [random.random() for _ in range(3)]  # RGB triplet
            ax.plot([x1, x2], [y1, y2], [z1, z2], color=color, linewidth=2)
            all_points.add((x1, y1, z1))
            all_points.add((x2, y2, z2))

        # Plot unique nodes at edge endpoints
        xs, ys, zs = zip(*all_points)
        ax.scatter(xs, ys, zs, color="black", s=node_size)

        # Automatically scale axes to fit the mesh
        ax.set_xlim(min(xs), max(xs))
        ax.set_ylim(min(ys), max(ys))
        ax.set_zlim(min(zs), max(zs))

        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        plt.tight_layout()
        plt.show()


def get_bounding_box_of_element(
    element: ifcopenshell.entity_instance,
) -> tuple[list[float], list[float]]:

    # Setup geometry settings
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)

    # Create shape
    shape = ifcopenshell.geom.create_shape(settings, element)
    geometry = shape.geometry  # This is a Triangulation object

    # Extract vertices and reshape into Nx3 array
    verts = np.array(geometry.verts).reshape(-1, 3)

    # Compute bounding box
    min_bounds = verts.min(axis=0)
    max_bounds = verts.max(axis=0)

    return min_bounds, max_bounds


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

    theta = np.arccos(cos_theta)

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

    vector1_normalized = np.array(vector) * 1 / np.linalg.norm(vector)

    return tuple(vector1_normalized.tolist())


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

    @classmethod
    def from_3pt_polyline(
        cls,
        p1: tuple[float, float, float],
        p2: tuple[float, float, float],
        p3: tuple[float, float, float],
        radius_of_curvature: float,
    ):

        # Get point of intersection of tangents
        point_of_intersection = p2

        # Get unit direction vectors of line segments
        u1 = calculate_unit_direction_vector_between_two_points(p1=p1, p2=p2)
        u2 = calculate_unit_direction_vector_between_two_points(p1=p2, p2=p3)

        # Calculate the central angle
        central_angle = calculate_angle_between_two_vectors(vector1=u2, vector2=u1)

        # Calculate the unit direction vector of the axis of rotation
        direction_of_axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=u1, vector2=u2
        )

        # Calculate tangent length
        tangent_length = radius_of_curvature * np.tan(central_angle / 2)

        # Calculate point of curvature
        point_of_curvature = (
            np.array(point_of_intersection) - np.array(u1) * tangent_length
        )
        point_of_curvature = tuple(point_of_curvature.tolist())

        # Calculate point of tangency
        point_of_tangency = (
            np.array(point_of_intersection) + np.array(u2) * tangent_length
        )
        point_of_tangency = tuple(point_of_tangency.tolist())

        # Calculate the point of center of curvature
        cross_product_of_axis_and_u1 = calculate_cross_product_of_two_vectors(
            vector1=direction_of_axis_of_rotation, vector2=u1
        )
        center_of_curvature = (
            np.array(point_of_curvature)
            + np.array(cross_product_of_axis_and_u1) * radius_of_curvature
        )
        center_of_curvature = tuple(center_of_curvature.tolist())

        return cls(
            point_of_intersection=point_of_intersection,
            central_angle=central_angle,
            radius_of_curvature=radius_of_curvature,
            direction_of_axis_of_rotation=direction_of_axis_of_rotation,
            point_of_curvature=point_of_curvature,
            point_of_tangency=point_of_tangency,
            center_of_curvature=center_of_curvature,
        )

    @classmethod
    def from_PC_and_PT_and_PI(
        cls,
        point_of_curvature: tuple[float, float, float],
        point_of_intersection: tuple[float, float, float],
        point_of_tangency: tuple[float, float, float],
    ):

        # Get unit direction vectors of line segments
        u1 = calculate_unit_direction_vector_between_two_points(
            p1=point_of_curvature, p2=point_of_intersection
        )
        u2 = calculate_unit_direction_vector_between_two_points(
            p1=point_of_intersection, p2=point_of_tangency
        )

        # Calculate the central angle
        central_angle = calculate_angle_between_two_vectors(vector1=u2, vector2=u1)

        # Calculate the unit direction vector of the axis of rotation
        direction_of_axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=u1, vector2=u2
        )

        # Calculate tangent length
        tangent_length = np.linalg.norm(
            np.array(point_of_intersection) - np.array(point_of_curvature)
        )

        # Calculate radius of curvature
        radius_of_curvature = float(tangent_length * 1 / np.tan(central_angle / 2))

        # Calculate the point of center of curvature
        cross_product_of_axis_and_u1 = calculate_cross_product_of_two_vectors(
            vector1=direction_of_axis_of_rotation, vector2=u1
        )
        center_of_curvature = (
            np.array(point_of_curvature)
            + np.array(cross_product_of_axis_and_u1) * radius_of_curvature
        )
        center_of_curvature = tuple(center_of_curvature.tolist())

        return cls(
            point_of_intersection=point_of_intersection,
            central_angle=central_angle,
            radius_of_curvature=radius_of_curvature,
            direction_of_axis_of_rotation=direction_of_axis_of_rotation,
            point_of_curvature=point_of_curvature,
            point_of_tangency=point_of_tangency,
            center_of_curvature=center_of_curvature,
        )

    @classmethod
    def from_PC_and_PT_and_CC(
        cls,
        point_of_curvature: tuple[float, float, float],
        point_on_center_of_curvature_side: tuple[float, float, float],
        point_of_tangency: tuple[float, float, float],
        radius_of_curvature: float,
    ):

        # Long chord length
        long_chord_length = np.linalg.norm(
            np.array(point_of_tangency) - np.array(point_of_curvature),
        )

        # Central Angle
        central_angle = 2 * np.arcsin(long_chord_length / 2 / radius_of_curvature)

        # Unit Vector from PC to PT
        vector_from_PC_to_PT = calculate_unit_direction_vector_between_two_points(
            p1=point_of_curvature,
            p2=point_of_tangency,
        )

        # Unit Vector from PC to point on CC side
        vector_from_PC_to_P3 = calculate_unit_direction_vector_between_two_points(
            p1=point_of_curvature,
            p2=point_on_center_of_curvature_side,
        )

        # Axis of rotation
        direction_of_axis_of_rotation = calculate_cross_product_of_two_vectors(
            vector1=vector_from_PC_to_PT,
            vector2=vector_from_PC_to_P3,
        )

        # Unit vector from center of curvature to point of intersection
        vector_from_CC_to_PI = calculate_cross_product_of_two_vectors(
            vector1=vector_from_PC_to_PT,
            vector2=direction_of_axis_of_rotation,
        )

        # Middle ordinate distance
        middle_ordinate_distance = radius_of_curvature * (
            1.0 - np.cos(central_angle / 2)
        )

        # External distance
        external_distance = radius_of_curvature * (1 / np.cos(central_angle / 2) - 1.0)

        # Point of intersection
        point_of_intersection = tuple(
            (
                np.array(point_of_curvature)
                + long_chord_length / 2 * np.array(vector_from_PC_to_PT)
                + (middle_ordinate_distance + external_distance)
                * np.array(vector_from_CC_to_PI)
            ).tolist()
        )

        return cls.from_PC_and_PT_and_PI(
            point_of_curvature=point_of_curvature,
            point_of_tangency=point_of_tangency,
            point_of_intersection=point_of_intersection,
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


def calculate_endpoint_coordinates_of_shortest_line_connecting_two_lines(
    coordinates_of_start_of_line_1: tuple[float, float, float],
    coordinates_of_end_of_line_1: tuple[float, float, float],
    coordinates_of_start_of_line_2: tuple[float, float, float],
    coordinates_of_end_of_line_2: tuple[float, float, float],
    assume_line_1_is_finite: bool,
    assume_line_2_is_finite: bool,
) -> tuple[tuple[float, float, float], tuple[float, float, float]] | tuple[None, None]:

    # Get coordinates of VertexPoints of Line 1
    p_i = np.array(coordinates_of_start_of_line_1)
    p_j = np.array(coordinates_of_end_of_line_1)

    # Get coordinates of VertexPoints of Line 2
    q_i = np.array(coordinates_of_start_of_line_2)
    q_j = np.array(coordinates_of_end_of_line_2)

    # Calculate unit vectors
    p_hat = (p_j - p_i) * 1 / np.linalg.norm(p_j - p_i)
    q_hat = (q_j - q_i) * 1 / np.linalg.norm(q_j - q_i)

    # Calculate the denominator
    denominator = np.dot(p_hat, q_hat) ** 2 - 1

    # Determine whether the edges are parallel
    edges_are_parallel = 0.0 == np.round(denominator, 4)

    # If edges are parallel, then exit without solution
    if edges_are_parallel:
        return None, None

    # Calculate the numerators
    numerator_for_t_p = np.dot(p_hat, p_i - q_i) - (
        np.dot(p_hat, q_hat) * np.dot(q_hat, p_i - q_i)
    )
    numerator_for_t_q = np.dot(-q_hat, p_i - q_i) + (
        np.dot(p_hat, q_hat) * np.dot(p_hat, p_i - q_i)
    )

    # Get the constants t_p and t_q
    t_p = numerator_for_t_p / denominator
    t_q = numerator_for_t_q / denominator

    # If line 1 is assumed to be finite, then adjust the constants
    if assume_line_1_is_finite:

        # t_p
        line_1_length = np.linalg.norm(p_j - p_i)
        if t_p < 0:
            t_p = 0
        if t_p > line_1_length:
            t_p = line_1_length

    # If line 2 is assumed to be finite, then adjust the constants
    if assume_line_2_is_finite:

        # t_q
        line_2_length = np.linalg.norm(q_j - q_i)
        if t_q < 0:
            t_q = 0
        if t_q > line_2_length:
            t_q = line_2_length

    # Calculate the coordiantes of the endpoints
    r_i = p_i + t_p * p_hat
    r_j = q_i + t_q * q_hat

    # Convert to tuples
    coordinates_of_connecting_line_start_point = tuple(r_i)
    coordinates_of_connecting_line_end_point = tuple(r_j)

    return (
        coordinates_of_connecting_line_start_point,
        coordinates_of_connecting_line_end_point,
    )


def calculate_coordinates_of_point_projected_onto_line(
    point: tuple[float, float, float],
    start_point_of_line: tuple[float, float, float],
    end_point_of_line: tuple[float, float, float],
    assume_line_is_finite: bool = False,
) -> tuple[float, float, float]:

    # Get vector of coordinates of VertexPoint
    p = np.array(point)

    # Get vector of coordinates of EdgeStart
    q_i = np.array(start_point_of_line)

    # Get vector of coordinates of EdgeEnd
    q_j = np.array(end_point_of_line)

    # Get unit vector of Edge
    q_hat = (q_j - q_i) * 1 / np.linalg.norm(q_j - q_i)

    # Get constant t
    t = np.dot(p - q_i, q_hat)

    # If the edge is assumed to be finite, then adjust the constant t
    if assume_line_is_finite:
        line_length = np.linalg.norm(q_j - q_i)
        if t < 0:
            t = 0
        if t > line_length:
            t = line_length

    # Calculate vector of projected coordinates of vertex point
    p_star = q_i + t * q_hat

    # Convert to tuple
    projected_point = tuple(float(val) for val in p_star.tolist())
    assert len(projected_point) == 3

    return projected_point


def barycentric_coords(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    eps=1e-12,
) -> np.ndarray:
    """
    Return barycentric coordinates (u, v, w) of point p relative to triangle (a,b,c).
    Assumes p is ON the plane of the triangle (project first if needed).
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    c = np.asarray(c, float)
    p = np.asarray(p, float)

    v0 = b - a
    v1 = c - a
    v2 = p - a

    d00 = np.dot(v0, v0)
    d01 = np.dot(v0, v1)
    d11 = np.dot(v1, v1)
    d20 = np.dot(v2, v0)
    d21 = np.dot(v2, v1)

    denom = d00 * d11 - d01 * d01
    if abs(denom) < eps:
        raise ValueError("Degenerate triangle: area ~ 0.")

    v = (d11 * d20 - d01 * d21) / denom
    w = (d00 * d21 - d01 * d20) / denom
    u = 1.0 - v - w
    return np.array([u, v, w])


def project_point_onto_triangle_plane(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    eps: float = 1e-12,
) -> tuple[
    np.ndarray,
    np.ndarray,
    float,
]:
    """
    Project a 3D point p onto the plane defined by triangle (a, b, c).

    Parameters
    ----------
    p, a, b, c : array-like shape (3,)
        3D coordinates (x, y, z). They can be lists/tuples/ndarrays.
    eps : float
        Tolerance to detect a degenerate triangle (near-zero area).

    Returns
    -------
    proj : np.ndarray shape (3,)
        The orthogonal projection of p onto the plane of triangle ABC.
    n : np.ndarray shape (3,)
        The unit normal vector of the plane (right-hand rule from A->B->C).
    signed_distance : float
        Signed distance from p to the plane along n. (proj = p - signed_distance * n)

    Raises
    ------
    ValueError
        If the triangle is degenerate (area ~ 0).
    """

    p = np.asarray(p, dtype=float)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)

    ab = b - a
    ac = c - a
    n = np.cross(ab, ac)
    norm_n = np.linalg.norm(n)
    if norm_n < eps:
        raise ValueError(
            "Degenerate triangle: vertices are collinear or too close together."
        )

    n /= norm_n
    signed_distance = np.dot(p - a, n)
    proj = p - signed_distance * n
    return proj, n, signed_distance


def project_and_test_inside(
    p: np.ndarray,
    a: np.ndarray,
    b: np.ndarray,
    c: np.ndarray,
    eps: float = 1e-12,
    tol: float = 1e-10,
) -> tuple[
    np.ndarray,
    np.ndarray,
    float,
    bool,
    np.ndarray,
]:
    """
    Project point p onto the plane of triangle (a,b,c), then test if the
    projected point is inside the triangle.

    Returns
    -------
    proj : (3,) np.ndarray       Orthogonal projection of p onto the plane.
    n : (3,) np.ndarray          Unit normal of the plane (A->B->C orientation).
    signed_distance : float      Signed distance from p to the plane along n.
    inside : bool                True if proj lies inside (or on edge of) triangle.
    bary : (3,) np.ndarray       Barycentric coordinates (u, v, w) of proj.
    """
    proj, n, signed_distance = project_point_onto_triangle_plane(p, a, b, c, eps=eps)
    u, v, w = barycentric_coords(proj, a, b, c, eps=eps)

    # Robust inside test with small tolerance to accept boundary points
    inside = (u >= -tol) and (v >= -tol) and (w >= -tol)
    return proj, n, signed_distance, inside, np.array([u, v, w])
