# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.util.element
import ifcopenshell.api.project


def add_element_type_for_material_layer_set(
    ifc_class: str,  # IfcWallType, IfcSlabType, IfcPlateType
    material_layer_set: ifcopenshell.entity_instance,
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Add an IfcElementType based on an IfcMaterialLayerSet. This function also
    automates material assignment and project declaration for the type."""

    ifc4_file = material_layer_set.file

    if check_for_duplicate:
        old_element_types = ifc4_file.by_type(
            type=ifc_class,
            include_subtypes=False,
        )
        for old_element_type in old_element_types:
            old_material = ifcopenshell.util.element.get_material(
                element=old_element_type,
                should_skip_usage=True,
            )
            if not isinstance(old_material, ifcopenshell.entity_instance):
                continue
            if not old_material.is_a("IfcMaterialLayerSet"):
                continue
            old_material_layer_set = old_material
            if material_layer_set == old_material_layer_set:
                return old_element_type

    element_type = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class=ifc_class,
        name=name,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[element_type],
        material=material_layer_set,
    )

    project = ifc4_file.by_type(
        type="IfcProject",
        include_subtypes=False,
    )[0]

    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[element_type],
        relating_context=project,
    )

    return element_type


def add_element_type_for_material_profile_set(
    ifc_class: str,  # IfcBeamType, IfcColumnType, IfcMemberType
    material_profile_set: ifcopenshell.entity_instance,
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Add an IfcElementType based on an IfcMaterialProfileSet. This function also
    automates material assignment and project declaration for the type."""

    ifc4_file = material_profile_set.file

    if check_for_duplicate:
        old_element_types = ifc4_file.by_type(
            type=ifc_class,
            include_subtypes=False,
        )
        for old_element_type in old_element_types:
            old_material = ifcopenshell.util.element.get_material(
                element=old_element_type,
                should_skip_usage=True,
            )
            if not isinstance(old_material, ifcopenshell.entity_instance):
                continue
            if not old_material.is_a("IfcMaterialProfileSet"):
                continue
            old_material_profile_set = old_material
            if material_profile_set == old_material_profile_set:
                return old_element_type

    element_type = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class=ifc_class,
        name=name,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[element_type],
        material=material_profile_set,
    )

    project = ifc4_file.by_type(
        type="IfcProject",
        include_subtypes=False,
    )[0]

    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[element_type],
        relating_context=project,
    )

    return element_type
