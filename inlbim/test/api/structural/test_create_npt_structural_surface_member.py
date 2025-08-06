# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

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
import inlbim.api.style
import inlbim.api.spatial_element
import inlbim.api.material
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

    # Add Building
    building = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        name="Building-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[building],
        relating_object=site,
    )
    inlbim.api.geometry.edit_object_placement(
        product=building,
        place_object_relative_to_parent=True,
    )

    # Create Space
    space = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=11.0,
        width=3.0,
        height=4.0,
        repositioned_origin=(1.0, 1.0, 0.0),
        name="Space-01",
        spatial_element=building,
        should_transform_relative_to_parent=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=space,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
    )

    # Add StructuralAnalysisModel
    structural_analysis_model = inlbim.api.structural.add_structural_analysis_model(
        ifc4_file=ifc4_file,
        name="SA Model 01",
    )

    # Get Material
    concrete_material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="C30/37",
        check_for_duplicate=True,
    )
    assert isinstance(concrete_material, ifcopenshell.entity_instance)

    # Create corresponding product
    wall_1 = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
        name="Wall-01",
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[wall_1],
        relating_structure=space,
    )

    # Create StructuralItem
    inlbim.api.structural.create_npt_structural_surface_member(
        outer_profile=[
            (1.0, 1.0, 0.0),
            (1.0 + 5.0, 1.0, 0.0),
            (1.0 + 5.0, 1.0, 0.0 + 3.0),
            (1.0 + 5.0 - 5.0, 1.0, 0.0 + 3.0),
        ],
        inner_profiles=[
            [
                (1.0 + 1.0, 1.0, 0.0 + 1.0),
                (1.0 + 1.0 + 1.0, 1.0, 0.0 + 1.0),
                (1.0 + 1.0 + 1.0, 1.0, 0.0 + 1.0 + 1.0),
                (1.0 + 1.0 + 1.0 - 1.0, 1.0, 0.0 + 1.0 + 1.0),
            ],
            [
                (1.0 + 1.0 + 2.0, 1.0, 0.0 + 1.0),
                (1.0 + 1.0 + 1.0 + 2.0, 1.0, 0.0 + 1.0),
                (1.0 + 1.0 + 1.0 + 2.0, 1.0, 0.0 + 1.0 + 1.0),
                (1.0 + 1.0 + 1.0 - 1.0 + 2.0, 1.0, 0.0 + 1.0 + 1.0),
            ],
        ],
        thickness=0.2,
        material=concrete_material,
        structural_analysis_model=structural_analysis_model,
        corresponding_product=wall_1,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_npt_structural_surface_member.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
