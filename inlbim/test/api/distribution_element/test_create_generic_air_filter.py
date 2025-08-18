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
import inlbim.api.distribution_element
import inlbim.api.spatial_element
import ifcopenshell.api.system


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

    # Add Space
    space = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=10.0,
        width=6.0,
        height=2.0,
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

    # Add DistributionSystem
    distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
    distribution_system.Name = "CVS"
    distribution_system.LongName = "Central Ventilation System"
    distribution_system.PredefinedType = "VENTILATION"

    # Create Element
    filter_1 = inlbim.api.distribution_element.create_generic_air_filter(
        ifc4_file=ifc4_file,
        length=6.0,
        width=1.0,
        height=6.0,
        name="Filter #1",
        spatial_element=space,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=filter_1,
        rgb_triplet=(248 / 255, 200 / 255, 220 / 255),
        transparency=0.0,
    )

    # Create Element
    filter_2 = inlbim.api.distribution_element.create_generic_air_filter(
        ifc4_file=ifc4_file,
        length=0.4572,
        width=0.0762,
        height=0.4064,
        name="Filter #2",
        spatial_element=space,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=filter_2,
        rgb_triplet=(248 / 255, 200 / 255, 220 / 255),
        transparency=0.0,
    )

    # Test translation
    inlbim.api.geometry.edit_object_placement(
        product=filter_2,
        repositioned_origin=(4.0, 2.0, 0.0),
        repositioned_x_axis=(0.0, 1.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_generic_air_filter.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
