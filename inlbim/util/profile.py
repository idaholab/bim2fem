# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import pickle
import os
from inlbim import REGION
from collections import Counter
import re
from difflib import SequenceMatcher
import ifcopenshell.util.element


def swap_strings(string_list: list[str], str1: str, str2: str):
    """
    # Example usage
    my_list = ["apple", "banana", "cherry", "date"]
    swap_strings(my_list, "banana", "date")
    print(my_list)  # Output: ['apple', 'date', 'cherry', 'banana']
    """
    try:
        index1 = string_list.index(str1)
        index2 = string_list.index(str2)

        # Swap the strings
        string_list[index1], string_list[index2] = (
            string_list[index2],
            string_list[index1],
        )

    except ValueError as e:
        print(f"Error: {e}")


def clean_string(s: str) -> str:
    # Retain alphanumerics and 'x', remove spaces and special characters
    return re.sub(r"[^A-Za-z0-9x]", "", s).upper()


def shared_char_count(s1: str, s2: str) -> int:
    c1 = Counter(s1)
    c2 = Counter(s2)
    shared = c1 & c2  # Intersection: min count of each common character
    return sum(shared.values())


def best_fuzzy_match(
    strings_matched_to: list[str],
    strings_matching: list[str],
    threshold: float = 0.5,
) -> str | None:

    candidates = {}
    highest_ratio = threshold
    best_match = None
    for string_matched_to in strings_matched_to:
        cleaned_string_matched_to = clean_string(s=string_matched_to)
        for string_matching in strings_matching:
            cleaned_string_matching = clean_string(s=string_matching)
            ratio = SequenceMatcher(
                None, cleaned_string_matched_to, cleaned_string_matching
            ).ratio()
            if ratio >= highest_ratio:
                candidates[string_matching] = ratio
                highest_ratio = ratio
                best_match = string_matching

    tied_candidates = {}
    for s, ratio in candidates.items():
        if ratio == highest_ratio:
            tied_candidates[s] = ratio

    if len(tied_candidates) > 1:

        candidates = {}
        highest_score = 0
        best_match = None
        for string_matched_to in strings_matched_to:
            cleaned_string_matched_to = clean_string(s=string_matched_to)
            for string_matching in tied_candidates.keys():
                cleaned_string_matching = clean_string(s=string_matching)
                score = shared_char_count(
                    s1=cleaned_string_matched_to, s2=cleaned_string_matching
                )
                if score >= highest_score:
                    candidates[string_matching] = score
                    highest_score = score
                    best_match = string_matching

        tied_candidates = {}
        for s, score in candidates.items():
            if score == highest_score:
                tied_candidates[s] = score

        if len(tied_candidates) > 1:
            best_match = None

    return best_match


def get_best_matching_standard_profile_from_element_metadata(
    element: ifcopenshell.entity_instance,
    region: REGION,
    other_standard_profile_names: list[str] = [],
) -> str | None:

    if region == "Europe":
        section_libraries = ["BSShapes2006", "Euro"]
    elif region == "UnitedStates":
        section_libraries = ["AISC14", "SJIJoists"]
    else:
        return None

    strings_that_might_contain_profile_information = []

    if element.Name:
        strings_that_might_contain_profile_information += element.Name.replace(
            " - ", ":"
        ).split(":")

    if element.Description:
        strings_that_might_contain_profile_information += element.Description.replace(
            " - ", ":"
        ).split(":")
    if element.ObjectType:
        strings_that_might_contain_profile_information += element.ObjectType.replace(
            " - ", ":"
        ).split(":")

    element_type = ifcopenshell.util.element.get_type(element=element)
    if element_type:
        material_for_element_type = ifcopenshell.util.element.get_material(
            element=element_type,
        )
        if material_for_element_type:
            if material_for_element_type.is_a("IfcMaterialProfileSet"):
                material_profile = material_for_element_type.MaterialProfiles[0]
                profile = material_profile.Profile
                strings_that_might_contain_profile_information += (
                    profile.ProfileName.replace(" - ", ":").split(":")
                )

    best_matching_standard_profile_name_from_given_list = best_fuzzy_match(
        strings_matched_to=strings_that_might_contain_profile_information,
        strings_matching=other_standard_profile_names,
        threshold=0.90,
    )
    if isinstance(best_matching_standard_profile_name_from_given_list, str):
        return best_matching_standard_profile_name_from_given_list

    best_matching_standard_profile_name_from_library = None
    for section_library in section_libraries:
        section_library_file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "property_libraries",
            "sections",
            f"{section_library}.pkl",
        )
        with open(section_library_file_path, "rb") as file:
            section_library_data = pickle.load(file)

        section_category_labels = list(section_library_data.keys())
        swap_strings(
            string_list=section_category_labels,
            str1="STEEL_TEE",
            str2="STEEL_I_SECTION",
        )
        for section_category_label in section_category_labels:
            section_category_dictionary = section_library_data[section_category_label]
            best_matching_standard_profile_name_from_library = best_fuzzy_match(
                strings_matched_to=strings_that_might_contain_profile_information,
                strings_matching=list(section_category_dictionary.keys()),
                threshold=0.80,
            )
            if best_matching_standard_profile_name_from_library:
                break
        if best_matching_standard_profile_name_from_library:
            break

    return best_matching_standard_profile_name_from_library


