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
import bim2fem.ifcplus.util
import bim2fem.ifcplus.util.geometry


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
    parent: ifcopenshell.entity_instance | None = None,
    reactor_coolant_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create reactor pressure vessel with default dimensions roughly corresponding to
    3500 MWth thermal capacity.
    """

    if reactor_pressure_vessel is None:
        reactor_pressure_vessel = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcTank",
            predefined_type="USERDEFINED",
        )
        reactor_pressure_vessel.ObjectType = "REACTOR_PRESSURE_VESSEL"

    diameter_of_cold_leg_inlet = 0.55 * scaling_factor_for_size
    length_of_cold_leg_inlet = 0.5 * scaling_factor_for_size

    diameter_of_hot_leg_outlet = 0.74 * scaling_factor_for_size
    length_of_hot_leg_outlet = 0.5 * scaling_factor_for_size

    diameter_of_body = 5.0 * scaling_factor_for_size
    height_overall = 12.5 * scaling_factor_for_size

    radius_of_body = diameter_of_body / 2.0
    height_of_cylinder = height_overall - 2.0 * radius_of_body

    point_at_center_of_bottom_sphere = (
        length_of_cold_leg_inlet + radius_of_body,
        length_of_cold_leg_inlet + radius_of_body,
        radius_of_body,
    )

    point_at_center_of_top_sphere = tuple(
        (
            np.array(point_at_center_of_bottom_sphere)
            + np.array([0.0, 0.0, 1.0]) * height_of_cylinder
        ).tolist()
    )

    sphere_of_bottom = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        repositioned_origin=point_at_center_of_bottom_sphere,
        radius=radius_of_body,
    )

    cylinder_for_subtraction_of_bottom_sphere = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_body,
            extrusion_depth=height_of_cylinder,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    hemisphere_of_bottom = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_bottom,
        second_items=[cylinder_for_subtraction_of_bottom_sphere],
        operator="DIFFERENCE",
    )[-1]

    sphere_of_top = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        repositioned_origin=point_at_center_of_top_sphere,
        radius=radius_of_body,
    )

    cylinder_for_subtraction_of_top_sphere = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_body,
            extrusion_depth=height_of_cylinder,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    hemisphere_of_top = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_top,
        second_items=[cylinder_for_subtraction_of_top_sphere],
        operator="DIFFERENCE",
    )[-1]

    cylinder_for_body = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_body,
            extrusion_depth=height_of_cylinder,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    z_axes_for_cold_leg_inlets = [
        (-1.0, 0.0, 0.0),
        (1.0, -1.0, 0.0),
        (1.0, 0.0, 0.0),
        (-1.0, 1.0, 0.0),
    ]

    names_for_cold_leg_inlets = [
        "CL-A",
        "CL-B",
        "CL-C",
        "CL-D",
    ]

    z_axes_for_hot_leg_outlets = [
        (1.0, 1.0, 0.0),
        (0.0, 1.0, 0.0),
        (-1.0, -1.0, 0.0),
        (0.0, -1.0, 0.0),
    ]

    names_for_hot_leg_inlets = [
        "HL-A",
        "HL-B",
        "HL-C",
        "HL-D",
    ]

    solid_bodies_of_ports = []
    z_axis_global = (0.0, 0.0, 1.0)
    elevation_of_ports = 9 / 12.5 * height_overall
    distance_from_center_of_bottom_sphere_to_port_elevation = (
        elevation_of_ports - radius_of_body
    )
    for (
        z_axis_for_cold_leg_inlet,
        z_axis_for_hot_leg_outlet,
        name_for_cold_leg_inlet,
        name_for_hot_leg_inlet,
    ) in zip(
        z_axes_for_cold_leg_inlets,
        z_axes_for_hot_leg_outlets,
        names_for_cold_leg_inlets,
        names_for_hot_leg_inlets,
    ):
        z_axis_for_cold_leg_inlet = bim2fem.ifcplus.util.geometry.unit_normalize_vector(
            vector=z_axis_for_cold_leg_inlet,
        )
        z_axis_for_hot_leg_outlet = bim2fem.ifcplus.util.geometry.unit_normalize_vector(
            vector=z_axis_for_hot_leg_outlet,
        )

        x_axis_for_cold_leg_inlet = (
            bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=z_axis_global,
                vector2=z_axis_for_cold_leg_inlet,
                unit_normalize=False,
            )
        )
        origin_of_cold_leg_inlet = tuple(
            (
                np.array(point_at_center_of_bottom_sphere)
                + np.array([0.0, 0.0, 1.0])
                * distance_from_center_of_bottom_sphere_to_port_elevation
                + -1
                * np.array(z_axis_for_cold_leg_inlet)
                * (radius_of_body + length_of_cold_leg_inlet)
            ).tolist()
        )
        cylinder_for_inlet_port = (
            bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
                ifc4_file=ifc4_file,
                radius=diameter_of_cold_leg_inlet / 2.0,
                extrusion_depth=length_of_cold_leg_inlet + radius_of_body / 2.0,
                repositioned_origin=origin_of_cold_leg_inlet,
                repositioned_z_axis=z_axis_for_cold_leg_inlet,
                repositioned_x_axis=x_axis_for_cold_leg_inlet,
            )
        )
        solid_bodies_of_ports.append(cylinder_for_inlet_port)
        cl_port = bim2fem.ifcplus.api.system.create_distribution_port(
            ifc4_file=ifc4_file,
            port_origin_in_distribution_element_coordinates=origin_of_cold_leg_inlet,
            port_z_axis_in_distribution_element_coordinates=z_axis_for_cold_leg_inlet,
            port_x_axis_in_distribution_element_coordinates=x_axis_for_cold_leg_inlet,
            distribution_element=reactor_pressure_vessel,
            flow_direction="SINK",
            predefined_type="PIPE",
            distribution_system=reactor_coolant_system,
        )
        cl_port.Name = name_for_cold_leg_inlet

        x_axis_for_hot_leg_outlet = (
            bim2fem.ifcplus.util.geometry.calculate_cross_product_of_two_vectors(
                vector1=z_axis_global,
                vector2=z_axis_for_hot_leg_outlet,
                unit_normalize=False,
            )
        )
        origin_of_hot_leg_outlet = tuple(
            (
                np.array(point_at_center_of_bottom_sphere)
                + np.array([0.0, 0.0, 1.0])
                * distance_from_center_of_bottom_sphere_to_port_elevation
                + np.array(z_axis_for_hot_leg_outlet)
                * (radius_of_body + length_of_hot_leg_outlet)
            ).tolist()
        )
        neg_z_axis_for_hot_leg_outlet = tuple(
            (np.array(z_axis_for_hot_leg_outlet) * -1).tolist()
        )
        neg_x_axis_for_hot_leg_outlet = tuple(
            (np.array(x_axis_for_hot_leg_outlet) * -1).tolist()
        )
        cylinder_for_outlet_port = (
            bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
                ifc4_file=ifc4_file,
                radius=diameter_of_hot_leg_outlet / 2.0,
                extrusion_depth=length_of_hot_leg_outlet + radius_of_body / 2.0,
                repositioned_origin=origin_of_hot_leg_outlet,
                repositioned_z_axis=neg_z_axis_for_hot_leg_outlet,
                repositioned_x_axis=neg_x_axis_for_hot_leg_outlet,
            )
        )
        solid_bodies_of_ports.append(cylinder_for_outlet_port)
        hl_port = bim2fem.ifcplus.api.system.create_distribution_port(
            ifc4_file=ifc4_file,
            port_origin_in_distribution_element_coordinates=origin_of_hot_leg_outlet,
            port_z_axis_in_distribution_element_coordinates=z_axis_for_hot_leg_outlet,
            port_x_axis_in_distribution_element_coordinates=x_axis_for_hot_leg_outlet,
            distribution_element=reactor_pressure_vessel,
            flow_direction="SOURCE",
            predefined_type="PIPE",
            distribution_system=reactor_coolant_system,
        )
        hl_port.Name = name_for_hot_leg_inlet

    complete_rpv = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=hemisphere_of_bottom,
        second_items=[cylinder_for_body, hemisphere_of_top] + solid_bodies_of_ports,
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=complete_rpv,
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
    ifcopenshell.api.pset_template.add_prop_template(
        file=ifc4_file,
        pset_template=inl_pset_template,
        name="FlowRate",
        primary_measure_type="IfcVolumetricFlowRateMeasure",
    )

    return inl_pset_template


def create_steam_generator(
    ifc4_file: ifcopenshell.file,
    scaling_factor_for_size: float = 1.0,
    steam_generator: ifcopenshell.entity_instance | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    reactor_coolant_system: ifcopenshell.entity_instance | None = None,
    secondary_coolant_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create steam generator vessel with default dimensions roughly corresponding to
        3500 MWth thermal capacity.

    # Reactor Pressure Vessel naming

    rpv1.Name = "RPV-1"
    rpv1_hot_leg_1a.Name = "HL-1A"
    rpv1_cold_leg_1a.Name = "CL-1A"
    rpv1_hot_leg_1b.Name = "HL-1B"
    rpv1_cold_leg_1b.Name = "CL-1B"
    rpv1_hot_leg_1c.Name = "HL-1C"
    rpv1_cold_leg_1c.Name = "CL-1C"
    rpv1_hot_leg_1d.Name = "HL-1D"
    rpv1_cold_leg_1d.Name = "CL-1D"

    # Steam Generator naming

    sg1a.Name = "SG-1A"
    sg1a_primary_coolant_in.Name = "SG-1A-PC-IN"
    sg1a_primary_coolant_out.Name = "SG-1A-PC-OUT"
    sg1a_feedwater.Name = "SG-1A-FW"
    sg1a_main_steam.Name = "SG-1A-MS"

    sg1b.Name = "SG-1B"
    sg1b_primary_coolant_in.Name = "SG-1B-PC-IN"
    sg1b_primary_coolant_out.Name = "SG-1B-PC-OUT"
    sg1b_feedwater.Name = "SG-1B-FW"
    sg1b_main_steam.Name = "SG-1B-MS"

    sg1c.Name = "SG-1C"
    sg1c_primary_coolant_in.Name = "SG-1C-PC-IN"
    sg1c_primary_coolant_out.Name = "SG-1C-PC-OUT"
    sg1c_feedwater.Name = "SG-1C-FW"
    sg1c_main_steam.Name = "SG-1C-MS"

    sg1d.Name = "SG-1D"
    sg1d_primary_coolant_in.Name = "SG-1D-PC-IN"
    sg1d_primary_coolant_out.Name = "SG-1D-PC-OUT"
    sg1d_feedwater.Name = "SG-1D-FW"
    sg1d_main_steam.Name = "SG-1D-MS"

    # Reactor Coolant Pump naming

    rcp1a.Name = "RCP-1A"
    rcp1a_inlet.Name = "RCP-1A-IN"
    rcp1a_outlet.Name = "RCP-1A-OUT"

    rcp1b.Name = "RCP-1B"
    rcp1b_inlet.Name = "RCP-1B-IN"
    rcp1b_outlet.Name = "RCP-1B-OUT"

    rcp1c.Name = "RCP-1C"
    rcp1c_inlet.Name = "RCP-1C-IN"
    rcp1c_outlet.Name = "RCP-1C-OUT"

    rcp1d.Name = "RCP-1D"
    rcp1d_inlet.Name = "RCP-1D-IN"
    rcp1d_outlet.Name = "RCP-1D-OUT"

    # Loops

    Loop A: HL-1A → SG-1A-PC-IN → SG-1A-PC-OUT → RCP-1A-IN → RCP-1A-OUT → CL-1A
    Loop B: HL-1B → SG-1B-PC-IN → SG-1B-PC-OUT → RCP-1B-IN → RCP-1B-OUT → CL-1B
    Loop C: HL-1C → SG-1C-PC-IN → SG-1C-PC-OUT → RCP-1C-IN → RCP-1C-OUT → CL-1C
    Loop D: HL-1D → SG-1D-PC-IN → SG-1D-PC-OUT → RCP-1D-IN → RCP-1D-OUT → CL-1D

    # Notes

    All equipment follows: [Component]-[Unit][Loop] pattern
    All ports follow consistent abbreviations (HL, CL, PC, FW, MS)
    Variable naming is systematic (rpv1_hot_leg_1a matches HL-1A)
    Abbreviations should match real plant P&IDs:
        HL = Hot Leg
        CL = Cold Leg
        PC = Primary Coolant
        FW = Feedwater
        MS = Main Steam
    """

    if steam_generator is None:
        steam_generator = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcHeatExchanger",
            predefined_type="USERDEFINED",
        )
        steam_generator.ObjectType = "STEAM_GENERATOR"

    diameter_of_primary_inlet_nozzle = 0.74 * scaling_factor_for_size
    diameter_primary_outlet_nozzle = 0.55 * scaling_factor_for_size

    diameter_of_steam_outlet = 0.6 * scaling_factor_for_size
    diameter_of_feedwater_inlet = 0.4 * scaling_factor_for_size

    diameter_of_lower_section = 3.65 * scaling_factor_for_size
    diameter_of_upper_section = 4.78 * scaling_factor_for_size

    height_of_lower_section = 11.8 * scaling_factor_for_size
    height_of_transition_section = 1.4 * scaling_factor_for_size
    height_of_upper_section = 7.8 * scaling_factor_for_size

    radius_of_lower_section = diameter_of_lower_section / 2.0
    radius_of_upper_section = diameter_of_upper_section / 2.0

    length_of_protrusion_of_primary_inlet_nozzle = 0.5
    length_of_protrusion_of_primary_outlet_nozzle = 0.5
    length_of_protrusion_of_steam_outlet = 0.5
    length_of_protrusion_of_feedwater_inlet = 0.3

    height_overall = (
        height_of_lower_section + height_of_transition_section + height_of_upper_section
    )

    point_at_bottom_of_sg = (
        max(
            [
                radius_of_upper_section,
                radius_of_lower_section + length_of_protrusion_of_primary_inlet_nozzle,
            ]
        ),
        0.0 + radius_of_upper_section + length_of_protrusion_of_feedwater_inlet,
        0.0,
    )
    point_at_center_of_bottom_sphere = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * radius_of_lower_section
        ).tolist()
    )
    point_at_bottom_of_transition_section = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * height_of_lower_section
        ).tolist()
    )
    point_at_center_of_top_sphere = tuple(
        (
            np.array(point_at_bottom_of_transition_section)
            + np.array([0.0, 0.0, 1.0])
            * (
                height_of_transition_section
                + height_of_upper_section
                - radius_of_upper_section
            )
        ).tolist()
    )
    point_at_bottom_of_upper_section = tuple(
        (
            np.array(point_at_bottom_of_transition_section)
            + np.array([0.0, 0.0, 1.0]) * height_of_transition_section
        ).tolist()
    )
    point_at_top_of_upper_section = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0])
            * (
                height_of_lower_section
                + height_of_transition_section
                + height_of_upper_section
            )
        ).tolist()
    )

    sphere_of_bottom = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_lower_section,
        repositioned_origin=point_at_center_of_bottom_sphere,
    )
    cylinder_of_lower_section_for_subtracting = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_lower_section,
            extrusion_depth=height_of_lower_section - radius_of_lower_section,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )
    hemisphere_of_bottom = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_bottom,
        second_items=[cylinder_of_lower_section_for_subtracting],
        operator="DIFFERENCE",
    )[-1]

    cylinder_of_lower_section_for_adding = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_lower_section,
            extrusion_depth=height_of_lower_section - radius_of_lower_section,
            repositioned_origin=point_at_center_of_bottom_sphere,
        )
    )

    thickness = radius_of_lower_section * 0.10
    cylinder_tapered_for_transition_section = (
        bim2fem.ifcplus.api.geometry.add_extruded_area_solid_tapered(
            ifc4_file=ifc4_file,
            swept_area=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcCircleHollowProfileDef",
                dimensions=[radius_of_lower_section, thickness],
            ),
            end_swept_area=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcCircleHollowProfileDef",
                dimensions=[radius_of_upper_section, thickness],
            ),
            depth=height_of_transition_section,
            repositioned_origin=point_at_bottom_of_transition_section,
        )
    )

    cylinder_of_upper_section_for_adding = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_upper_section,
            extrusion_depth=height_of_upper_section - radius_of_upper_section,
            repositioned_origin=point_at_bottom_of_upper_section,
        )
    )

    sphere_of_top = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_upper_section,
        repositioned_origin=point_at_center_of_top_sphere,
    )
    cylinder_of_upper_section_for_subtracting = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_upper_section,
            extrusion_depth=height_of_upper_section - radius_of_upper_section,
            repositioned_origin=point_at_bottom_of_upper_section,
        )
    )
    hemisphere_for_top = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=sphere_of_top,
        second_items=[cylinder_of_upper_section_for_subtracting],
        operator="DIFFERENCE",
    )[-1]

    elevation_of_primary_coolant_nozzles = 2.0 / 21.0 * height_overall
    z_axis_of_primary_inlet_nozzle = (1.0, 0.0, 0.0)
    x_axis_of_primary_inlet_nozzle = (0.0, 1.0, 0.0)
    origin_of_primary_inlet_nozzle = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * elevation_of_primary_coolant_nozzles
            - np.array([1.0, 0.0, 0.0])
            * (radius_of_lower_section + length_of_protrusion_of_primary_inlet_nozzle)
        ).tolist()
    )
    cylinder_for_primary_inlet_nozzle = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=diameter_of_primary_inlet_nozzle / 2.0,
            extrusion_depth=length_of_protrusion_of_primary_inlet_nozzle
            + 1 / 4 * radius_of_lower_section,
            repositioned_origin=origin_of_primary_inlet_nozzle,
            repositioned_z_axis=z_axis_of_primary_inlet_nozzle,
            repositioned_x_axis=x_axis_of_primary_inlet_nozzle,
        )
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
    )

    z_axis_of_primary_outlet_nozzle = (1.0, 0.0, 0.0)
    x_axis_of_primary_outlet_nozzle = (0.0, 1.0, 0.0)
    origin_of_primary_outlet_nozzle = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * elevation_of_primary_coolant_nozzles
            + np.array([1.0, 0.0, 0.0])
            * (radius_of_lower_section + length_of_protrusion_of_primary_outlet_nozzle)
        ).tolist()
    )
    neg_z_axis_of_primary_outlet_nozzle = tuple(
        (np.array(z_axis_of_primary_outlet_nozzle) * -1).tolist()
    )
    neg_x_axis_of_primary_outlet_nozzle = tuple(
        (np.array(x_axis_of_primary_outlet_nozzle) * -1).tolist()
    )
    cylinder_for_primary_outlet_nozzle = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=diameter_primary_outlet_nozzle / 2.0,
            extrusion_depth=length_of_protrusion_of_primary_outlet_nozzle
            + 1 / 4 * radius_of_lower_section,
            repositioned_origin=origin_of_primary_outlet_nozzle,
            repositioned_z_axis=neg_z_axis_of_primary_outlet_nozzle,
            repositioned_x_axis=neg_x_axis_of_primary_outlet_nozzle,
        )
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
    )

    z_axis_of_steam_outlet = (0.0, 0.0, 1.0)
    x_axis_of_steam_outlet = (1.0, 0.0, 0.0)
    origin_of_steam_outlet = tuple(
        (
            np.array(point_at_top_of_upper_section)
            + np.array([0.0, 0.0, 1.0]) * length_of_protrusion_of_steam_outlet
        ).tolist()
    )
    neg_z_axis_of_steam_outlet = tuple((np.array(z_axis_of_steam_outlet) * -1).tolist())
    neg_x_axis_of_steam_outlet = tuple((np.array(x_axis_of_steam_outlet) * -1).tolist())
    cylinder_for_steam_outlet = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=diameter_of_steam_outlet / 2.0,
            extrusion_depth=radius_of_upper_section * 1 / 2
            + length_of_protrusion_of_steam_outlet,
            repositioned_origin=origin_of_steam_outlet,
            repositioned_z_axis=neg_z_axis_of_steam_outlet,
            repositioned_x_axis=neg_x_axis_of_steam_outlet,
        )
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
    )

    height_of_feedwater_inlet = 15.85 / 21 * height_overall
    origin_of_feedwater_inlet = tuple(
        (
            np.array(point_at_bottom_of_sg)
            + np.array([0.0, 0.0, 1.0]) * height_of_feedwater_inlet
            + np.array([0.0, -1.0, 0.0])
            * (radius_of_upper_section + length_of_protrusion_of_feedwater_inlet)
        ).tolist()
    )
    radius_of_feedwater_inlet = diameter_of_feedwater_inlet / 2.0
    z_axis_of_feedwater_inlet = (0.0, 1.0, 0.0)
    x_axis_of_feedwater_inlet = (-1.0, 0.0, 0.0)
    length_of_cylinder_for_feedwater_inlet = (
        radius_of_upper_section * 1 / 2 + length_of_protrusion_of_feedwater_inlet
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

    complete_steam_generator_body = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=hemisphere_of_bottom,
        second_items=[
            cylinder_of_lower_section_for_adding,
            cylinder_tapered_for_transition_section,
            cylinder_of_upper_section_for_adding,
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

    return steam_generator


def create_reactor_coolant_pump(
    ifc4_file: ifcopenshell.file,
    scale_factor: float = 1.0,
    reactor_coolant_pump: ifcopenshell.entity_instance | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    reactor_coolant_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create reactor coolant pump with default dimensions roughly corresponding to
    5.5 m^3/s flow rate.
    """

    if reactor_coolant_pump is None:
        reactor_coolant_pump = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPump",
            predefined_type="USERDEFINED",
        )
        reactor_coolant_pump.ObjectType = "REACTOR_COOLANT_PUMP"

    height_of_lower_section = 2.4 * scale_factor
    height_of_upper_section = 4.0 * scale_factor

    diameter_of_lower_section = 2.1 * scale_factor
    diameter_of_upper_section = 1.5 * scale_factor

    diameter_of_inlet = 0.55 * scale_factor
    diameter_of_outlet = 0.55 * scale_factor

    length_of_nozzle = 0.5

    radius_of_lower_section = diameter_of_lower_section / 2.0
    radius_of_upper_section = diameter_of_upper_section / 2.0
    radius_of_inlet = diameter_of_inlet / 2.0
    radius_of_outlet = diameter_of_outlet / 2.0

    elevation_of_outlet = 1.0

    point_at_bottom_of_lower_section = (
        radius_of_lower_section,
        radius_of_lower_section,
        length_of_nozzle,
    )
    point_at_bottom_of_upper_section = (
        radius_of_lower_section,
        radius_of_lower_section,
        length_of_nozzle + height_of_lower_section,
    )

    cylinder_for_lower_section = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_lower_section,
            extrusion_depth=height_of_lower_section,
            repositioned_origin=point_at_bottom_of_lower_section,
        )
    )

    cylinder_for_upper_section = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_upper_section,
            extrusion_depth=height_of_upper_section,
            repositioned_origin=point_at_bottom_of_upper_section,
        )
    )

    z_axis_of_inlet = (0.0, 0.0, 1.0)
    x_axis_of_inlet = (1.0, 0.0, 0.0)
    origin_of_inlet = (radius_of_lower_section, radius_of_lower_section, 0.0)
    cylinder_for_inlet = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_inlet,
            extrusion_depth=length_of_nozzle,
            repositioned_origin=origin_of_inlet,
            repositioned_z_axis=z_axis_of_inlet,
            repositioned_x_axis=x_axis_of_inlet,
        )
    )
    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_inlet,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_inlet,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_inlet,
        distribution_element=reactor_coolant_pump,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )

    z_axis_of_outlet = (1.0, 0.0, 0.0)
    x_axis_of_outlet = (0.0, 1.0, 0.0)
    origin_of_outlet = (
        radius_of_lower_section + radius_of_lower_section + length_of_nozzle,
        radius_of_lower_section,
        elevation_of_outlet,
    )
    neg_z_axis_of_steam_outlet = tuple((np.array(z_axis_of_outlet) * -1).tolist())
    neg_x_axis_of_steam_outlet = tuple((np.array(x_axis_of_outlet) * -1).tolist())
    cylinder_for_outlet = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_outlet,
            extrusion_depth=length_of_nozzle + 1 / 2 * radius_of_lower_section,
            repositioned_origin=origin_of_outlet,
            repositioned_z_axis=neg_z_axis_of_steam_outlet,
            repositioned_x_axis=neg_x_axis_of_steam_outlet,
        )
    )
    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=origin_of_outlet,
        port_z_axis_in_distribution_element_coordinates=z_axis_of_outlet,
        port_x_axis_in_distribution_element_coordinates=x_axis_of_outlet,
        distribution_element=reactor_coolant_pump,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )

    complete_rcp = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=cylinder_for_lower_section,
        second_items=[
            cylinder_for_upper_section,
            cylinder_for_inlet,
            cylinder_for_outlet,
        ],
        operator="UNION",
    )[-1]

    csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=complete_rcp,
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
        product=reactor_coolant_pump,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[reactor_coolant_pump],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=reactor_coolant_pump,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(reactor_coolant_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[reactor_coolant_pump],
            system=reactor_coolant_system,
        )

    return reactor_coolant_pump
