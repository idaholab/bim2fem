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
import inlbim.api.system
import inlbim.util.geometry
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

    # Add Building
    building = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        name="Building-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[building],
        relating_object=project,
    )
    inlbim.api.geometry.edit_object_placement(
        product=building,
        place_object_relative_to_parent=True,
    )

    # Get Material
    steel_material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_file,
        region="Europe",
        material_name="S355",
        check_for_duplicate=True,
    )
    assert isinstance(steel_material, ifcopenshell.entity_instance)

    # Add DistributionSystem
    distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
    distribution_system.Name = "WS"
    distribution_system.LongName = "Water Supply for Building"
    distribution_system.PredefinedType = "WATERSUPPLY"

    # Set pipe nominal diameter and thickness
    nominal_diameter = 2.0
    thickness = 0.1

    # Polyline
    polyline = [
        (10.0, 5.0, 0.0),
        (10.0, 17.0, 0.0),
        (21.0, 17.0, 0.0),
        (28.0, 24.0, 0.0),
    ]

    # Create Element
    horizontal_curve_1 = inlbim.util.geometry.HorizontalCurve.from_3pt_polyline(
        p1=polyline[0],
        p2=polyline[1],
        p3=polyline[2],
        radius_of_curvature=1.5 * nominal_diameter,
    )
    print(horizontal_curve_1.__repr__())
    inlbim.api.system.create_elbow(
        horizontal_curve=horizontal_curve_1,
        nominal_diameter=nominal_diameter,
        thickness=thickness,
        material=steel_material,
        name="Elbow-1",
        spatial_element=building,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )

    # Create Element
    horizontal_curve_2 = inlbim.util.geometry.HorizontalCurve.from_3pt_polyline(
        p1=polyline[1],
        p2=polyline[2],
        p3=polyline[3],
        radius_of_curvature=1.5 * nominal_diameter,
    )
    print(horizontal_curve_2.__repr__())
    inlbim.api.system.create_elbow(
        horizontal_curve=horizontal_curve_2,
        nominal_diameter=nominal_diameter,
        thickness=thickness,
        material=steel_material,
        name="Elbow-2",
        spatial_element=building,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_elbow.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
