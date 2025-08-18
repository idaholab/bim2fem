# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell.api.pset
import ifcopenshell.api.material
import pickle
import os
import inlbim.api.style
from inlbim import REGION, RGB_STEEL, RGB_CONCRETE


def add_material_with_structural_properties(
    ifc4_file: ifcopenshell.file,
    name: str | None = None,
    category: str | None = None,
    mass_density: float = 7849.0,  # kg/m^3
    young_modulus: float = 210000000000.0,  # N/m^2
    poisson_ratio: float = 0.3,
    thermal_expansion_coefficient: float = 1.17e-05,  # 1 / C
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Create a IfcMaterial with common and mechanical property sets"""

    if check_for_duplicate and name and category:
        old_materials = ifc4_file.by_type(type="IfcMaterial", include_subtypes=False)
        for old_material in old_materials:
            names_match = str(old_material.Name).upper() == name.upper()
            categories_match = str(old_material.Category).upper() == category.upper()
            if names_match and categories_match:
                return old_material

    generic_material = ifcopenshell.api.material.add_material(
        file=ifc4_file,
        name=name,
        category=category,
    )

    mat_common_pset = ifcopenshell.api.pset.add_pset(
        file=ifc4_file,
        product=generic_material,
        name="Pset_MaterialCommon",
    )
    ifcopenshell.api.pset.edit_pset(
        file=ifc4_file,
        pset=mat_common_pset,
        properties={"MassDensity": mass_density},
    )

    mat_mech_pset = ifcopenshell.api.pset.add_pset(
        file=ifc4_file,
        product=generic_material,
        name="Pset_MaterialMechanical",
    )
    ifcopenshell.api.pset.edit_pset(
        file=ifc4_file,
        pset=mat_mech_pset,
        properties={
            "YoungModulus": young_modulus,
            "PoissonRatio": poisson_ratio,
            "ThermalExpansionCoefficient": thermal_expansion_coefficient,
        },
    )

    return generic_material


def add_material_from_standard_library(
    ifc4_file: ifcopenshell.file,
    region: REGION,
    material_name: str,  # S355, C30/37
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance | None:
    """Load IfcMaterial from library"""

    if check_for_duplicate:
        old_materials = ifc4_file.by_type(type="IfcMaterial", include_subtypes=False)
        for old_material in old_materials:
            names_match = str(old_material.Name).upper() == material_name.upper()
            if names_match:
                return old_material

    if region == "Europe":
        material_library = "Europe"
    elif region == "UnitedStates":
        material_library = "UnitedStates"
    else:
        return None

    material_library_file_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "property_libraries",
        "materials",
        f"MaterialLibrary{material_library}.pkl",
    )

    with open(material_library_file_path, "rb") as file:
        material_library_data = pickle.load(file)

    matching_material_data_dictionary = None
    matching_material_category = None
    for standard_key, standard_data in material_library_data.items():
        for mat_type_key, mat_type_data in standard_data.items():
            matching_material_data_dictionary = mat_type_data.get(material_name)
            if matching_material_data_dictionary:
                matching_material_category = mat_type_key
                break
        if matching_material_data_dictionary:
            break
    if not isinstance(matching_material_data_dictionary, dict):
        return None

    material_from_library = add_material_with_structural_properties(
        ifc4_file=ifc4_file,
        name=material_name,
        category=matching_material_category,
        mass_density=matching_material_data_dictionary["MassDensity"],
        young_modulus=matching_material_data_dictionary["YoungModulus"],
        poisson_ratio=matching_material_data_dictionary["PoissonRatio"],
        thermal_expansion_coefficient=matching_material_data_dictionary[
            "ThermalExpansionCoefficient"
        ],
        check_for_duplicate=True,
    )

    if matching_material_category in ["steel", "coldformed", "rebar", "tendon"]:
        mat_steel_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=material_from_library,
            name="Pset_MaterialSteel",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=mat_steel_pset,
            properties={
                "YieldStress": matching_material_data_dictionary["YieldStress"],
                "UltimateStress": matching_material_data_dictionary["UltimateStress"],
            },
        )
        inlbim.api.style.assign_color_to_material(
            material=material_from_library,
            rgb_triplet=RGB_STEEL,
        )

    if matching_material_category in ["concrete"]:
        mat_concrete_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=material_from_library,
            name="Pset_MaterialConcrete",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=mat_concrete_pset,
            properties={
                "CompressiveStrength": matching_material_data_dictionary[
                    "CompressiveStrength"
                ],
            },
        )
        inlbim.api.style.assign_color_to_material(
            material=material_from_library,
            rgb_triplet=RGB_CONCRETE,
        )

    return material_from_library


def add_material_profile_set_with_single_material_profile(
    material: ifcopenshell.entity_instance,
    profile: ifcopenshell.entity_instance,
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Crean an IfcMaterialProfileSet for with a single IfcMaterialProfile. Suitable
    for prismatic and homogenous frame members (i.e., IfcBeam, IfcColumn, and
    IfcMember)"""

    assert material.is_a("IfcMaterial")
    assert profile.is_a("IfcProfileDef")

    ifc4_file = material.file

    if check_for_duplicate:
        for old_material_profile_set in ifc4_file.by_type(
            type="IfcMaterialProfileSet", include_subtypes=False
        ):
            old_profile = old_material_profile_set.MaterialProfiles[0].Profile
            old_material = old_material_profile_set.MaterialProfiles[0].Material
            if old_material == material and old_profile == profile:
                return old_material_profile_set

    material_profile_set = ifcopenshell.api.material.add_material_set(
        file=ifc4_file,
        name=name if name else f"{material.Name} {profile.ProfileName}",
        set_type="IfcMaterialProfileSet",
    )

    ifcopenshell.api.material.add_profile(
        file=ifc4_file,
        profile_set=material_profile_set,
        material=material,
        profile=profile,
    )

    return material_profile_set


def add_material_layer_set(
    materials: list[ifcopenshell.entity_instance],
    thicknesses: list[float],
    name: str | None = None,
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance:
    """Add an IfcMaterialLayerSet composed of various materials and corresponding
    thicknesses."""

    ifc4_file = materials[0].file

    if check_for_duplicate:
        for old_material_layer_set in ifc4_file.by_type(
            type="IfcMaterialLayerSet", include_subtypes=False
        ):
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
            return old_material_layer_set

    material_layer_set = ifcopenshell.api.material.add_material_set(
        file=ifc4_file,
        name=(
            name
            if name
            else " | ".join([material.Name for material in materials])
            + f" {sum(thicknesses)}"
        ),
        set_type="IfcMaterialLayerSet",
    )

    for material, thickness in zip(materials, thicknesses):
        layer = ifcopenshell.api.material.add_layer(
            file=ifc4_file,
            layer_set=material_layer_set,
            material=material,
        )
        ifcopenshell.api.material.edit_layer(
            file=ifc4_file,
            layer=layer,
            attributes={"LayerThickness": thickness},
        )

    return material_layer_set
