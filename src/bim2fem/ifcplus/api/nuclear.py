# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.util.representation
from typing import cast
import numpy as np
import ifcopenshell.api.system
import bim2fem.ifcplus.api.system
import ifcopenshell.api.pset_template
import bim2fem.ifcplus.api.profile


def create_nuclear_reactor_containment_structure(
    ifc4_file: ifcopenshell.file,
    material: ifcopenshell.entity_instance,
    slab_outer_radius: float = 25.0,
    slab_thickness: float = 3.0,
    cylinder_outer_radius: float = 23.0,
    cylinder_wall_thickness: float = 1.0,
    cylinder_height: float = 35.0,
    nuclear_reactor_containment_structure: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if nuclear_reactor_containment_structure is None:
        nuclear_reactor_containment_structure = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            predefined_type="USERDEFINED",
            ifc_class="IfcElementAssembly",
            name=name,
        )
        nuclear_reactor_containment_structure.ObjectType = (
            "NUCLEAR_REACTOR_CONTAINMENT_STRUCTURE"
        )

    base_slab = ifcopenshell.api.root.create_entity(
        file=ifc4_file, ifc_class="IfcSlab", predefined_type="BASESLAB", name="Basemat"
    )

    base_slab_representation_item = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=slab_outer_radius,
            extrusion_depth=slab_thickness,
            repositioned_origin=(0.0, 0.0, -slab_thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    base_slab_representation_shape_representation = (
        bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[base_slab_representation_item]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[base_slab_representation_item],
        )
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=base_slab,
        representation=base_slab_representation_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[base_slab],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=base_slab,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    hollow_cylindrical_wall = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
        predefined_type="SOLIDWALL",
        name="Cylindrical Wall",
    )

    hollow_cylindrical_wall_representation_item = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=cylinder_outer_radius,
            extrusion_depth=cylinder_height,
            wall_thickness=cylinder_wall_thickness,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    hollow_cylindrical_wall_shape_representation = (
        bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[hollow_cylindrical_wall_representation_item]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[hollow_cylindrical_wall_representation_item],
        )
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=hollow_cylindrical_wall,
        representation=hollow_cylindrical_wall_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[hollow_cylindrical_wall],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=hollow_cylindrical_wall,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    dome = ifcopenshell.api.root.create_entity(
        file=ifc4_file, ifc_class="IfcSlab", predefined_type="ROOF", name="Dome"
    )

    outer_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius,
    )

    inner_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius - cylinder_wall_thickness,
    )

    subtracting_cylinder = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=cylinder_outer_radius * 2.0,
            extrusion_depth=cylinder_height,
            repositioned_origin=(0.0, 0.0, -cylinder_height),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    hollow_sphere = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=outer_sphere,
        second_items=[inner_sphere, subtracting_cylinder],
        operator="DIFFERENCE",
    )[-1]

    dome_representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=hollow_sphere,
    )

    dome_shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(
                items=[dome_representation_item]
            ),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[dome_representation_item],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=dome,
        representation=dome_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[dome],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=dome,
        repositioned_origin=(0.0, 0.0, cylinder_height),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[hollow_cylindrical_wall, base_slab, dome],
        material=material,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[nuclear_reactor_containment_structure],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=nuclear_reactor_containment_structure,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return nuclear_reactor_containment_structure


def create_reactor_box(
    ifc4_file: ifcopenshell.file,
    length: float = 20.0,
    width: float = 20.0,
    height: float = 15.0,
    reactor_box: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if reactor_box is None:
        reactor_box = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcEnergyConversionDevice",
            name=name,
        )

    block = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
    )

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[block]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[block],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=reactor_box,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[reactor_box],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=reactor_box,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return reactor_box


