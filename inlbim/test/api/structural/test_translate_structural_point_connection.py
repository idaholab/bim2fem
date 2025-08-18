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
import inlbim.util.structural


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
            p1=(0.0, 0.0, 0.0),
            p2=(0.0, 0.0, 8.0),
            p3=(0.0, 0.0, 1.0),
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
            p1=(9.0, 0.0, 0.0),
            p2=(9.0, 0.0, 8.0),
            p3=(9.0, 0.0, 1.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_column_2,
        )
    )

    # Create Member #1
    architectural_member_1 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcMember",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[architectural_member_1],
        relating_structure=site,
    )
    structural_analysis_member_1 = (
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=(10.0, 0.0, 8.0),
            p2=(18.0, 0.0, 0.0),
            p3=(20.0, 0.0, 2.0),
            profile_def=ipe_400,
            material=s335,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_member_1,
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
                (0.0, 1.0, 8.0),
                (9.0, 1.0, 8.0),
                (9.0, 6.0, 8.0),
            ],
            inner_profiles=[],
            thickness=0.2,
            material=c30_37,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=architectural_slab,
        )
    )

    # Select Top Node of Member #1
    top_node_of_member_1 = inlbim.util.structural.select_structural_point_connections(
        ifc4_sav_file=ifc4_file,
        x_min=10.0,
        x_max=10.0,
        y_min=0.0,
        y_max=0.0,
        z_min=8.0,
        z_max=8.0,
    )[0]
    print(top_node_of_member_1)

    # Translate Top Node of Member #1
    inlbim.api.structural.translate_structural_point_connection(
        structural_point_connection=top_node_of_member_1,
        translation=(-1.0, 0.0, 0.0),
    )

    # Select First Node of Slab
    first_node_of_slab = inlbim.util.structural.select_structural_point_connections(
        ifc4_sav_file=ifc4_file,
        x_min=0.0,
        x_max=0.0,
        y_min=1.0,
        y_max=1.0,
        z_min=8.0,
        z_max=8.0,
    )[0]
    print(first_node_of_slab)

    # Translate First Node of Slab
    inlbim.api.structural.translate_structural_point_connection(
        structural_point_connection=first_node_of_slab,
        translation=(0.0, -1.0, 0.0),
    )

    # Select Second Node of Slab
    second_node_of_slab = inlbim.util.structural.select_structural_point_connections(
        ifc4_sav_file=ifc4_file,
        x_min=9.0,
        x_max=9.0,
        y_min=1.0,
        y_max=1.0,
        z_min=8.0,
        z_max=8.0,
    )[0]
    print(second_node_of_slab)

    # Translate Second Node of Slab
    inlbim.api.structural.translate_structural_point_connection(
        structural_point_connection=second_node_of_slab,
        translation=(0.0, -1.0, 0.0),
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
                "test_translate_structural_point_connection.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
