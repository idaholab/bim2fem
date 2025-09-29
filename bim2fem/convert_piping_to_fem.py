# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to convert IFC4 file from ReferenceView/DesignTransferView MVDs to
StructuralAnalysisView MVD"""


import ifcopenshell
import inlbim.api.file
import ifcopenshell.util.selector
from bim2fem.helpers.convert_pipe_segment import (
    convert_linear_pipe_segment_to_structural_curve_member,
)
from bim2fem.helpers.convert_pipe_fitting import (
    convert_pipe_fitting_to_structural_items,
)
from inlbim import REGION
import ifcopenshell.util.element
import inlbim.api.structural
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import inlbim.api.geometry


def convert_piping_from_reference_view_to_structural_analysis_view(
    ifc4_source_file: ifcopenshell.file,
    element_deselection_query: str | None = None,
    region: REGION = "Europe",
) -> ifcopenshell.file:
    """Convert Piping Model from IFC4 ReferenceView to IFC4 StructuralAnalysisView"""

    # Element Selection Query
    element_selection_query = "IfcPipeSegment, IfcPipeFitting"

    # Create empty IFC4 StructuralAnalysisView File
    ifc4_destination_file = inlbim.api.file.create_ifc4_file(
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
    inlbim.api.geometry.edit_object_placement(
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

    # Get IfcPipeSegments slated for conversion from source file
    pipe_segments_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcPipeSegment",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcPipeSegments: {len(pipe_segments_from_source_file)}")

    # Get sets of IfcPipeFittings slated for conversion from source file
    pipe_fittings_from_source_file = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_source_file,
        query="IfcPipeFitting",
        elements=elements_slated_for_conversion_from_source_file,
    )
    print(f"IfcPipeFittings: {len(pipe_fittings_from_source_file)}")

    # Add StructuralAnalysisModel
    structural_analysis_model = inlbim.api.structural.add_structural_analysis_model(
        ifc4_file=ifc4_destination_file,
        name=None,
    )

    # Track conversion results
    conversion_success_tracker = {}

    # Convert IfcPipeSegments
    num_pipe_segments = len(pipe_segments_from_source_file)
    for index, pipe_segment_from_source_file in enumerate(
        list(pipe_segments_from_source_file)
    ):
        print(
            "".join(
                [
                    f"Converting IfcPipeSegment {index+1}/{num_pipe_segments} | ",
                    f"{pipe_segment_from_source_file}",
                ]
            )
        )
        structural_curve_member = (
            convert_linear_pipe_segment_to_structural_curve_member(
                pipe_segment_from_source_file=pipe_segment_from_source_file,
                ifc4_destination_file=ifc4_destination_file,
                region=region,
                structural_analysis_model=structural_analysis_model,
            )
        )
        if structural_curve_member is not None:
            conversion_success_tracker[pipe_segment_from_source_file] = True
        else:
            conversion_success_tracker[pipe_segment_from_source_file] = False

    # Convert IfcPipeFittings
    num_pipe_fittings = len(pipe_fittings_from_source_file)
    for index, pipe_fitting_from_source_file in enumerate(
        list(pipe_fittings_from_source_file)
    ):
        print(
            "".join(
                [
                    f"Converting IfcPipeFitting {index+1}/{num_pipe_fittings} | ",
                    f"{pipe_fittings_from_source_file}",
                ]
            )
        )
        structural_curve_member = convert_pipe_fitting_to_structural_items(
            pipe_fitting_from_source_file=pipe_fitting_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        if structural_curve_member is not None:
            conversion_success_tracker[pipe_fitting_from_source_file] = True
        else:
            conversion_success_tracker[pipe_fitting_from_source_file] = False

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
    inlbim.api.structural.merge_all_coincident_structural_point_connections(
        ifc4sav_file=ifc4_destination_file
    )

    return ifc4_destination_file
