# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Piping Element Creation Module"""

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
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    point_defining_plane_of_arc_and_center_of_curvature_side: tuple[
        float, float, float
    ],
    radius_of_curvature: float,
    nominal_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Create piping elbow as an IfcPipeFitting."""

    ifc4_file = distribution_system.file

    elbow = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcPipeFitting",
        predefined_type="JUNCTION",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=elbow,
    )

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

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=elbow,
        repositioned_location=horizontal_curve.point_of_curvature,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[elbow],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(0.0, 0.0, 0.0),
        z_axis=(0.0, 0.0, 1.0),
        x_axis=(1.0, 0.0, 0.0),
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
        location=source_port_origin_in_object_coordinates,
        z_axis=source_port_z_axis_in_object_coordinates,
        x_axis=source_port_x_axis_in_object_coordinates,
        distribution_element=elbow,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    return elbow


def create_pipe_segment(
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    outer_diameter: float,
    thickness: float,
    material: ifcopenshell.entity_instance,
    distribution_system: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:
    """Create an IfcPipeSegment."""

    ifc4_file = distribution_system.file

    pipe_segment = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcPipeSegment",
        predefined_type="NOTDEFINED",
    )
    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=pipe_segment,
    )

    outer_radius = outer_diameter / 2.0

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

    bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
        product=pipe_segment,
        repositioned_location=start_point,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
    )

    ifcopenshell.api.system.assign_system(
        file=ifc4_file,
        products=[pipe_segment],
        system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(0.0, 0.0, 0.0),
        z_axis=(0.0, 0.0, 1.0),
        x_axis=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SINK",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    bim2fem.ifcplus.api.system.create_distribution_port(
        location=(0.0, 0.0, length),
        z_axis=(0.0, 0.0, 1.0),
        x_axis=(1.0, 0.0, 0.0),
        distribution_element=pipe_segment,
        flow_direction="SOURCE",
        predefined_type="PIPE",
        distribution_system=distribution_system,
    )

    return pipe_segment
