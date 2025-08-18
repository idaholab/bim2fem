# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import os
import pickle
from inlbim.util.profile import best_fuzzy_match
from inlbim import REGION
import ifcopenshell.util.element


def sum_material_layer_thicknesses(
    material_layer_set: ifcopenshell.entity_instance,
) -> float:
    """Sum MaterialLayer thicknesses of MaterialLayerSet"""
    thicknesses = []
    for material_layer in material_layer_set.MaterialLayers:
        thicknesses.append(material_layer.LayerThickness)
    return sum(thicknesses)


def get_best_matching_standard_material_from_element_metadata(
    element: ifcopenshell.entity_instance,
    region: REGION,
    other_material_names: list[str] = [],
) -> str | None:

    if region == "Europe":
        material_library = "Europe"
    elif region == "UnitedStates":
        material_library = "UnitedStates"
    else:
        return None

    strings_that_might_contain_material_information = []

    # if product.Name:
    #     # strings_that_might_contain_material_information.append(product.Name)
    #     strings_that_might_contain_material_information += re.split(
    #         "[:]+", product.Name
    #     )
    # if product.Description:
    #     # strings_that_might_contain_material_information.append(product.Description)
    #     strings_that_might_contain_material_information += re.split(
    #         "[:]+", product.Description
    #     )
    # if product.ObjectType:
    #     # strings_that_might_contain_material_information.append(product.ObjectType)
    #     strings_that_might_contain_material_information += re.split(
    #         "[:]+", product.ObjectType
    #     )

    psets = ifcopenshell.util.element.get_psets(element=element, psets_only=True)
    for _, pset_data in psets.items():
        for property_name, property_value in pset_data.items():
            if "MAT" in property_name.upper():
                strings_that_might_contain_material_information += (
                    property_value.replace(" - ", ":").split(":")
                )

    materials_in_file_for_product = ifcopenshell.util.element.get_materials(
        element=element
    )
    for material_in_file_for_product in materials_in_file_for_product:
        if not material_in_file_for_product.is_a("IfcMaterial"):
            continue
        if not material_in_file_for_product.Name:
            continue
        strings_that_might_contain_material_information += (
            material_in_file_for_product.Name.replace(" - ", ":").split(":")
        )

    best_matching_standard_material_name_from_given_list = best_fuzzy_match(
        strings_matched_to=strings_that_might_contain_material_information,
        strings_matching=other_material_names,
        threshold=0.80,
    )
    if isinstance(best_matching_standard_material_name_from_given_list, str):
        return best_matching_standard_material_name_from_given_list

    best_matching_standard_material_name_from_library = None
    material_library_file_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "property_libraries",
        "materials",
        f"MaterialLibrary{material_library}.pkl",
    )
    with open(material_library_file_path, "rb") as file:
        material_library_data = pickle.load(file)
    for standard_data_dictionary in material_library_data.values():
        for material_data_dictionary in standard_data_dictionary.values():
            best_matching_standard_material_name_from_library = best_fuzzy_match(
                strings_matched_to=strings_that_might_contain_material_information,
                strings_matching=list(material_data_dictionary.keys()),
                threshold=0.50,
            )
            if best_matching_standard_material_name_from_library:
                break
        if best_matching_standard_material_name_from_library:
            break

    return best_matching_standard_material_name_from_library
