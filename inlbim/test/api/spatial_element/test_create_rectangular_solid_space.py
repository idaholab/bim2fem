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
        name=None,
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
        name=None,
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

    # Geometry of Spaces
    spaces_information = [
        {
            "name": "Space-01",
            "x": 0.0,
            "y": 0.0,
            "length": 5.0,
            "width": 2.0,
            "height": 1.0,
        },
        {
            "name": "Space-02",
            "x": 5.0,
            "y": 0.0,
            "length": 3.0,
            "width": 5.0,
            "height": 1.0,
        },
        {
            "name": "Space-03",
            "x": 0.0,
            "y": 2.0,
            "length": 5.0,
            "width": 3.0,
            "height": 1.0,
        },
    ]

    # Create Spaces
    for space_information in spaces_information:
        space = inlbim.api.spatial_element.create_rectangular_solid_space(
            ifc4_file=ifc4_file,
            length=space_information["length"],
            width=space_information["width"],
            height=space_information["height"],
            repositioned_origin=(space_information["x"], space_information["y"], 0.0),
            name=space_information["name"],
            spatial_element=building,
            should_transform_relative_to_parent=True,
        )
        inlbim.api.style.assign_color_to_element(
            element=space,
            rgb_triplet=inlbim.api.style.generate_random_rgb(),
            transparency=0.1,
        )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_rectangular_solid_space.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
