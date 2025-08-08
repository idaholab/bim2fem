# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell
import inlbim.util.geometry
import inlbim.util.structural
import inlbim.api.structural
import ifcopenshell.util.element
import numpy as np
import inlbim.util.file


def snap_frame_members(
    ifc4_sav_file: ifcopenshell.file,
) -> ifcopenshell.file:

    # Print Statement
    print("\nSnap Structural Framing Together")

    # Get Columns
    columns = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcColumn",
        )
    )
    print(f"\tlen(columns): {len(columns)}")

    # Get Beams
    beams = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcBeam",
        )
    )
    print(f"\tlen(beams): {len(beams)}")

    # Get Members
    members = (
        inlbim.util.structural.get_structural_items_assigned_to_specified_element_class(
            ifc4_sav_file=ifc4_sav_file,
            ifc_element_class="IfcMember",
        )
    )
    print(f"\tlen(members): {len(members)}")

    # Loop
    static_members = columns
    snapping_members = beams + members
    print(f"\tlen(static_members): {len(static_members)}")
    print(f"\tlen(snapping_members): {len(snapping_members)}")
    cycle_num = 0
    while True:

        # Print snapping cycle
        cycle_num += 1
        print(f"\nSnap Cycle {cycle_num}")

        # Print before dividing
        print("\tBefore Dividing")
        print(f"\t\tstatic_members: {len(static_members)}")
        print(f"\t\tdivisible_members: {len(snapping_members)}")

        # If there are no more snapping members, break
        if len(snapping_members) == 0:
            break

        # If there are no more static_members, break
        if len(static_members) == 0:
            break

        # Divide two sets of structural framing
        divided_snapping_members = divide_structural_curve_members_at_intersection_points_on_spans_with_other_members(
            indivisible_members=static_members,
            divisible_members=snapping_members,
        )

        # Print after dividing
        print("\tAfter Dividing")
        print(f"\t\tdivided_snapping_members: {len(divided_snapping_members)}")

        # Print before snapping
        print("\tBefore Snapping")
        print(f"\t\tstatic_members: {len(static_members)}")
        print(f"\t\tsnapping_members: {len(divided_snapping_members)}")

        # Snap two sets of structural framing together
        unsnapped_members, partially_snapped_members, fully_snapped_members = (
            snap_sets_of_structural_curve_members_together(
                ifc_file=ifc4_sav_file,
                static_members=static_members,
                snapping_members=divided_snapping_members,
            )
        )

        # Get static_members and snapping_members
        static_members = fully_snapped_members + partially_snapped_members
        snapping_members = unsnapped_members

        if len(partially_snapped_members) > 0:
            snap_sets_of_structural_curve_members_together(
                ifc_file=ifc4_sav_file,
                static_members=fully_snapped_members,
                snapping_members=partially_snapped_members,
            )

        # Print after snapping
        print("\tAfter Snapping")
        print(f"\t\tstatic_members: {len(static_members)}")
        print(f"\t\tsnapping_members: {len(snapping_members)}")

    return ifc4_sav_file


