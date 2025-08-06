# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.root
import inlbim.api.representation
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import inlbim.api.geometry
import ifcopenshell.api.system
import inlbim.api.system
import ifcopenshell.util.type
import inlbim.api.element_type
import ifcopenshell.api.type
import numpy as np


PRESET_ELEMENT_TYPES = [
    "MAKEUP_AIR_UNIT",
    "MOTORIZED_VALVE",
    "GENERIC_AIR_FILTER",
    "AIR_FILTRATION_CONTAINMENT_HOUSING",
    "HPRS_EXHAUST_FAN",
    "STACK",
]


def create_make_up_air_unit(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcUnitaryEquipment",
            name=name,
            predefined_type="AIRHANDLER",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length,
            width=width,
            height=height,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=height,
            width=width,
            height=2 * height,
            repositioned_origin=(0.0, 0.0, height),
            repositioned_z_axis=(1.0, 0.0, -1.0),
            repositioned_x_axis=(-1.0, 0.0, -1.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=["DIFFERENCE"],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="MAKEUP_AIR_UNIT",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (length, width / 2.0, height / 2)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SOURCE"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1],
            arrow_size=0.10 * height,
        )

    return element


def create_motorized_valve(
    ifc4_file: ifcopenshell.file,
    outer_diameter: float,
    thickness: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcValve",
            name=name,
            predefined_type="MOTORIZED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=2 * outer_diameter,
            width=2 / 5 * outer_diameter,
            height=2 / 5 * outer_diameter,
            repositioned_origin=(0.0, 0.0, outer_diameter),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Cylinder
            ifc4_file=ifc4_file,
            radius=outer_diameter / 2.0,
            extrusion_depth=2 / 5 * outer_diameter,
            repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 1.0),
        ),
        inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Cylinder
            ifc4_file=ifc4_file,
            radius=outer_diameter / 2.0 - thickness,
            extrusion_depth=2 / 5 * outer_diameter,
            repositioned_origin=(1.5 * outer_diameter, 0.0, outer_diameter / 2.0),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 1.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=["UNION", "DIFFERENCE"],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="MOTORIZED_VALVE",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (
        1.5 * outer_diameter,
        0.0,
        outer_diameter / 2.0,
    )
    port1_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1_x_axis_in_object_coordinates = (1.0, 0.0, 1.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        1.5 * outer_diameter,
        2 / 5 * outer_diameter,
        outer_diameter / 2.0,
    )
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 1.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.10 * outer_diameter,
        )

    return element


def create_generic_air_filter(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    thickness = 1 / 12 * length
    operands = [
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length,
            width=width,
            height=height,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length - thickness * 2,
            width=width,
            height=height - thickness * 2,
            repositioned_origin=(thickness, 0.0, thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length - thickness * 2,
            width=width / 4.0,
            height=height - thickness * 2,
            repositioned_origin=(thickness, width / 8.0, thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
    ]

    # # Set Boolean operations
    # boolean_operations = ["DIFFERENCE", "UNION"]

    # # Subtract Holes
    # origin_coordinates_for_holes = inlbim.util.geometry.generate_grid_points(
    #     x_min=1 / 6 * length,
    #     x_max=5 / 6 * length,
    #     y_min=1 / 6 * height,
    #     y_max=5 / 6 * height,
    #     x_spacing=1 / 6 * length,
    #     y_spacing=1 / 6 * height,
    # )
    # for origin_coordinates_for_hole in origin_coordinates_for_holes:
    #     x_pos = origin_coordinates_for_hole[0]
    #     z_pos = origin_coordinates_for_hole[1]
    #     operands.append(
    #         inlbim.api.representation.add_cylindrical_extruded_area_solid(  # Cylinder
    #             ifc4_file=ifc4_file,
    #             radius=hole_size / 2.0,
    #             extrusion_depth=hole_depth,
    #             repositioned_origin=(x_pos, 0.0, z_pos),
    #             repositioned_z_axis=(0.0, 1.0, 0.0),
    #             repositioned_x_axis=(1.0, 0.0, 1.0),
    #         )
    #     )
    #     boolean_operations.append("DIFFERENCE")

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "DIFFERENCE",
            "UNION",
        ],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="GENERIC_AIR_FILTER",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (
        0.0 + length / 2.0,
        0.0,
        0.0 + height / 2.0,
    )
    port1_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        0.0 + length / 2,
        0.0 + width,
        0.0 + height / 2,
    )
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.4 * thickness,
        )

    return element


