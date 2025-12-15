# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""HVAC Element Creation Module"""

import ifcopenshell
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.system
import bim2fem.ifcplus.api.system
import numpy as np
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.system
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import numpy as np
import bim2fem.ifcplus.api.system
import ifcopenshell.util.representation


def create_make_up_air_unit(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create make-up air unit as an IfcUnitaryEquipment."""

    ifc4_file = distribution_system.file

    make_up_air_unit = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcUnitaryEquipment",
        predefined_type="AIRHANDLER",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=make_up_air_unit,
    )

    length = 4.0 * scale_factor
    width = 1.5 * scale_factor
    height = 1.5 * scale_factor

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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=make_up_air_unit,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[make_up_air_unit],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            length,
            width / 2.0,
            height / 2,
        ),
        z_axis=(1.0, 0.0, 0.0),
        x_axis=(0.0, 1.0, 0.0),
        distribution_element=make_up_air_unit,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=make_up_air_unit,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return make_up_air_unit


def create_hepa_containment_housing(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create air filtration containment housing as an IfcFilter."""

    ifc4_file = distribution_system.file

    hepa_housing = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcUnitaryEquipment",
        predefined_type="HEPA_CONTAINMENT_HOUSING",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=hepa_housing,
    )

    length = 8.0 * scale_factor
    width = 1.0 * scale_factor
    height = 2.0 * scale_factor

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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=hepa_housing,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[hepa_housing],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            0.0,
            width / 2.0,
            height / 2.0,
        ),
        z_axis=(1.0, 0.0, 0.0),
        x_axis=(0.0, 1.0, 0.0),
        distribution_element=hepa_housing,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            length,
            width / 2.0,
            height / 2.0,
        ),
        z_axis=(1.0, 0.0, 0.0),
        x_axis=(0.0, 1.0, 0.0),
        distribution_element=hepa_housing,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=hepa_housing,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return hepa_housing


def create_motorized_valve(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create motorized valve as an IfcValve."""

    ifc4_file = distribution_system.file

    motorized_valve = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcValve",
        predefined_type="MOTORIZED_CONTROL_VALVE",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=motorized_valve,
    )

    outer_diameter = 0.5 * scale_factor
    thickness = 0.1 * scale_factor

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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=motorized_valve,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[motorized_valve],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            1.5 * outer_diameter,
            0.0,
            outer_diameter / 2.0,
        ),
        z_axis=(0.0, 1.0, 0.0),
        x_axis=(1.0, 0.0, 1.0),
        distribution_element=motorized_valve,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            1.5 * outer_diameter,
            2 / 5 * outer_diameter,
            outer_diameter / 2.0,
        ),
        z_axis=(0.0, 1.0, 0.0),
        x_axis=(1.0, 0.0, 1.0),
        distribution_element=motorized_valve,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=motorized_valve,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return motorized_valve


def create_generic_air_filter(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create generic air filter as an IfcFilter."""

    ifc4_file = distribution_system.file

    air_filter = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcFilter",
        predefined_type="AIRPARTICLEFILTER",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=air_filter,
    )

    length = 0.5 * scale_factor
    width = 0.1 * scale_factor
    height = 0.4 * scale_factor

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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=air_filter,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[air_filter],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            0.0 + length / 2.0,
            0.0,
            0.0 + height / 2.0,
        ),
        z_axis=(0.0, 1.0, 0.0),
        x_axis=(-1.0, 0.0, 0.0),
        distribution_element=air_filter,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            0.0 + length / 2,
            0.0 + width,
            0.0 + height / 2,
        ),
        z_axis=(0.0, 1.0, 0.0),
        x_axis=(-1.0, 0.0, 0.0),
        distribution_element=air_filter,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=air_filter,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return air_filter


def create_hprs_exhaust_fan(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create hprs exhaust fan as an IfcFan."""

    ifc4_file = distribution_system.file

    fan = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcFan",
        predefined_type="HPRS_EXHAUST_FAN",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=fan,
    )

    length = 2.0 * scale_factor
    width = 1.0 * scale_factor
    height = 1.0 * scale_factor

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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=fan,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[fan],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            0.0,
            width / 2.0,
            2.5 / 4 * height,
        ),
        z_axis=(1.0, 0.0, 0.0),
        x_axis=(0.0, 1.0, 0.0),
        distribution_element=fan,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            1 / 10 * length,
            width,
            3.5 / 4.0 * height,
        ),
        z_axis=(0.0, 1.0, 0.0),
        x_axis=(1.0, 0.0, 0.0),
        distribution_element=fan,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=fan,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return fan


def create_exhaust_stack(
    distribution_system: ifcopenshell.entity_instance,
    scale_factor: float = 1.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create exhaust stack as an IfcDistributionElement."""

    ifc4_file = distribution_system.file

    exhaust_stack = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcStackTerminal",
        predefined_type="EXHAUST_STACK",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=exhaust_stack,
    )

    base_diameter = 0.5 * scale_factor
    height = 8.0 * scale_factor

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

    sink_port_location = (
        base_diameter * 2.0,
        base_diameter / 2.0,
        1 / 5 * height,
    )
    hollow_cylinder_2 = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=1.5 * base_diameter,
            repositioned_origin=(
                base_diameter * 2.0,
                base_diameter / 2.0,
                1 / 5 * height,
            ),
            repositioned_z_axis=(-1.0, 0.0, 0.0),
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

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=exhaust_stack,
        representation=shape_representation,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[exhaust_stack],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=sink_port_location,
        z_axis=(-1.0, 0.0, 0.0),
        x_axis=(0.0, 1.0, 0.0),
        distribution_element=exhaust_stack,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(
            base_diameter / 2.0,
            base_diameter / 2.0,
            height,
        ),
        z_axis=(0.0, 0.0, 1.0),
        x_axis=(1.0, 0.0, 0.0),
        distribution_element=exhaust_stack,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=exhaust_stack,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return exhaust_stack
