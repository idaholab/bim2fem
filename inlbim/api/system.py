# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell.api.system
import ifcopenshell.util.system
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import inlbim.api.geometry
import inlbim.api.representation
import inlbim.api.profile
import ifcopenshell.api.geometry
import inlbim.util.geometry
import ifcopenshell.api.material
import inlbim.api.style
import numpy as np
from typing import Literal
import inlbim.api.system
import ifcopenshell.util.placement

ELBOW_RADIUS_TYPE = Literal["LONG", "SHORT"]


def create_elbow(
    horizontal_curve: inlbim.util.geometry.HorizontalCurve,
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    elbow: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Get IFC4 File
    ifc4_file = material.file

    # Create Elbow
    if elbow is None:
        elbow = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeFitting",
            name=name,
            predefined_type="JUNCTION",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[elbow],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=elbow,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[elbow],
            system=distribution_system,
        )

    # Outer radius
    outer_radius = nominal_diameter / 2 + thickness / 2

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_revolved_area_solid(
        ifc4_file=ifc4_file,
        profile=inlbim.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[outer_radius, thickness],
        ),
        central_angle_of_curvature=horizontal_curve.central_angle,
        center_of_curvature_in_object_xy_plane=(
            horizontal_curve.radius_of_curvature,
            0.0,
        ),
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="SweptSolid",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=elbow,
        representation=shape_model,
    )

    # Calculate object z-axis
    object_z_axis_in_global_coordinates = (
        inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=horizontal_curve.point_of_curvature,
            p2=horizontal_curve.point_of_intersection,
        )
    )

    # Calculate object x-axis
    object_x_axis_in_global_coordinates = (
        inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=horizontal_curve.point_of_curvature,
            p2=horizontal_curve.center_of_curvature,
        )
    )

    # Get object origin
    object_origin_in_global_coordinates = horizontal_curve.point_of_curvature

    # Edit Placement
    inlbim.api.geometry.edit_object_placement(
        product=elbow,
        repositioned_origin=object_origin_in_global_coordinates,
        repositioned_z_axis=object_z_axis_in_global_coordinates,
        repositioned_x_axis=object_x_axis_in_global_coordinates,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Assign Material
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[elbow],
        material=material,
    )

    # Port 1
    port1_origin_in_object_coordinates = (0.0, 0.0, 0.0)
    port1_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=elbow)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "PIPE"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = elbow.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    radius_of_curvature = horizontal_curve.radius_of_curvature
    central_angle = horizontal_curve.central_angle
    port2_origin_in_object_coordinates = (
        float(radius_of_curvature - radius_of_curvature * np.cos(central_angle)),
        0.0,
        float(radius_of_curvature * np.sin(central_angle)),
    )
    port2_z_axis_in_object_coordinates = (
        float(np.sin(horizontal_curve.central_angle)),
        0.0,
        float(np.cos(horizontal_curve.central_angle)),
    )
    port2_x_axis_in_object_coordinates = (
        float(np.cos(horizontal_curve.central_angle)),
        0.0,
        float(-1 * np.sin(horizontal_curve.central_angle)),
    )
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=elbow)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "PIPE"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = elbow.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=nominal_diameter * 0.10,
        )

    return elbow