# def create_chiller(
#     ifc4_file: ifcopenshell.file,
#     length: float,
#     width: float,
#     height: float,
#     element: ifcopenshell.entity_instance | None = None,
#     name: str | None = None,
#     spatial_element: ifcopenshell.entity_instance | None = None,
#     distribution_system: ifcopenshell.entity_instance | None = None,
#     place_object_relative_to_parent: bool = False,
#     add_shape_representation_to_ports: bool = False,
# ) -> ifcopenshell.entity_instance:

#     # Create Element
#     if element is None:
#         element = ifcopenshell.api.root.create_entity(
#             file=ifc4_file,
#             ifc_class="IfcFilter",
#             name=name,
#             predefined_type="AIRPARTICLEFILTER",
#         )

#     # Assign spatial container
#     if isinstance(spatial_element, ifcopenshell.entity_instance):
#         ifcopenshell.api.spatial.assign_container(
#             file=ifc4_file,
#             products=[element],
#             relating_structure=spatial_element,
#         )
#         inlbim.api.geometry.edit_object_placement(
#             product=element,
#             place_object_relative_to_parent=True,
#         )

#     # Assign System
#     if isinstance(distribution_system, ifcopenshell.entity_instance):
#         ifcopenshell.api.system.assign_system(
#             file=ifc4_file,
#             products=[element],
#             system=distribution_system,
#         )

#     # Create Constituted Solid Geometry
#     thickness = 1 / 12 * length
#     operands = [
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=length,
#             width=width,
#             height=height,
#             repositioned_origin=(0.0, 0.0, 0.0),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=0.54 * length,
#             width=width,
#             height=0.29 * height,
#             repositioned_origin=(0.07 * length, 0.0, 0.23 * height),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=0.30 * length,
#             width=width,
#             height=0.29 * height,
#             repositioned_origin=(0.65 * length, 0.0, 0.23 * height),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=0.54 * length,
#             width=width - 2 / 8 * width,
#             height=0.29 * height,
#             repositioned_origin=(0.07 * length, 1 / 8 * width, 0.0),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=0.30 * length,
#             width=width - 2 / 8 * width,
#             height=0.29 * height,
#             repositioned_origin=(0.65 * length, 1 / 8 * width, 0.0),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#         inlbim.api.representation.add_block(  # Block
#             ifc4_file=ifc4_file,
#             length=length,
#             width=width - 2 / 8 * width,
#             height=0.29 * height,
#             repositioned_origin=(0.0, 1 / 8 * width, 0.23 * height),
#             repositioned_z_axis=(0.0, 0.0, 1.0),
#             repositioned_x_axis=(1.0, 0.0, 0.0),
#         ),
#     ]

#     # Add and Assign Representation
#     representation_item = inlbim.api.representation.add_csg_solid(
#         operands=operands,
#         boolean_operators=[
#             "DIFFERENCE",
#             "DIFFERENCE",
#             "DIFFERENCE",
#             "DIFFERENCE",
#             "DIFFERENCE",
#         ],
#     )
#     shape_model = inlbim.api.representation.add_shape_model(
#         ifc4_file=ifc4_file,
#         shape_model_class="IfcShapeRepresentation",
#         representation_identifier="Body",
#         representation_type="CSG",
#         context_type="Model",
#         target_view="MODEL_VIEW",
#         items=[representation_item],
#     )
#     ifcopenshell.api.geometry.assign_representation(
#         file=ifc4_file,
#         product=element,
#         representation=shape_model,
#     )

#     # Edit Element Placement
#     inlbim.api.geometry.edit_object_placement(
#         product=element,
#         repositioned_origin=(0.0, 0.0, 0.0),
#         repositioned_z_axis=(0.0, 0.0, 1.0),
#         repositioned_x_axis=(1.0, 0.0, 0.0),
#         place_object_relative_to_parent=place_object_relative_to_parent,
#     )

#     # Add and Assign Type
#     element_type = inlbim.api.element_type.add_element_type(
#         ifc4_file=ifc4_file,
#         ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
#             0
#         ],
#         name="AIR_FILTRATION_CONTAINMENT_HOUSING",
#         check_for_duplicate=True,
#     )
#     ifcopenshell.api.type.assign_type(
#         file=ifc4_file,
#         related_objects=[element],
#         relating_type=element_type,
#     )

