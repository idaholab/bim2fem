# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import bim2fem.ifcplus.api.geometry
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
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
from typing import Literal
import ifcopenshell.util.system
import bim2fem.ifcplus.api.material
import bim2fem.ifcplus.api.built_element
import ifcopenshell.api.profile
import ifcopenshell.api.pset
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial

REACTOR_COOLANT_LOOP_LABEL = Literal[
    "A",
    "B",
    "C",
    "D",
]


def create_simplified_rectangular_hall_building(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    material: ifcopenshell.entity_instance | None = None,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
):

    building = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        predefined_type="RECTANGULAR_HALL",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=building,
    )

    if material is None:
        material = bim2fem.ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )
        material = cast(
            ifcopenshell.entity_instance,
            material,
        )

    thickness = 0.5
    wall_height = height - thickness * 2.0

    base_slab = bim2fem.ifcplus.api.built_element.create_slab(
        profile=ifcopenshell.api.profile.add_arbitrary_profile(
            file=ifc4_file,
            profile=[
                (0.0, 0.0),
                (length, 0.0),
                (length, width),
                (0.0, width),
                (0.0, 0.0),
            ],
        ),
        materials=[material],
        thicknesses=[thickness],
        location=(0.0, 0.0, 0.0),
    )
    base_slab.PredefinedType = "BASESLAB"

    wall_1 = bim2fem.ifcplus.api.built_element.create_linear_wall(
        start_point_2d=(0.0, thickness / 2.0),
        end_point_2d=(0.0 + length, thickness / 2.0),
        elevation=thickness,
        height=wall_height,
        materials=[material],
        thicknesses=[thickness],
    )

    wall_2 = bim2fem.ifcplus.api.built_element.create_linear_wall(
        start_point_2d=(0.0, width - thickness / 2.0),
        end_point_2d=(0.0 + length, width - thickness / 2.0),
        elevation=thickness,
        height=wall_height,
        materials=[material],
        thicknesses=[thickness],
    )

    wall_3 = bim2fem.ifcplus.api.built_element.create_linear_wall(
        start_point_2d=(thickness / 2.0, thickness),
        end_point_2d=(thickness / 2.0, width - thickness),
        elevation=thickness,
        height=wall_height,
        materials=[material],
        thicknesses=[thickness],
    )

    wall_4 = bim2fem.ifcplus.api.built_element.create_linear_wall(
        start_point_2d=(length - thickness / 2.0, thickness),
        end_point_2d=(length - thickness / 2.0, width - thickness),
        elevation=thickness,
        height=wall_height,
        materials=[material],
        thicknesses=[thickness],
    )

    roof_slab = bim2fem.ifcplus.api.built_element.create_slab(
        profile=ifcopenshell.api.profile.add_arbitrary_profile(
            file=ifc4_file,
            profile=[
                (0.0, 0.0),
                (length, 0.0),
                (length, width),
                (0.0, width),
                (0.0, 0.0),
            ],
        ),
        location=(0.0, 0.0, thickness + wall_height),
        materials=[material],
        thicknesses=[thickness],
    )
    roof_slab.PredefinedType = "ROOF"

    bim2fem.ifcplus.api.spatial.assign_container_v2(
        products=[
            base_slab,
            wall_1,
            wall_2,
            wall_3,
            wall_4,
            roof_slab,
        ],
        relating_structure=building,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=building,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return building


def create_pressurized_reactor_containment_structure(
    ifc4_file: ifcopenshell.file,
    radius: float = 20.0,
    height: float = 73.0,
    thickness: float = 1.0,
    material: ifcopenshell.entity_instance | None = None,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:

    building = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        predefined_type="REACTOR_CONTAINMENT",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=building,
    )

    thickness_of_base_slab = thickness * 3
    thickness_of_cylindrical_wall = thickness
    radius_of_dome = radius
    radius_of_cylindrical_wall = radius
    radius_of_base_slab = radius
    thickness_of_dome = thickness
    height_of_cylindrical_wall = height - thickness_of_base_slab - radius_of_dome

    if material is None:
        material = bim2fem.ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )
        material = cast(
            ifcopenshell.entity_instance,
            material,
        )

    point_at_bottom_of_base_slab = (
        radius_of_base_slab,
        radius_of_base_slab,
        0.0,
    )
    point_at_bottom_of_cylindrical_wall = (
        radius_of_base_slab,
        radius_of_base_slab,
        thickness_of_base_slab,
    )
    point_at_top_of_cylindrical_wall = (
        radius_of_cylindrical_wall,
        radius_of_cylindrical_wall,
        height_of_cylindrical_wall + thickness_of_base_slab,
    )

    base_slab = bim2fem.ifcplus.api.built_element.create_slab(
        profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleProfileDef",
            dimensions=[radius_of_base_slab],
        ),
        materials=[material],
        thicknesses=[thickness_of_base_slab],
        location=point_at_bottom_of_base_slab,
    )
    base_slab.PredefinedType = "BASESLAB"
    base_slab.Name = "Containment Base Mat"
    base_slab.Description = (
        "Reinforced concrete foundation mat for reactor containment structure"
    )

    cylindrical_wall = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
        predefined_type="CONTAINMENT_SHELL",
        name="Containment Shell Wall",
    )
    cylindrical_wall.Description = (
        "Cylindrical reinforced concrete containment structure wall"
    )
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[cylindrical_wall],
        material=material,
    )
    cylindrical_extruded_area_solid = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_cylindrical_wall,
            wall_thickness=thickness_of_cylindrical_wall,
            extrusion_depth=height_of_cylindrical_wall,
        )
    )
    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(
                items=[cylindrical_extruded_area_solid]
            ),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[cylindrical_extruded_area_solid],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=cylindrical_wall,
        representation=shape_representation,
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=cylindrical_wall,
        repositioned_location=point_at_bottom_of_cylindrical_wall,
    )

    dome_cap = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuildingElementProxy",
        predefined_type="CONTAINMENT_DOME",
        name="Containment Dome",
    )
    dome_cap.Description = "Hemispherical reinforced concrete dome roof structure"
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[dome_cap],
        material=material,
    )
    outer_sphere_of_top = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_dome,
    )
    innner_sphere_of_top = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=radius_of_dome - thickness_of_dome,
    )
    cylinder_of_for_subtracting = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=radius_of_cylindrical_wall * 2.0,
            extrusion_depth=radius_of_dome * 2,
            repositioned_origin=(0.0, 0.0, -radius_of_dome * 2),
        )
    )
    hollow_hemisphere_of_top = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=outer_sphere_of_top,
        second_items=[
            innner_sphere_of_top,
            cylinder_of_for_subtracting,
        ],
        operator="DIFFERENCE",
    )[-1]
    csg_solid_of_dome_cap = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=hollow_hemisphere_of_top,
    )
    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[csg_solid_of_dome_cap]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[csg_solid_of_dome_cap],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=dome_cap,
        representation=shape_representation,
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=dome_cap,
        repositioned_location=point_at_top_of_cylindrical_wall,
    )

    bim2fem.ifcplus.api.spatial.assign_container_v2(
        products=[cylindrical_wall, dome_cap, base_slab],
        relating_structure=building,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=building,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return building


def create_reactor_box(
    ifc4_file: ifcopenshell.file,
    length: float = 20.0,
    width: float = 20.0,
    height: float = 15.0,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:

    reactor_box = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcEnergyConversionDevice",
        predefined_type="REACTOR_BOX",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_box,
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

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_box,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return reactor_box


def create_reactor_pressure_vessel(
    ifc4_file: ifcopenshell.file,
    reactor_coolant_system: ifcopenshell.entity_instance,
    num_loops: int = 4,
    thermal_power_capacity: float = 3500e6,  # Wth
    reactor_unit_num: int | None = None,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create reactor pressure vessel with default dimensions roughly corresponding to
    3500 MWth thermal capacity.
    """

    reactor_pressure_vessel = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcTank",
        predefined_type="REACTOR_PRESSURE_VESSEL",
        name=f"RPV-{reactor_unit_num}" if reactor_unit_num else "RPV",
    )
    reactor_pressure_vessel.Description = (
        f"Reactor Pressure Vessel of Unit {reactor_unit_num} with {thermal_power_capacity*1e-6} MWth thermal power capacity"
        if reactor_unit_num
        else f"Reactor Pressure Vessel with {thermal_power_capacity*1e-6} thermal power capacity"
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_pressure_vessel,
    )

    reference_thermal_power_capacity = 3500e6  # Wth
    scale_factor = (thermal_power_capacity / reference_thermal_power_capacity) ** (
        1 / 3
    )

    diameter_of_cold_leg_inlet = 0.55 * scale_factor
    length_of_cold_leg_inlet = 0.5 * scale_factor

    diameter_of_hot_leg_outlet = 0.74 * scale_factor
    length_of_hot_leg_outlet = 0.5 * scale_factor

    diameter_of_body = 5.0 * scale_factor
    height_overall = 12.5 * scale_factor

    radius_of_body = diameter_of_body / 2.0
    height_of_cylinder = height_overall - 2.0 * radius_of_body

    if num_loops == 1:
        point_at_center_of_bottom_sphere = (
            radius_of_body,
            radius_of_body,
            radius_of_body,
        )
    else:
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

    text_before_loop_label_in_name = reactor_unit_num if reactor_unit_num else ""
    text_after_loop_label_in_description = (
        f" of Unit {reactor_unit_num}" if reactor_unit_num else ""
    )

    if num_loops == 1:
        z_axes_for_cold_leg_inlets = [
            (-1.0, 0.0, 0.0),
        ]
        names_for_cold_leg_inlets = [
            f"CL-{text_before_loop_label_in_name}{loop_label}" for loop_label in ["A"]
        ]
        descriptions_for_cold_leg_inlets = [
            f"Cold Leg Inlet for Loop {loop_label}{text_after_loop_label_in_description}"
            for loop_label in ["A"]
        ]
        z_axes_for_hot_leg_outlets = [
            (0.0, 1.0, 0.0),
        ]
        names_for_hot_leg_outlets = [
            f"HL-{text_before_loop_label_in_name}{loop_label}" for loop_label in ["A"]
        ]
        descriptions_for_hot_leg_outlets = [
            f"Hot Leg Outlet for Loop {loop_label}{text_after_loop_label_in_description}"
            for loop_label in ["A"]
        ]
    else:
        z_axes_for_cold_leg_inlets = [
            (-1.0, 0.0, 0.0),
            (1.0, -1.0, 0.0),
            (1.0, 0.0, 0.0),
            (-1.0, 1.0, 0.0),
        ]
        names_for_cold_leg_inlets = [
            f"CL-{text_before_loop_label_in_name}{loop_label}"
            for loop_label in ["A", "B", "C", "D"]
        ]
        descriptions_for_cold_leg_inlets = [
            f"Cold Leg Inlet for Loop {loop_label}{text_after_loop_label_in_description}"
            for loop_label in ["A", "B", "C", "D"]
        ]
        z_axes_for_hot_leg_outlets = [
            (1.0, 1.0, 0.0),
            (0.0, 1.0, 0.0),
            (-1.0, -1.0, 0.0),
            (0.0, -1.0, 0.0),
        ]
        names_for_hot_leg_outlets = [
            f"HL-{text_before_loop_label_in_name}{loop_label}"
            for loop_label in ["A", "B", "C", "D"]
        ]
        descriptions_for_hot_leg_outlets = [
            f"Hot Leg Outlet for Loop {loop_label}{text_after_loop_label_in_description}"
            for loop_label in ["A", "B", "C", "D"]
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
        name_for_hot_leg_outlet,
        description_for_cold_leg_inlet,
        description_for_hot_leg_outlet,
    ) in zip(
        z_axes_for_cold_leg_inlets,
        z_axes_for_hot_leg_outlets,
        names_for_cold_leg_inlets,
        names_for_hot_leg_outlets,
        descriptions_for_cold_leg_inlets,
        descriptions_for_hot_leg_outlets,
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
            location=origin_of_cold_leg_inlet,
            z_axis=z_axis_for_cold_leg_inlet,
            x_axis=x_axis_for_cold_leg_inlet,
            distribution_element=reactor_pressure_vessel,
            flow_direction="SINK",
            predefined_type="PIPE",
            distribution_system=reactor_coolant_system,
        )
        cl_port.Name = name_for_cold_leg_inlet
        cl_port.Description = description_for_cold_leg_inlet

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
            location=origin_of_hot_leg_outlet,
            z_axis=z_axis_for_hot_leg_outlet,
            x_axis=x_axis_for_hot_leg_outlet,
            distribution_element=reactor_pressure_vessel,
            flow_direction="SOURCE",
            predefined_type="PIPE",
            distribution_system=reactor_coolant_system,
        )
        hl_port.Name = name_for_hot_leg_outlet
        hl_port.Description = description_for_hot_leg_outlet

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

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[reactor_pressure_vessel],
        system=reactor_coolant_system,
    )

    inl_pset_template = create_INL_nuclear_property_set_template(
        ifc4_file=ifc4_file,
        check_for_duplicate=True,
    )
    rpv_pset = ifcopenshell.api.pset.add_pset(
        file=ifc4_file,
        product=reactor_pressure_vessel,
        name="INL_ReactorPressureVesselCommon",
    )
    ifcopenshell.api.pset.edit_pset(
        file=ifc4_file,
        pset=rpv_pset,
        properties={
            "ThermalPowerCapacity": thermal_power_capacity,  # Wth
        },
        pset_template=inl_pset_template,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_pressure_vessel,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return reactor_pressure_vessel


def create_INL_nuclear_property_set_template(
    ifc4_file: ifcopenshell.file,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:

    if check_for_duplicate:
        for old_pset_template in ifc4_file.by_type(
            type="IfcPropertySetTemplate",
            include_subtypes=False,
        ):
            if old_pset_template.Name == "INL_pset_template":
                return old_pset_template

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
    reactor_coolant_system: ifcopenshell.entity_instance,
    secondary_coolant_system: ifcopenshell.entity_instance,
    thermal_power_capacity: float = 3500e6,  # Wth
    reactor_unit_num: int | None = None,
    loop_label: str | None = None,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
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

    steam_generator = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcHeatExchanger",
        predefined_type="STEAM_GENERATOR",
        name=f"SG-{reactor_unit_num}{loop_label}" if reactor_unit_num else "SG",
    )
    steam_generator.Description = (
        f"Steam Generator for Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Steam Generator"
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=steam_generator,
    )

    reference_thermal_power_capacity = 3500e6  # Wth
    scale_factor = (thermal_power_capacity / reference_thermal_power_capacity) ** (
        1 / 3
    )

    diameter_of_primary_inlet_nozzle = 0.74 * scale_factor
    diameter_primary_outlet_nozzle = 0.55 * scale_factor

    diameter_of_steam_outlet = 0.6 * scale_factor
    diameter_of_feedwater_inlet = 0.4 * scale_factor

    diameter_of_lower_section = 3.65 * scale_factor
    diameter_of_upper_section = 4.78 * scale_factor

    height_of_lower_section = 11.8 * scale_factor
    height_of_transition_section = 1.4 * scale_factor
    height_of_upper_section = 7.8 * scale_factor

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
    sg_primary_coolant_in = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_primary_inlet_nozzle,
        z_axis=z_axis_of_primary_inlet_nozzle,
        x_axis=x_axis_of_primary_inlet_nozzle,
        distribution_element=steam_generator,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )
    sg_primary_coolant_in.Name = (
        f"SG-{reactor_unit_num}{loop_label}-PC-IN" if reactor_unit_num else "SG-PC-IN"
    )
    sg_primary_coolant_in.Description = (
        f"Primary Inlet Nozzle for Steam Generator of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Primary Inlet Nozzle for Steam Generator"
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
    sg_primary_coolant_out = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_primary_outlet_nozzle,
        z_axis=z_axis_of_primary_outlet_nozzle,
        x_axis=x_axis_of_primary_outlet_nozzle,
        distribution_element=steam_generator,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )
    sg_primary_coolant_out.Name = (
        f"SG-{reactor_unit_num}{loop_label}-PC-OUT" if reactor_unit_num else "SG-PC-OUT"
    )
    sg_primary_coolant_out.Description = (
        f"Primary Outlet Nozzle for Steam Generator of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Primary Outlet Nozzle for Steam Generator"
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
    sg_main_steam_outlet = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_steam_outlet,
        z_axis=z_axis_of_steam_outlet,
        x_axis=x_axis_of_steam_outlet,
        distribution_element=steam_generator,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=secondary_coolant_system,
    )
    sg_main_steam_outlet.Name = (
        f"SG-{reactor_unit_num}{loop_label}-MS" if reactor_unit_num else "SG-MS"
    )
    sg_main_steam_outlet.Description = (
        f"Main Steam Outlet for Steam Generator of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Main Steam Outlet for Steam Generator"
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
    sg_feedwater_inlet = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_feedwater_inlet,
        z_axis=z_axis_of_feedwater_inlet,
        x_axis=x_axis_of_feedwater_inlet,
        distribution_element=steam_generator,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=secondary_coolant_system,
    )
    sg_feedwater_inlet.Name = (
        f"SG-{reactor_unit_num}{loop_label}-FW" if reactor_unit_num else "SG-FW"
    )
    sg_feedwater_inlet.Description = (
        f"Feedwater Inlet for Steam Generator of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Feedwater Inlet for Steam Generator"
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

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[steam_generator],
        system=reactor_coolant_system,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[steam_generator],
        system=secondary_coolant_system,
    )

    inl_pset_template = create_INL_nuclear_property_set_template(
        ifc4_file=ifc4_file,
        check_for_duplicate=True,
    )
    sg_pset = ifcopenshell.api.pset.add_pset(
        file=ifc4_file,
        product=steam_generator,
        name="INL_SteamGeneratorCommon",
    )
    ifcopenshell.api.pset.edit_pset(
        file=ifc4_file,
        pset=sg_pset,
        properties={
            "ThermalPowerCapacity": thermal_power_capacity,  # Wth
        },
        pset_template=inl_pset_template,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=steam_generator,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return steam_generator


def create_reactor_coolant_pump(
    ifc4_file: ifcopenshell.file,
    reactor_coolant_system: ifcopenshell.entity_instance,
    flow_rate: float = 5.5,  # cumecs
    reactor_unit_num: int | None = None,
    loop_label: str | None = None,
    location: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis: tuple[float, float, float] = (1.0, 0.0, 0.0),
) -> ifcopenshell.entity_instance:
    """Create reactor coolant pump with default dimensions roughly corresponding to
    5.5 m^3/s flow rate.
    """

    reactor_coolant_pump = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcPump",
        predefined_type="REACTOR_COOLANT_PUMP",
        name=f"RCP-{reactor_unit_num}{loop_label}" if reactor_unit_num else "RCP",
    )
    reactor_coolant_pump.Description = (
        f"Reactor Coolant Pump for Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Reactor Coolant Pump"
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_coolant_pump,
    )

    reference_flow_rate = 5.5  # cumecs
    scale_factor = (flow_rate / reference_flow_rate) ** (1 / 3)

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
    rcp_inlet = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_inlet,
        z_axis=z_axis_of_inlet,
        x_axis=x_axis_of_inlet,
        distribution_element=reactor_coolant_pump,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )
    rcp_inlet.Name = (
        f"RCP-{reactor_unit_num}{loop_label}-IN" if reactor_unit_num else "RCP-IN"
    )
    rcp_inlet.Description = (
        f"Inlet for Reactor Coolant Pump of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Inlet for Reactor Coolant Pump"
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
    rcp_outlet = bim2fem.ifcplus.api.system.create_distribution_port(
        location=origin_of_outlet,
        z_axis=z_axis_of_outlet,
        x_axis=x_axis_of_outlet,
        distribution_element=reactor_coolant_pump,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=reactor_coolant_system,
    )
    rcp_outlet.Name = (
        f"RCP-{reactor_unit_num}{loop_label}-OUT" if reactor_unit_num else "RCP-OUT"
    )
    rcp_outlet.Description = (
        f"Outlet for Reactor Coolant Pump of Loop {loop_label} of Unit {reactor_unit_num}"
        if reactor_unit_num
        else "Outlet for Reactor Coolant Pump"
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

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[reactor_coolant_pump],
        system=reactor_coolant_system,
    )

    inl_pset_template = create_INL_nuclear_property_set_template(
        ifc4_file=ifc4_file,
        check_for_duplicate=True,
    )
    rcp_pset = ifcopenshell.api.pset.add_pset(
        file=ifc4_file,
        product=reactor_coolant_pump,
        name="INL_ReactorCoolantPumpCommon",
    )
    ifcopenshell.api.pset.edit_pset(
        file=ifc4_file,
        pset=rcp_pset,
        properties={
            "FlowRate": flow_rate,  # m^3/s
        },
        pset_template=inl_pset_template,
    )

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=reactor_coolant_pump,
        repositioned_location=location,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    return reactor_coolant_pump
