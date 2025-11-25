# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to convert IFC4 file from ReferenceView/DesignTransferView MVDs to
StructuralAnalysisView MVD"""


import ifcopenshell
import bim2fem.ifcplus.api.project
import ifcopenshell.util.selector
from bim2fem.core.convert.convert_linear_frame_member import (
    convert_linear_frame_member_to_linear_structural_curve_member,
)
from bim2fem.core.convert.convert_planar_building_element import (
    convert_planar_wall_or_slab_to_structural_surface_members,
)
from bim2fem.ifcplus import REGION
import bim2fem.ifcplus.api.structural
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import bim2fem.ifcplus.api.placement


def convert_frame_structure_to_fem(
    ifc4_source_file: ifcopenshell.file,
    element_deselection_query: str | None = None,
    region: REGION = "Europe",
) -> ifcopenshell.file:
    """Convert Building Model from IFC4 ReferenceView to IFC4 StructuralAnalysisView"""

    element_selection_query = "IfcColumn, IfcSlab, IfcWall, IfcBeam, IfcMember"

    ifc4_destination_file = bim2fem.ifcplus.api.project.create_ifc4_file(
        model_view_definition="StructuralAnalysisView",
        precision=1e-4,
    )

    project = ifc4_destination_file.by_type(
        type="IfcProject",
        include_subtypes=False,
    )[0]

    site = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class="IfcSite",
        name="Spatial Container for Elements",
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_destination_file,
        products=[site],
        relating_object=project,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    all_elements_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcElement",
        elements=None,
    )

    selected_elements_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query=element_selection_query,
        elements=all_elements_from_source_file,
    )

    if isinstance(element_deselection_query, str):
        deselected_elements_from_source_file = (
            ifcopenshell.util.selector.filter_elements(
                ifc_file=ifc4_source_file,
                query=element_deselection_query,
                elements=all_elements_from_source_file,
            )
        )
        print("debug")
    else:
        deselected_elements_from_source_file = set()

    elements_slated_for_conversion_from_source_file = (
        selected_elements_from_source_file.difference(
            deselected_elements_from_source_file
        )
    )

    beams_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcBeam",
        elements=elements_slated_for_conversion_from_source_file,
    )

    columns_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcColumn",
        elements=elements_slated_for_conversion_from_source_file,
    )

    members_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcMember",
        elements=elements_slated_for_conversion_from_source_file,
    )

    slabs_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcSlab",
        elements=elements_slated_for_conversion_from_source_file,
    )

    walls_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcWall",
        elements=elements_slated_for_conversion_from_source_file,
    )

    structural_analysis_model = (
        bim2fem.ifcplus.api.structural.add_structural_analysis_model(
            ifc4_file=ifc4_destination_file,
            name=None,
        )
    )

    conversion_success_tracker = {}

    for beam_from_source_file in beams_from_source_file:
        structural_curve_member = (
            convert_linear_frame_member_to_linear_structural_curve_member(
                linear_frame_member_from_source_file=beam_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_curve_member is not None:
            conversion_success_tracker[beam_from_source_file] = True
        else:
            conversion_success_tracker[beam_from_source_file] = False

    for column_from_source_file in columns_from_source_file:
        structural_curve_member = (
            convert_linear_frame_member_to_linear_structural_curve_member(
                linear_frame_member_from_source_file=column_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_curve_member is not None:
            conversion_success_tracker[column_from_source_file] = True
        else:
            conversion_success_tracker[column_from_source_file] = False

    for member_from_source_file in members_from_source_file:
        structural_curve_member = (
            convert_linear_frame_member_to_linear_structural_curve_member(
                linear_frame_member_from_source_file=member_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_curve_member is not None:
            conversion_success_tracker[member_from_source_file] = True
        else:
            conversion_success_tracker[member_from_source_file] = False

    for slab_from_source_file in slabs_from_source_file:
        structural_surface_members = (
            convert_planar_wall_or_slab_to_structural_surface_members(
                planar_wall_or_slab_from_source_file=slab_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_surface_members is not None:
            conversion_success_tracker[slab_from_source_file] = True
        else:
            conversion_success_tracker[slab_from_source_file] = False

    for wall_from_source_file in walls_from_source_file:
        structural_surface_members = (
            convert_planar_wall_or_slab_to_structural_surface_members(
                planar_wall_or_slab_from_source_file=wall_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_surface_members is not None:
            conversion_success_tracker[wall_from_source_file] = True
        else:
            conversion_success_tracker[wall_from_source_file] = False

    bim2fem.ifcplus.api.structural.merge_all_coincident_structural_point_connections(
        ifc4sav_file=ifc4_destination_file
    )

    return ifc4_destination_file
