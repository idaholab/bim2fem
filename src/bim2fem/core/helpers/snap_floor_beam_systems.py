# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import inlbim.util.geometry
import inlbim.util.structural
import inlbim.api.structural
import ifcopenshell.util.element
import numpy as np
import inlbim.util.profile
import inlbim.util.material


def snap_floor_beam_systems(
    ifc4_sav_file: ifcopenshell.file,
    minimum_allowable_snapping_distance=1.0,
) -> ifcopenshell.file:

    # Print Statement
    print("\nSnap Floor Beam Systems")

    # Get Beams
    beams = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcBeam",
        )
    )
    print(f"\tlen(beams): {len(beams)}")

    # Get Columns
    columns = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcColumn",
        )
    )
    print(f"\tlen(columns): {len(columns)}")

    # Get Members
    members = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcMember",
        )
    )
    print(f"\tlen(members): {len(members)}")

    # Get slabs
    slabs = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcSlab",
        )
    )
    print(f"\tlen(slabs): {len(slabs)}")

    # Largest dimensions of beam profiles mapped to associated beam nodes
    largest_profile_dimensions_mapped_to_nodes = {}

    # Get all nodes associated with frame members
    all_frame_member_nodes = []
    for frame_member in beams + columns + members:

        # Get Nodes
        nodes = inlbim.util.structural.get_ordered_structural_point_connections_of_linear_structural_curve_member(
            linear_structural_curve_member=frame_member
        )
        all_frame_member_nodes += nodes

        # Get ProfileDef and Material
        material_profile_set = ifcopenshell.util.element.get_material(
            element=frame_member,
            should_skip_usage=True,
        )
        assert isinstance(material_profile_set, ifcopenshell.entity_instance)
        profile_def = material_profile_set.MaterialProfiles[0].Profile

        # Get largest dimension
        largest_dimension = (
            inlbim.util.profile.get_large_dimension_of_parameterized_profile_def(
                parameterized_profile_def=profile_def
            )
        )

        # Assign largest profile dimension information to nodes
        for node in nodes:
            if node not in largest_profile_dimensions_mapped_to_nodes.keys():
                largest_profile_dimensions_mapped_to_nodes[node] = largest_dimension
            else:
                if largest_profile_dimensions_mapped_to_nodes[node] < largest_dimension:
                    largest_profile_dimensions_mapped_to_nodes[node] = largest_dimension

    # Remove repeat nodes
    all_frame_member_nodes = list(set(all_frame_member_nodes))

    # Get thicknesses for each slab
    thicknesses_for_slabs = {}
    for slab in slabs:
        material_layer_set = ifcopenshell.util.element.get_material(
            element=slab,
            should_skip_usage=True,
        )
        assert material_layer_set
        thickness = inlbim.util.material.sum_material_layer_thicknesses(
            material_layer_set=material_layer_set
        )
        thicknesses_for_slabs[slab] = thickness

    # Cycle through beam nodes
    count_of_snapped_frame_member_nodes = 0
    for beam_node in all_frame_member_nodes:

        # Cycle through slabs
        for slab in slabs:

            # Get the allowable snapping distance
            profile_dimension = largest_profile_dimensions_mapped_to_nodes[beam_node]
            slab_thickness = thicknesses_for_slabs[slab]
            allowable_snapping_distance_based_on_dimensions = float(
                1.1 * np.mean([profile_dimension, slab_thickness])
            )
            allowable_snapping_distance = max(
                [
                    minimum_allowable_snapping_distance,
                    allowable_snapping_distance_based_on_dimensions,
                ]
            )

            # Get beam coordinates
            beam_node_coordinates = (
                inlbim.util.structural.get_coordinates_of_structural_point_connection(
                    structural_point_connection=beam_node
                )
            )

            # Get slab coordinates
            slab_coordinates = inlbim.util.structural.get_coordinates_of_points_on_outer_bound_of_structural_surface_member(
                triangular_structural_surface_member=slab
            )

            # Project Beam Node onto slab and test inside
            projected_beam_node_coordinates, _, signed_distance, inside, _ = (
                inlbim.util.geometry.project_point_onto_triangle_plane_and_test_inside(
                    p=np.array(beam_node_coordinates),
                    a=np.array(slab_coordinates[0]),
                    b=np.array(slab_coordinates[1]),
                    c=np.array(slab_coordinates[2]),
                )
            )

            # Check snapping criteria
            beam_node_is_close_enough_for_snapping = (
                abs(signed_distance) <= allowable_snapping_distance
            )
            projected_beam_node_is_inside_slab = inside
            snapping_criteria_satisfied = (
                beam_node_is_close_enough_for_snapping
                and projected_beam_node_is_inside_slab
            )

            # If snapping criteria is satisfied, then translate
            if snapping_criteria_satisfied:
                translation_vector = projected_beam_node_coordinates - np.array(
                    beam_node_coordinates
                )
                translation = tuple(float(val) for val in translation_vector.tolist())
                assert len(translation) == 3
                inlbim.api.structural.translate_structural_point_connection(
                    structural_point_connection=beam_node,
                    translation=translation,
                )
                count_of_snapped_frame_member_nodes += 1

    print(f"\tcount_of_all_frame_member_nodes: {len(all_frame_member_nodes)}")
    print(
        f"\tcount_of_snapped_frame_member_nodes: {count_of_snapped_frame_member_nodes}"
    )

    return ifc4_sav_file