def add_shape_representation_to_distribution_ports(
    ports: list[ifcopenshell.entity_instance],
    arrow_size: float = 0.1,
):
    ifc4_file = ports[0].file

    sink_arrow = None
    source_arrow = None
    sphere = None

    for port in ports:
        if port.FlowDirection == "SINK":
            if sink_arrow is None:
                sink_arrow = inlbim.api.representation.add_csg_solid(
                    operands=[
                        inlbim.api.representation.add_rectangular_pyramid(
                            ifc4_file=ifc4_file,
                            length=arrow_size,
                            width=arrow_size,
                            height=arrow_size,
                            repositioned_origin=(-arrow_size / 2, -arrow_size / 2, 0.0),
                        )
                    ],
                    boolean_operators=[],
                )
            representation_item = sink_arrow
            color = (0.0, 0.0, 1.0)

        elif port.FlowDirection == "SOURCE":
            if source_arrow is None:
                source_arrow = inlbim.api.representation.add_csg_solid(
                    operands=[
                        inlbim.api.representation.add_rectangular_pyramid(
                            ifc4_file=ifc4_file,
                            length=arrow_size,
                            width=arrow_size,
                            height=arrow_size,
                            repositioned_origin=(
                                -arrow_size / 2,
                                -arrow_size / 2,
                                -arrow_size,
                            ),
                        )
                    ],
                    boolean_operators=[],
                )
            representation_item = source_arrow
            color = (1.0, 0.0, 0.0)

        else:
            if sphere is None:
                sphere = inlbim.api.representation.add_csg_solid(
                    operands=[
                        inlbim.api.representation.add_sphere(
                            ifc4_file=ifc4_file,
                            radius=arrow_size,
                        )
                    ],
                    boolean_operators=[],
                )
            representation_item = sphere
            color = None

        shape_model = inlbim.api.representation.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type="CSG",
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[representation_item],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=port,
            representation=shape_model,
        )
        if color:
            inlbim.api.style.assign_color_to_element(
                element=port,
                rgb_triplet=color,
                transparency=0.0,
            )


def create_pipe_segment(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
    pipe_segment: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Get IFC4 File
    ifc4_file = material.file

    # Create Element
    if pipe_segment is None:
        pipe_segment = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeSegment",
            name=name,
            predefined_type="NOTDEFINED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[pipe_segment],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=pipe_segment,
            place_object_relative_to_parent=True,
        )

    # Assign System
    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[pipe_segment],
        system=distribution_system,
    )

    # Calculate Axes
    object_z_axis_in_global_coordinates = np.array(p2) - np.array(p1)
    angle_between_local_and_global_z_axes = (
        inlbim.util.geometry.calculate_angle_between_two_vectors(
            vector1=tuple(object_z_axis_in_global_coordinates.tolist()),
            vector2=(0.0, 0.0, 1.0),
        )
    )
    angle_between_local_and_global_z_axes_is_zero = (
        angle_between_local_and_global_z_axes <= 1e-4
    )
    angle_between_local_and_global_z_axes_is_pi = (
        abs(angle_between_local_and_global_z_axes - np.pi) <= 1e-4
    )
    if (
        angle_between_local_and_global_z_axes_is_zero
        or angle_between_local_and_global_z_axes_is_pi
    ):
        object_y_axis_in_global_coordinates = np.array([0.0, 1.0, 0.0])
    else:
        object_y_axis_in_global_coordinates = np.cross(
            np.array([0.0, 0.0, 1.0]), object_z_axis_in_global_coordinates
        )
    object_x_axis_in_global_coordinates = np.cross(
        object_y_axis_in_global_coordinates, object_z_axis_in_global_coordinates
    )

    # Calculate length
    length = float(np.linalg.norm(object_z_axis_in_global_coordinates))

    # Outer radius
    outer_radius = nominal_diameter / 2 + thickness / 2

    # Add and assign representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=inlbim.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[outer_radius, thickness],
        ),
        extrusion_depth=length,
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="SweptSolid",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=pipe_segment,
        representation=shape_model,
    )

    # Get object origin
    object_origin_in_global_coordinates = p1

    # Edit Placement
    inlbim.api.geometry.edit_object_placement(
        product=pipe_segment,
        repositioned_origin=object_origin_in_global_coordinates,
        repositioned_z_axis=object_z_axis_in_global_coordinates,
        repositioned_x_axis=object_x_axis_in_global_coordinates,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Assign Material
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[pipe_segment],
        material=material,
    )

    # Port 1
    port1_origin_in_object_coordinates = (0.0, 0.0, 0.0)
    port1_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=pipe_segment)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "PIPE"
    port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = pipe_segment.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (0.0, 0.0, length)
    port2_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=pipe_segment)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "PIPE"
    port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = pipe_segment.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=nominal_diameter * 0.10,
        )

    return pipe_segment


