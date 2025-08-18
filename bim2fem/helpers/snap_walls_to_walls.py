# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell
import inlbim.util.geometry
import inlbim.util.structural
import inlbim.api.structural
import ifcopenshell.util.element
import numpy as np
import inlbim.util.material
from inlbim.util.geometry import convert_3pt_ndarray_to_tuple_of_floats


def snap_walls_to_perpendicular_walls(
    ifc4_sav_file: ifcopenshell.file,
    minimum_allowable_snapping_distance: float = 1.0,
) -> ifcopenshell.file:

    # Print Statement
    print("\nSnap structural walls to other nearby perpendicular walls")

    # Get walls
    walls = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcWall",
        )
    )
    print(f"\tlen(walls): {len(walls)}")

    # numeric_scale = inlbim.util.file.get_numeric_scale_of_project(
    #     ifc4_file=ifc4_sav_file
    # )

    # Get thicknesses
    thicknesses_for_walls = {}
    for wall in walls:
        material_layer_set = ifcopenshell.util.element.get_material(
            element=wall,
            should_skip_usage=True,
        )
        assert material_layer_set
        thickness = inlbim.util.material.sum_material_layer_thicknesses(
            material_layer_set=material_layer_set
        )
        thicknesses_for_walls[wall] = thickness

    original_coordinates_of_walls = {}
    for wall in walls:
        coordinates_of_wall = inlbim.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
            triangular_structural_surface_member=wall
        )
        original_coordinates_of_walls[wall] = coordinates_of_wall

    for wall_1 in walls:

        original_coordinates_of_points_of_wall_1 = original_coordinates_of_walls[wall_1]

        for wall_2 in walls:

            walls_are_different = wall_1 != wall_2
            if not walls_are_different:
                continue

            original_coordinates_of_points_of_wall_2 = original_coordinates_of_walls[
                wall_2
            ]

            walls_are_perpendicular, _ = inlbim.util.geometry.planes_are_right_angled(
                a1=original_coordinates_of_points_of_wall_1[0],
                b1=original_coordinates_of_points_of_wall_1[1],
                c1=original_coordinates_of_points_of_wall_1[2],
                a2=original_coordinates_of_points_of_wall_2[0],
                b2=original_coordinates_of_points_of_wall_2[1],
                c2=original_coordinates_of_points_of_wall_2[2],
            )
            if not walls_are_perpendicular:
                continue

            thickness_of_wall_1 = thicknesses_for_walls[wall_1]
            thickness_of_wall_2 = thicknesses_for_walls[wall_2]
            allowable_snapping_distance_based_on_dimensions = float(
                1.1 * np.mean([thickness_of_wall_1, thickness_of_wall_2])
            )
            allowable_snapping_distance = max(
                [
                    minimum_allowable_snapping_distance,
                    allowable_snapping_distance_based_on_dimensions,
                ]
            )

            a_min, a_max = inlbim.util.geometry.aabb_from_points(
                points=original_coordinates_of_points_of_wall_1
            )
            b_min, b_max = inlbim.util.geometry.aabb_from_points(
                points=original_coordinates_of_points_of_wall_2
            )
            overlap, _ = inlbim.util.geometry.aabb_overlap_3d(
                a_min=a_min,
                a_max=a_max,
                b_min=b_min,
                b_max=b_max,
                tol=allowable_snapping_distance,
                inclusive=True,
            )
            walls_are_close_to_each_other = overlap
            if not walls_are_close_to_each_other:
                continue

            p0, dir = inlbim.util.geometry.plane_intersection_line(
                a1=original_coordinates_of_points_of_wall_1[0],
                b1=original_coordinates_of_points_of_wall_1[1],
                c1=original_coordinates_of_points_of_wall_1[2],
                a2=original_coordinates_of_points_of_wall_2[0],
                b2=original_coordinates_of_points_of_wall_2[1],
                c2=original_coordinates_of_points_of_wall_2[2],
            )
            p1 = p0 + dir
            # p0 = tuple(float(val) for val in p0.tolist())
            # assert len(p0) == 3
            # p1 = tuple(float(val) for val in p1.tolist())
            # assert len(p1) == 3

            nodes_of_wall_1 = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
                triangular_structural_surface_member=wall_1
            )
            nodes_of_wall_2 = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
                triangular_structural_surface_member=wall_2
            )

            for wall_node in nodes_of_wall_1 + nodes_of_wall_2:

                coordinates_of_wall_node = inlbim.util.structural.get_coordinates_of_structural_point_connection(
                    structural_point_connection=wall_node
                )

                projected_coordinates_of_wall_node = inlbim.util.geometry.calculate_coordinates_of_point_projected_onto_line(
                    point=coordinates_of_wall_node,
                    start_point_of_line=convert_3pt_ndarray_to_tuple_of_floats(p0),
                    end_point_of_line=convert_3pt_ndarray_to_tuple_of_floats(p1),
                    assume_line_is_finite=False,
                )

                snapping_distance = np.linalg.norm(
                    np.array(projected_coordinates_of_wall_node)
                    - np.array(coordinates_of_wall_node)
                )

                if snapping_distance > allowable_snapping_distance:
                    continue

                # translation = tuple(
                #     float(val)
                #     for val in (
                #         np.array(projected_coordinates_of_wall_node)
                #         - np.array(coordinates_of_wall_node)
                #     ).tolist()
                # )
                # assert len(translation) == 3
                translation = np.array(projected_coordinates_of_wall_node) - np.array(
                    coordinates_of_wall_node
                )

                inlbim.api.structural.translate_structural_point_connection(
                    structural_point_connection=wall_node,
                    translation=convert_3pt_ndarray_to_tuple_of_floats(translation),
                )

    return ifc4_sav_file
