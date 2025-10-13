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
from typing import Literal
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


ELBOW_RADIUS_TYPE = Literal["LONG", "SHORT"]


def create_elbow(
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

    ifc4_file = material.file

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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=elbow,
            place_object_relative_to_parent=True,
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
    assert isinstance(representation_type, str)

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=representation_type,
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

    port1_origin_in_object_coordinates = (0.0, 0.0, 0.0)
    port1_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=elbow)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "PIPE"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = elbow.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

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
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = elbow.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=nominal_diameter * 0.10,
        )

    return elbow


def create_pipe_segment(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
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

    ifc4_file = material.file

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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=pipe_segment,
            place_object_relative_to_parent=True,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[pipe_segment],
            system=distribution_system,
        )

    object_z_axis_in_global_coordinates = np.array(p2) - np.array(p1)
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
            np.array([0.0, 0.0, 1.0]), object_z_axis_in_global_coordinates
        )
    object_x_axis_in_global_coordinates = np.cross(
        object_y_axis_in_global_coordinates, object_z_axis_in_global_coordinates
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
    assert isinstance(representation_type, str)

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=representation_type,
        items=[extruded_area_solid],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=pipe_segment,
        representation=shape_model,
    )

    object_origin_in_global_coordinates = p1

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

    port1_origin_in_object_coordinates = (0.0, 0.0, 0.0)
    port1_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=pipe_segment)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "PIPE"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = pipe_segment.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    port2_origin_in_object_coordinates = (0.0, 0.0, length)
    port2_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=pipe_segment)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "PIPE"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = pipe_segment.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    block_1 = bim2fem.ifcplus.api.geometry.add_block(  # Block
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )

    block_2 = bim2fem.ifcplus.api.geometry.add_block(  # Block
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

    representation_type = ifcopenshell.util.representation.guess_type(items=[csg_solid])
    assert isinstance(representation_type, str)

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=representation_type,
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

    port1_origin_in_object_coordinates = (length, width / 2.0, height / 2)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SOURCE"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1],
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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
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
    assert isinstance(representation_type, str)

    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=representation_type,
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

    port1_origin_in_object_coordinates = (0.0, width / 2.0, height / 2.0)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    port2_origin_in_object_coordinates = (length, width / 2.0, height / 2.0)
    port2_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * height,
        )

    return element


def create_motorized_valve(
    ifc4_file: ifcopenshell.file,
    outer_diameter: float,
    thickness: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcValve",
            name=name,
            predefined_type="MOTORIZED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        bim2fem.ifcplus.api.geometry.add_block(  # Block
            ifc4_file=ifc4_file,
            length=2 * outer_diameter,
            width=2 / 5 * outer_diameter,
            height=2 / 5 * outer_diameter,
            repositioned_origin=(0.0, 0.0, outer_diameter),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(  # Cylinder
            ifc4_file=ifc4_file,
            radius=outer_diameter / 2.0,
            extrusion_depth=2 / 5 * outer_diameter,
            repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 1.0),
        ),
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(  # Cylinder
            ifc4_file=ifc4_file,
            radius=outer_diameter / 2.0 - thickness,
            extrusion_depth=2 / 5 * outer_diameter,
            repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 1.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        operands=operands,
        boolean_operators=["UNION", "DIFFERENCE"],
    )
    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
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

    # Port 1
    port1_origin_in_object_coordinates = (
        1.5 * outer_diameter,
        0.0,
        outer_diameter / 2.0,
    )
    port1_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 1.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        1.5 * outer_diameter,
        2 / 5 * outer_diameter,
        outer_diameter / 2.0,
    )
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 1.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.10 * outer_diameter,
        )

    return element