#     # Port 1
#     port1_origin_in_object_coordinates = (
#         0.0 + length / 2.0,
#         0.0,
#         0.0 + height / 2.0,
#     )
#     port1_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
#     port1_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
#     port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
#     port1.FlowDirection = "SINK"
#     port1.PredefinedType = "DUCT"
#     if isinstance(distribution_system, ifcopenshell.entity_instance):
#         port1.SystemType = distribution_system.PredefinedType
#     inlbim.api.geometry.edit_object_placement(
#         product=port1,
#         place_object_relative_to_parent=False,
#     )
#     port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
#     inlbim.api.geometry.edit_object_placement(
#         product=port1,
#         repositioned_origin=port1_origin_in_object_coordinates,
#         repositioned_z_axis=port1_z_axis_in_object_coordinates,
#         repositioned_x_axis=port1_x_axis_in_object_coordinates,
#         place_object_relative_to_parent=True,
#     )

#     # Port 2
#     port2_origin_in_object_coordinates = (
#         0.0 + length / 2,
#         0.0 + width,
#         0.0 + height / 2,
#     )
#     port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
#     port2_x_axis_in_object_coordinates = (-1.0, 0.0, 0.0)
#     port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
#     port2.FlowDirection = "SOURCE"
#     port2.PredefinedType = "DUCT"
#     if isinstance(distribution_system, ifcopenshell.entity_instance):
#         port2.SystemType = distribution_system.PredefinedType
#     inlbim.api.geometry.edit_object_placement(
#         product=port2,
#         place_object_relative_to_parent=False,
#     )
#     port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
#     inlbim.api.geometry.edit_object_placement(
#         product=port2,
#         repositioned_origin=port2_origin_in_object_coordinates,
#         repositioned_z_axis=port2_z_axis_in_object_coordinates,
#         repositioned_x_axis=port2_x_axis_in_object_coordinates,
#         place_object_relative_to_parent=True,
#     )

#     if add_shape_representation_to_ports:
#         inlbim.api.system.add_shape_representation_to_distribution_ports(
#             ports=[port1, port2],
#             arrow_size=0.4 * thickness,
#         )

#     return element


