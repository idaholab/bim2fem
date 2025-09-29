# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
from inlbim import REGION
from bim2fem.helpers.convert_linear_building_element import (
    convert_linear_building_element_to_structural_curve_member,
)


def convert_linear_pipe_segment_to_structural_curve_member(
    pipe_segment_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    # Check IFC Class
    required_ifc_class = "IfcPipeSegment"
    if not pipe_segment_from_source_file.is_a(required_ifc_class):
        print(
            " ".join(
                [
                    "\tWarning: Failed Conversion for",
                    f"{pipe_segment_from_source_file}. ",
                    f"IfcElement class must be {required_ifc_class}.",
                ]
            )
        )
        return None

    # Convert Element
    structural_curve_member_from_destination_file = (
        convert_linear_building_element_to_structural_curve_member(
            linear_building_element_from_source_file=pipe_segment_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
    )

    return structural_curve_member_from_destination_file
