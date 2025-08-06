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
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=[
            inlbim.api.representation.add_block(  # Block
                ifc4_file=ifc4_file,
                length=42.5,
                width=20.0,
                height=0.2,
                repositioned_origin=(0.0, 0.0, -0.2),
            )
        ],
        boolean_operators=[],
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="CSG",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=site,
        representation=shape_model,
    )
    inlbim.api.geometry.edit_object_placement(
        product=site,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=site,
        rgb_triplet=inlbim.RGB_CONCRETE,
        transparency=0.0,
    )

    # Add Space for YARD_IN
    space_for_yard_in = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=5.8,
        width=3.0,
        height=2.0,
        repositioned_origin=(0.70, 14.3, 0.0),
        name="YARD_IN",
        spatial_element=site,
        should_transform_relative_to_parent=True,
    )
    space_for_yard_in.Description = "Yard Supply Section"
    inlbim.api.style.assign_color_to_element(
        element=space_for_yard_in,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
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
        spatial_element=space_for_yard_in,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    mau.Description = "Preconditioning Unit"
    inlbim.api.geometry.edit_object_placement(
        product=mau,
        repositioned_origin=(0.7, 1.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Add Building for CONT
    containment_structure_diameter = 3.8 * 2.0
    containment_structure_cylinder_height = 4.9
    containment_structure_thickness = 0.3
    building_for_cont = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        name="CONT",
    )
    building_for_cont.Description = "Containment Structure"
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[building_for_cont],
        relating_object=site,
    )
    inlbim.api.geometry.edit_object_placement(
        product=building_for_cont,
        place_object_relative_to_parent=True,
    )
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=[
            inlbim.api.representation.add_sphere(  # Sphere
                ifc4_file=ifc4_file,
                radius=containment_structure_diameter / 2.0,
                repositioned_origin=(
                    containment_structure_diameter / 2.0,
                    containment_structure_diameter / 2.0,
                    containment_structure_cylinder_height,
                ),
            ),
            inlbim.api.representation.add_sphere(  # Minus Sphere
                ifc4_file=ifc4_file,
                radius=containment_structure_diameter / 2.0
                - containment_structure_thickness,
                repositioned_origin=(
                    containment_structure_diameter / 2.0,
                    containment_structure_diameter / 2.0,
                    containment_structure_cylinder_height,
                ),
            ),
            inlbim.api.representation.add_block(  # Minus Block
                ifc4_file=ifc4_file,
                length=containment_structure_diameter,
                width=containment_structure_diameter,
                height=containment_structure_cylinder_height,
            ),
            inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Plus Cylinder
                ifc4_file=ifc4_file,
                radius=containment_structure_diameter / 2.0,
                extrusion_depth=containment_structure_cylinder_height,
                repositioned_origin=(
                    containment_structure_diameter / 2.0,
                    containment_structure_diameter / 2.0,
                    0.0,
                ),
            ),
            inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Minus Cylinder
                ifc4_file=ifc4_file,
                radius=containment_structure_diameter / 2.0
                - containment_structure_thickness,
                extrusion_depth=containment_structure_cylinder_height,
                repositioned_origin=(
                    containment_structure_diameter / 2.0,
                    containment_structure_diameter / 2.0,
                    0.0,
                ),
            ),
        ],
        boolean_operators=["DIFFERENCE", "DIFFERENCE", "UNION", "DIFFERENCE"],
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="CSG",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=building_for_cont,
        representation=shape_model,
    )
    inlbim.api.geometry.edit_object_placement(
        product=building_for_cont,
        repositioned_origin=(8.8, 2.12, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=building_for_cont,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.2,
    )

    # Add Space inside CONT
    space_inside_cont = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=containment_structure_diameter / 2.0,
        width=containment_structure_diameter / 2.0,
        height=containment_structure_cylinder_height / 2.0,
        repositioned_origin=(
            containment_structure_diameter / 4.0,
            containment_structure_diameter / 4.0,
            0.0,
        ),
        name="CONT",
        spatial_element=building_for_cont,
        should_transform_relative_to_parent=True,
    )
    space_inside_cont.Description = "Containment Interior"
    inlbim.api.style.assign_color_to_element(
        element=space_inside_cont,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
    )

    # Create V4
    outer_diameter = 0.5334 / 2
    thickness = 1 / 5 * outer_diameter
    valve_4 = inlbim.api.distribution_element.create_motorized_valve(
        ifc4_file=ifc4_file,
        outer_diameter=outer_diameter,
        thickness=thickness,
        name="V4",
        spatial_element=space_inside_cont,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    valve_4.Description = "Motorized Valve 4"
    inlbim.api.geometry.edit_object_placement(
        product=valve_4,
        repositioned_origin=(1.0, 2.0, 1.0),
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
        branch_name="MAU to V1",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=True,
    )

    # Create HEPA1
    hepa_1 = inlbim.api.distribution_element.create_generic_air_filter(
        ifc4_file=ifc4_file,
        length=0.4572,
        width=0.0762,
        height=0.4064,
        name="HEPA1",
        spatial_element=space_inside_cont,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    hepa_1.Description = "Interior HEPA 1"
    inlbim.api.geometry.edit_object_placement(
        product=hepa_1,
        repositioned_origin=(3.0 - 1.0, 1.0 - 0.5, 2.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(0.0, -1.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Create V3
    outer_diameter = 0.5334 / 2
    thickness = 1 / 5 * outer_diameter
    valve_3 = inlbim.api.distribution_element.create_motorized_valve(
        ifc4_file=ifc4_file,
        outer_diameter=outer_diameter,
        thickness=thickness,
        name="V3",
        spatial_element=space_inside_cont,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    valve_3.Description = "Motorized Valve 3"
    inlbim.api.geometry.edit_object_placement(
        product=valve_3,
        repositioned_origin=(3.0, 2.0 + 1.5, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Connect HEPA1 source port to V3 sink port
    inlbim.api.system.connect_two_distribution_ports_via_piping(
        source_port=ifcopenshell.util.system.get_ports(
            element=hepa_1,
            flow_direction="SOURCE",
        )[0],
        sink_port=ifcopenshell.util.system.get_ports(
            element=valve_3,
            flow_direction="SINK",
        )[0],
        nominal_diameter=0.26,
        thickness=1 / 10 * 0.26,
        material=steel_material,
        elbow_radius_type="SHORT",
        branch_name="HEPA1 to V3",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=True,
    )

    # Add Space for YARD_OUT
    space_for_yard_out = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=5.8 * 3.0 + 2.0,
        width=3.0,
        height=8.0,
        repositioned_origin=(20.1, 14.3, 0.0),
        name="YARD_OUT",
        spatial_element=site,
        should_transform_relative_to_parent=True,
    )
    space_for_yard_out.Description = "Yard Exhaust Section"
    inlbim.api.style.assign_color_to_element(
        element=space_for_yard_out,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
    )

    # Create HEPA3
    hepa_3 = inlbim.api.distribution_element.create_air_filtration_containment_housing(
        ifc4_file=ifc4_file,
        length=7.9502,
        width=0.8001,
        height=1.8288,
        name="HEPA3",
        spatial_element=space_for_yard_out,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    hepa_3.Description = "Two-stage HEPA filter"
    inlbim.api.geometry.edit_object_placement(
        product=hepa_3,
        repositioned_origin=(0.0, 1.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Connect V3 source port to HEPA3 sink port
    inlbim.api.system.connect_two_distribution_ports_via_piping(
        source_port=ifcopenshell.util.system.get_ports(
            element=valve_3,
            flow_direction="SOURCE",
        )[0],
        sink_port=ifcopenshell.util.system.get_ports(
            element=hepa_3,
            flow_direction="SINK",
        )[0],
        nominal_diameter=0.26,
        thickness=1 / 10 * 0.26,
        material=steel_material,
        elbow_radius_type="SHORT",
        branch_name="V3 to HEPA3",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=True,
    )

    # Create E3
    e3 = inlbim.api.distribution_element.create_hprs_exhaust_fan(
        ifc4_file=ifc4_file,
        length=1.281112,
        width=0.9398,
        height=1.150937 * 0.8,
        name="E3",
        spatial_element=space_for_yard_out,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    e3.Description = "Exhaust Fan 3"
    inlbim.api.geometry.edit_object_placement(
        product=e3,
        repositioned_origin=(12.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Connect HEPA3 source port to E3 sink port
    inlbim.api.system.connect_two_distribution_ports_via_piping(
        source_port=ifcopenshell.util.system.get_ports(
            element=hepa_3,
            flow_direction="SOURCE",
        )[0],
        sink_port=ifcopenshell.util.system.get_ports(
            element=e3,
            flow_direction="SINK",
        )[0],
        nominal_diameter=0.26 / 2.0,
        thickness=1 / 10 * 0.26 / 2.0,
        material=steel_material,
        elbow_radius_type="SHORT",
        branch_name="HEPA3 to E3",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=True,
    )

    # Create ST
    stack = inlbim.api.distribution_element.create_stack(
        ifc4_file=ifc4_file,
        base_diameter=0.3556,
        height=7.62,
        name="ST",
        spatial_element=space_for_yard_out,
        distribution_system=distribution_system,
        place_object_relative_to_parent=True,
        add_shape_representation_to_ports=True,
    )
    stack.Description = "Stack"
    inlbim.api.geometry.edit_object_placement(
        product=stack,
        repositioned_origin=(19.0, 1.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(-1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Connect E3 source port to stack sink port
    inlbim.api.system.connect_two_distribution_ports_via_piping(
        source_port=ifcopenshell.util.system.get_ports(
            element=e3,
            flow_direction="SOURCE",
        )[0],
        sink_port=ifcopenshell.util.system.get_ports(
            element=stack,
            flow_direction="SINK",
        )[0],
        nominal_diameter=0.26 / 2.0,
        thickness=1 / 10 * 0.26 / 2.0,
        material=steel_material,
        elbow_radius_type="SHORT",
        branch_name="E3 to Stack",
        spatial_element=site,
        distribution_system=distribution_system,
        add_shape_representation_to_ports=True,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_manual_ventilation_system.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
