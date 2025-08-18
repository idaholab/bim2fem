# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)


from inlbim import current_time
import time
import chime
import inlbim.api.file
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import inlbim.api.geometry
import inlbim.api.material
import inlbim.api.profile
import inlbim.api.structural
import ifcopenshell.api.spatial
import bim2fem.helpers.snap_frame_members


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Add IFC File
    ifc4_file = inlbim.api.file.create_ifc4_file(
        model_view_definition="ReferenceView_V1.2",
        precision=1e-4,
    )

    # Get Project
    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    # Add Site
    site = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSite",
        name="Site-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[site],
        relating_object=project,
    )
    inlbim.api.geometry.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    # Add StructuralAnalysisModel
    structural_analysis_model = inlbim.api.structural.add_structural_analysis_model(
        ifc4_file=ifc4_file,
        name="SA Model 01",
    )

    # Get Steel Material
    s335 = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="S355",
        check_for_duplicate=True,
    )
    assert isinstance(s335, ifcopenshell.entity_instance)

    # Get Profile
    ipe_400 = inlbim.api.profile.add_profile_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        profile_name="IPE400",
    )
    assert isinstance(ipe_400, ifcopenshell.entity_instance)

    # Create StructuralCurveMembers
    columns = []
    beams = []
    arguments_for_all_structural_curve_members = [
        {
            "architectural_element_class": "IfcColumn",
            "p1": (0.0, 0.0, 0.0),
            "p2": (0.0, 0.0, 4.5),
            "p3": (0.0, 1.0, 0.0),
        },
        {
            "architectural_element_class": "IfcColumn",
            "p1": (0.0 + 2.5, 0.0, 0.0),
            "p2": (0.0 + 2.5, 0.0, 4.5),
            "p3": (0.0 + 2.5, 1.0, 0.0),
        },
        {
            "architectural_element_class": "IfcColumn",
            "p1": (0.0 + 5.0, 0.0, 0.0),
            "p2": (0.0 + 5.0, 0.0, 2.5),
            "p3": (0.0 + 5.0, 1.0, 0.0),
        },
        {
            "architectural_element_class": "IfcColumn",
            "p1": (0.0 + 10.0, 0.0, 0.0),
            "p2": (0.0 + 10.0, 0.0, 4.5),
            "p3": (0.0 + 10.0, 1.0, 0.0),
        },
        {
            "architectural_element_class": "IfcBeam",
            "p1": (0.5, 0.1, 2.0),
            "p2": (9.5, 0.1, 2.0),
            "p3": (0.5, 0.1, 2.0 + 1.0),
        },
        {
            "architectural_element_class": "IfcBeam",
            "p1": (0.5, 0.1, 2.0 + 2.0),
            "p2": (9.5, 0.1, 2.0 + 2.0),
            "p3": (0.5, 0.1, 2.0 + 1.0 + 2.0),
        },
    ]
    for (
        arguments_for_structural_curve_member
    ) in arguments_for_all_structural_curve_members:
        architectural_element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class=arguments_for_structural_curve_member[
                "architectural_element_class"
            ],
        )
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[architectural_element],
            relating_structure=site,
        )
        structural_curve_member = (
            inlbim.api.structural.create_3pt_structural_curve_member(
                p1=arguments_for_structural_curve_member["p1"],
                p2=arguments_for_structural_curve_member["p2"],
                p3=arguments_for_structural_curve_member["p3"],
                profile_def=ipe_400,
                material=s335,
                structural_analysis_model=structural_analysis_model,
                corresponding_product=architectural_element,
            )
        )
        if (
            arguments_for_structural_curve_member["architectural_element_class"]
            == "IfcColumn"
        ):
            columns.append(structural_curve_member)
        elif (
            arguments_for_structural_curve_member["architectural_element_class"]
            == "IfcBeam"
        ):
            beams.append(structural_curve_member)
    print(f"len(columns): {len(columns)}")
    print(f"len(beams): {len(beams)}")

    # Divide the columns and beams
    divided_beams = bim2fem.helpers.snap_frame_members.divide_structural_curve_members_at_intersection_points_on_spans_with_other_members(
        indivisible_members=columns,
        divisible_members=beams,
    )
    print(f"len(divided_beams): {len(divided_beams)}")

    # Merge Nodes
    inlbim.api.structural.merge_all_coincident_structural_point_connections(
        ifc4sav_file=ifc4_file
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_divide_structural_curve_members_at_intersection_points_on_spans_with_other_members.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
