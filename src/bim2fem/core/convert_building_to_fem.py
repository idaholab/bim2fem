# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to convert IFC4 file from ReferenceView/DesignTransferView MVDs to
StructuralAnalysisView MVD"""


import ifcopenshell
import bim2fem.ifcplus.api.project
import ifcopenshell.util.selector
from bim2fem.core.helpers.convert_linear_building_element import (
    convert_linear_beam_to_structural_curve_member,
    convert_linear_column_to_structural_curve_member,
    convert_linear_member_to_structural_curve_member,
)
from bim2fem.core.helpers.convert_planar_building_element import (
    convert_planar_slab_to_structural_surface_members,
    convert_planar_wall_to_structural_surface_members,
)
from bim2fem.ifcplus import REGION
import ifcopenshell.util.element
import bim2fem.ifcplus.api.structural
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import bim2fem.ifcplus.api.placement


def convert_building_from_reference_view_to_structural_analysis_view(
    ifc4_source_file: ifcopenshell.file,
    element_deselection_query: str | None = None,
    region: REGION = "Europe",
) -> ifcopenshell.file:
    """Convert Building Model from IFC4 ReferenceView to IFC4 StructuralAnalysisView"""

    # Element Selection Query
    element_selection_query = "IfcColumn, IfcSlab, IfcWall, IfcBeam, IfcMember"

    # Create empty IFC4 StructuralAnalysisView File
    ifc4_destination_file = bim2fem.ifcplus.api.project.create_ifc4_file(
        model_view_definition="StructuralAnalysisView",
        precision=1e-4,
    )

    # Get Project
    project = ifc4_destination_file.by_type(type="IfcProject", include_subtypes=False)[
        0
    ]

    # Add Site
    site = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class="IfcSite",
        name="Site-01",
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

    # Get list of all elements
    all_elements_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcElement",
        elements=None,
    )

    # Get list of selected elements
    selected_elements_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query=element_selection_query,
        elements=all_elements_from_source_file,
    )

    # Get list of deselected elements
    if isinstance(element_deselection_query, str):
        deselected_elements_from_source_file = (
            ifcopenshell.util.selector.filter_elements(
                ifc_file=ifc4_source_file,
                query=element_deselection_query,
                elements=all_elements_from_source_file,
            )
        )
    else:
        deselected_elements_from_source_file = set()

    # Get resulting set of elements slated for conversion
    elements_slated_for_conversion_from_source_file = (
        selected_elements_from_source_file.difference(
            deselected_elements_from_source_file
        )
    )

    # Get IfcBeams slated for conversion from source file
    beams_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcBeam",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcBeams: {len(beams_from_source_file)}")

    # Get IfcColumns slated for conversion from source file
    columns_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcColumn",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcColumns: {len(columns_from_source_file)}")

    # Get IfcMembers slated for conversion from source file
    members_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcMember",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcMembers: {len(members_from_source_file)}")

    # Get IfcSlabs slated for conversion from source file
    slabs_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcSlab",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcSlabs: {len(slabs_from_source_file)}")

    walls_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcWall",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcWalls: {len(walls_from_source_file)}")

    # Add StructuralAnalysisModel
    structural_analysis_model = (
        bim2fem.ifcplus.api.structural.add_structural_analysis_model(
            ifc4_file=ifc4_destination_file,
            name=None,
        )
    )

    # Track conversion results
    conversion_success_tracker = {}

    # Convert IfcBeams
    num_beams = len(beams_from_source_file)
    for index, beam_from_source_file in enumerate(list(beams_from_source_file)):
        print(f"Converting IfcBeam {index+1}/{num_beams} | {beam_from_source_file}")
        structural_curve_member = convert_linear_beam_to_structural_curve_member(
            beam_from_source_file=beam_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_curve_member is not None:
            conversion_success_tracker[beam_from_source_file] = True
        else:
            conversion_success_tracker[beam_from_source_file] = False

    # Convert IfcColumns
    num_columns = len(columns_from_source_file)
    for index, column_from_source_file in enumerate(list(columns_from_source_file)):
        print(
            f"Converting IfcColumn {index+1}/{num_columns} | {column_from_source_file}"
        )
        structural_curve_member = convert_linear_column_to_structural_curve_member(
            column_from_source_file=column_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_curve_member is not None:
            conversion_success_tracker[column_from_source_file] = True
        else:
            conversion_success_tracker[column_from_source_file] = False

    # Convert IfcMembers
    num_members = len(members_from_source_file)
    for index, member_from_source_file in enumerate(list(members_from_source_file)):
        print(f"Converting IfcMember {index+1}/{num_members}")
        structural_curve_member = convert_linear_member_to_structural_curve_member(
            member_from_source_file=member_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_curve_member is not None:
            conversion_success_tracker[member_from_source_file] = True
        else:
            conversion_success_tracker[member_from_source_file] = False

    # Convert IfcSlabs
    num_slabs = len(slabs_from_source_file)
    for index, slab_from_source_file in enumerate(list(slabs_from_source_file)):
        print(f"Converting IfcSlab {index+1}/{num_slabs}")
        structural_surface_members = convert_planar_slab_to_structural_surface_members(
            slab_from_source_file=slab_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_surface_members is not None:
            conversion_success_tracker[slab_from_source_file] = True
        else:
            conversion_success_tracker[slab_from_source_file] = False

    # Convert IfcWalls
    num_walls = len(walls_from_source_file)
    for index, wall_from_source_file in enumerate(list(walls_from_source_file)):
        print(f"Converting IfcWall {index+1}/{num_walls}")
        structural_surface_members = convert_planar_wall_to_structural_surface_members(
            wall_from_source_file=wall_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_surface_members is not None:
            conversion_success_tracker[wall_from_source_file] = True
        else:
            conversion_success_tracker[wall_from_source_file] = False

    # Print out ElementTypes
    print("\nElementTypes:")
    for element_type in ifc4_destination_file.by_type(
        type="IfcElementType",
        include_subtypes=True,
    ):
        count_of_assignments_for_element_type = len(
            ifcopenshell.util.element.get_types(type=element_type)
        )
        print(
            " ".join(
                [
                    f"\tElementType: {element_type.to_string()}",
                    f"assigned {count_of_assignments_for_element_type} times",
                ]
            )
        )

    # Print out Conversion Results
    print("\nConversion Results:")
    for key, value in conversion_success_tracker.items():
        if value:
            result = "OK"
        else:
            result = "NG"
        print(f"\t{key.GlobalId} {key.is_a()}: {result}")

    # Merge Nodes
    bim2fem.ifcplus.api.structural.merge_all_coincident_structural_point_connections(
        ifc4sav_file=ifc4_destination_file
    )

    return ifc4_destination_file
