# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

from re import T
import ifcopenshell
import ifcopenshell.util.element
import ifcplus.util.geometry
import ifcplus.util.material
import ifcplus.api.material
from ifcplus import REGION
import ifcplus.util.profile
import ifcopenshell.api.root
import ifcplus.api.profile
import ifcplus.api.structural
import ifcopenshell.util.representation
import ifcopenshell.util.placement
import numpy as np
import ifcplus.util.representation
from ifcplus.util.geometry import TriangularMesh
import bim2fem.helpers.classify_beam_shape
import ifcopenshell.util.unit
import ifcplus.api.element_type
import ifcopenshell.api.type
import ifcopenshell.api.spatial
import ifcplus.util.project
import ifcopenshell.api.project
import ifcopenshell.util.system
import ifcplus.util.structural
import math


def convert_pipe_fitting_to_structural_items(
    pipe_fitting_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance] | None:

    print("\tconvert_pipe_fitting_to_structural_items()")
    print(f"\telement_from_source_file: {pipe_fitting_from_source_file}")
    print(f"\tregion: {region}")
    print(f"\tstructural_analysis_model: {structural_analysis_model}")

    # Check IFC Class
    required_ifc_class = "IfcPipeFitting"
    if not pipe_fitting_from_source_file.is_a(required_ifc_class):
        print(
            " ".join(
                [
                    "\tWarning: Failed Conversion for",
                    f"{pipe_fitting_from_source_file}. ",
                    f"IfcElement class must be {required_ifc_class}.",
                ]
            )
        )
        return None

    # Copy Element to Destination File
    pipe_fitting_copied_to_destination_file = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class=pipe_fitting_from_source_file.is_a(),
        name=pipe_fitting_from_source_file.Name,
    )
    pipe_fitting_copied_to_destination_file.GlobalId = (
        pipe_fitting_from_source_file.GlobalId
    )

    # Assign Element to Site
    site = ifc4_destination_file.by_type(type="IfcSite", include_subtypes=False)[0]
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_destination_file,
        products=[pipe_fitting_copied_to_destination_file],
        relating_structure=site,
    )

    # Get best matching standard material name, if it exists
    material_names_from_destination_file = list(
        {
            material.Name
            for material in ifc4_destination_file.by_type(
                type="IfcMaterial",
                include_subtypes=False,
            )
        }
    )
    standard_material_name = (
        ifcplus.util.material.get_best_matching_standard_material_from_element_metadata(
            element=pipe_fitting_from_source_file,
            region=region,
            other_material_names=material_names_from_destination_file,
        )
    )
    if standard_material_name is None:
        if region == "Europe":
            standard_material_name = "S355"
        elif region == "UnitedStates":
            standard_material_name = "A36"
        else:
            standard_material_name = "S355"
    print(f"\tstandard_material_name: {standard_material_name}")

    # Get the number of ports
    connected_from = ifcopenshell.util.system.get_connected_from(
        element=pipe_fitting_from_source_file,
    )
    connected_to = ifcopenshell.util.system.get_connected_to(
        element=pipe_fitting_from_source_file,
    )
    number_of_connections = len(connected_from) + len(connected_to)

    if number_of_connections == 2:

        first_pipe_as_architectural_element = ifc4_destination_file.by_guid(
            guid=connected_from[0].GlobalId
        )
        first_pipe_as_analytical_element = (
            ifcplus.util.structural.get_structural_items_of_assigned_product(
                assigned_product=first_pipe_as_architectural_element
            )
        )[0]
        first_pipe_endpoint_coordinates = ifcplus.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
            linear_structural_curve_member=first_pipe_as_analytical_element
        )
        first_pipe_vector = (
            ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
                p1=first_pipe_endpoint_coordinates[0],
                p2=first_pipe_endpoint_coordinates[1],
            )
        )

        second_pipe_as_architectural_element = ifc4_destination_file.by_guid(
            guid=connected_to[0].GlobalId
        )
        second_pipe_as_analytical_element = (
            ifcplus.util.structural.get_structural_items_of_assigned_product(
                assigned_product=second_pipe_as_architectural_element
            )
        )[0]
        second_pipe_endpoint_coordinates = ifcplus.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
            linear_structural_curve_member=second_pipe_as_analytical_element
        )
        second_pipe_vector = (
            ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
                p1=second_pipe_endpoint_coordinates[0],
                p2=second_pipe_endpoint_coordinates[1],
            )
        )

        angle = ifcplus.util.geometry.calculate_angle_between_two_vectors(
            vector1=first_pipe_vector,
            vector2=second_pipe_vector,
        )
        angle_in_degrees = float(angle * 180 / np.pi)
        angle_is_acute = 45 * 0.9 <= angle_in_degrees <= 0.9 * 180

        print("debug")

        if angle_is_acute:

            material_profile_set = ifcopenshell.util.element.get_material(
                element=first_pipe_as_analytical_element, should_skip_usage=True
            )
            assert isinstance(material_profile_set, ifcopenshell.entity_instance)
            profile_def = material_profile_set.MaterialProfiles[0].Profile
            nominal_diameter = (
                profile_def.Radius - profile_def.WallThickness / 2.0
            ) * 2.0
            incoming_segment, outgoing_segment = orient_flow_segments(
                incoming_segment=first_pipe_endpoint_coordinates[0:2],
                outgoing_segment=second_pipe_endpoint_coordinates[0:2],
            )

            connecting_segment_of_inf_lines = ifcplus.util.geometry.calculate_endpoint_coordinates_of_shortest_line_connecting_two_lines(
                coordinates_of_start_of_line_1=incoming_segment[0],
                coordinates_of_end_of_line_1=incoming_segment[1],
                coordinates_of_start_of_line_2=outgoing_segment[0],
                coordinates_of_end_of_line_2=outgoing_segment[1],
                assume_line_1_is_finite=False,
                assume_line_2_is_finite=False,
            )
            if connecting_segment_of_inf_lines[0] is None:
                return None

            dist = distance_3d(
                p1=connecting_segment_of_inf_lines[0],
                p2=connecting_segment_of_inf_lines[1],
            )

            intersection_of_pipe_segments_exists = np.round(dist, 4) == 0.0
            if not intersection_of_pipe_segments_exists:
                return None

            radius_of_curvature_assuming_long_elbow = 1.5 * nominal_diameter
            radius_of_curvature_assuming_short_elbow = 1.0 * nominal_diameter

            horizontal_curve_assuming_long_elbow = (
                ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                    first_point=incoming_segment[1],
                    second_point=connecting_segment_of_inf_lines[0],
                    third_point=outgoing_segment[0],
                    radius_of_curvature=radius_of_curvature_assuming_long_elbow,
                )
            )

            horizontal_curve_assuming_short_elbow = (
                ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                    first_point=incoming_segment[1],
                    second_point=connecting_segment_of_inf_lines[0],
                    third_point=outgoing_segment[0],
                    radius_of_curvature=radius_of_curvature_assuming_short_elbow,
                )
            )

            error_for_horizontal_curve_assuming_long_elbow = np.linalg.norm(
                np.array(horizontal_curve_assuming_long_elbow.point_of_curvature)
                - np.array(incoming_segment[1])
            )
            error_for_horizontal_curve_assuming_short_elbow = np.linalg.norm(
                np.array(horizontal_curve_assuming_short_elbow.point_of_curvature)
                - np.array(incoming_segment[1])
            )
            if (
                error_for_horizontal_curve_assuming_long_elbow
                < error_for_horizontal_curve_assuming_short_elbow
            ):
                horizontal_curve = horizontal_curve_assuming_long_elbow
            else:
                horizontal_curve = horizontal_curve_assuming_short_elbow

            edge_for_incoming_pipe_segment = (
                first_pipe_as_analytical_element.Representation.Representations[
                    0
                ].Items[0]
            )
            edge_for_incoming_pipe_segment.EdgeStart.VertexGeometry.Coordinates = (
                incoming_segment[0]
            )
            edge_for_incoming_pipe_segment.EdgeEnd.VertexGeometry.Coordinates = (
                horizontal_curve.point_of_curvature
            )

            edge_for_outgoing_pipe_segment = (
                second_pipe_as_analytical_element.Representation.Representations[
                    0
                ].Items[0]
            )
            edge_for_outgoing_pipe_segment.EdgeStart.VertexGeometry.Coordinates = (
                horizontal_curve.point_of_tangency
            )
            edge_for_outgoing_pipe_segment.EdgeEnd.VertexGeometry.Coordinates = (
                outgoing_segment[1]
            )

            # Create the standard material
            material = ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_destination_file,
                region=region,
                material_name=standard_material_name,
                check_for_duplicate=True,
            )
            assert isinstance(material, ifcopenshell.entity_instance)

            incoming_segment_vector = (
                ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
                    p1=incoming_segment[0],
                    p2=incoming_segment[1],
                )
            )
            outgoing_segment_vector = (
                ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
                    p1=outgoing_segment[0],
                    p2=outgoing_segment[1],
                )
            )
            local_z_axis_in_global_coordinates = (
                ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                    vector1=incoming_segment_vector, vector2=outgoing_segment_vector
                )
            )
            orientation_point = np.array(
                horizontal_curve.point_of_curvature
            ) + np.array(local_z_axis_in_global_coordinates)
            orientation_point = tuple(float(val) for val in orientation_point.tolist())
            assert len(orientation_point) == 3

            # Create StructuralItem
            structural_curve_member = (
                ifcplus.api.structural.create_curved_structural_curve_member(
                    horizontal_curve,
                    orientation_point=orientation_point,
                    profile_def=profile_def,
                    material=material,
                    structural_analysis_model=structural_analysis_model,
                    corresponding_product=pipe_fitting_copied_to_destination_file,
                )
            )

            return [structural_curve_member]

    print("debug")

    return None


