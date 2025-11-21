# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import ifcopenshell.util.representation
from typing import cast


def create_nuclear_reactor_containment_structure(
    ifc4_file: ifcopenshell.file,
    material: ifcopenshell.entity_instance,
    slab_outer_radius: float = 25.0,
    slab_thickness: float = 3.0,
    cylinder_outer_radius: float = 23.0,
    cylinder_wall_thickness: float = 1.0,
    cylinder_height: float = 35.0,
    nuclear_reactor_containment_structure: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if nuclear_reactor_containment_structure is None:
        nuclear_reactor_containment_structure = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            predefined_type="USERDEFINED",
            ifc_class="IfcElementAssembly",
            name=name,
        )
        nuclear_reactor_containment_structure.ObjectType = (
            "NUCLEAR_REACTOR_CONTAINMENT_STRUCTURE"
        )

    base_slab = ifcopenshell.api.root.create_entity(
        file=ifc4_file, ifc_class="IfcSlab", predefined_type="BASESLAB", name="Basemat"
    )

    base_slab_representation_item = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=slab_outer_radius,
            extrusion_depth=slab_thickness,
            repositioned_origin=(0.0, 0.0, -slab_thickness),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    base_slab_representation_shape_representation = (
        bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[base_slab_representation_item]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[base_slab_representation_item],
        )
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=base_slab,
        representation=base_slab_representation_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[base_slab],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=base_slab,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    hollow_cylindrical_wall = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
        predefined_type="SOLIDWALL",
        name="Cylindrical Wall",
    )

    hollow_cylindrical_wall_representation_item = (
        bim2fem.ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=cylinder_outer_radius,
            extrusion_depth=cylinder_height,
            wall_thickness=cylinder_wall_thickness,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    hollow_cylindrical_wall_shape_representation = (
        bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[hollow_cylindrical_wall_representation_item]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[hollow_cylindrical_wall_representation_item],
        )
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=hollow_cylindrical_wall,
        representation=hollow_cylindrical_wall_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[hollow_cylindrical_wall],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=hollow_cylindrical_wall,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    dome = ifcopenshell.api.root.create_entity(
        file=ifc4_file, ifc_class="IfcSlab", predefined_type="ROOF", name="Dome"
    )

    outer_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius,
    )

    inner_sphere = bim2fem.ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius - cylinder_wall_thickness,
    )

    subtracting_cylinder = (
        bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=cylinder_outer_radius * 2.0,
            extrusion_depth=cylinder_height,
            repositioned_origin=(0.0, 0.0, -cylinder_height),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )

    hollow_sphere = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=outer_sphere,
        second_items=[inner_sphere, subtracting_cylinder],
        operator="DIFFERENCE",
    )[-1]

    dome_representation_item = bim2fem.ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=hollow_sphere,
    )

    dome_shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(
                items=[dome_representation_item]
            ),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[dome_representation_item],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=dome,
        representation=dome_shape_representation,
    )

    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[dome],
        relating_object=nuclear_reactor_containment_structure,
    )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=dome,
        repositioned_origin=(0.0, 0.0, cylinder_height),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )

    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[hollow_cylindrical_wall, base_slab, dome],
        material=material,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[nuclear_reactor_containment_structure],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=nuclear_reactor_containment_structure,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return nuclear_reactor_containment_structure


def create_reactor_box(
    ifc4_file: ifcopenshell.file,
    length: float = 20.0,
    width: float = 20.0,
    height: float = 15.0,
    reactor_box: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if reactor_box is None:
        reactor_box = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcEnergyConversionDevice",
            name=name,
        )

    block = bim2fem.ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
    )

    shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(
            str,
            ifcopenshell.util.representation.guess_type(items=[block]),
        ),
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[block],
    )

    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=reactor_box,
        representation=shape_representation,
    )

    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[reactor_box],
            relating_structure=parent,
        )

    bim2fem.ifcplus.api.placement.edit_object_placement(
        product=reactor_box,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return reactor_box
