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
import inlbim.api.distribution_element
import inlbim.api.spatial_element
import ifcopenshell.api.system
import inlbim.api.material
import inlbim.api.system
import ifcopenshell.util.system
import inlbim.api.representation
import ifcopenshell.api.geometry


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
        name="Site #1",
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
    distribution_system.Name = "CVS"
    distribution_system.LongName = "Central Ventilation System"
    distribution_system.PredefinedType = "VENTILATION"

    # Create MAU
    mau = inlbim.api.distribution_element.create_make_up_air_unit(
        ifc4_file=ifc4_file,
        length=4.71678,
        width=0.9017,
        height=1.016,
        name="MAU",
        spatial_element=site,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=False,
    )
    mau.Description = "Preconditioning Unit"
    inlbim.api.geometry.edit_object_placement(
        product=mau,
        repositioned_origin=(0.7, 1.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Create V4
    outer_diameter = 0.5334 / 2
    thickness = 1 / 5 * outer_diameter
    valve_4 = inlbim.api.distribution_element.create_motorized_valve(
        ifc4_file=ifc4_file,
        outer_diameter=outer_diameter,
        thickness=thickness,
        name="MV",
        spatial_element=site,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=False,
    )
    valve_4.Description = "Motorized Valve"
    inlbim.api.geometry.edit_object_placement(
        product=valve_4,
        repositioned_origin=(1.0 + 10.0 - 2.0, 2.0 + 2.0, 1.0 + 2.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(0.0, -1.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Connect MAU source port to Valve sink port
    mau_source_port = ifcopenshell.util.system.get_ports(
        element=mau,
        flow_direction="SOURCE",
    )[0]
    v4_sink_port = ifcopenshell.util.system.get_ports(
        element=valve_4,
        flow_direction="SINK",
    )[0]
    inlbim.api.system.connect_two_distribution_ports_via_piping(
        source_port=mau_source_port,
        sink_port=v4_sink_port,
        nominal_diameter=0.26,
        thickness=1 / 10 * 0.26,
        material=steel_material,
        elbow_radius_type="SHORT",
        branch_name="MAU to MV",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=False,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_valve.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