def get_local_origin_and_x_axis_of_parameterized_profile_def(
    parameterized_profile_def: ifcopenshell.entity_instance,
) -> tuple[
    tuple[float, float],
    tuple[float, float],
]:

    pos = parameterized_profile_def.Position

    if pos is None:
        local_origin, local_x_axis = (0.0, 0.0), (1.0, 0.0)
        return local_origin, local_x_axis

    local_origin = pos.Location.Coordinates

    if pos.RefDirection is None:
        local_x_axis = (1.0, 0.0)
    else:
        local_x_axis = pos.RefDirection.DirectionRatios

    return local_origin, local_x_axis


def get_large_dimension_of_parameterized_profile_def(
    parameterized_profile_def: ifcopenshell.entity_instance,
) -> float:

    # Default value
    largest_dimension = 0

    # IfcRectangleProfileDef
    if parameterized_profile_def.is_a() == "IfcRectangleProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.XDim,
                parameterized_profile_def.YDim,
            ]
        )

    # IfcRectangleHollowProfileDef
    if parameterized_profile_def.is_a() == "IfcRectangleHollowProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.XDim,
                parameterized_profile_def.YDim,
                parameterized_profile_def.WallThickness,
            ]
        )

    # IfcCircleProfileDef
    if parameterized_profile_def.is_a() == "IfcCircleProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.Radius,
            ]
        )

    # IfcCircleHollowProfileDef
    if parameterized_profile_def.is_a() == "IfcCircleHollowProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.Radius,
                parameterized_profile_def.WallThickness,
            ]
        )

    # IfcIShapeProfileDef
    if parameterized_profile_def.is_a() == "IfcIShapeProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.OverallWidth,
                parameterized_profile_def.OverallDepth,
                parameterized_profile_def.WebThickness,
                parameterized_profile_def.FlangeThickness,
            ]
        )

    # IfcLShapeProfileDef
    if parameterized_profile_def.is_a() == "IfcLShapeProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.Depth,
                parameterized_profile_def.Width,
                parameterized_profile_def.Thickness,
            ]
        )

    # IfcUShapeProfileDef
    if parameterized_profile_def.is_a() == "IfcUShapeProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.Depth,
                parameterized_profile_def.FlangeWidth,
                parameterized_profile_def.WebThickness,
                parameterized_profile_def.FlangeThickness,
            ]
        )

    # IfcTShapeProfileDef
    if parameterized_profile_def.is_a() == "IfcTShapeProfileDef":
        largest_dimension = max(
            [
                parameterized_profile_def.Depth,
                parameterized_profile_def.FlangeWidth,
                parameterized_profile_def.WebThickness,
                parameterized_profile_def.FlangeThickness,
            ]
        )

    return largest_dimension
