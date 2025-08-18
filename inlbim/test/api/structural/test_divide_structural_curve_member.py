# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")),
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

    # Create Beam #1
    architectural_beam_1 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBeam",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_beam_1],
        relating_structure=site,
    )
    inlbim.api.structural.create_3pt_structural_curve_member(
        p1=(4.0, 0.0, 0.0),
        p2=(4.0, 10.0, 0.0),
        p3=(4.0, 0.0, 1.0),
        profile_def=ipe_400,
        material=s335,
        structural_analysis_model=structural_analysis_model,
        corresponding_product=architectural_beam_1,
    )

    # Create Beam #2
    architectural_beam_2 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBeam",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_beam_2],
        relating_structure=site,
    )
    structural_analysis_beam_2 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(6.0, 0.0, 0.0),
            p2=(6.0, 10.0, 0.0),
            p3=(6.0, 0.0, 1.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_beam_2,
        )
    )

    # Create Beam #3
    architectural_beam_3 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBeam",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_beam_3],
        relating_structure=site,
    )
    structural_analysis_beam_3 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(8.0, 0.0, 0.0),
            p2=(8.0, 10.0, 0.0),
            p3=(8.0, 0.0, 1.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_beam_3,
        )
    )

    # Create Beam #4
    architectural_beam_4 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBeam",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_beam_4],
        relating_structure=site,
    )
    structural_analysis_beam_4 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(10.0, 0.0, 0.0),
            p2=(10.0, 10.0, 0.0),
            p3=(10.0, 0.0, 1.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_beam_4,
        )
    )

    # Divide Beam #2
    inlbim.api.structural.divide_structural_curve_member(
        structural_curve_member=structural_analysis_beam_2,
        division_locations_as_proportions_of_length=[0.25],
    )

    # Divide Beam #3
    inlbim.api.structural.divide_structural_curve_member(
        structural_curve_member=structural_analysis_beam_3,
        division_locations_as_proportions_of_length=[0.25, 0.50],
    )

    # Divide Beam #4
    inlbim.api.structural.divide_structural_curve_member(
        structural_curve_member=structural_analysis_beam_4,
        division_locations_as_proportions_of_length=[0.25, 0.50, 0.90],
    )

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
                "test_divide_structural_curve_member.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
