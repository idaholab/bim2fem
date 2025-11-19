# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell.api.system
import ifcopenshell.util.system
import ifcplus.api.distribution_element
import ifcplus.util.geometry
import numpy as np
import ifcplus.util.system
import ifcplus.api.placement
from typing import Literal

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
    ifc4_file: ifcopenshell.file,
    port_origin_in_distribution_element_coordinates: tuple[float, float, float],
    port_z_axis_in_distribution_element_coordinates: tuple[float, float, float],
    port_x_axis_in_distribution_element_coordinates: tuple[float, float, float],
    distribution_element: ifcopenshell.entity_instance,
    flow_direction: FLOW_DIRECTION,
    predefined_type: DISTRIBUTION_PORT_PREDEFINED_TYPE,
    distribution_system: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:

    distribution_port = ifcopenshell.api.system.add_port(
        file=ifc4_file,
        element=distribution_element,
    )

    distribution_port.FlowDirection = flow_direction

    distribution_port.PredefinedType = predefined_type

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        distribution_port.SystemType = distribution_system.PredefinedType

    ifcplus.api.placement.edit_object_placement(
        product=distribution_port,
        repositioned_origin=port_origin_in_distribution_element_coordinates,
        repositioned_z_axis=port_z_axis_in_distribution_element_coordinates,
        repositioned_x_axis=port_x_axis_in_distribution_element_coordinates,
        place_object_relative_to_parent=True,
    )

    return distribution_port


def create_pipe_run_from_polyline(
    ifc4_file: ifcopenshell.file,
    polyline: list[tuple[float, float, float]],
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
    elbow_radius_type: ELBOW_RADIUS_TYPE = "LONG",
    branch_name: str = "Pipe Run",
    spatial_element: ifcopenshell.entity_instance | None = None,
    place_objects_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> list[ifcopenshell.entity_instance]:
    """Create a single path pipe run composed of IfcPipeSegments and
    IfcPipeFittings (Elbows)."""

    if len(polyline) < 2:
        return []

    if len(polyline) == 2:
        pipe_segment = ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc4_file,
            start_point=polyline[0],
            end_point=polyline[1],
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Pipe #1 of {branch_name}",
            parent=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
        )
        return [pipe_segment]

    polyline = ifcplus.util.geometry.filter_out_colinear_points_from_polyline(
        polyline=polyline,
    )

    if elbow_radius_type == "LONG":
        radius_of_curvature = 1.5 * nominal_diameter
    else:
        radius_of_curvature = 1.0 * nominal_diameter

    piping_elements = []

    pipe_segment_start_point = polyline[0]

    for index in range(len(polyline)):

        if index + 2 == len(polyline):
            last_pipe_segment = ifcplus.api.distribution_element.create_pipe_segment(
                ifc4_file=ifc4_file,
                start_point=pipe_segment_start_point,
                end_point=polyline[-1],
                nominal_diameter=nominal_diameter,
                thickness=thickness,
                material=material,
                name=f"Pipe #{[index + 1]} of {branch_name}",
                parent=spatial_element,
                distribution_system=distribution_system,
                place_object_relative_to_parent=place_objects_relative_to_parent,
            )
            piping_elements += [last_pipe_segment]
            break

        horizontal_curve = ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
            first_point=polyline[index],
            second_point=polyline[index + 1],
            third_point=polyline[index + 2],
            radius_of_curvature=radius_of_curvature,
        )

        pipe_segment_end_point = horizontal_curve.point_of_curvature

        pipe_segment = ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc4_file,
            start_point=pipe_segment_start_point,
            end_point=pipe_segment_end_point,
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Pipe #{[index + 1]} of {branch_name}",
            parent=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
        )

        elbow = ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve,
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Elbow #{[index + 1]} of {branch_name}",
            parent=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
        )

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


def connect_two_distribution_ports_via_pipe_run(
    ifc4_file: ifcopenshell.file,
    source_port: ifcopenshell.entity_instance,
    sink_port: ifcopenshell.entity_instance,
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
    elbow_radius_type: ELBOW_RADIUS_TYPE = "LONG",
    branch_name: str = "Unnamed Branch",
    spatial_element: ifcopenshell.entity_instance | None = None,
    add_shape_representation_to_ports: bool = False,
) -> list[ifcopenshell.entity_instance]:
    """Connect two IfcDistributionPorts using a pipe run formed via no
    intelligent method."""

    source_port_origin = ifcplus.util.system.get_port_location(
        distribution_port=source_port,
    )
    source_port_z_axis = ifcplus.util.system.get_port_z_axis(
        distribution_port=source_port
    )

    sink_port_origin = ifcplus.util.system.get_port_location(
        distribution_port=sink_port,
    )
    sink_port_z_axis = ifcplus.util.system.get_port_z_axis(distribution_port=sink_port)

    outer_diameter_of_piping = nominal_diameter + thickness

    second_point = tuple(
        (
            np.array(source_port_origin)
            + np.array(source_port_z_axis) * 1.5 * outer_diameter_of_piping
        ).tolist()
    )

    penultimate_point = tuple(
        (
            np.array(sink_port_origin)
            + -1 * np.array(sink_port_z_axis) * 1.5 * outer_diameter_of_piping
        ).tolist()
    )

    delta_x_between_second_and_penultimate_point = (
        np.array(penultimate_point) - np.array(second_point)
    )[0]

    delta_y_between_second_and_penultimate_point = (
        np.array(penultimate_point) - np.array(second_point)
    )[1]

    third_point = tuple(
        (
            np.array(second_point)
            + np.array([delta_x_between_second_and_penultimate_point, 0.0, 0.0])
        ).tolist()
    )

    fourth_point = tuple(
        (
            np.array(third_point)
            + np.array([0.0, delta_y_between_second_and_penultimate_point, 0.0])
        ).tolist()
    )

    piping_elements = create_pipe_run_from_polyline(
        ifc4_file=ifc4_file,
        polyline=[
            source_port_origin,
            second_point,
            third_point,
            fourth_point,
            penultimate_point,
            sink_port_origin,
        ],
        nominal_diameter=nominal_diameter,
        thickness=thickness,
        material=material,
        elbow_radius_type=elbow_radius_type,
        branch_name=branch_name,
        spatial_element=spatial_element,
        distribution_system=distribution_system,
        place_objects_relative_to_parent=False,
        add_shape_representation_to_ports=add_shape_representation_to_ports,
    )

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