def distance_3d(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
) -> float:
    """Calculate Euclidean distance between two 3D points."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))


def orient_flow_segments(
    incoming_segment: tuple[tuple[float, float, float], tuple[float, float, float]],
    outgoing_segment: tuple[tuple[float, float, float], tuple[float, float, float]],
) -> tuple[
    tuple[tuple[float, float, float], tuple[float, float, float]],
    tuple[tuple[float, float, float], tuple[float, float, float]],
]:
    """
    Orient pipe segments according to flow direction.

    Args:
        incoming_segment: Two 3D points defining the incoming flow pipe segment
        outgoing_segment: Two 3D points defining the outgoing flow pipe segment

    Returns:
        Tuple of oriented segments where:
        - Incoming segment: (start_point, end_point) where vector points toward elbow
        - Outgoing segment: (start_point, end_point) where vector points away from elbow
    """

    # Unpack the segments
    in_p1, in_p2 = incoming_segment
    out_p1, out_p2 = outgoing_segment

    # Calculate all possible distances between endpoints
    distances = [
        (distance_3d(in_p1, out_p1), "in_p1", "out_p1"),
        (distance_3d(in_p1, out_p2), "in_p1", "out_p2"),
        (distance_3d(in_p2, out_p1), "in_p2", "out_p1"),
        (distance_3d(in_p2, out_p2), "in_p2", "out_p2"),
    ]

    # Find the minimum distance - these are the points at the elbow
    min_dist, in_point, out_point = min(distances)

    # Orient the incoming segment so it ends at the elbow
    if in_point == "in_p1":
        # in_p1 is at the elbow, so flow goes from in_p2 to in_p1
        oriented_incoming = (in_p2, in_p1)
    else:
        # in_p2 is at the elbow, so flow goes from in_p1 to in_p2
        oriented_incoming = (in_p1, in_p2)

    # Orient the outgoing segment so it starts at the elbow
    if out_point == "out_p1":
        # out_p1 is at the elbow, so flow goes from out_p1 to out_p2
        oriented_outgoing = (out_p1, out_p2)
    else:
        # out_p2 is at the elbow, so flow goes from out_p2 to out_p1
        oriented_outgoing = (out_p2, out_p1)

    return oriented_incoming, oriented_outgoing