def divide_structural_curve_members_at_intersection_points_on_spans_with_other_members(
    indivisible_members: list[ifcopenshell.entity_instance],
    divisible_members: list[ifcopenshell.entity_instance],
) -> list[ifcopenshell.entity_instance]:

    # Initialize division locations
    division_locations_as_proportion_of_length_for_each_divisible_member = {}
    for divisible_member in divisible_members:
        division_locations_as_proportion_of_length_for_each_divisible_member[
            divisible_member
        ] = []

    # Loop through indivisible members
    for indivisible_member in indivisible_members:

        # Get coordinates of indivisible member
        start_point_of_indivisble_member, end_point_of_indivisble_member, _ = (
            inlbim.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
                linear_structural_curve_member=indivisible_member
            )
        )

        # Loop through divisible members
        for divisible_member in divisible_members:

            # Get the allowable snapping distance
            allowable_snapping_distance = (
                get_allowable_snapping_distance_between_structural_curve_members(
                    structural_curve_member_1=indivisible_member,
                    structural_curve_member_2=divisible_member,
                )
            )

            # Get coordinates of divisible member
            start_point_of_divisble_member, end_point_of_divisble_member, _ = (
                inlbim.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
                    linear_structural_curve_member=divisible_member
                )
            )

            # Calculate coordinates of endpoints of shortest line connecting the two members
            (
                start_point_of_connecting_line,
                end_point_of_connecting_line,
            ) = inlbim.util.geometry.calculate_endpoint_coordinates_of_shortest_line_connecting_two_lines(
                coordinates_of_start_of_line_1=start_point_of_indivisble_member,
                coordinates_of_end_of_line_1=end_point_of_indivisble_member,
                coordinates_of_start_of_line_2=start_point_of_divisble_member,
                coordinates_of_end_of_line_2=end_point_of_divisble_member,
                assume_line_1_is_finite=True,
                assume_line_2_is_finite=True,
            )

            # Check if None values were returned for the intersecting line (indicates that the edges are parallel)
            if start_point_of_connecting_line is None:
                continue

            # Get vectors of the intersecting line endpoints
            r_i = np.array(start_point_of_connecting_line)
            r_j = np.array(end_point_of_connecting_line)

            # Get vectors of the edge_of_divisible_member endpoints
            q_i = np.array(start_point_of_divisble_member)
            q_j = np.array(end_point_of_divisble_member)

            # Calculate the distance between edges
            distance_between_edges = np.linalg.norm(r_j - r_i)

            # Determine whether the snapping threshold is exceeded
            snapping_distance_is_within_threshold = (
                distance_between_edges <= allowable_snapping_distance
            )

            # Determine whether the connecting line endpoints are too close to the divisible Edge endpoints
            connecting_line_is_too_close_to_divisible_member_endpoint = any(
                [
                    np.linalg.norm(r_j - q_i) <= allowable_snapping_distance,
                    np.linalg.norm(r_j - q_j) <= allowable_snapping_distance,
                ]
            )

            # Check whether the intersection meets the criteria
            intersecting_line_between_the_edges_meets_criteria_for_defining_a_division_point = all(
                [
                    snapping_distance_is_within_threshold,
                    not connecting_line_is_too_close_to_divisible_member_endpoint,
                ]
            )

            if intersecting_line_between_the_edges_meets_criteria_for_defining_a_division_point:
                division_location_as_distance_from_start_point_of_divisible_member = (
                    np.linalg.norm(q_i - r_j)
                )
                length_of_divisible_member = np.linalg.norm(q_j - q_i)
                division_location_as_proportion_of_length_of_divisible_member = (
                    division_location_as_distance_from_start_point_of_divisible_member
                    / length_of_divisible_member
                )
                division_locations_as_proportion_of_length_for_each_divisible_member[
                    divisible_member
                ].append(division_location_as_proportion_of_length_of_divisible_member)

    # Divide the items
    new_structural_curve_members_after_division = []
    for divisible_member in divisible_members:
        division_locations_as_proportion_of_length = (
            division_locations_as_proportion_of_length_for_each_divisible_member[
                divisible_member
            ]
        )
        new_structural_curve_members = inlbim.api.structural.divide_structural_curve_member(
            structural_curve_member=divisible_member,
            division_locations_as_proportions_of_length=division_locations_as_proportion_of_length,
        )
        new_structural_curve_members_after_division += new_structural_curve_members

    return new_structural_curve_members_after_division


