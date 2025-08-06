# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
from typing import Literal
import numpy as np
import ifcopenshell.api.type
import ifcopenshell.api.material
import inlbim.api.element_type
import ifcopenshell.api.project
import ifcopenshell
import ifcopenshell.api.geometry
import inlbim.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import inlbim.api.representation
import inlbim.api.profile

BUILT_ELEMENT_FRAME_MEMBER = Literal["IfcBeam", "IfcColumn", "IfcMember"]


def create_3pt_beam_or_column_or_member(
    ifc_class: BUILT_ELEMENT_FRAME_MEMBER,
    p1: tuple[float, float, float],
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
        inlbim.api.geometry.edit_object_placement(
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
    z_axis = np.array(p2) - np.array(p1)
    y_axis = np.array(p3) - np.array(p1)
    x_axis = np.cross(y_axis, z_axis)

    # Calculate length
    length = float(np.linalg.norm(z_axis))

    # Add and assign representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile_def,
        extrusion_depth=length,
    )
    shape_model = inlbim.api.representation.add_shape_model(
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
    inlbim.api.geometry.edit_object_placement(
        product=beam_or_column_or_member,
        repositioned_origin=p1,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    # Add and assign Type
    if beam_or_column_or_member.is_a("IfcBeam"):
        element_type_class = "IfcBeamType"
    elif beam_or_column_or_member.is_a("IfcColumn"):
        element_type_class = "IfcColumnType"
    else:
        element_type_class = "IfcMemberType"
    element_type = inlbim.api.element_type.add_beam_or_column_or_member_type(
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
    inlbim.api.geometry.edit_object_placement(
        product=opening_element,
        place_object_relative_to_parent=False,
    )
    opening_element.ObjectPlacement.PlacementRelTo = voided_element.ObjectPlacement

    # Add Profile
    profile = inlbim.api.profile.add_arbitrary_profile_with_or_without_voids(
        file=ifc4_file,
        outer_profile=profile_points,
        inner_profiles=[],
        name=None,
    )

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile,
        extrusion_depth=depth,
        repositioned_origin=origin_relative_to_voided_element,
        repositioned_x_axis=x_axis_relative_to_voided_element,
        repositioned_z_axis=z_axis_relative_to_voided_element,
    )
    shape_model = inlbim.api.representation.add_shape_model(
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
    p1: tuple[float, float],  # global XY
    p2: tuple[float, float],  # global XY
    height: float,
    elevation: float,  # global Z
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    inner_openings: list[list[tuple[float, float]]] = [],  # Local XZ
    wall: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    structure_contained_in: ifcopenshell.entity_instance | None = None,
    should_transform_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    # Get IFC4 File
    ifc4_file = materials[0].file

    # Create Wall
    if wall is None:
        wall = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcWall",
            name=name,
            predefined_type="NOTDEFINED",
        )

    # Assign spatial container
    if isinstance(structure_contained_in, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[wall],
            relating_structure=structure_contained_in,
        )
        inlbim.api.geometry.edit_object_placement(
            product=wall,
            place_object_relative_to_parent=True,
        )

    # Calculate thickness
    thickness = sum(thicknesses)

    # Calculate Axes
    z_axis = np.array([0.0, 0.0, 1.0])
    v12 = np.array(p2) - np.array(p1)
    x_axis = (v12[0], v12[1], 0.0)

    # Calculate length
    length = float(np.linalg.norm(x_axis))

    # Add and assign representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=inlbim.api.profile.add_arbitrary_profile_with_or_without_voids(
            file=ifc4_file,
            outer_profile=[
                (0.0, 0.0 - thickness / 2),
                (0.0 + length, 0.0 - thickness / 2),
                (0.0 + length, 0.0 + thickness - thickness / 2),
                (0.0 + length - length, 0.0 + thickness - thickness / 2),
                (0.0, 0.0 - thickness / 2),
            ],
            inner_profiles=[],
            name=None,
        ),
        extrusion_depth=height,
    )
    shape_model = inlbim.api.representation.add_shape_model(
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
        product=wall,
        representation=shape_model,
    )

    # Edit Placement
    inlbim.api.geometry.edit_object_placement(
        product=wall,
        repositioned_origin=(p1[0], p1[1], elevation),
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    # Add and assign Type
    wall_type = inlbim.api.element_type.add_slab_or_wall_or_plate_element_type(
        ifc_class="IfcWallType",
        materials=materials,
        thicknesses=thicknesses,
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[wall],
        relating_type=wall_type,
    )

    # Declare Type on Project
    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[wall_type],
        relating_context=project,
    )

    # Assign MaterialProfileSetUsage (material deduced from assigned element type
    # automatically)
    rel_associates_material = ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[wall],
        type="IfcMaterialLayerSetUsage",
    )
    assert isinstance(rel_associates_material, ifcopenshell.entity_instance)
    material_layer_set_usage = rel_associates_material.RelatingMaterial
    material_layer_set_usage.OffsetFromReferenceLine = -thickness / 2

    # Openings
    for inner_opening_coordinates in inner_openings:
        create_opening_element(
            voided_element=wall,
            profile_points=inner_opening_coordinates,
            depth=thickness,
            origin_relative_to_voided_element=(0.0, thickness / 2, 0.0),
            x_axis_relative_to_voided_element=(1.0, 0.0, 0.0),
            z_axis_relative_to_voided_element=(0.0, -1.0, 0.0),
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
        inlbim.api.geometry.edit_object_placement(
            product=slab,
            place_object_relative_to_parent=True,
        )

    # Calculate thickness
    thickness = sum(thicknesses)

    # Add and assign representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=inlbim.api.profile.add_arbitrary_profile_with_or_without_voids(
            file=ifc4_file,
            outer_profile=outer_profile,
            inner_profiles=[],
            name=None,
        ),
        repositioned_origin=(0.0, 0.0, -thickness / 2),
        extrusion_depth=thickness,
    )
    shape_model = inlbim.api.representation.add_shape_model(
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
    inlbim.api.geometry.edit_object_placement(
        product=slab,
        repositioned_origin=(0.0, 0.0, elevation),
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    # Add and assign Type
    slab_type = inlbim.api.element_type.add_slab_or_wall_or_plate_element_type(
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
