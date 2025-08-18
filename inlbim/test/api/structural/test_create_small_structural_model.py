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

    # Get Concrete Material
    c30_37 = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="C30/37",
        check_for_duplicate=True,
    )
    assert isinstance(c30_37, ifcopenshell.entity_instance)

    # Get Profile
    ipe_400 = inlbim.api.profile.add_profile_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        profile_name="IPE400",
    )
    assert isinstance(ipe_400, ifcopenshell.entity_instance)

    # Create Column #1
    architectural_column_1 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcColumn",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_column_1],
        relating_structure=site,
    )
    structural_analysis_column_1 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(2.0, 2.0, 0.0),
            p2=(2.0, 2.0, 4.0),
            p3=(3.0, 2.0, 4.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_column_1,
        )
    )

    # Create Column #2
    architectural_column_2 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcColumn",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_column_2],
        relating_structure=site,
    )
    structural_analysis_column_2 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(2.0, 2.0 + 4.0, 0.0),
            p2=(2.0, 2.0 + 4.0, 4.0),
            p3=(3.0, 2.0 + 4.0, 4.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_column_2,
        )
    )

    # Create Slab
    architectural_slab = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSlab",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_slab],
        relating_structure=site,
    )
    structural_analysis_slab = (
        inlbim.api.structural.create_npt_structural_surface_member(
            outer_profile=[
                (2.0, 2.0, 4.0),
                (2.0 + 5.0, 2.0, 4.0),
                (2.0 + 5.0, 2.0 + 4.0, 4.0),
                (2.0 + 5.0 - 5.0, 2.0 + 4.0, 4.0),
            ],
            inner_profiles=[],
            thickness=0.2,
            material=c30_37,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_slab,
        )
    )

    # Create Wall
    architectural_wall = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_wall],
        relating_structure=site,
    )
    structural_analysis_wall = (
        inlbim.api.structural.create_npt_structural_surface_member(
            outer_profile=[
                (7.0, 2.0, 0.0),
                (7.0, 2.0 + 4.0, 0.0),
                (7.0, 2.0 + 4.0, 0.0 + 4.0),
                (7.0, 2.0 + 4.0 - 4.0, 0.0 + 4.0),
            ],
            inner_profiles=[],
            thickness=0.2,
            material=c30_37,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_wall,
        )
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
                "test_create_small_structural_model.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
