# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import ifcopenshell.api.system
import bim2fem.ifcplus.api.system
import ifcopenshell.util.type
import bim2fem.ifcplus.api.element_type
import ifcopenshell.api.type
import numpy as np
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.system
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.profile
import ifcopenshell.api.geometry
import bim2fem.ifcplus.util.geometry
import ifcopenshell.api.material
import numpy as np
import bim2fem.ifcplus.api.system
import ifcopenshell.util.representation


def create_elbow(
    ifc4_file: ifcopenshell.file,
    horizontal_curve: bim2fem.ifcplus.util.geometry.HorizontalCurve,
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
    """Create piping elbow as an IfcPipeFitting."""

    if elbow is None:
        elbow = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeFitting",
            name=name,
            predefined_type="JUNCTION",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[elbow],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[elbow],
            system=distribution_system,
        )

    outer_radius = nominal_diameter / 2 + thickness / 2

    revolved_area_solid = bim2fem.ifcplus.api.geometry.add_revolved_area_solid(
        ifc4_file=ifc4_file,
        profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[outer_radius, thickness],
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        ),
        central_angle_of_curvature=horizontal_curve.central_angle,
        center_of_curvature_in_object_xy_plane=(
            horizontal_curve.radius_of_curvature,
            0.0,
        ),
    )

    representation_type = ifcopenshell.util.representation.guess_type(
        items=[revolved_area_solid]
    )

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[revolved_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=elbow,
        representation=shape_model,
    )

    object_z_axis_in_global_coordinates = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
        p1=horizontal_curve.point_of_curvature,
        p2=horizontal_curve.point_of_intersection,
    )

    object_x_axis_in_global_coordinates = bim2fem.ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
        p1=horizontal_curve.point_of_curvature,
        p2=horizontal_curve.center_of_curvature,
    )

    object_origin_in_global_coordinates = horizontal_curve.point_of_curvature

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=elbow,
        repositioned_origin=object_origin_in_global_coordinates,
        repositioned_z_axis=object_z_axis_in_global_coordinates,
        repositioned_x_axis=object_x_axis_in_global_coordinates,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[elbow],
        material=material,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(0.0, 0.0, 0.0),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=elbow,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    radius_of_curvature = horizontal_curve.radius_of_curvature
    central_angle = horizontal_curve.central_angle
    source_port_origin_in_object_coordinates = (
        float(radius_of_curvature - radius_of_curvature * np.cos(central_angle)),
        0.0,
        float(radius_of_curvature * np.sin(central_angle)),
    )
    source_port_z_axis_in_object_coordinates = (
        float(np.sin(horizontal_curve.central_angle)),
        0.0,
        float(np.cos(horizontal_curve.central_angle)),
    )
    source_port_x_axis_in_object_coordinates = (
        float(np.cos(horizontal_curve.central_angle)),
        0.0,
        float(-1 * np.sin(horizontal_curve.central_angle)),
    )
    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=source_port_origin_in_object_coordinates,
        port_z_axis_in_distribution_element_coordinates=source_port_z_axis_in_object_coordinates,
        port_x_axis_in_distribution_element_coordinates=source_port_x_axis_in_object_coordinates,
        distribution_element=elbow,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=nominal_diameter * 0.10,
        )

    return elbow


