# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Built Element Creation Module

Checklist for built element creation:
- Add Material/MaterialLayerSet/MaterialProfileSet
- Add Type
- Declare Type on Project
- Assign Material to Type
- Add Element
- Assign Type to Element
- Add MaterialLayerSetUsage/MaterialProfileSetUsage
- Assign MaterialLayerSetUsage/MaterialProfileSetUsage to Wall
- Add Representation
- Assign Representation to Element
- Place Element in Spatial Container
- Edit Element Placement

"""

import ifcopenshell
import ifcopenshell.api.geometry
from typing import Literal
import numpy as np
import ifcopenshell.api.type
import ifcopenshell.api.material
import ifcplus.api.element_type
import ifcopenshell
import ifcopenshell.api.geometry
import ifcplus.api.placement
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcplus.api.geometry
import ifcplus.api.material
import ifcopenshell.util.representation
from typing import cast
import ifcplus.util.geometry
import ifcplus.util.project
import ifcopenshell.api.profile


FRAME_MEMBER_CLASS = Literal[
    "IfcBeam",
    "IfcColumn",
    "IfcMember",
]


def create_linear_frame_member(
    frame_member_class: FRAME_MEMBER_CLASS,
    start_point: tuple[float, float, float],
    end_point: tuple[float, float, float],
    orientation_point: tuple[float, float, float],
    profile: ifcopenshell.entity_instance,
    material: ifcopenshell.entity_instance,
    frame_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a linear, prismatic, and homogenous IfcBeam or IfcColumn or IfcMember with
    IfcMaterialProfileSetUsage.

    The start and end points define the endpoints of the frame member and the
    direction of the z-axis of the Object coordinate systm.

    The orientation point defines a plane (with the start and end points) containing
    the z-axis and y-axis of the Object coordinate system.

    The y-axis usually corresponds to the axis of weak bending for the cross-section,
    whereas the x-axis usually corresponds to the axis of strong bending.

    The ObjectPlacement z-axis is the longitudinal axis in the direction of intial
    tangency.

    The ObjectPlacement y-axis is the vertical orientation of the cross-section.
    The
    ObjectPlacement xy plane contains the cross-section.

    The orientation point defines a plane containing the ObjectPlacement z and
    y-axes and the start and end points.
    """

    ifc4_file = profile.file

    material_profile_set = (
        ifcplus.api.material.add_material_profile_set_with_single_material_profile(
            material=material,
            profile=profile,
            name=None,
            check_for_duplicate=True,
        )
    )

    if frame_member_class == "IfcBeam":
        element_type_class = "IfcBeamType"
    elif frame_member_class == "IfcColumn":
        element_type_class = "IfcColumnType"
    else:
        element_type_class = "IfcMemberType"

    element_type = ifcplus.api.element_type.add_element_type_for_material_profile_set(
        ifc_class=element_type_class,
        material_profile_set=material_profile_set,
        name=material_profile_set.Name,
        check_for_duplicate=True,
    )

    if frame_member is None:
        frame_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class=frame_member_class,
            name=name,
            predefined_type="NOTDEFINED",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[frame_member],
        relating_type=element_type,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[frame_member],
        type="IfcMaterialProfileSetUsage",
        material=None,  # inferred from assigned IfcElementType
    )

    z_axis = tuple((np.array(end_point) - np.array(start_point)).tolist())

    vector_from_start_point_to_orientation_point = tuple(
        (np.array(orientation_point) - np.array(start_point)).tolist()
    )

    x_axis = tuple(
        np.cross(
            vector_from_start_point_to_orientation_point,
            z_axis,
        ).tolist()
    )

    frame_member_length = float(
        np.linalg.norm(np.array(end_point) - np.array(start_point))
    )

    extruded_area_solid = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=profile,
        depth=frame_member_length,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[extruded_area_solid]),
        ),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=frame_member,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[frame_member],
            relating_structure=parent,
        )

    ifcplus.api.placement.edit_object_placement(
        product=frame_member,
        repositioned_origin=start_point,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return frame_member


def create_opening_element(
    voided_element: ifcopenshell.entity_instance,
    profile: ifcopenshell.entity_instance,
    depth: float,  # Extrusion depth in the local z direction of the opening element
    origin_relative_to_voided_element: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis_relative_to_voided_element: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis_relative_to_voided_element: tuple[float, float, float] = (1.0, 0.0, 0.0),
):

    ifc4_file = voided_element.file

    opening_element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcOpeningElement",
        name=None,
        predefined_type=None,
    )

    representation_item = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=profile,
        depth=depth,
    )

    representation_type = ifcopenshell.util.representation.guess_type(
        items=[representation_item]
    )

    shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=opening_element,
        representation=shape_model,
    )

    rel_voids_element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcRelVoidsElement",
    )
    rel_voids_element.RelatingBuildingElement = voided_element
    rel_voids_element.RelatedOpeningElement = opening_element

    ifcplus.api.placement.edit_object_placement(
        product=opening_element,
        place_object_relative_to_parent=False,
    )
    opening_element.ObjectPlacement.PlacementRelTo = voided_element.ObjectPlacement
    opening_element.ObjectPlacement.RelativePlacement = (
        ifc4_file.createIfcAxis2Placement3D(
            ifc4_file.createIfcCartesianPoint(origin_relative_to_voided_element),
            ifc4_file.createIfcDirection(z_axis_relative_to_voided_element),
            ifc4_file.createIfcDirection(x_axis_relative_to_voided_element),
        )
    )

    return opening_element