def create_air_filtration_containment_housing(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFilter",
            name=name,
            predefined_type="AIRPARTICLEFILTER",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=length - 4 / 25 * length,
            width=width,
            height=height,
            repositioned_origin=(2 / 25 * length, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_rectangular_pyramid(
            ifc4_file=ifc4_file,
            length=height,
            width=width,
            height=3 / 25 * length,
            repositioned_origin=(23 / 25 * length, 0.0, height),
            repositioned_z_axis=(1.0, 0.0, 0.0),
            repositioned_x_axis=(0.0, 0.0, -1.0),
        ),
        inlbim.api.representation.add_rectangular_pyramid(
            ifc4_file=ifc4_file,
            length=height,
            width=width,
            height=3 / 25 * length,
            repositioned_origin=(2 / 25 * length, 0.0, 0.0),
            repositioned_z_axis=(-1.0, 0.0, 0.0),
            repositioned_x_axis=(0.0, 0.0, 1.0),
        ),
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=2 / 25 * length,
            width=width,
            height=height,
            repositioned_origin=(-2 / 25 * length, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=2 / 25 * length,
            width=width,
            height=height,
            repositioned_origin=(length, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "UNION",
            "UNION",
            "DIFFERENCE",
            "DIFFERENCE",
        ],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="AIR_FILTRATION_CONTAINMENT_HOUSING",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (0.0, width / 2.0, height / 2.0)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (length, width / 2.0, height / 2.0)
    port2_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * height,
        )

    return element


def create_hprs_exhaust_fan(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcFan",
            name=name,
            predefined_type="CENTRIFUGALBACKWARDINCLINEDCURVED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        inlbim.api.representation.add_block(  # Block
            ifc4_file=ifc4_file,
            length=5 / 5 * length,
            width=width,
            height=3 / 4 * height,
            repositioned_origin=(1 / 5 * length, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        inlbim.api.representation.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=width / 2.0,
            extrusion_depth=1 / 5 * length,
            repositioned_origin=(1 / 5 * length, width / 2.0, 2.5 / 4 * height),
            repositioned_z_axis=(-1.0, 0.0, 0.0),
            repositioned_x_axis=(0.0, 0.0, 1.0),
        ),
        inlbim.api.representation.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=1 / 10 * length * 0.9,
            wall_thickness=1 / 10 * 1 / 10 * length * 0.9,
            extrusion_depth=width / 2.0,
            repositioned_origin=(
                1 / 10 * length,
                width / 2.0,
                3.5 / 4 * height,
            ),
            repositioned_z_axis=(0.0, 1.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "UNION",
            "UNION",
        ],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="HPRS_EXHAUST_FAN",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (0.0, width / 2.0, 2.5 / 4 * height)
    port1_z_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (1 / 10 * length, width, 3.5 / 4.0 * height)
    port2_z_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * height,
        )

    return element


def create_stack(
    ifc4_file: ifcopenshell.file,
    base_diameter: float,
    height: float,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    distribution_system: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
    add_shape_representation_to_ports: bool = False,
) -> ifcopenshell.entity_instance:

    # Create Element
    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcDistributionElement",
            name=name,
            predefined_type="NOTDEFINED",
        )

    # Assign spatial container
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=element,
            place_object_relative_to_parent=True,
        )

    # Assign System
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        ifcopenshell.api.system.assign_system(
            file=ifc4_file,
            products=[element],
            system=distribution_system,
        )

    # Create Constituted Solid Geometry
    operands = [
        inlbim.api.representation.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=height,
            repositioned_origin=(base_diameter / 2.0, base_diameter / 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        ),
        # inlbim.api.representation.add_cylindrical_extruded_area_solid(
        #     ifc4_file=ifc4_file,
        #     radius=base_diameter / 2.0,
        #     extrusion_depth=base_diameter * 1.5,
        #     repositioned_origin=(
        #         base_diameter / 2.0,
        #         base_diameter / 2.0,
        #         1 / 5 * height,
        #     ),
        #     repositioned_z_axis=(1.0, 0.0, -1.0),
        #     repositioned_x_axis=(0.0, 1.0, 0.0),
        # ),
        inlbim.api.representation.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=base_diameter / 2.0,
            wall_thickness=0.10 * base_diameter,
            extrusion_depth=1.5 * 2 / np.sqrt(2) * base_diameter,
            repositioned_origin=(
                base_diameter * 2.0,
                base_diameter / 2.0,
                1 / 5 * height,
            ),
            repositioned_z_axis=(-1.0, 0.0, 1.0),
            repositioned_x_axis=(0.0, 1.0, 0.0),
        ),
    ]

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_csg_solid(
        operands=operands,
        boolean_operators=[
            "UNION",
        ],
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
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    # Add and Assign Type
    element_type = inlbim.api.element_type.add_element_type(
        ifc4_file=ifc4_file,
        ifc_class=ifcopenshell.util.type.get_applicable_types(ifc_class=element.is_a())[
            0
        ],
        name="STACK",
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_file,
        related_objects=[element],
        relating_type=element_type,
    )

    # Port 1
    port1_origin_in_object_coordinates = (
        base_diameter * 2.0,
        base_diameter / 2.0,
        1 / 5 * height,
    )
    port1_z_axis_in_object_coordinates = (-1.0, 0.0, 1.0)
    port1_x_axis_in_object_coordinates = (0.0, 1.0, 0.0)
    port1 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port1.FlowDirection = "SINK"
    port1.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port1.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        place_object_relative_to_parent=False,
    )
    port1.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port1,
        repositioned_origin=port1_origin_in_object_coordinates,
        repositioned_z_axis=port1_z_axis_in_object_coordinates,
        repositioned_x_axis=port1_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    # Port 2
    port2_origin_in_object_coordinates = (
        base_diameter / 2.0,
        base_diameter / 2.0,
        height,
    )
    port2_z_axis_in_object_coordinates = (0.0, 0.0, 1.0)
    port2_x_axis_in_object_coordinates = (1.0, 0.0, 0.0)
    port2 = ifcopenshell.api.system.add_port(file=ifc4_file, element=element)
    port2.FlowDirection = "SOURCE"
    port2.PredefinedType = "DUCT"
    if isinstance(distribution_system, ifcopenshell.entity_instance):
        port2.SystemType = distribution_system.PredefinedType
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        place_object_relative_to_parent=False,
    )
    port2.ObjectPlacement.PlacementRelTo = element.ObjectPlacement
    inlbim.api.geometry.edit_object_placement(
        product=port2,
        repositioned_origin=port2_origin_in_object_coordinates,
        repositioned_z_axis=port2_z_axis_in_object_coordinates,
        repositioned_x_axis=port2_x_axis_in_object_coordinates,
        place_object_relative_to_parent=True,
    )

    if add_shape_representation_to_ports:
        inlbim.api.system.add_shape_representation_to_distribution_ports(
            ports=[port1, port2],
            arrow_size=0.1 * base_diameter,
        )

    return element