def filter_out_colinear_points_from_polyline(
    polyline: list[tuple[float, float, float]],
) -> list[tuple[float, float, float]]:

    def remove_items_by_indices(lst: list, indices: list) -> list:
        # Convert indices to a set for faster lookup
        indices_set = set(indices)
        # Use list comprehension to create a new list without the specified indices
        return [item for idx, item in enumerate(lst) if idx not in indices_set]

    assert len(polyline) >= 3

    indices_of_points_to_remove = []

    for index in range(len(polyline)):

        if index == len(polyline) - 2:
            break

        p1 = polyline[index]
        p2 = polyline[index + 1]
        p3 = polyline[index + 2]

        v12 = inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=p1,
            p2=p2,
        )

        v23 = inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=p2,
            p2=p3,
        )

        angle = inlbim.util.geometry.calculate_angle_between_two_vectors(
            vector1=v12, vector2=v23
        )

        if angle == 0.0:
            indices_of_points_to_remove.append(index + 1)

        new_polyine = remove_items_by_indices(
            lst=polyline, indices=indices_of_points_to_remove
        )

    return new_polyine


def create_piping_system_with_polyline(
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

    ifc4_file = material.file

    assert len(polyline) >= 2

    if len(polyline) == 2:
        pipe_segment = inlbim.api.system.create_pipe_segment(
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
            last_pipe_segment = inlbim.api.system.create_pipe_segment(
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
            piping_elements += [last_pipe_segment]
            break

        horizontal_curve = inlbim.util.geometry.HorizontalCurve.from_3pt_polyline(
            p1=polyline[index],
            p2=polyline[index + 1],
            p3=polyline[index + 2],
            radius_of_curvature=radius_of_curvature,
        )

        pipe_segment_end_point = horizontal_curve.point_of_curvature

        # Create Element
        pipe_segment = inlbim.api.system.create_pipe_segment(
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

        # Create Element
        elbow = inlbim.api.system.create_elbow(
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


def connect_two_distribution_ports_via_piping(
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

    # Source Port Local Placement in Global Coordinates
    source_port_local_placement = ifcopenshell.util.placement.get_local_placement(
        placement=source_port.ObjectPlacement
    )
    source_port_origin = tuple(
        [float(row[3]) for row in source_port_local_placement[0:-1]]
    )
    source_port_z_axis = tuple(
        [float(row[2]) for row in source_port_local_placement[0:-1]]
    )

    # Sink Port Local Placement in Global Coordinates
    sink_port_local_placement = ifcopenshell.util.placement.get_local_placement(
        placement=sink_port.ObjectPlacement
    )
    print(sink_port_local_placement)
    sink_port_origin = tuple([float(row[3]) for row in sink_port_local_placement[0:-1]])
    sink_port_z_axis = tuple([float(row[2]) for row in sink_port_local_placement[0:-1]])

    # Check length of port location coordinates
    assert len(source_port_origin) == 3
    assert len(sink_port_origin) == 3

    # Calculate outer diameter of piping
    outer_diameter_of_piping = nominal_diameter + thickness

    # Second Point
    second_point = tuple(
        (
            np.array(source_port_origin)
            + np.array(source_port_z_axis) * 1.5 * outer_diameter_of_piping
        ).tolist()
    )

    # Penultimate Point
    penultimate_point = tuple(
        (
            np.array(sink_port_origin)
            + -1 * np.array(sink_port_z_axis) * 1.5 * outer_diameter_of_piping
        ).tolist()
    )

    # Delta_X and Delta_Y between Second Point and Penultimate Point
    delta_x, delta_y, _ = tuple(
        (np.array(penultimate_point) - np.array(second_point)).tolist()
    )

    # Third Point
    third_point = tuple(
        (np.array(second_point) + np.array([delta_x, 0.0, 0.0])).tolist()
    )

    # Fourth Point
    fourth_point = tuple(
        (np.array(third_point) + np.array([0.0, delta_y, 0.0])).tolist()
    )

    # Create Piping Elements
    piping_elements = inlbim.api.system.create_piping_system_with_polyline(
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

    # Connect original source and sink ports to the new piping system
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
