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
import inlbim.api.style
import inlbim.api.spatial_element
import inlbim.api.material
import inlbim.api.building_element


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

    # Add Space
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

    # Get Materials
    concrete_material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="C30/37",
        check_for_duplicate=True,
    )
    assert isinstance(concrete_material, ifcopenshell.entity_instance)
    steel_material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="S355",
        check_for_duplicate=True,
    )
    assert isinstance(steel_material, ifcopenshell.entity_instance)

    # Create Element
    inlbim.api.building_element.create_2pt_wall(
        name="Wall-01",
        p1=(0.0, 0.0),
        p2=(5.0, 0.0),
        height=3.0,
        elevation=0.0,
        materials=[concrete_material, steel_material, concrete_material],
        thicknesses=[0.05, 0.1, 0.05],
        structure_contained_in=space,
        inner_openings=[
            [
                (1.0, 1.0),
                (1.0 + 2.0, 1.0),
                (1.0 + 2.0, 1.0 + 2.0),
                (1.0 + 2.0 - 2.0, 1.0 + 2.0),
                (1.0 + 2.0 - 2.0, 1.0 + 2.0 - 2.0),
            ],
        ],
        should_transform_relative_to_parent=True,
    )

    # Create Element
    inlbim.api.building_element.create_2pt_wall(
        name="Wall-02",
        p1=(6.0, 1.0),
        p2=(11.0, 3.0),
        height=2.0,
        elevation=0.5,
        materials=[concrete_material, steel_material, concrete_material],
        thicknesses=[0.05, 0.1, 0.05],
        structure_contained_in=space,
        inner_openings=[
            [
                (1.0, 0.5),
                (1.0 + 1.0, 0.5),
                (1.0 + 1.0, 0.5 + 1.0),
                (1.0 + 1.0 - 1.0, 0.5 + 1.0),
                (1.0 + 1.0 - 1.0, 0.5 + 1.0 - 1.0),
            ],
            [
                (1.0 + 2.0, 0.5),
                (1.0 + 1.0 + 2.0, 0.5),
                (1.0 + 1.0 + 2.0, 0.5 + 1.0),
                (1.0 + 1.0 - 1.0 + 2.0, 0.5 + 1.0),
                (1.0 + 1.0 - 1.0 + 2.0, 0.5 + 1.0 - 1.0),
            ],
        ],
        should_transform_relative_to_parent=True,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_2pt_wall.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
