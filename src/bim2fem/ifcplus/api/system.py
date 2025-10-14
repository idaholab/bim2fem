# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell.api.system
import ifcopenshell.util.system
import bim2fem.ifcplus.api.distribution_element
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import bim2fem.ifcplus.util.geometry
import bim2fem.ifcplus.api.style
import numpy as np
import ifcopenshell.util.placement
import ifcopenshell.util.representation
from bim2fem.ifcplus.api.distribution_element import ELBOW_RADIUS_TYPE
import bim2fem.ifcplus.util.system


def add_shape_representation_to_distribution_ports(
    ports: list[ifcopenshell.entity_instance],
    arrow_size: float = 0.1,
) -> None:
    ifc4_file = ports[0].file

    sink_arrow = None
    source_arrow = None
    ambiguous_arrow = None

    for port in ports:
        if port.FlowDirection == "SINK":
            if sink_arrow is None:
                sink_arrow = bim2fem.ifcplus.api.geometry.add_csg_solid(
                    boolean_result_or_primitive=bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
                        ifc4_file=ifc4_file,
                        length=arrow_size,
                        width=arrow_size,
                        height=arrow_size,
                        repositioned_origin=(-arrow_size / 2, -arrow_size / 2, 0.0),
                    ),
                )
            csg_solid = sink_arrow
            color = (0.0, 0.0, 1.0)

        elif port.FlowDirection == "SOURCE":
            if source_arrow is None:
                source_arrow = bim2fem.ifcplus.api.geometry.add_csg_solid(
                    boolean_result_or_primitive=bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
                        ifc4_file=ifc4_file,
                        length=arrow_size,
                        width=arrow_size,
                        height=arrow_size,
                        repositioned_origin=(
                            -arrow_size / 2,
                            -arrow_size / 2,
                            -arrow_size,
                        ),
                    ),
                )
            csg_solid = source_arrow
            color = (1.0, 0.0, 0.0)

        else:
            if ambiguous_arrow is None:
                ambiguous_arrow = bim2fem.ifcplus.api.geometry.add_csg_solid(
                    boolean_result_or_primitive=bim2fem.ifcplus.api.geometry.add_sphere(
                        ifc4_file=ifc4_file,
                        radius=arrow_size,
                    ),
                )
            csg_solid = ambiguous_arrow
            color = None

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        if representation_type is None:
            return None

        shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=port,
            representation=shape_model,
        )

        if color:
            bim2fem.ifcplus.api.style.assign_color_to_element(
                element=port,
                rgb_triplet=color,
                transparency=0.0,
            )


def filter_out_colinear_points_from_polyline(
    polyline: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:

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

        v12 = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=p1,
            p2=p2,
        )

        v23 = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=p2,
            p2=p3,
        )

        angle = bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
            vector1=v12, vector2=v23
        )

        if angle == 0.0:
            indices_of_points_to_remove.append(index + 1)

        new_polyine = remove_items_by_indices(
            lst=polyline, indices=indices_of_points_to_remove
        )

    return new_polyine


def create_piping_system_from_polyline(
    ifc4_file: ifcopenshell.file,
    polyline: list[tuple[float, float, float]],
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
    elbow_radius_type: ELBOW_RADIUS_TYPE = "LONG",
    branch_name: str = "Unnamed Branch",
    spatial_element: ifcopenshell.entity_instance | None = None,
    place_objects_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> list[ifcopenshell.entity_instance]:
    """Create a single path pipe branch composed of IfcPipeSegments and
    IfcPipeFittings (Elbows)."""

    if len(polyline) < 2:
        return []

    if len(polyline) == 2:
        pipe_segment = bim2fem.ifcplus.api.distribution_element.create_pipe_segment(
            p1=polyline[0],
            p2=polyline[1],
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Pipe #1 of {branch_name}",
            spatial_element=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
            add_shape_representation_to_ports=add_shape_representation_to_ports,
        )
        return [pipe_segment]

    polyline = filter_out_colinear_points_from_polyline(polyline=polyline)

    if elbow_radius_type == "LONG":
        radius_of_curvature = 1.5 * nominal_diameter
    else:
        radius_of_curvature = 1.0 * nominal_diameter

    piping_elements = []

    pipe_segment_start_point = polyline[0]

    for index in range(len(polyline)):

        if index + 2 == len(polyline):
            last_pipe_segment = (
                bim2fem.ifcplus.api.distribution_element.create_pipe_segment(
                    p1=pipe_segment_start_point,
                    p2=polyline[-1],
                    nominal_diameter=nominal_diameter,
                    thickness=thickness,
                    material=material,
                    name=f"Pipe #{[index + 1]} of {branch_name}",
                    spatial_element=spatial_element,
                    distribution_system=distribution_system,
                    place_object_relative_to_parent=place_objects_relative_to_parent,
                    add_shape_representation_to_ports=add_shape_representation_to_ports,
                )
            )
            piping_elements += [last_pipe_segment]
            break

        horizontal_curve = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                first_point=polyline[index],
                second_point=polyline[index + 1],
                third_point=polyline[index + 2],
                radius_of_curvature=radius_of_curvature,
            )
        )

        pipe_segment_end_point = horizontal_curve.point_of_curvature

        pipe_segment = bim2fem.ifcplus.api.distribution_element.create_pipe_segment(
            p1=pipe_segment_start_point,
            p2=pipe_segment_end_point,
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Pipe #{[index + 1]} of {branch_name}",
            spatial_element=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
            add_shape_representation_to_ports=add_shape_representation_to_ports,
        )

        elbow = bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve,
            nominal_diameter=nominal_diameter,
            thickness=thickness,
            material=material,
            name=f"Elbow #{[index + 1]} of {branch_name}",
            spatial_element=spatial_element,
            distribution_system=distribution_system,
            place_object_relative_to_parent=place_objects_relative_to_parent,
            add_shape_representation_to_ports=add_shape_representation_to_ports,
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


def connect_two_distribution_ports_via_piping_with_no_intelligence(
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
    """Connect two IfcDistributionPorts using a single path pipe branch formed via no
    intelligent method."""

    source_port_origin = bim2fem.ifcplus.util.system.get_port_location(
        distribution_port=source_port,
    )
    source_port_z_axis = bim2fem.ifcplus.util.system.get_port_z_axis(
        distribution_port=source_port
    )

    sink_port_origin = bim2fem.ifcplus.util.system.get_port_location(
        distribution_port=sink_port,
    )
    sink_port_z_axis = bim2fem.ifcplus.util.system.get_port_z_axis(
        distribution_port=sink_port
    )

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

    (
        delta_x_between_second_and_penultimate_point,
        delta_y_between_second_and_penultimate_point,
        _,
    ) = tuple((np.array(penultimate_point) - np.array(second_point)).tolist())

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

    piping_elements = create_piping_system_from_polyline(
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
