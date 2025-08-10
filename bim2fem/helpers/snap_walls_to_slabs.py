# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell
import inlbim.util.geometry
import inlbim.util.structural
import inlbim.api.structural
import ifcopenshell.util.element
import numpy as np
import inlbim.util.material
from inlbim.util.geometry import convert_3pt_ndarray_to_tuple_of_floats


def snap_walls_to_slabs(
    ifc4_sav_file: ifcopenshell.file,
    minimum_allowable_snapping_distance: float = 1.0,
) -> ifcopenshell.file:

    # Print Statement
    print("\nSnap walls to slabs")

    # Get walls
    walls = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcWall",
        )
    )
    print(f"\tlen(walls): {len(walls)}")

    # Get slabs
    slabs = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcSlab",
        )
    )
    print(f"\tlen(slabs): {len(slabs)}")

    # Get thicknesses
    thicknesses_for_walls_and_slabs = {}
    for structural_surface_member in walls + slabs:
        material_layer_set = ifcopenshell.util.element.get_material(
            element=structural_surface_member,
            should_skip_usage=True,
        )
        assert material_layer_set
        thickness = inlbim.util.material.sum_material_layer_thicknesses(
            material_layer_set=material_layer_set
        )
        thicknesses_for_walls_and_slabs[structural_surface_member] = thickness

    original_coordinates_of_walls_and_walls = {}
    for structural_surface_member in walls + slabs:
        coordinates_of_structural_surface_member = inlbim.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
            triangular_structural_surface_member=structural_surface_member
        )
        original_coordinates_of_walls_and_walls[structural_surface_member] = (
            coordinates_of_structural_surface_member
        )

    tracker_for_snapped_walls = {}
    for wall in walls:
        tracker_for_snapped_walls[wall] = False

    # tracker_for_snapped_nodes = {}
    # for node in ifc4_sav_file.by_type()

    for wall in walls:

        wall_has_snapped_already = tracker_for_snapped_walls[wall]
        if wall_has_snapped_already:
            continue

        # coordinates_of_wall = inlbim.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
        #     triangular_structural_surface_member=wall
        # )

        original_coordinates_of_wall = original_coordinates_of_walls_and_walls[wall]

        # nodes_of_wall = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
        #     triangular_structural_surface_member=wall
        # )

        for slab in slabs:

            original_coordinates_of_slab = original_coordinates_of_walls_and_walls[slab]

            # coordinates_of_slab = inlbim.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
            #     triangular_structural_surface_member=slab
            # )

            wall_and_slab_are_perpendicular, _ = (
                inlbim.util.geometry.planes_are_right_angled(
                    a1=np.array(original_coordinates_of_wall[0]),
                    b1=np.array(original_coordinates_of_wall[1]),
                    c1=np.array(original_coordinates_of_wall[2]),
                    a2=np.array(original_coordinates_of_slab[0]),
                    b2=np.array(original_coordinates_of_slab[1]),
                    c2=np.array(original_coordinates_of_slab[2]),
                )
            )
            if not wall_and_slab_are_perpendicular:
                continue

            thickness_of_wall = thicknesses_for_walls_and_slabs[wall]
            thickness_of_slab = thicknesses_for_walls_and_slabs[slab]
            allowable_snapping_distance_based_on_dimensions = float(
                1.1 * np.mean([thickness_of_wall, thickness_of_slab])
            )
            allowable_snapping_distance = max(
                [
                    minimum_allowable_snapping_distance,
                    allowable_snapping_distance_based_on_dimensions,
                ]
            )

            a_min, a_max = inlbim.util.geometry.aabb_from_points(
                points=original_coordinates_of_wall
            )
            b_min, b_max = inlbim.util.geometry.aabb_from_points(
                points=original_coordinates_of_slab
            )
            overlap, _ = inlbim.util.geometry.aabb_overlap_3d(
                a_min=a_min,
                a_max=a_max,
                b_min=b_min,
                b_max=b_max,
                tol=allowable_snapping_distance,
                inclusive=True,
            )
            wall_and_slab_are_close_to_each_other = overlap
            if not wall_and_slab_are_close_to_each_other:
                continue

            translation_for_wall = None
            slab_edges = [
                [original_coordinates_of_slab[0], original_coordinates_of_slab[1]],
                [original_coordinates_of_slab[1], original_coordinates_of_slab[2]],
                [original_coordinates_of_slab[2], original_coordinates_of_slab[0]],
            ]
            for slab_edge in slab_edges:

                slab_edge_is_parallel_to_wall, _, _ = (
                    inlbim.util.geometry.line_parallel_to_triangle_plane(
                        p0=slab_edge[0],
                        p1=slab_edge[1],
                        a=original_coordinates_of_wall[0],
                        b=original_coordinates_of_wall[1],
                        c=original_coordinates_of_wall[2],
                    )
                )
                if not slab_edge_is_parallel_to_wall:
                    continue

                coordinates_of_slab_node = slab_edge[0]
                projected_slab_node_coordinates, _, signed_distance, inside, _ = (
                    inlbim.util.geometry.project_point_onto_triangle_plane_and_test_inside(
                        p=np.array(coordinates_of_slab_node),
                        a=np.array(original_coordinates_of_wall[0]),
                        b=np.array(original_coordinates_of_wall[1]),
                        c=np.array(original_coordinates_of_wall[2]),
                    )
                )
                slab_node_is_close_enough_to_wall_to_tell_us_how_to_translate_wall = (
                    abs(signed_distance) <= allowable_snapping_distance
                )
                if (
                    not slab_node_is_close_enough_to_wall_to_tell_us_how_to_translate_wall
                ):
                    continue

                translation_for_wall = (
                    np.array(coordinates_of_slab_node) - projected_slab_node_coordinates
                )

            if isinstance(translation_for_wall, np.ndarray):

                connected_walls = get_walls_connected_to_wall(wall=wall)

                nodes_that_need_translation = []
                for connected_wall in connected_walls:
                    nodes_of_connected_wall = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
                        triangular_structural_surface_member=connected_wall
                    )
                    nodes_that_need_translation += nodes_of_connected_wall
                nodes_that_need_translation = list(set(nodes_that_need_translation))

                for node_that_needs_translation in nodes_that_need_translation:
                    inlbim.api.structural.translate_structural_point_connection(
                        structural_point_connection=node_that_needs_translation,
                        translation=convert_3pt_ndarray_to_tuple_of_floats(
                            translation_for_wall
                        ),
                    )

                for connected_wall in connected_walls:
                    tracker_for_snapped_walls[connected_wall] = True

                break

            if tracker_for_snapped_walls[wall]:
                break

    return ifc4_sav_file


def get_walls_connected_to_wall(
    wall: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance]:

    nodes_of_given_wall = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
        triangular_structural_surface_member=wall
    )

    walls_connected_to_nodes_of_given_wall = []
    for wall_node in nodes_of_given_wall:
        for rel in wall_node.ConnectsStructuralMembers:
            walls_connected_to_nodes_of_given_wall.append(rel.RelatingStructuralMember)

    walls_connected_to_nodes_of_given_wall = list(
        set(walls_connected_to_nodes_of_given_wall)
    )

    return walls_connected_to_nodes_of_given_wall


# def translate_wall(
#     wall: ifcopenshell.entity_instance,
#     translation: tuple[float, float, float],
# ):

#     nodes_of_wall = inlbim.util.structural.get_ordered_structural_point_connections_of_triangular_structural_surface_member(
#         triangular_structural_surface_member=wall
#     )

#     for wall_node in nodes_of_wall:
#         inlbim.api.structural.translate_structural_point_connection(
#             structural_point_connection=wall_node,
#             translation=translation,
#         )

#     return