def create_reactor_pressure_vessel(
    ifc4_file: ifcopenshell.file,
    scaling_factor_for_size: float = 1.0,
    reactor_pressure_vessel: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    reactor_coolant_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create reactor pressure vessel with default dimensions roughly corresponding to
    3500 MWth thermal capacity."""

    if reactor_pressure_vessel is None:
        reactor_pressure_vessel = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcTank",
            name=name,
            predefined_type="USERDEFINED",
        )
        reactor_pressure_vessel.ObjectType = "REACTOR_PRESSURE_VESSEL"

    rpv_outlet_nozzle_diameter = 1.07 * scaling_factor_for_size
    rpv_inlet_nozzle_diameter = 0.76 * scaling_factor_for_size
    body_diameter = 5.0 * scaling_factor_for_size
    overall_height = 12.5 * scaling_factor_for_size

    cylindrical_body_height = overall_height - body_diameter / 2.0 - body_diameter / 2.0
    inlet_port_protrusion_length = 0.5

    point_at_center_of_bottom_sphere = (
        inlet_port_protrusion_length + body_diameter / 2.0,
        body_diameter / 2.0,
        body_diameter / 2.0,
    )

    point_at_center_of_top_sphere = tuple(
        (
            np.array(point_at_center_of_bottom_sphere)
            + np.array([0.0, 0.0, cylindrical_body_height])
        ).tolist()
    )

    bottom_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        repositioned_origin=point_at_center_of_bottom_sphere,
        radius=body_diameter / 2.0,
    )

    top_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        repositioned_origin=point_at_center_of_top_sphere,
        radius=body_diameter / 2.0,
    )

    both_spheres_combined = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=bottom_sphere,
        second_items=[top_sphere],
        operator="UNION",
    )[-1]

    cylinder_for_subtraction = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=body_diameter / 2.0,
            extrusion_depth=cylindrical_body_height,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    top_and_bottom_hemispheres = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=both_spheres_combined,
        second_items=[cylinder_for_subtraction],
        operator="DIFFERENCE",
    )[-1]

    cylinder_for_body = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=body_diameter / 2.0,
            extrusion_depth=cylindrical_body_height,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    rpv_body_and_ends = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=top_and_bottom_hemispheres,
        second_items=[cylinder_for_body],
        operator="UNION",
    )[-1]

    inlet_elevation = 9 / 12.5 * overall_height

    inlet_port_origin = tuple(
        (
            np.array(point_at_center_of_bottom_sphere)
            - np.array([1.0, 0.0, 0.0])
            * (body_diameter / 2.0 + inlet_port_protrusion_length)
            + np.array([0.0, 0.0, 1.0]) * (inlet_elevation - body_diameter / 2.0)
        ).tolist()
    )

    inlet_port_z_axis = (1.0, 0.0, 0.0)

    inlet_port_x_axis = (0.0, 1.0, 0.0)

    cylinder_for_inlet_port = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=rpv_inlet_nozzle_diameter / 2.0,
            extrusion_depth=inlet_port_protrusion_length + body_diameter / 4.0,
            repositioned_origin=inlet_port_origin,
            repositioned_z_axis=inlet_port_z_axis,
            repositioned_x_axis=inlet_port_x_axis,
        )
    )

    outlet_elevation = 9 / 12.5 * overall_height

    outlet_port_origin = tuple(
        (
            np.array(point_at_center_of_bottom_sphere)
            + np.array([1.0, 0.0, 0.0])
            * (body_diameter / 2.0 + inlet_port_protrusion_length)
            + np.array([0.0, 0.0, 1.0]) * (outlet_elevation - body_diameter / 2.0)
        ).tolist()
    )

    outlet_port_z_axis = (1.0, 0.0, 0.0)

    outlet_port_x_axis = (0.0, 1.0, 0.0)

    cylinder_for_outlet_port = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=rpv_outlet_nozzle_diameter / 2.0,
            extrusion_depth=inlet_port_protrusion_length + body_diameter / 4.0,
            repositioned_origin=outlet_port_origin,
            repositioned_z_axis=tuple((np.array(outlet_port_z_axis) * -1).tolist()),
            repositioned_x_axis=tuple((np.array(outlet_port_x_axis) * -1).tolist()),
        )
    )

    rpv_body_and_ends_and_ports = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=rpv_body_and_ends,
        second_items=[
            cylinder_for_inlet_port,
            cylinder_for_outlet_port,
        ],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=rpv_body_and_ends_and_ports,
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
        product=reactor_pressure_vessel,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[reactor_pressure_vessel],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=reactor_pressure_vessel,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(reactor_coolant_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[reactor_pressure_vessel],
            system=reactor_coolant_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=inlet_port_origin,
        port_z_axis_in_distribution_element_coordinates=inlet_port_z_axis,
        port_x_axis_in_distribution_element_coordinates=inlet_port_x_axis,
        distribution_element=reactor_pressure_vessel,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
        name="RPV Inlet",
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=outlet_port_origin,
        port_z_axis_in_distribution_element_coordinates=outlet_port_z_axis,
        port_x_axis_in_distribution_element_coordinates=outlet_port_x_axis,
        distribution_element=reactor_pressure_vessel,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
        name="RPV Outlet",
    )

    return reactor_pressure_vessel


def create_INL_nuclear_property_set_templte(
    ifc4_file: ifcopenshell.file,
) -> ifcopenshell.entity_instance:

    inl_pset_template = ifcopenshell.api.pset_template.add_pset_template(
        file=ifc4_file,
        name="INL_pset_template",
    )
    ifcopenshell.api.pset_template.add_prop_template(
        file=ifc4_file,
        pset_template=inl_pset_template,
        name="ThermalPowerCapacity",
        primary_measure_type="IfcPowerMeasure",
    )
    ifcopenshell.api.pset_template.add_prop_template(
        file=ifc4_file,
        pset_template=inl_pset_template,
        name="DesignPressure",
        primary_measure_type="IfcPressureMeasure",
    )
    ifcopenshell.api.pset_template.add_prop_template(
        file=ifc4_file,
        pset_template=inl_pset_template,
        name="DesignTemperature",
        primary_measure_type="IfcThermodynamicTemperatureMeasure",
    )
    ifcopenshell.api.pset_template.add_prop_template(
        file=ifc4_file,
        pset_template=inl_pset_template,
        name="ReactorType",
        primary_measure_type="IfcLabel",
    )

    return inl_pset_template


def create_steam_generator(
    ifc4_file: ifcopenshell.file,
    scaling_factor_for_size: float = 1.0,
    steam_generator: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    reactor_coolant_system: ifcopenshell.entity_instance | None = None,
    secondary_coolant_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create reactor pressure vessel with default dimensions roughly corresponding to
    3500 MWth thermal capacity."""

    if steam_generator is None:
        steam_generator = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcHeatExchanger",
            name=name,
            predefined_type="USERDEFINED",
        )
        steam_generator.ObjectType = "STEAM_GENERATOR"

    diameter_of_primary_inlet_nozzle = 1.07 * scaling_factor_for_size
    diameter_primary_outlet_nozzle = 0.76 * scaling_factor_for_size

    diameter_of_steam_outlet = 0.6 * scaling_factor_for_size
    diameter_of_feedwater_inlet = 0.4 * scaling_factor_for_size

    diameter_of_lower_section = 2.0 * scaling_factor_for_size
    diameter_of_upper_section = 3.5 * scaling_factor_for_size

    height_of_lower_section = 4.0 * scaling_factor_for_size
    height_of_transition_section = 3.0 * scaling_factor_for_size
    height_of_upper_section = 14.0 * scaling_factor_for_size

    radius_of_lower_section = diameter_of_lower_section / 2.0
    radius_of_upper_section = diameter_of_upper_section / 2.0

    protrusion_length_of_primary_inlet_nozzle = 0.5

    location_of_bottom_of_sg = (
        max(
            [
                radius_of_upper_section,
                radius_of_lower_section + protrusion_length_of_primary_inlet_nozzle,
            ]
        ),
        0.0 + radius_of_upper_section,
        0.0,
    )

    location_of_center_of_bottom_sphere = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * radius_of_lower_section
        ).tolist()
    )
    sphere_of_bottom = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_lower_section,
        repositioned_origin=location_of_center_of_bottom_sphere,
    )

    cylinder_for_lower_section_for_subtracting = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_lower_section,
            extrusion_depth=height_of_lower_section - radius_of_lower_section,
            repositioned_origin=location_of_center_of_bottom_sphere,
        )
    )

    hemisphere_of_bottom = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_bottom,
        second_items=[cylinder_for_lower_section_for_subtracting],
        operator="DIFFERENCE",
    )[-1]

    cylinder_for_lower_section_for_adding = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_lower_section,
            extrusion_depth=height_of_lower_section - radius_of_lower_section,
            repositioned_origin=location_of_center_of_bottom_sphere,
        )
    )

    origin_of_primary_inlet_nozzle = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * 1 / 2 * height_of_lower_section
            - np.array([1.0, 0.0, 0.0])
            * (radius_of_lower_section + protrusion_length_of_primary_inlet_nozzle)
        ).tolist()
    )
    radius_of_primary_inlet_nozzle = diameter_of_primary_inlet_nozzle / 2.0
    z_axis_of_primary_inlet_nozzle = (1.0, 0.0, 0.0)
    x_axis_of_primary_inlet_nozzle = (0.0, 1.0, 0.0)
    cylinder_for_primary_inlet_nozzle = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_primary_inlet_nozzle,
            extrusion_depth=protrusion_length_of_primary_inlet_nozzle
            + 1 / 4 * radius_of_lower_section,
            repositioned_origin=origin_of_primary_inlet_nozzle,
            repositioned_z_axis=z_axis_of_primary_inlet_nozzle,
            repositioned_x_axis=x_axis_of_primary_inlet_nozzle,
        )
    )

    protrusion_length_of_primary_outlet_nozzle = 0.5
    origin_of_primary_outlet_nozzle = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * 1 / 2 * height_of_lower_section
            + np.array([1.0, 0.0, 0.0])
            * (radius_of_lower_section + protrusion_length_of_primary_outlet_nozzle)
        ).tolist()
    )
    radius_of_primary_outlet_nozzle = diameter_primary_outlet_nozzle / 2.0
    z_axis_of_primary_outlet_nozzle = (1.0, 0.0, 0.0)
    x_axis_of_primary_outlet_nozzle = (0.0, 1.0, 0.0)
    neg_z_axis_of_primary_outlet_nozzle = tuple(
        (np.array(z_axis_of_primary_outlet_nozzle) * -1).tolist()
    )
    neg_x_axis_of_primary_outlet_nozzle = tuple(
        (np.array(x_axis_of_primary_outlet_nozzle) * -1).tolist()
    )
    cylinder_for_primary_outlet_nozzle = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_primary_outlet_nozzle,
            extrusion_depth=protrusion_length_of_primary_outlet_nozzle
            + 1 / 4 * radius_of_lower_section,
            repositioned_origin=origin_of_primary_outlet_nozzle,
            repositioned_z_axis=neg_z_axis_of_primary_outlet_nozzle,
            repositioned_x_axis=neg_x_axis_of_primary_outlet_nozzle,
        )
    )

    location_of_bottom_of_transition_section = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * height_of_lower_section
        ).tolist()
    )
    cylinder_tapered_for_transition_section = (
        bim2fem.ifcplus.api.geometry.add_extruded_area_solid_tapered(
            ifc4_file=ifc4_file,
            swept_area=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcCircleProfileDef",
                dimensions=[radius_of_lower_section],
            ),
            end_swept_area=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcCircleProfileDef",
                dimensions=[radius_of_upper_section],
            ),
            depth=height_of_transition_section,
            repositioned_origin=location_of_bottom_of_transition_section,
        )
    )

    location_of_center_of_top_sphere = tuple(
        (
            np.array(location_of_bottom_of_transition_section)
            + np.array([0.0, 0.0, 1.0])
            * (
                height_of_transition_section
                + height_of_upper_section
                - radius_of_upper_section
            )
        ).tolist()
    )
    sphere_of_top = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_upper_section,
        repositioned_origin=location_of_center_of_top_sphere,
    )

    location_of_bottom_of_upper_section = tuple(
        (
            np.array(location_of_bottom_of_transition_section)
            + np.array([0.0, 0.0, 1.0])
            * (height_of_transition_section - height_of_transition_section)
        ).tolist()
    )
    cylinder_for_upper_section_for_subtracting = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_upper_section,
            extrusion_depth=height_of_upper_section - radius_of_upper_section,
            repositioned_origin=location_of_bottom_of_upper_section,
        )
    )

    hemisphere_for_top = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_top,
        second_items=[cylinder_for_upper_section_for_subtracting],
        operator="DIFFERENCE",
    )[-1]

    cylinder_for_upper_section_for_adding = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_upper_section,
            extrusion_depth=height_of_upper_section - radius_of_upper_section,
            repositioned_origin=location_of_bottom_of_upper_section,
        )
    )

    protrusion_length_of_steam_outlet = 0.5
    location_of_top_of_upper_section = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0])
            * (
                height_of_lower_section
                + height_of_transition_section
                + height_of_upper_section
            )
        ).tolist()
    )
    origin_of_steam_outlet = tuple(
        (
            np.array(location_of_top_of_upper_section)
            + np.array([0.0, 0.0, 1.0]) * protrusion_length_of_steam_outlet
        ).tolist()
    )
    radius_of_steam_outlet = diameter_of_steam_outlet / 2.0
    z_axis_of_steam_outlet = (0.0, 0.0, 1.0)
    x_axis_of_steam_outlet = (1.0, 0.0, 0.0)
    length_of_cylinder_for_steam_outlet = (
        radius_of_upper_section * 1 / 2 + protrusion_length_of_steam_outlet
    )
    origin_of_cylinder_for_steam_outlet = tuple(
        (
            np.array(origin_of_steam_outlet)
            - np.array([0.0, 0.0, 1.0]) * length_of_cylinder_for_steam_outlet
        ).tolist()
    )
    cylinder_for_steam_outlet = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_steam_outlet,
            extrusion_depth=length_of_cylinder_for_steam_outlet,
            repositioned_origin=origin_of_cylinder_for_steam_outlet,
            repositioned_z_axis=z_axis_of_steam_outlet,
            repositioned_x_axis=x_axis_of_steam_outlet,
        )
    )

    protrusion_length_of_feedwater_inlet = 0.3
    total_height_of_main_body = (
        height_of_lower_section + height_of_transition_section + height_of_upper_section
    )
    height_of_feedwater_inlet = 10 / 21 * total_height_of_main_body
    origin_of_feedwater_inlet = tuple(
        (
            np.array(location_of_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * height_of_feedwater_inlet
            + np.array([1.0, 0.0, 0.0])
            * (radius_of_upper_section + protrusion_length_of_feedwater_inlet)
        ).tolist()
    )
    radius_of_feedwater_inlet = diameter_of_feedwater_inlet / 2.0
    z_axis_of_feedwater_inlet = (-1.0, 0.0, 0.0)
    x_axis_of_feedwater_inlet = (0.0, -1.0, 0.0)
    length_of_cylinder_for_feedwater_inlet = (
        radius_of_upper_section * 1 / 2 + protrusion_length_of_feedwater_inlet
    )
    origin_of_cylinder_for_feedwater_inlet = origin_of_feedwater_inlet
    cylinder_for_feedwater_inlet = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_feedwater_inlet,
            extrusion_depth=length_of_cylinder_for_feedwater_inlet,
            repositioned_origin=origin_of_cylinder_for_feedwater_inlet,
            repositioned_z_axis=z_axis_of_feedwater_inlet,
            repositioned_x_axis=x_axis_of_feedwater_inlet,
        )
    )

    complete_steam_generator_body = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=hemisphere_of_bottom,
        second_items=[
            cylinder_for_lower_section_for_adding,
            cylinder_tapered_for_transition_section,
            cylinder_for_upper_section_for_adding,
            hemisphere_for_top,
            cylinder_for_primary_inlet_nozzle,
            cylinder_for_primary_outlet_nozzle,
            cylinder_for_steam_outlet,
            cylinder_for_feedwater_inlet,
        ],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=complete_steam_generator_body,
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
        product=steam_generator,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[steam_generator],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=steam_generator,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(reactor_coolant_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[steam_generator],
            system=reactor_coolant_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_primary_inlet_nozzle,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_primary_inlet_nozzle,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_primary_inlet_nozzle,
        distribution_element=steam_generator,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
        name="SG Primary Inlet Nozzle",
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_primary_outlet_nozzle,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_primary_outlet_nozzle,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_primary_outlet_nozzle,
        distribution_element=steam_generator,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
        name="SG Primary Outlet Nozzle",
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_steam_outlet,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_steam_outlet,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_steam_outlet,
        distribution_element=steam_generator,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=secondary_coolant_system,
        name="SG Steam Outlet",
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_feedwater_inlet,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_feedwater_inlet,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_feedwater_inlet,
        distribution_element=steam_generator,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=secondary_coolant_system,
        name="SG Feedwater Inlet",
    )

    return steam_generator
