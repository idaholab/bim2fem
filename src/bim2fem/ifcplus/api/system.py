# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell.api.system
import ifcopenshell.util.system
import bim2fem.ifcplus.util.geometry
import numpy as np
import bim2fem.ifcplus.api.geometry
from typing import Literal
import ifcopenshell.util.element
import bim2fem.ifcplus.api.material
import bim2fem.ifcplus.api.piping

FLOW_DIRECTION = Literal[
    "SINK",
    "SOURCE",
    "SOURCEANDSINK",
    "NOTDEFINED",
]

DISTRIBUTION_PORT_PREDEFINED_TYPE = Literal[
    "CABLE",
    "CABLECARRIER",
    "DUCT",
    "PIPE",
    "WIRELESS",
    "USERDEFINED",
    "NOTDEFINED",
]

ELBOW_RADIUS_TYPE = Literal[
    "LONG",
    "SHORT",
]


def create_distribution_port(
    distribution_element: ifcopenshell.entity_instance,
    flow_direction: FLOW_DIRECTION,
    predefined_type: DISTRIBUTION_PORT_PREDEFINED_TYPE,
    distribution_system: ifcopenshell.entity_instance,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:

    ifc4_file = distribution_system.file

    distribution_port = ifcopenshell.api.system.add_port(
        file=ifc4_file,
        element=distribution_element,
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=distribution_port,
    )
    distribution_port.FlowDirection = flow_direction
    distribution_port.PredefinedType = predefined_type
    distribution_port.SystemType = distribution_system.PredefinedType

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=distribution_port,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    distribution_port.ObjectPlacement.PlacementRelTo = (
        distribution_element.ObjectPlacement
    )

    return distribution_port


def create_pipe_run_from_polyline(
    polyline: list[tuple[float, float, float]],
    outer_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
    elbow_radius_type: ELBOW_RADIUS_TYPE = "LONG",
    branch_name: str = "Pipe Run",
) -> list[ifcopenshell.entity_instance]:
    """Create a single path pipe run composed of IfcPipeSegments and
    IfcPipeFittings (Elbows)."""

    ifc4_file = distribution_system.file

    if len(polyline) < 2:
        return []

    if len(polyline) == 2:
        pipe_segment = bim2fem.ifcplus.api.piping.create_pipe_segment(
            start_point=polyline[0],
            end_point=polyline[1],
            outer_diameter=outer_diameter,
            thickness=thickness,
            material=material,
            distribution_system=distribution_system,
        )
        pipe_segment.Name = f"Pipe #1 of {branch_name}"
        return [pipe_segment]

    polyline = bim2fem.ifcplus.util.geometry.filter_out_colinear_points_from_polyline(
        polyline=polyline,
    )

    nominal_diameter = outer_diameter - thickness

    if elbow_radius_type == "LONG":
        radius_of_curvature = 1.5 * nominal_diameter
    else:
        radius_of_curvature = 1.0 * nominal_diameter

    piping_elements = []

    pipe_segment_start_point = polyline[0]

    for index in range(len(polyline)):

        if index + 2 == len(polyline):
            last_pipe_segment = bim2fem.ifcplus.api.piping.create_pipe_segment(
                start_point=pipe_segment_start_point,
                end_point=polyline[-1],
                outer_diameter=outer_diameter,
                thickness=thickness,
                material=material,
                distribution_system=distribution_system,
            )
            last_pipe_segment.Name = f"Pipe #{[index + 1]} of {branch_name}"
            piping_elements += [last_pipe_segment]
            break

        p1 = polyline[index]
        p2 = polyline[index + 1]
        p3 = polyline[index + 2]
        radius_of_curvature = radius_of_curvature
        horizontal_curve = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                first_point=p1,
                second_point=p2,
                third_point=p3,
                radius_of_curvature=radius_of_curvature,
            )
        )

        pipe_segment_end_point = horizontal_curve.point_of_curvature

        pipe_segment = bim2fem.ifcplus.api.piping.create_pipe_segment(
            start_point=pipe_segment_start_point,
            end_point=pipe_segment_end_point,
            outer_diameter=outer_diameter,
            thickness=thickness,
            material=material,
            distribution_system=distribution_system,
        )
        pipe_segment.Name = f"Pipe #{[index + 1]} of {branch_name}"

        elbow = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve.point_of_curvature,
            end_point=horizontal_curve.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve.center_of_curvature,
            radius_of_curvature=horizontal_curve.radius_of_curvature,
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            distribution_system=distribution_system,
        )
        elbow.Name = f"Elbow #{[index + 1]} of {branch_name}"

        piping_elements += [pipe_segment, elbow]

        pipe_segment_start_point = horizontal_curve.point_of_tangency

    for index_for_an_elbow in range(len(piping_elements))[1::2]:
        pipe_segment_1 = piping_elements[index_for_an_elbow - 1]
        elbow = piping_elements[index_for_an_elbow]
        pipe_segment_2 = piping_elements[index_for_an_elbow + 1]
        ifcopenshell.api.system.connect_port(
            file=ifc4_file,
            port1=ifcopenshell.util.system.get_ports(
                element=pipe_segment_1,
                flow_direction="SOURCE",
            )[0],
            port2=ifcopenshell.util.system.get_ports(
                element=elbow,
                flow_direction="SINK",
            )[0],
            direction="SOURCE",
        )
        ifcopenshell.api.system.connect_port(
            file=ifc4_file,
            port1=ifcopenshell.util.system.get_ports(
                element=elbow,
                flow_direction="SOURCE",
            )[0],
            port2=ifcopenshell.util.system.get_ports(
                element=pipe_segment_2,
                flow_direction="SINK",
            )[0],
            direction="SOURCE",
        )

    return piping_elements


