# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Distribution Element Creation Module"""

import ifcopenshell
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import ifcopenshell.api.system
import bim2fem.ifcplus.api.system
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
import numpy as np
import bim2fem.ifcplus.api.system
import ifcopenshell.util.representation
import bim2fem.ifcplus.api.material
import bim2fem.ifcplus.api.element_type
import ifcopenshell.api.type


def create_elbow(
    ifc4_file: ifcopenshell.file,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    point_defining_plane_of_arc_and_center_of_curvature_side: tuple[
        float, float, float
    ],
    radius_of_curvature: float,
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    elbow: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create piping elbow as an IfcPipeFitting."""

    outer_radius = nominal_diameter / 2 + thickness / 2

    profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
        ifc4_file=ifc4_file,
        profile_class="IfcCircleHollowProfileDef",
        dimensions=[outer_radius, thickness],
        profile_name=None,
        check_for_duplicate=True,
        calculate_mechanical_properties=True,
    )

    material_profile_set = bim2fem.ifcplus.api.material.add_material_profile_set_with_single_material_profile(
        material=material,
        profile=profile,
        name=None,
        check_for_duplicate=True,
    )

    element_type = (
        bim2fem.ifcplus.api.element_type.add_element_type_for_material_profile_set(
            ifc_class="IfcPipeFittingType",
            material_profile_set=material_profile_set,
            name=material_profile_set.Name,
            check_for_duplicate=True,
        )
    )

    if elbow is None:
        elbow = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeFitting",
            name=name,
            predefined_type="JUNCTION",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[elbow],
        relating_type=element_type,
    )

    horizontal_curve = bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_on_center_of_curvature_side=point_defining_plane_of_arc_and_center_of_curvature_side,
        point_of_curvature=start_point,
        point_of_tangency=end_point,
        radius_of_curvature=radius_of_curvature,
    )

    revolved_area_solid = bim2fem.ifcplus.api.geometry.add_revolved_area_solid(
        ifc4_file=ifc4_file,
        swept_area=profile,
        central_angle_of_curvature=horizontal_curve.central_angle,
        center_of_curvature_in_object_xy_plane=(
            horizontal_curve.radius_of_curvature,
            0.0,
        ),
    )

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[revolved_area_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[revolved_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=elbow,
        representation=shape_representation,
    )

    z_axis = tuple(
        (
            np.array(horizontal_curve.point_of_intersection)
            - np.array(horizontal_curve.point_of_curvature)
        ).tolist()
    )

    x_axis = tuple(
        (
            np.array(horizontal_curve.center_of_curvature)
            - np.array(horizontal_curve.point_of_curvature)
        ).tolist()
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[elbow],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=elbow,
        repositioned_origin=horizontal_curve.point_of_curvature,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[elbow],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
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

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=source_port_origin_in_object_coordinates,
        port_z_axis_in_distribution_element_coordinates=source_port_z_axis_in_object_coordinates,
        port_x_axis_in_distribution_element_coordinates=source_port_x_axis_in_object_coordinates,
        distribution_element=elbow,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
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
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create an IfcPipeSegment."""

    outer_radius = nominal_diameter / 2 + thickness / 2

    profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
        ifc4_file=ifc4_file,
        profile_class="IfcCircleHollowProfileDef",
        dimensions=[outer_radius, thickness],
        check_for_duplicate=True,
        calculate_mechanical_properties=True,
    )

    material_profile_set = bim2fem.ifcplus.api.material.add_material_profile_set_with_single_material_profile(
        material=material,
        profile=profile,
        name=None,
        check_for_duplicate=True,
    )

    element_type = (
        bim2fem.ifcplus.api.element_type.add_element_type_for_material_profile_set(
            ifc_class="IfcPipeSegmentType",
            material_profile_set=material_profile_set,
            name=material_profile_set.Name,
            check_for_duplicate=True,
        )
    )

    if pipe_segment is None:
        pipe_segment = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcPipeSegment",
            name=name,
            predefined_type="NOTDEFINED",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[pipe_segment],
        relating_type=element_type,
    )

    z_axis = tuple((np.array(end_point) - np.array(start_point)).tolist())

    angle_between_local_and_global_z_axes = (
        bim2fem.ifcplus.util.geometry.calculate_angle_between_two_vectors(
            vector1=z_axis,
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
        y_axis = (0.0, 1.0, 0.0)
    else:
        y_axis = np.cross(
            (0.0, 0.0, 1.0),
            z_axis,
        )

    x_axis = tuple(np.cross(y_axis, z_axis).tolist())

    length = float(np.linalg.norm(z_axis))

    extruded_area_solid = bim2fem.ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=profile,
        depth=length,
    )

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[extruded_area_solid]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=pipe_segment,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[pipe_segment],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=pipe_segment,
        repositioned_origin=start_point,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[pipe_segment],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(0.0, 0.0, 0.0),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(0.0, 0.0, length),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    return pipe_segment


def create_make_up_air_unit(
    ifc4_file: ifcopenshell.file,
    length: float = 4.0,
    width: float = 1.5,
    height: float = 1.5,
    make_up_air_unit: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create make-up air unit as an IfcUnitaryEquipment."""

    if make_up_air_unit is None:
        make_up_air_unit = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcUnitaryEquipment",
            name=name,
            predefined_type="AIRHANDLER",
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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[make_up_air_unit],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=make_up_air_unit,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[make_up_air_unit],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            length,
            width / 2.0,
            height / 2,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=make_up_air_unit,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return make_up_air_unit


def create_hepa_containment_housing(
    ifc4_file: ifcopenshell.file,
    length: float = 8.0,
    width: float = 1.0,
    height: float = 2.0,
    hepa_housing: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create air filtration containment housing as an IfcFilter."""

    if hepa_housing is None:
        hepa_housing = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcUnitaryEquipment",
            name=name,
            predefined_type="USERDEFINED",
        )
        hepa_housing.ObjectType = "HEPA_CONTAINMENT_HOUSING"

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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[hepa_housing],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=hepa_housing,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[hepa_housing],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0,
            width / 2.0,
            height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=hepa_housing,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            length,
            width / 2.0,
            height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=hepa_housing,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return hepa_housing


def create_motorized_valve(
    ifc4_file: ifcopenshell.file,
    outer_diameter: float = 0.5,
    thickness: float = 0.1,
    motorized_valve: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create motorized valve as an IfcValve."""

    if motorized_valve is None:
        motorized_valve = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcValve",
            name=name,
            predefined_type="USERDEFINED",
        )
        motorized_valve.ObjectType = "MOTORIZED_CONTROL_VALVE"

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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[motorized_valve],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=motorized_valve,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[motorized_valve],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1.5 * outer_diameter,
            0.0,
            outer_diameter / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 1.0),
        distribution_element=motorized_valve,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1.5 * outer_diameter,
            2 / 5 * outer_diameter,
            outer_diameter / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 1.0),
        distribution_element=motorized_valve,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return motorized_valve


def create_generic_air_filter(
    ifc4_file: ifcopenshell.file,
    length: float = 0.5,
    width: float = 0.1,
    height: float = 0.4,
    air_filter: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create generic air filter as an IfcFilter."""

    if air_filter is None:
        air_filter = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[air_filter],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=air_filter,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[air_filter],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0 + length / 2.0,
            0.0,
            0.0 + height / 2.0,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(-1.0, 0.0, 0.0),
        distribution_element=air_filter,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0 + length / 2,
            0.0 + width,
            0.0 + height / 2,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(-1.0, 0.0, 0.0),
        distribution_element=air_filter,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return air_filter


def create_hprs_exhaust_fan(
    ifc4_file: ifcopenshell.file,
    length: float = 2.0,
    width: float = 1.0,
    height: float = 1.0,
    fan: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create hprs exhaust fan as an IfcFan."""

    if fan is None:
        fan = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFan",
            name=name,
            predefined_type="USERDEFINED",
        )
        fan.ObjectType = "HPRS_EXHAUST_FAN"

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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[fan],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=fan,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[fan],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            0.0,
            width / 2.0,
            2.5 / 4 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=fan,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            1 / 10 * length,
            width,
            3.5 / 4.0 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=fan,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return fan


def create_exhaust_stack(
    ifc4_file: ifcopenshell.file,
    base_diameter: float = 0.5,
    height: float = 8.0,
    exhaust_stack: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """Create exhaust stack as an IfcDistributionElement."""

    if exhaust_stack is None:
        exhaust_stack = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStackTerminal",
            name=name,
            predefined_type="USERDEFINED",
        )
        exhaust_stack.ObjectType = "EXHAUST_STACK"

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

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[exhaust_stack],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=exhaust_stack,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[exhaust_stack],
            system=distribution_system,
        )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            base_diameter * 2.0,
            base_diameter / 2.0,
            1 / 5 * height,
        ),
        port_z_axis_in_distribution_element_coordinates=(-1.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(0.0, 1.0, 0.0),
        distribution_element=exhaust_stack,
        flow_direction="SINK",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        ifc4_file=ifc4_file,
        port_origin_in_distribution_element_coordinates=(
            base_diameter / 2.0,
            base_diameter / 2.0,
            height,
        ),
        port_z_axis_in_distribution_element_coordinates=(0.0, 0.0, 1.0),
        port_x_axis_in_distribution_element_coordinates=(1.0, 0.0, 0.0),
        distribution_element=exhaust_stack,
        flow_direction="SOURCE",
        predefined_type="DUCT",
        distribution_system=distribution_system,
    )

    return exhaust_stack
