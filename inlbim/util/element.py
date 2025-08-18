# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.util.element
from ifcopenshell.guid import _CHARS64_IFC
import string
import os
import json

IFC_GUID_CHARS = set(_CHARS64_IFC)
ASCII_CHARS = set(string.ascii_uppercase + string.ascii_lowercase)


def get_dictionary_of_ifc_classes_mapped_to_elements(
    list_of_elements: list[ifcopenshell.entity_instance],
):
    """Get dictionary of IFC classes mapped to IfcElements from a list of IfcElements"""

    elements_by_class = {}

    for entity in list_of_elements:
        if entity.is_a("IfcElement"):
            ifc_class = entity.is_a()
            if not elements_by_class.get(ifc_class):
                elements_by_class[ifc_class] = []
            elements_by_class[ifc_class].append(entity)

    return elements_by_class


def select_ifc_elements_based_on_tags(
    ifc4_file: ifcopenshell.file,
    tags: list[str],
) -> tuple[list[ifcopenshell.entity_instance], list[ifcopenshell.entity_instance]]:
    """Select IfcElements to preserve based on tags"""

    def is_valid_str(s: str, approved_chars: set) -> bool:
        return all(char in approved_chars for char in s)

    def tag_is_exclusionary(tag: str) -> bool:
        return tag[0] == "-"

    def tag_is_an_ifc_class(tag: str) -> bool:

        if tag_is_exclusionary(tag=tag):
            tag = tag[1:]

        tag_begins_with_ifc = tag[0:3] == "Ifc"
        if not tag_begins_with_ifc:
            return False

        tag_only_contains_alphabet = is_valid_str(s=tag, approved_chars=ASCII_CHARS)
        if not tag_only_contains_alphabet:
            return False

        return True

    def tag_is_an_ifc_guid(tag: str) -> bool:

        if tag_is_exclusionary(tag=tag):
            tag = tag[1:]

        tag_is_22_chars_long = len(tag) == 22
        if not tag_is_22_chars_long:
            return False

        tag_only_contains_ifc_guid_chars = is_valid_str(
            s=tag, approved_chars=IFC_GUID_CHARS
        )
        if not tag_only_contains_ifc_guid_chars:
            return False

        return True

    def one_or_more_keywords_in_string(keywords: list[str], given_string: str) -> bool:
        for keyword in keywords:
            if keyword.lower() in given_string.lower():
                return True
        return False

    all_elements_in_ifc_file = ifc4_file.by_type(
        type="IfcElement", include_subtypes=True
    )

    included_classes = []
    included_guids = []
    included_keywords = []
    excluded_classes = []
    excluded_guids = []
    excluded_keywords = []

    for tag in tags:

        if tag_is_an_ifc_class(tag=tag):
            if tag_is_exclusionary(tag=tag):
                excluded_classes.append(tag[1:])
            else:
                included_classes.append(tag)

        elif tag_is_an_ifc_guid(tag=tag):
            if tag_is_exclusionary(tag=tag):
                excluded_guids.append(tag[1:])
            else:
                included_guids.append(tag)

        else:
            if tag_is_exclusionary(tag=tag):
                excluded_keywords.append(tag[1:])
            else:
                included_keywords.append(tag)

    selected_elements = []
    unselected_elements = []
    for element in all_elements_in_ifc_file:

        if element.is_a() in excluded_classes:
            unselected_elements.append(element)
            continue
        if element.GlobalId in excluded_guids:
            unselected_elements.append(element)
            continue
        if one_or_more_keywords_in_string(
            keywords=excluded_keywords,
            given_string=element.to_string(),
        ):
            unselected_elements.append(element)
            continue

        element_type = ifcopenshell.util.element.get_type(element=element)
        if element_type:
            if element_type.is_a() in excluded_classes:
                unselected_elements.append(element)
                continue
            if element_type.GlobalId in excluded_guids:
                unselected_elements.append(element)
                continue
            if one_or_more_keywords_in_string(
                keywords=excluded_keywords,
                given_string=element_type.to_string(),
            ):
                unselected_elements.append(element)
                continue

        containing_structure = ifcopenshell.util.element.get_container(element=element)
        if containing_structure:
            if containing_structure.is_a() in excluded_classes:
                unselected_elements.append(element)
                continue
            if containing_structure.GlobalId in excluded_guids:
                unselected_elements.append(element)
                continue
            if one_or_more_keywords_in_string(
                keywords=excluded_keywords,
                given_string=containing_structure.to_string(),
            ):
                unselected_elements.append(element)
                continue

        if element.is_a() in included_classes:
            selected_elements.append(element)
            continue
        if element.GlobalId in included_guids:
            selected_elements.append(element)
            continue
        if one_or_more_keywords_in_string(
            keywords=included_keywords,
            given_string=element.to_string(),
        ):
            selected_elements.append(element)
            continue

        if element_type:
            if element_type.is_a() in included_classes:
                selected_elements.append(element)
                continue
            if element_type.GlobalId in included_guids:
                selected_elements.append(element)
                continue
            if one_or_more_keywords_in_string(
                keywords=included_keywords,
                given_string=element_type.to_string(),
            ):
                selected_elements.append(element)
                continue

        if containing_structure:
            if containing_structure.is_a() in included_classes:
                selected_elements.append(element)
                continue
            if containing_structure.GlobalId in included_guids:
                selected_elements.append(element)
                continue
            if one_or_more_keywords_in_string(
                keywords=included_keywords,
                given_string=containing_structure.to_string(),
            ):
                selected_elements.append(element)
                continue

        unselected_elements.append(element)

    n = len(selected_elements)
    x = len(unselected_elements)
    total = len(all_elements_in_ifc_file)

    total_number_of_elements_is_conserved = n + x == total
    if not total_number_of_elements_is_conserved:
        exit(
            "Sum of selected + unselected IfcElements is not equal to total IfcElements"
        )

    return selected_elements, unselected_elements


def get_list_of_all_IFC4_element_classes():

    def parse_json_file(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        return data

    # Get IFC input filename
    json_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "schema",
            "IfcElement_IFC4.json",
        )
    )

    element_data = parse_json_file(json_fname)

    return list(element_data.keys())


def get_list_of_all_IFC4_spatial_element_classes():

    def parse_json_file(file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        return data

    # Get IFC input filename
    json_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "schema",
            "IfcSpatialElement_IFC4.json",
        )
    )

    element_data = parse_json_file(json_fname)

    return list(element_data.keys())