def create_pipe_segment(
    ifc4_file: ifcopenshell.file,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    pipe_segment: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create an IfcPipeSegment."""

    if pipe_segment is None:
        pipe_segment = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeSegment",
            name=name,
            predefined_type="NOTDEFINED",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[pipe_segment],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[pipe_segment],
            system=distribution_system,
        )

    object_z_axis_in_global_coordinates = np.array(end_point) - np.array(start_point)
    angle_between_local_and_global_z_axes = (
        bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
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
            np.array([0.0, 0.0, 1.0]),
            object_z_axis_in_global_coordinates,
        )
    object_x_axis_in_global_coordinates = np.cross(
        object_y_axis_in_global_coordinates,
        object_z_axis_in_global_coordinates,
    )

    object_z_axis_in_global_coordinates = (
        bim2fem.ifcplus.util.geometry.convert_3pt_ndarray_to_tuple_of_floats(
            numpy_3pt_array=object_z_axis_in_global_coordinates,
        )
    )

    object_x_axis_in_global_coordinates = (
        bim2fem.ifcplus.util.geometry.convert_3pt_ndarray_to_tuple_of_floats(
            numpy_3pt_array=object_x_axis_in_global_coordinates,
        )
    )

    length = float(np.linalg.norm(object_z_axis_in_global_coordinates))

    outer_radius = nominal_diameter / 2 + thickness / 2

    extruded_area_solid = bim2fem.ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[outer_radius, thickness],
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        ),
        extrusion_depth=length,
    )

    representation_type = ifcopenshell.util.representation.guess_type(
        items=[extruded_area_solid]
    )

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[extruded_area_solid],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=pipe_segment,
        representation=shape_model,
    )

    object_origin_in_global_coordinates = start_point

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=pipe_segment,
        repositioned_origin=object_origin_in_global_coordinates,
        repositioned_z_axis=object_z_axis_in_global_coordinates,
        repositioned_x_axis=object_x_axis_in_global_coordinates,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[pipe_segment],
        material=material,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(0.0, 0.0, 0.0),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(0.0, 0.0, length),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=nominal_diameter * 0.10,
        )

    return pipe_segment


def create_make_up_air_unit(
    ifc4_file: ifcopenshell.file,
    length: float = 4.0,
    width: float = 1.5,
    height: float = 1.5,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create make-up air unit as an IfcUnitaryEquipment."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcUnitaryEquipment",
            name=name,
            predefined_type="AIRHANDLER",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    block_1 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    block_2 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=height,
        width=width,
        height=2 * height,
        repositioned_origin=(0.0, 0.0, height),
        repositioned_z_axis=(1.0, 0.0, -1.0),
        repositioned_x_axis=(-1.0, 0.0, -1.0),
    )

    boolean_results = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=block_1,
        second_items=[block_2],
        operator="DIFFERENCE",
    )

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_results[-1],
    )

    representation_type = ifcopenshell.util.representation.guess_type(
        items=[csg_solid],
    )

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="MAKEUP_AIR_UNIT",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            length,
            width / 2.0,
            height / 2,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[source_port],
            arrow_size=0.10 * height,
        )

    return element


def create_air_filtration_containment_housing(
    ifc4_file: ifcopenshell.file,
    length: float = 8.0,
    width: float = 1.0,
    height: float = 2.0,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create air filtration containment housing as an IfcFilter."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    block_1 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length - 4 / 25 * length,
        width=width,
        height=height,
        repositioned_origin=(2 / 25 * length, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    rect_pyramid_1 = bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
        ifc4_file=ifc4_file,
        length=height,
        width=width,
        height=3 / 25 * length,
        repositioned_origin=(23 / 25 * length, 0.0, height),
        repositioned_z_axis=(1.0, 0.0, 0.0),
        repositioned_x_axis=(0.0, 0.0, -1.0),
    )

    rect_pyramid_2 = bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
        ifc4_file=ifc4_file,
        length=height,
        width=width,
        height=3 / 25 * length,
        repositioned_origin=(2 / 25 * length, 0.0, 0.0),
        repositioned_z_axis=(-1.0, 0.0, 0.0),
        repositioned_x_axis=(0.0, 0.0, 1.0),
    )

    block_2 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=2 / 25 * length,
        width=width,
        height=height,
        repositioned_origin=(-2 / 25 * length, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    block_3 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=2 / 25 * length,
        width=width,
        height=height,
        repositioned_origin=(length, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    boolean_result_1 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=block_1,
        second_items=[rect_pyramid_1, rect_pyramid_2],
        operator="UNION",
    )[-1]

    boolean_result_2 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=boolean_result_1,
        second_items=[block_2, block_3],
        operator="DIFFERENCE",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_result_2,
    )

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="AIR_FILTRATION_CONTAINMENT_HOUSING",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0,
            width / 2.0,
            height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=element,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            length,
            width / 2.0,
            height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=0.1 * height,
        )

    return element


def create_motorized_valve(
    ifc4_file: ifcopenshell.file,
    outer_diameter: float = 0.5,
    thickness: float = 0.1,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create motorized valve as an IfcValve."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcValve",
            name=name,
            predefined_type="MOTORIZED",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    block = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=2 * outer_diameter,
        width=2 / 5 * outer_diameter,
        height=2 / 5 * outer_diameter,
        repositioned_origin=(0.0, 0.0, outer_diameter),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    cylinder_1 = bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
        ifc4_file=ifc4_file,
        radius=outer_diameter / 2.0,
        extrusion_depth=2 / 5 * outer_diameter,
        repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
        repositioned_z_axis=(0.0, 1.0, 0.0),
        repositioned_x_axis=(1.0, 0.0, 1.0),
    )

    cylinder_2 = bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
        ifc4_file=ifc4_file,
        radius=outer_diameter / 2.0 - thickness,
        extrusion_depth=2 / 5 * outer_diameter,
        repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
        repositioned_z_axis=(0.0, 1.0, 0.0),
        repositioned_x_axis=(1.0, 0.0, 1.0),
    )

    boolean_result_1 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=block,
        second_items=[cylinder_1],
        operator="UNION",
    )[-1]

    boolean_result_2 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=boolean_result_1,
        second_items=[cylinder_2],
        operator="DIFFERENCE",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_result_2,
    )

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="MOTORIZED_VALVE",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1.5 * outer_diameter,
            0.0,
            outer_diameter / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 1.0),
        distribution_element=element,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1.5 * outer_diameter,
            2 / 5 * outer_diameter,
            outer_diameter / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 1.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=0.10 * outer_diameter,
        )

    return element


def create_generic_air_filter(
    ifc4_file: ifcopenshell.file,
    length: float = 0.5,
    width: float = 0.4,
    height: float = 0.1,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create generic air filter as an IfcFilter."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    thickness = 1 / 12 * length

    block_1 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    block_2 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length - thickness * 2,
        width=width,
        height=height - thickness * 2,
        repositioned_origin=(thickness, 0.0, thickness),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    block_3 = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length - thickness * 2,
        width=width / 4.0,
        height=height - thickness * 2,
        repositioned_origin=(thickness, width / 8.0, thickness),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    boolean_result_1 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=block_1,
        second_items=[block_2],
        operator="DIFFERENCE",
    )[-1]

    boolean_result_2 = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=boolean_result_1,
        second_items=[block_3],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_result_2,
    )

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="GENERIC_AIR_FILTER",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0 + length / 2.0,
            0.0,
            0.0 + height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(-1.0, 0.0, 0.0),
        distribution_element=element,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0 + length / 2,
            0.0 + width,
            0.0 + height / 2,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(-1.0, 0.0, 0.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=0.4 * thickness,
        )

    return element


def create_hprs_exhaust_fan(
    ifc4_file: ifcopenshell.file,
    length: float = 2.0,
    width: float = 1.0,
    height: float = 1.0,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create hprs exhaust fan as an IfcFan."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFan",
            name=name,
            predefined_type="CENTRIFUGALBACKWARDINCLINEDCURVED",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    block = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=5 / 5 * length,
        width=width,
        height=3 / 4 * height,
        repositioned_origin=(1 / 5 * length, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    cylinder = bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
        ifc4_file=ifc4_file,
        radius=width / 2.0,
        extrusion_depth=1 / 5 * length,
        repositioned_origin=(1 / 5 * length, width / 2.0, 2.5 / 4 * height),
        repositioned_z_axis=(-1.0, 0.0, 0.0),
        repositioned_x_axis=(0.0, 0.0, 1.0),
    )

    hollow_cylinder = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=1 / 10 * length * 0.9,
            wall_thickness=1 / 10 * 1 / 10 * length * 0.9,
            extrusion_depth=width / 2.0,
            repositioned_origin=(
                1 / 10 * length,
                width / 2.0,
                3.5 / 4 * height,
            ),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    boolean_result = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=block,
        second_items=[cylinder, hollow_cylinder],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_result,
    )

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="HPRS_EXHAUST_FAN",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0,
            width / 2.0,
            2.5 / 4 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=element,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1 / 10 * length,
            width,
            3.5 / 4.0 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=0.1 * height,
        )

    return element


def create_stack(
    ifc4_file: ifcopenshell.file,
    base_diameter: float = 0.5,
    height: float = 8.0,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:
    """Create exhaust stack as an IfcDistributionElement."""

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcDistributionElement",
            name=name,
            predefined_type="NOTDEFINED",
        )

    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    hollow_cylinder_1 = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=height,
            repositioned_origin=(base_diameter / 2.0, base_diameter / 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    hollow_cylinder_2 = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=1.5 * 2 / np.sqrt(2) * base_diameter,
            repositioned_origin=(
                base_diameter * 2.0,
                base_diameter / 2.0,
                1 / 5 * height,
            ),
            repositioned_z_axis=(-1.0, 0.0, 1.0),
            repositioned_x_axis=(0.0, 1.0, 0.0),
        )
    )

    boolean_result = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=hollow_cylinder_1,
        second_items=[hollow_cylinder_2],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=boolean_result,
    )

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    element_type = bim2fem.ifcplus.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="STACK",
        check_for_duplicate=True,
    )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    sink_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            base_diameter * 2.0,
            base_diameter / 2.0,
            1 / 5 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(-1.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=element,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    source_port = bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            base_diameter / 2.0,
            base_diameter / 2.0,
            height,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=element,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[sink_port, source_port],
            arrow_size=0.1 * base_diameter,
        )

    return element
