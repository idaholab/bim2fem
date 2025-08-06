# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.util.element
import inlbim.api.material
from typing import Literal


BEAM_OR_COLUMN_OR_MEMBER_TYPE_CLASS = Literal[
    "IfcBeamType",
    "IfcColumnType",
    "IfcMemberType",
]

SLAB_OR_WALL_PLATE_TYPE_CLASS = Literal[
    "IfcSlabType",
    "IfcWallType",
    "IfcPlateType",
]


def add_beam_or_column_or_member_type(
    ifc_class: BEAM_OR_COLUMN_OR_MEMBER_TYPE_CLASS,
    material: ifcopenshell.entity_instance,
    profile: ifcopenshell.entity_instance,
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Add an IfcBeamType, IfcColumnType, or IfcMemberType that is prismatic and
    homogeneous."""

    ifc4_file = material.file

    if check_for_duplicate:
        for old_type in ifc4_file.by_type(type=ifc_class, include_subtypes=False):
            old_material_profile_set = ifcopenshell.util.element.get_material(
                element=old_type, should_skip_usage=True
            )
            assert isinstance(old_material_profile_set, ifcopenshell.entity_instance)
            old_profile = old_material_profile_set.MaterialProfiles[0].Profile
            old_material = old_material_profile_set.MaterialProfiles[0].Material
            if old_material == material and old_profile == profile:
                return old_type

    beam_or_column_or_element_type = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class=ifc_class,
        name=name if name else f"{material.Name} {profile.ProfileName}",
    )

    material_profile_set = (
        inlbim.api.material.add_material_profile_set_with_single_material_profile(
            material=material,
            profile=profile,
            name=beam_or_column_or_element_type.Name,
            check_for_duplicate=check_for_duplicate,
        )
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[beam_or_column_or_element_type],
        material=material_profile_set,
    )

    return beam_or_column_or_element_type


def add_slab_or_wall_or_plate_element_type(
    ifc_class: SLAB_OR_WALL_PLATE_TYPE_CLASS,
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Add an IfcWallType or IfcSlabType or IfcPlateType composed of various materials and corresponding thicknesses."""

    materials_and_thicknesses_are_one_to_one = len(materials) == len(thicknesses)
    assert materials_and_thicknesses_are_one_to_one

    ifc4_file = materials[0].file

    if check_for_duplicate:
        for old_type in ifc4_file.by_type(type=ifc_class, include_subtypes=False):
            old_material_layer_set = ifcopenshell.util.element.get_material(
                element=old_type, should_skip_usage=True
            )
            assert isinstance(old_material_layer_set, ifcopenshell.entity_instance)
            old_materials = []
            old_thicknesses = []
            for old_material_layer in old_material_layer_set.MaterialLayers:
                old_materials.append(old_material_layer.Material)
                old_thicknesses.append(old_material_layer.LayerThickness)
            if len(old_materials) != len(materials):
                break
            if len(old_thicknesses) != len(thicknesses):
                break
            for old_material, material in zip(old_materials, materials):
                if old_material != material:
                    break
            for old_thickness, thickness in zip(old_thicknesses, thicknesses):
                if old_thickness != thickness:
                    break
            return old_type

    wall_or_slab_type = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class=ifc_class,
        name=(
            name
            if name
            else " | ".join([material.Name for material in materials])
            + f" {sum(thicknesses)}"
        ),
    )

    material_layer_set = inlbim.api.material.add_material_layer_set(
        materials=materials,
        thicknesses=thicknesses,
        name=wall_or_slab_type.Name,
        check_for_duplicate=check_for_duplicate,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[wall_or_slab_type],
        material=material_layer_set,
    )

    return wall_or_slab_type


def add_element_type(
    ifc4_file: ifcopenshell.file,
    ifc_class: str,
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:

    if check_for_duplicate:
        for old_type in ifc4_file.by_type(type=ifc_class, include_subtypes=False):
            if old_type.Name == name:
                return old_type

    element_type = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class=ifc_class,
        name=name,
    )

    assert element_type.is_a("IfcElementType")

    return element_type