def get_allowable_snapping_distance_between_structural_curve_members(
    structural_curve_member_1: ifcopenshell.entity_instance,
    structural_curve_member_2: ifcopenshell.entity_instance,
) -> float:

    # Create empty list
    largest_dimensions = []

    # Loop
    for structural_curve_member in [
        structural_curve_member_1,
        structural_curve_member_2,
    ]:

        # Get ProfileDef and Material
        material_profile_set = ifcopenshell.util.element.get_material(
            element=structural_curve_member,
            should_skip_usage=True,
        )
        assert isinstance(material_profile_set, ifcopenshell.entity_instance)
        profile_def = material_profile_set.MaterialProfiles[0].Profile

        # Default value
        largest_dimension = 0

        # IfcRectangleProfileDef
        if profile_def.is_a() == "IfcRectangleProfileDef":
            largest_dimension = max(
                [
                    profile_def.XDim,
                    profile_def.YDim,
                ]
            )

        # IfcRectangleHollowProfileDef
        if profile_def.is_a() == "IfcRectangleHollowProfileDef":
            largest_dimension = max(
                [
                    profile_def.XDim,
                    profile_def.YDim,
                    profile_def.WallThickness,
                ]
            )

        # IfcCircleProfileDef
        if profile_def.is_a() == "IfcCircleProfileDef":
            largest_dimension = max(
                [
                    profile_def.Radius,
                ]
            )

        # IfcCircleHollowProfileDef
        if profile_def.is_a() == "IfcCircleHollowProfileDef":
            largest_dimension = max(
                [
                    profile_def.Radius,
                    profile_def.WallThickness,
                ]
            )

        # IfcIShapeProfileDef
        if profile_def.is_a() == "IfcIShapeProfileDef":
            largest_dimension = max(
                [
                    profile_def.OverallWidth,
                    profile_def.OverallDepth,
                    profile_def.WebThickness,
                    profile_def.FlangeThickness,
                ]
            )

        # IfcLShapeProfileDef
        if profile_def.is_a() == "IfcLShapeProfileDef":
            largest_dimension = max(
                [
                    profile_def.Depth,
                    profile_def.Width,
                    profile_def.Thickness,
                ]
            )

        # IfcUShapeProfileDef
        if profile_def.is_a() == "IfcUShapeProfileDef":
            largest_dimension = max(
                [
                    profile_def.Depth,
                    profile_def.FlangeWidth,
                    profile_def.WebThickness,
                    profile_def.FlangeThickness,
                ]
            )

        # IfcTShapeProfileDef
        if profile_def.is_a() == "IfcTShapeProfileDef":
            largest_dimension = max(
                [
                    profile_def.Depth,
                    profile_def.FlangeWidth,
                    profile_def.WebThickness,
                    profile_def.FlangeThickness,
                ]
            )

        # Append to list
        largest_dimensions.append(largest_dimension)

    # Calculate allowable snapping distance
    allowable_snapping_distance = float(1.1 * np.mean(largest_dimensions))

    # Determine whether one of the StructuralCurveMembers is an IfcMember
    one_of_the_structural_curve_members_is_assigned_to_an_ifc_member = False
    for structural_curve_member in [
        structural_curve_member_1,
        structural_curve_member_2,
    ]:
        assigned_product = (
            inlbim.util.structural.get_assigned_product_of_structural_item(
                structural_item=structural_curve_member
            )
        )
        if isinstance(assigned_product, ifcopenshell.entity_instance):
            if assigned_product.is_a("IfcMember"):
                one_of_the_structural_curve_members_is_assigned_to_an_ifc_member = True
                break

    # Give some more allowable snapping distance for IfcMembers, since they are mostly
    # likely at an angle and attache to a gusset place that creates a large distance
    # between the IfcMember and the beam-column joint that it is connected to
    if one_of_the_structural_curve_members_is_assigned_to_an_ifc_member:
        allowable_snapping_distance = max(0.5, allowable_snapping_distance)

    return allowable_snapping_distance