def create_generic_air_filter(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    thickness = 1 / 12 * length
    operands = [
        bim2fem.ifcplus.api.geometry.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length,
            width=width,
            height=height,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        bim2fem.ifcplus.api.geometry.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length - thickness * 2,
            width=width,
            height=height - thickness * 2,
            repositioned_origin=(thickness, 0.0, thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        bim2fem.ifcplus.api.geometry.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length - thickness * 2,
            width=width / 4.0,
            height=height - thickness * 2,
            repositioned_origin=(thickness, width / 8.0, thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
    ]

    # # Set Boolean operations
    # boolean_operations = ["DIFFERENCE", "UNION"]

    # # Subtract Holes
    # origin_coordinates_for_holes = inlbim.util.geometry.generate_grid_points(
    #     x_min=1 / 6 * length,
    #     x_max=5 / 6 * length,
    #     y_min=1 / 6 * height,
    #     y_max=5 / 6 * height,
    #     x_spacing=1 / 6 * length,
    #     y_spacing=1 / 6 * height,
    # )
    # for origin_coordinates_for_hole in origin_coordinates_for_holes:
    #     x_pos = origin_coordinates_for_hole[0]
    #     z_pos = origin_coordinates_for_hole[1]
    #     operands.append(
    #         inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Cylinder
    #             ifc4_file=ifc4_file,
    #             radius=hole_size / 2.0,
    #             extrusion_depth=hole_depth,
    #             repositioned_origin=(x_pos, 0.0, z_pos),
    #             repositioned_z_axis=(0.0, 1.0, 0.0),
    #             repositioned_x_axis=(1.0, 0.0, 1.0),
    #         )
    #     )
    #     boolean_operations.append("DIFFERENCE")

    # Add and Assign Representation
    representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "DIFFERENCE",
            "UNION",
        ],
    )
    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
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

    # Port 1
    port1_origin_in_object_coordinates = (
        0.0 + length / 2.0,
        0.0,
        0.0 + height / 2.0,
    )
    port1_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        0.0 + length / 2,
        0.0 + width,
        0.0 + height / 2,
    )
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.4 * thickness,
        )

    return element


def create_hprs_exhaust_fan(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFan",
            name=name,
            predefined_type="CENTRIFUGALBACKWARDINCLINEDCURVED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        bim2fem.ifcplus.api.geometry.add_block(  # Block
            ifc4_file=ifc4_file,
            length=5 / 5 * length,
            width=width,
            height=3 / 4 * height,
            repositioned_origin=(1 / 5 * length, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=width / 2.0,
            extrusion_depth=1 / 5 * length,
            repositioned_origin=(1 / 5 * length, width / 2.0, 2.5 / 4 * height),
            repositioned_z_axis=(-1.0, 0.0, 0.0),
            repositioned_x_axis=(0.0, 0.0, 1.0),
        ),
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
        ),
    ]

    # Add and Assign Representation
    representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "UNION",
            "UNION",
        ],
    )
    shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
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

    # Port 1
    port1_origin_in_object_coordinates = (0.0, width / 2.0, 2.5 / 4 * height)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (1 / 10 * length, width, 3.5 / 4.0 * height)
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * height,
        )

    return element


def create_stack(
    ifc4_file: ifcopenshell.file,
    base_diameter: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcDistributionElement",
            name=name,
            predefined_type="NOTDEFINED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=height,
            repositioned_origin=(base_diameter / 2.0, base_diameter / 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        # inlbim.api.representation.add_cylindrical_extruded_area_solid(
        #     ifc4_file=ifc4_file,
        #     radius=base_diameter / 2.0,
        #     extrusion_depth=base_diameter * 1.5,
        #     repositioned_origin=(
        #         base_diameter / 2.0,
        #         base_diameter / 2.0,
        #         1 / 5 * height,
        #     ),
        #     repositioned_z_axis=(1.0, 0.0, -1.0),
        #     repositioned_x_axis=(0.0, 1.0, 0.0),
        # ),
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
        ),
    ]

    # Add and Assign Representation
    representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "UNION",
        ],
    )
    shape_model = bim2fem.ifcplus.api.representation.add_shape_model(
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
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

    # Port 1
    port1_origin_in_object_coordinates = (
        base_diameter * 2.0,
        base_diameter / 2.0,
        1 / 5 * height,
    )
    port1_z_axis_in_object_coordinates = (-1.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        base_diameter / 2.0,
        base_diameter / 2.0,
        height,
    )
    port2_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        bim2fem.ifcplus.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * base_diameter,
        )

    return element
