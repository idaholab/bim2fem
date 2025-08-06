# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to convert IFC4 file from ReferenceView/DesignTransferView MVDs to
StructuralAnalysisView MVD"""


import ifcopenshell
import inlbim.api.file
import ifcopenshell.util.selector
from bim2fem.helpers.convert_frame_member_to_structural_item import (
    convert_linear_frame_member_to_structural_item,
)
from bim2fem.helpers.convert_slab_or_wall_to_strucutral_item import (
    convert_planar_slab_or_wall_to_structural_item,
)
from inlbim import REGION
import ifcopenshell.util.element
import inlbim.api.structural
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import inlbim.api.geometry


def convert_ifc_to_fem(
    ifc4_source_file: ifcopenshell.file,
    element_selection_query: str = "IfcColumn, IfcSlab, IfcWall, IfcBeam, IfcMember",
    element_deselection_query: str | None = None,
    region: REGION = "Europe",
) -> ifcopenshell.file:
    """Convert IFC to FEM"""

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

    # Get sets of elements slated for conversion from source file
    beams_slated_for_conversion_from_source_file = (
        ifcopenshell.util.selector.filter_elements(
            ifc_file=ifc4_source_file,
            query="IfcBeam",
            elements=elements_slated_for_conversion_from_source_file,
        )
    )
    print(f"beamns: {len(beams_slated_for_conversion_from_source_file)}")
    columns_slated_for_conversion_from_source_file = (
        ifcopenshell.util.selector.filter_elements(
            ifc_file=ifc4_source_file,
            query="IfcColumn",
            elements=elements_slated_for_conversion_from_source_file,
        )
    )
    print(f"columns: {len(columns_slated_for_conversion_from_source_file)}")
    members_slated_for_conversion_from_source_file = (
        ifcopenshell.util.selector.filter_elements(
            ifc_file=ifc4_source_file,
            query="IfcMember",
            elements=elements_slated_for_conversion_from_source_file,
        )
    )
    print(f"members: {len(members_slated_for_conversion_from_source_file)}")
    slabs_slated_for_conversion_from_source_file = (
        ifcopenshell.util.selector.filter_elements(
            ifc_file=ifc4_source_file,
            query="IfcSlab",
            elements=elements_slated_for_conversion_from_source_file,
        )
    )
    print(f"slabs: {len(slabs_slated_for_conversion_from_source_file)}")
    walls_slated_for_conversion_from_source_file = (
        ifcopenshell.util.selector.filter_elements(
            ifc_file=ifc4_source_file,
            query="IfcWall",
            elements=elements_slated_for_conversion_from_source_file,
        )
    )
    print(f"walls: {len(walls_slated_for_conversion_from_source_file)}")

    # Add StructuralAnalysisModel
    structural_analysis_model = inlbim.api.structural.add_structural_analysis_model(
        ifc4_file=ifc4_destination_file,
        name=None,
    )

    # Track conversion results
    conversion_results = {}

    # Convert beams
    num_beams = len(beams_slated_for_conversion_from_source_file)
    for index, beam_from_source_file in enumerate(
        list(beams_slated_for_conversion_from_source_file)
    ):
        print(f"Converting Beam {index+1}/{num_beams} | {beam_from_source_file}")
        structural_curve_member = convert_linear_frame_member_to_structural_item(
            frame_member_from_source_file=beam_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        conversion_results[beam_from_source_file] = structural_curve_member

    # Convert columns
    num_columns = len(columns_slated_for_conversion_from_source_file)
    for index, column_from_source_file in enumerate(
        list(columns_slated_for_conversion_from_source_file)
    ):
        print(f"Converting Column {index+1}/{num_columns} | {column_from_source_file}")
        structural_curve_member = convert_linear_frame_member_to_structural_item(
            frame_member_from_source_file=column_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        conversion_results[column_from_source_file] = structural_curve_member

    # Convert members
    num_members = len(members_slated_for_conversion_from_source_file)
    for index, member_from_source_file in enumerate(
        list(members_slated_for_conversion_from_source_file)
    ):
        print(f"Converting Member {index+1}/{num_members}")
        structural_curve_member = convert_linear_frame_member_to_structural_item(
            frame_member_from_source_file=member_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        conversion_results[member_from_source_file] = structural_curve_member

    # Convert slabs
    num_slabs = len(slabs_slated_for_conversion_from_source_file)
    for index, slab_from_source_file in enumerate(
        list(slabs_slated_for_conversion_from_source_file)
    ):
        print(f"Converting Slab {index+1}/{num_slabs}")
        structural_surface_members = convert_planar_slab_or_wall_to_structural_item(
            slab_or_wall_from_source_file=slab_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        conversion_results[slab_from_source_file] = structural_surface_members

    # Convert walls
    num_walls = len(walls_slated_for_conversion_from_source_file)
    for index, wall_from_source_file in enumerate(
        list(walls_slated_for_conversion_from_source_file)
    ):
        print(f"Converting Wall {index+1}/{num_walls}")
        structural_surface_members = convert_planar_slab_or_wall_to_structural_item(
            slab_or_wall_from_source_file=wall_from_source_file,
            ifc4_destination_file=ifc4_destination_file,
            region=region,
            structural_analysis_model=structural_analysis_model,
        )
        conversion_results[wall_from_source_file] = structural_surface_members

    # Print out ElementTypes
    print("\nElement Types:")
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
                    f"\telement_type: {element_type.to_string()}",
                    f"assigned {count_of_assignments_for_element_type} times",
                ]
            )
        )

    # Print out Conversion Results
    print("\nConversion Results:")
    for key, value in conversion_results.items():
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