def snap_sets_of_structural_curve_members_together(
    ifc_file: ifcopenshell.file,
    static_members: list[ifcopenshell.entity_instance],
    snapping_members: list[ifcopenshell.entity_instance],
):
    # Get Numeric Scale of Project
    numeric_scale = inlbim.util.file.get_numeric_scale_of_project(ifc4_file=ifc_file)

    # Record total number of members
    total_number_of_members_before_operation = len(static_members + snapping_members)

    # Track the number of snapped endpoints
    count_for_snapped_endpoints = {}
    for snapping_member in snapping_members:
        count_for_snapped_endpoints[snapping_member.id()] = 0

    # Loop through static members
    for static_member in static_members:

        # Get coordinates of indivisible member
        start_point_of_static_member, end_point_of_static_member, _ = (
            inlbim.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
                linear_structural_curve_member=static_member
            )
        )

        # Loop through snapping_members
        for snapping_member in snapping_members:

            # Check whether both endpoints are snapped
            if count_for_snapped_endpoints[snapping_member.id()] > 1:
                continue

            # Get the allowable snapping distance
            allowable_snapping_distance = (
                get_allowable_snapping_distance_between_structural_curve_members(
                    structural_curve_member_1=static_member,
                    structural_curve_member_2=snapping_member,
                )
            )

            # Get StructuralPointConnections of snapping member
            structural_point_connections_of_snapping_member = inlbim.util.structural.get_ordered_structural_point_connections_of_linear_structural_curve_member(
                linear_structural_curve_member=snapping_member,
            )

            # Loop through StructuralPointConnections
            for (
                structural_point_connection_of_snapping_member
            ) in structural_point_connections_of_snapping_member:

                # Get coordinates of StructuralPointConnection of snapping member
                coordinates_of_structural_point_connection = inlbim.util.structural.get_coordinates_of_structural_point_connection(
                    structural_point_connection=structural_point_connection_of_snapping_member
                )

                # Get coordinates of VertexPoint projected onto Edge
                projected_coordinates_of_structural_point_connection = inlbim.util.geometry.calculate_coordinates_of_point_projected_onto_line(
                    point=coordinates_of_structural_point_connection,
                    start_point_of_line=start_point_of_static_member,
                    end_point_of_line=end_point_of_static_member,
                    assume_line_is_finite=True,
                )

                # Calculate the translation vector
                translation_vector = np.array(
                    projected_coordinates_of_structural_point_connection
                ) - np.array(coordinates_of_structural_point_connection)

                # Calculate the distance from the snapping VertexPoint and the Edge
                snapping_distance = np.linalg.norm(translation_vector)

                # Determine whether the snapping distance is within defined limits
                snapping_distance_is_within_threshold = (
                    np.round(snapping_distance, numeric_scale)
                    <= allowable_snapping_distance
                )

                # If the snapping distance is within the threshold, then snap
                if snapping_distance_is_within_threshold:

                    # If the snapping distance is greater than zero, then translate
                    if 0.0 < np.round(snapping_distance, numeric_scale):
                        translation = tuple(
                            float(val) for val in translation_vector.tolist()
                        )
                        assert len(translation) == 3
                        inlbim.api.structural.translate_structural_point_connection(
                            structural_point_connection=structural_point_connection_of_snapping_member,
                            translation=translation,
                        )

                    # Update the count for snapped endpoints
                    count_for_snapped_endpoints[snapping_member.id()] += 1

                    # Break the loop of the VertexPoints
                    break

    # Initialize final lists
    unsnapped_members, partially_snapped_members, fully_snapped_members = [], [], []

    # Populate final lists
    for ifc_id, num_snaps in count_for_snapped_endpoints.items():

        # Get the member
        member = ifc_file.by_id(id=ifc_id)

        # Update unsnapped_members
        if num_snaps == 0:
            unsnapped_members.append(member)

        # Update partially_snapped_members
        if num_snaps == 1:
            partially_snapped_members.append(member)

        # Update fully_snapped_members
        if num_snaps == 2:
            fully_snapped_members.append(member)

    # Check that all members are accounted for
    total_number_of_members_after_operation = len(
        unsnapped_members
        + partially_snapped_members
        + fully_snapped_members
        + static_members
    )

    assert (
        total_number_of_members_before_operation
        == total_number_of_members_after_operation
    )

    return unsnapped_members, partially_snapped_members, fully_snapped_members
