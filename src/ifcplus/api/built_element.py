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
import ifcopenshell.api.project
import ifcopenshell
import ifcopenshell.api.geometry
import ifcplus.api.placement
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcplus.api.geometry
import ifcplus.api.profile
import ifcplus.api.material
import ifcopenshell.util.representation
from typing import cast

BUILT_ELEMENT_FRAME_MEMBER = Literal["IfcBeam", "IfcColumn", "IfcMember"]


def create_3pt_beam_or_column_or_member(
    ifc_class: BUILT_ELEMENT_FRAME_MEMBER,
    start_point_2d: tuple[float, float, float],
    p2: tuple[float, float, float],
    p3: tuple[float, float, float],
    profile_def: ifcopenshell.entity_instance,
    material: ifcopenshell.entity_instance,
    beam_or_column_or_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    structure_contained_in: ifcopenshell.entity_instance | None = None,
    should_transform_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for a linear, prismatic, and homogenous
    IfcBeam|IfcColumn|IfcMember defined by three points (starting location, ending
    loation, and y-axis orientation), and then automatically assign it.
    """

    # Get IFC4 File
    ifc4_file = profile_def.file

    # Create Beam | Column | Member
    if beam_or_column_or_member is None:
        beam_or_column_or_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class=ifc_class,
            name=name,
            predefined_type="NOTDEFINED",
        )

    # Assign spatial container
    if isinstance(structure_contained_in, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[beam_or_column_or_member],
            relating_structure=structure_contained_in,
        )
        ifcplus.api.placement.edit_object_placement(
            product=beam_or_column_or_member,
            place_object_relative_to_parent=True,
        )

    # Check IfcBeam/IfcColumn/IfcMember, IfcProfileDef, and IfcMaterial
    assert (
        beam_or_column_or_member.is_a("IfcBeam")
        or beam_or_column_or_member.is_a("IfcColumn")
        or beam_or_column_or_member.is_a("IfcMember")
    )
    assert profile_def.is_a("IfcProfileDef")
    assert material.is_a("IfcMaterial")

    # Calculate Axes
    z_axis = np.array(p2) - np.array(start_point_2d)
    y_axis = np.array(p3) - np.array(start_point_2d)
    x_axis = np.cross(y_axis, z_axis)

    # Calculate length
    length = float(np.linalg.norm(z_axis))

    # Add and assign representation
    representation_item = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile_def,
        extrusion_depth=length,
    )
    shape_model = ifcplus.api.geometry.add_shape_model(
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
        product=beam_or_column_or_member,
        representation=shape_model,
    )

    # Edit Placement
    ifcplus.api.placement.edit_object_placement(
        product=beam_or_column_or_member,
        repositioned_origin=start_point_2d,
        repositioned_z_axis=tuple(z_axis.tolist()),
        repositioned_x_axis=tuple(x_axis.tolist()),
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    # Add and assign Type
    if beam_or_column_or_member.is_a("IfcBeam"):
        element_type_class = "IfcBeamType"
    elif beam_or_column_or_member.is_a("IfcColumn"):
        element_type_class = "IfcColumnType"
    else:
        element_type_class = "IfcMemberType"
    element_type = ifcplus.api.element_type.add_prismatic_homogenous_linear_elment_type(
        ifc_class=element_type_class,
        material=material,
        profile=profile_def,
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[beam_or_column_or_member],
        relating_type=element_type,
    )

    # Declare Type on Project
    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[element_type],
        relating_context=project,
    )

    # Assign MaterialProfileSetUsage (material deduced from assigned element type
    # automatically)
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[beam_or_column_or_member],
        type="IfcMaterialProfileSetUsage",
    )

    return beam_or_column_or_member


def create_opening_element(
    voided_element: ifcopenshell.entity_instance,
    profile_points: list[tuple[float, float]],  # 2D profile in XY coords of opening
    depth: float,  # Extrusion depth in the local z direction of the opening element
    origin_relative_to_voided_element: tuple[float, float, float] = (0.0, 0.0, 0.0),
    z_axis_relative_to_voided_element: tuple[float, float, float] = (0.0, 0.0, 1.0),
    x_axis_relative_to_voided_element: tuple[float, float, float] = (1.0, 0.0, 0.0),
):

    ifc4_file = voided_element.file

    # Create Element
    opening_element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcOpeningElement",
        name=None,
        predefined_type=None,
    )
    ifcplus.api.placement.edit_object_placement(
        product=opening_element,
        place_object_relative_to_parent=False,
    )
    opening_element.ObjectPlacement.PlacementRelTo = voided_element.ObjectPlacement

    # Add Profile
    profile = ifcplus.api.profile.add_arbitrary_profile_with_or_without_voids(
        file=ifc4_file,
        outer_profile=profile_points,
        inner_profiles=[],
        name=None,
    )

    # Add and Assign Representation
    representation_item = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile,
        extrusion_depth=depth,
        repositioned_origin=origin_relative_to_voided_element,
        repositioned_x_axis=x_axis_relative_to_voided_element,
        repositioned_z_axis=z_axis_relative_to_voided_element,
    )
    shape_model = ifcplus.api.geometry.add_shape_model(
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
        product=opening_element,
        representation=shape_model,
    )

    # Void Relationship
    rel_voids_element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcRelVoidsElement",
    )
    rel_voids_element.RelatingBuildingElement = voided_element
    rel_voids_element.RelatedOpeningElement = opening_element

    return opening_element


def create_2pt_wall(
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

    extruded_area_solid = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=ifcplus.api.profile.add_arbitrary_profile_with_or_without_voids(
            file=ifc4_file,
            outer_profile=[
                (0.0, 0.0 - total_thickness / 2),
                (0.0 + length, 0.0 - total_thickness / 2),
                (0.0 + length, 0.0 + total_thickness - total_thickness / 2),
                (0.0 + length - length, 0.0 + total_thickness - total_thickness / 2),
                (0.0, 0.0 - total_thickness / 2),
            ],
            inner_profiles=[],
            name=None,
        ),
        extrusion_depth=height,
    )

    representation_type = ifcopenshell.util.representation.guess_type(
        items=[extruded_area_solid]
    )

    shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, representation_type),  # SweptSolid
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[extruded_area_solid],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=wall,
        representation=shape_model,
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


def create_npt_slab(
    outer_profile: list[tuple[float, float]],  # global XY
    elevation: float,  # global Z
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    inner_openings: list[list[tuple[float, float]]] = [],  # Local XY
    slab: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    structure_contained_in: ifcopenshell.entity_instance | None = None,
    should_transform_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for an IfcSlab represented by an IfcIndexedPolyCurve
    composed of straight lines defined by 2D points, and then automatically assign the
    reprsentation.
    """

    # Get IFC4 File
    ifc4_file = materials[0].file

    # Create Slab
    if slab is None:
        slab = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSlab",
            name=name,
            predefined_type=None,
        )

    # Assign spatial container
    if isinstance(structure_contained_in, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[slab],
            relating_structure=structure_contained_in,
        )
        ifcplus.api.placement.edit_object_placement(
            product=slab,
            place_object_relative_to_parent=True,
        )

    # Calculate thickness
    thickness = sum(thicknesses)

    # Add and assign representation
    representation_item = ifcplus.api.geometry.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=ifcplus.api.profile.add_arbitrary_profile_with_or_without_voids(
            file=ifc4_file,
            outer_profile=outer_profile,
            inner_profiles=[],
            name=None,
        ),
        repositioned_origin=(0.0, 0.0, -thickness / 2),
        extrusion_depth=thickness,
    )
    shape_model = ifcplus.api.geometry.add_shape_model(
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
        product=slab,
        representation=shape_model,
    )

    # Edit Placement
    ifcplus.api.placement.edit_object_placement(
        product=slab,
        repositioned_origin=(0.0, 0.0, elevation),
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    # Add and assign Type
    slab_type = ifcplus.api.element_type.add_slab_or_wall_or_plate_element_type(
        ifc_class="IfcSlabType",
        materials=materials,
        thicknesses=thicknesses,
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[slab],
        relating_type=slab_type,
    )

    # Declare Type on Project
    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[slab_type],
        relating_context=project,
    )

    # Assign MaterialProfileSetUsage (material deduced from assigned element type
    # automatically)
    rel_associates_material = ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[slab],
        type="IfcMaterialLayerSetUsage",
    )
    assert isinstance(rel_associates_material, ifcopenshell.entity_instance)
    material_layer_set_usage = rel_associates_material.RelatingMaterial
    material_layer_set_usage.OffsetFromReferenceLine = -thickness / 2

    # Openings
    for inner_opening_coordinates in inner_openings:
        create_opening_element(
            voided_element=slab,
            profile_points=inner_opening_coordinates,
            depth=thickness,
            origin_relative_to_voided_element=(0.0, 0.0, -thickness / 2),
            x_axis_relative_to_voided_element=(1.0, 0.0, 0.0),
            z_axis_relative_to_voided_element=(0.0, 0.0, 1.0),
        )

    return slab