def connect_two_distribution_ports_via_dumb_piping(
    source_port: ifcopenshell.entity_instance,
    sink_port: ifcopenshell.entity_instance,
    outer_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance | None,
    distribution_system: ifcopenshell.entity_instance,
    elbow_radius_type: ELBOW_RADIUS_TYPE = "LONG",
    branch_name: str = "Unnamed Branch",
    polyline: list[tuple[float, float, float]] | None = None,
) -> list[ifcopenshell.entity_instance]:
    """Connect two IfcDistributionPorts using a pipe run formed via no
    intelligent method."""

    ifc4_file = distribution_system.file

    if polyline is None:

        source_port_origin = (
            bim2fem.ifcplus.util.geometry.get_location_in_global_coordinates(
                product=source_port,
            )
        )
        sink_port_origin = (
            bim2fem.ifcplus.util.geometry.get_location_in_global_coordinates(
                product=sink_port,
            )
        )
        source_port_z_axis = (
            bim2fem.ifcplus.util.geometry.get_z_axis_in_global_coordinates(
                product=source_port,
            )
        )
        sink_port_z_axis = (
            bim2fem.ifcplus.util.geometry.get_z_axis_in_global_coordinates(
                product=sink_port,
            )
        )

        direction_vector_0_to_1 = tuple(
            (np.array(source_port_z_axis) * 1.5 * outer_diameter).tolist()
        )
        direction_vector_4_to_5 = tuple(
            (np.array(sink_port_z_axis) * 1.5 * outer_diameter).tolist()
        )

        point_0 = source_port_origin
        point_5 = sink_port_origin

        point_1 = tuple(
            (np.array(point_0) + np.array(direction_vector_0_to_1)).tolist()
        )
        point_4 = tuple(
            (np.array(point_5) + -1 * np.array(direction_vector_4_to_5)).tolist()
        )

        point_4_minus_point_1 = tuple((np.array(point_4) - np.array(point_1)).tolist())
        dx, dy, dz = point_4_minus_point_1

        direction_vector_1_to_2 = (dx, 0.0, 0.0)
        direction_vector_2_to_3 = (0.0, dy, 0.0)
        direction_vector_3_to_4 = (0.0, 0.0, dz)

        angle_a = bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
            vector1=direction_vector_0_to_1,
            vector2=direction_vector_1_to_2,
        )
        angle_a_is_180d = np.round(abs(angle_a - np.pi), 4) == 0.0

        angle_b = bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
            vector1=direction_vector_3_to_4,
            vector2=direction_vector_4_to_5,
        )
        angle_b_is_180d = np.round(abs(angle_b - np.pi), 4) == 0.0

        if angle_a_is_180d:
            direction_vector_1_to_2, direction_vector_2_to_3 = (
                direction_vector_2_to_3,
                direction_vector_1_to_2,
            )
        if angle_b_is_180d:
            direction_vector_2_to_3, direction_vector_3_to_4 = (
                direction_vector_3_to_4,
                direction_vector_2_to_3,
            )

        polyline = [point_0]
        for direction_vector in [
            direction_vector_0_to_1,
            direction_vector_1_to_2,
            direction_vector_2_to_3,
            direction_vector_3_to_4,
            direction_vector_4_to_5,
        ]:
            prev_point = polyline[-1]
            new_point = tuple(
                (np.array(prev_point) + np.array(direction_vector)).tolist()
            )
            polyline.append(new_point)
        print("debug")

    if material is None:
        material = bim2fem.ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc4_file,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

    piping_elements = create_pipe_run_from_polyline(
        polyline=polyline,
        outer_diameter=outer_diameter,
        thickness=thickness,
        material=material,
        elbow_radius_type=elbow_radius_type,
        branch_name=branch_name,
        distribution_system=distribution_system,
    )

    for port in [source_port, sink_port]:
        for rel in port.ConnectedTo or []:
            history = rel.OwnerHistory
            ifc4_file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(ifc4_file, history)
        for rel in port.ConnectedFrom or []:
            history = rel.OwnerHistory
            ifc4_file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(ifc4_file, history)

    first_pipe_segment = piping_elements[0]
    last_pipe_segment = piping_elements[-1]
    sink_port_of_first_pipe_segment = ifcopenshell.util.system.get_ports(
        element=first_pipe_segment,
        flow_direction="SINK",
    )[0]
    source_port_of_last_pipe_segment = ifcopenshell.util.system.get_ports(
        element=last_pipe_segment,
        flow_direction="SOURCE",
    )[0]
    ifcopenshell.api.system.connect_port(
        file=source_port.file,
        port1=source_port,
        port2=sink_port_of_first_pipe_segment,
    )
    ifcopenshell.api.system.connect_port(
        file=source_port.file,
        port1=source_port_of_last_pipe_segment,
        port2=sink_port,
    )

    return piping_elements