def create_linear_wall(
    start_point_2d: tuple[float, float],
    end_point_2d: tuple[float, float],
    elevation: float,
    height: float,
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    wall: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
):
    """Add straight IfcWall with IfcMaterialLayerSetUsage based on two points in
    XY space."""

    ifc4_file = materials[0].file

    material_layer_set = ifcplus.api.material.add_material_layer_set(
        materials=materials,
        thicknesses=thicknesses,
        name=None,
        check_for_duplicate=True,
    )

    wall_type = ifcplus.api.element_type.add_element_type_for_material_layer_set(
        ifc_class="IfcWallType",
        material_layer_set=material_layer_set,
        name=material_layer_set.LayerSetName,
        check_for_duplicate=True,
    )

    if wall is None:
        wall = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcWall",
            name=name,
            predefined_type="NOTDEFINED",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[wall],
        relating_type=wall_type,
    )

    total_thickness = 0.0
    for material_layer in material_layer_set.MaterialLayers:
        total_thickness += material_layer.LayerThickness

    rel_associates_material = ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[wall],
        type="IfcMaterialLayerSetUsage",
        material=None,  # inferred from assigned IfcElementType
    )
    material_layer_set_usage = cast(
        ifcopenshell.entity_instance, rel_associates_material
    ).RelatingMaterial
    material_layer_set_usage.OffsetFromReferenceLine = -total_thickness / 2

    start_point_3d = (start_point_2d[0], start_point_2d[1], elevation)
    end_point_3d = (end_point_2d[0], end_point_2d[1], elevation)
    vector_from_start_point_to_end_point = np.array(end_point_3d) - np.array(
        start_point_3d
    )
    length = float(np.linalg.norm(vector_from_start_point_to_end_point))

    arbitrary_closed_profile_def = ifcopenshell.api.profile.add_arbitrary_profile(
        file=ifc4_file,
        profile=[
            (0.0, 0.0 - total_thickness / 2),
            (0.0 + length, 0.0 - total_thickness / 2),
            (0.0 + length, 0.0 + total_thickness - total_thickness / 2),
            (0.0 + length - length, 0.0 + total_thickness - total_thickness / 2),
            (0.0, 0.0 - total_thickness / 2),
        ],
        name=None,
    )

    extruded_area_solid = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=arbitrary_closed_profile_def,
        depth=height,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[extruded_area_solid]),
        ),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=wall,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[wall],
            relating_structure=parent,
        )

    ifcplus.api.placement.edit_object_placement(
        product=wall,
        repositioned_origin=start_point_3d,
        repositioned_x_axis=tuple(vector_from_start_point_to_end_point.tolist()),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return wall


def create_curved_wall(
    point_of_curvature_2d: tuple[float, float],
    point_on_center_of_curvature_side_2d: tuple[float, float],
    point_of_tangency_2d: tuple[float, float],
    radius_of_curvature: float,
    elevation: float,
    height: float,
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    wall: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
):
    """Add curved IfcWall with IfcMaterialLayerSetUsage based on a horizontal curve."""

    ifc4_file = materials[0].file

    numeric_scale = ifcplus.util.project.get_numeric_scale_of_project(
        ifc4_file=ifc4_file,
    )

    material_layer_set = ifcplus.api.material.add_material_layer_set(
        materials=materials,
        thicknesses=thicknesses,
        name=None,
        check_for_duplicate=True,
    )

    wall_type = ifcplus.api.element_type.add_element_type_for_material_layer_set(
        ifc_class="IfcWallType",
        material_layer_set=material_layer_set,
        name=material_layer_set.LayerSetName,
        check_for_duplicate=True,
    )

    if wall is None:
        wall = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcWall",
            name=name,
            predefined_type="NOTDEFINED",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[wall],
        relating_type=wall_type,
    )

    total_thickness = 0.0
    for material_layer in material_layer_set.MaterialLayers:
        total_thickness += material_layer.LayerThickness

    rel_associates_material = ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[wall],
        type="IfcMaterialLayerSetUsage",
        material=None,  # inferred from assigned IfcElementType
    )
    material_layer_set_usage = cast(
        ifcopenshell.entity_instance, rel_associates_material
    ).RelatingMaterial
    material_layer_set_usage.OffsetFromReferenceLine = -total_thickness / 2

    radius_of_curvature_for_middle_curve = radius_of_curvature
    point_of_curvature_3d_for_middle_curve = (
        point_of_curvature_2d[0],
        point_of_curvature_2d[1],
        elevation,
    )
    point_of_tangency_3d_for_middle_curve = (
        point_of_tangency_2d[0],
        point_of_tangency_2d[1],
        elevation,
    )
    point_on_center_of_curvature_side_3d_for_middle_curve = (
        point_on_center_of_curvature_side_2d[0],
        point_on_center_of_curvature_side_2d[1],
        elevation,
    )

    middle_horizontal_curve = ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_of_curvature=point_of_curvature_3d_for_middle_curve,
        point_on_center_of_curvature_side=point_on_center_of_curvature_side_3d_for_middle_curve,
        point_of_tangency=point_of_tangency_3d_for_middle_curve,
        radius_of_curvature=radius_of_curvature_for_middle_curve,
    )

    point_of_center_of_curvature_3d_for_all_curves = (
        middle_horizontal_curve.center_of_curvature
    )

    unit_vector_from_CC_to_PC = (
        ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=point_of_center_of_curvature_3d_for_all_curves,
            p2=point_of_curvature_3d_for_middle_curve,
        )
    )
    unit_vector_from_CC_to_PT = (
        ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=point_of_center_of_curvature_3d_for_all_curves,
            p2=point_of_tangency_3d_for_middle_curve,
        )
    )

    radius_of_curvature_for_inner_curve = (
        radius_of_curvature_for_middle_curve - total_thickness / 2.0
    )
    point_of_curvature_3d_for_inner_curve = tuple(
        (
            np.array(point_of_center_of_curvature_3d_for_all_curves)
            + np.array(unit_vector_from_CC_to_PC) * radius_of_curvature_for_inner_curve
        ).tolist()
    )
    point_of_tangency_3d_for_inner_curve = tuple(
        (
            np.array(point_of_center_of_curvature_3d_for_all_curves)
            + np.array(unit_vector_from_CC_to_PT) * radius_of_curvature_for_inner_curve
        ).tolist()
    )
    inner_horizontal_curve = ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_of_curvature=point_of_curvature_3d_for_inner_curve,
        point_on_center_of_curvature_side=point_of_center_of_curvature_3d_for_all_curves,
        point_of_tangency=point_of_tangency_3d_for_inner_curve,
        radius_of_curvature=radius_of_curvature_for_inner_curve,
    )

    radius_of_curvature_for_outer_curve = (
        radius_of_curvature_for_middle_curve + total_thickness / 2.0
    )
    point_of_curvature_3d_for_outer_curve = tuple(
        (
            np.array(point_of_center_of_curvature_3d_for_all_curves)
            + np.array(unit_vector_from_CC_to_PC) * radius_of_curvature_for_outer_curve
        ).tolist()
    )
    point_of_tangency_3d_for_outer_curve = tuple(
        (
            np.array(point_of_center_of_curvature_3d_for_all_curves)
            + np.array(unit_vector_from_CC_to_PT) * radius_of_curvature_for_outer_curve
        ).tolist()
    )
    outer_horizontal_curve = ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_of_curvature=point_of_curvature_3d_for_outer_curve,
        point_on_center_of_curvature_side=point_of_center_of_curvature_3d_for_all_curves,
        point_of_tangency=point_of_tangency_3d_for_outer_curve,
        radius_of_curvature=radius_of_curvature_for_outer_curve,
    )

    points_list_3d = [
        inner_horizontal_curve.point_of_curvature,
        outer_horizontal_curve.point_of_curvature,
        outer_horizontal_curve.point_at_midpoint_of_curve,
        outer_horizontal_curve.point_of_tangency,
        inner_horizontal_curve.point_of_tangency,
        inner_horizontal_curve.point_at_midpoint_of_curve,
    ]

    points_list_2d = []
    for point_3d in points_list_3d:
        point_3d_relative_to_PC_of_middle_curve = tuple(
            np.round(
                (
                    np.array(point_3d)
                    - np.array(middle_horizontal_curve.point_of_curvature)
                ),
                numeric_scale,
            ).tolist()
        )
        points_list_2d.append(point_3d_relative_to_PC_of_middle_curve[0:2])

    cartesian_point_list = ifc4_file.create_entity(
        type="IfcCartesianPointList2D",
        CoordList=points_list_2d,
    )

    indexed_polycurve = ifc4_file.create_entity(
        type="IfcIndexedPolyCurve",
        Points=cartesian_point_list,
        Segments=[
            ifc4_file.create_entity("IfcLineIndex", [1, 2]),
            ifc4_file.create_entity("IfcArcIndex", [2, 3, 4]),
            ifc4_file.create_entity("IfcLineIndex", [4, 5]),
            ifc4_file.create_entity("IfcArcIndex", [5, 6, 1]),
        ],
        SelfIntersect=False,
    )

    arbitrary_closed_profile_def = ifc4_file.create_entity(
        type="IfcArbitraryClosedProfileDef",
        ProfileType="AREA",
        ProfileName=name,
        OuterCurve=indexed_polycurve,
    )

    extruded_area_solid = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=arbitrary_closed_profile_def,
        depth=height,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[extruded_area_solid]),
        ),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=wall,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[wall],
            relating_structure=parent,
        )

    unit_vector_from_PC_to_PI = (
        ifcplus.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=middle_horizontal_curve.point_of_curvature,
            p2=middle_horizontal_curve.point_of_intersection,
        )
    )
    ifcplus.api.placement.edit_object_placement(
        product=wall,
        repositioned_origin=middle_horizontal_curve.point_of_curvature,
        repositioned_x_axis=unit_vector_from_PC_to_PI,
        repositioned_z_axis=(0.0, 0.0, 1.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return wall


def create_slab(
    profile: ifcopenshell.entity_instance,
    point_at_placement_of_slab_profile: tuple[float, float, float],
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    slab: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
):

    ifc4_file = materials[0].file

    material_layer_set = ifcplus.api.material.add_material_layer_set(
        materials=materials,
        thicknesses=thicknesses,
        name=None,
        check_for_duplicate=True,
    )

    slab_type = ifcplus.api.element_type.add_element_type_for_material_layer_set(
        ifc_class="IfcSlabType",
        material_layer_set=material_layer_set,
        name=material_layer_set.LayerSetName,
        check_for_duplicate=True,
    )

    if slab is None:
        slab = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSlab",
            name=name,
            predefined_type="NOTDEFINED",
        )

    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[slab],
        relating_type=slab_type,
    )

    total_thickness = 0.0
    for material_layer in material_layer_set.MaterialLayers:
        total_thickness += material_layer.LayerThickness

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[slab],
        type="IfcMaterialLayerSetUsage",
        material=None,  # inferred from assigned IfcElementType
    )

    extruded_area_solid = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        swept_area=profile,
        depth=total_thickness,
    )

    shape_representation = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[extruded_area_solid]),
        ),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=slab,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[slab],
            relating_structure=parent,
        )

    ifcplus.api.placement.edit_object_placement(
        product=slab,
        repositioned_origin=point_at_placement_of_slab_profile,
        repositioned_x_axis=(1.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return slab
