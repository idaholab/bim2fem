# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.aggregate
import ifcopenshell.api.root
import ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.spatial
import ifcplus.api.placement
import ifcopenshell.util.representation
from typing import cast
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcplus.api.placement
import ifcplus.api.geometry
import ifcopenshell.api.geometry
import ifcopenshell.api.material
import numpy as np
import ifcopenshell.util.representation
from typing import cast


def create_reactor_containment_structure(
    ifc4_file: ifcopenshell.file,
    material: ifcopenshell.entity_instance,
    slab_outer_radius: float = 25.0,
    slab_thickness: float = 3.0,
    cylinder_outer_radius: float = 23.0,
    cylinder_wall_thickness: float = 1.0,
    cylinder_height: float = 35.0,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            predefined_type="USERDEFINED",
            ifc_class="IfcElementAssembly",
            name=name,
        )
        element.ObjectType = "REACTOR_CONTAINMENT_STRUCTURE"
    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=parent,
        )
    ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    base_slab = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSlab",
        predefined_type="BASESLAB",
    )
    base_slab_representation = ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
        ifc4_file=ifc4_file,
        radius=slab_outer_radius,
        extrusion_depth=slab_thickness,
        repositioned_origin=(0.0, 0.0, -slab_thickness),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )
    base_slab_representation_type = ifcopenshell.util.representation.guess_type(
        items=[base_slab_representation]
    )
    base_slab_shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, base_slab_representation_type),
        items=[base_slab_representation],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=base_slab,
        representation=base_slab_shape_model,
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[base_slab],
        relating_object=element,
    )
    ifcplus.api.placement.edit_object_placement(
        product=base_slab,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[base_slab],
        material=material,
    )

    cylindrical_wall = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcWall",
        predefined_type="SOLIDWALL",
    )
    cylindrical_wall_representation = (
        ifcplus.api.geometry.add_hollow_cylindrical_extruded_area_solid(
            ifc4_file=ifc4_file,
            radius=cylinder_outer_radius,
            extrusion_depth=cylinder_height,
            wall_thickness=cylinder_wall_thickness,
            repositioned_origin=(0.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
    )
    cylindrical_wall_representation_type = ifcopenshell.util.representation.guess_type(
        items=[cylindrical_wall_representation]
    )
    cylindrical_wall_shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, cylindrical_wall_representation_type),
        items=[cylindrical_wall_representation],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=cylindrical_wall,
        representation=cylindrical_wall_shape_model,
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[cylindrical_wall],
        relating_object=element,
    )
    ifcplus.api.placement.edit_object_placement(
        product=cylindrical_wall,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[cylindrical_wall],
        material=material,
    )

    dome = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcRoof",
        predefined_type="DOME_ROOF",
    )
    outer_sphere = ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius,
    )
    inner_sphere = ifcplus.api.geometry.add_sphere(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius - cylinder_wall_thickness,
    )
    subtracting_cylinder = ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
        ifc4_file=ifc4_file,
        radius=cylinder_outer_radius * 2.0,
        extrusion_depth=cylinder_height,
        repositioned_origin=(0.0, 0.0, -cylinder_height),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
    )
    hollow_sphere = ifcopenshell.api.geometry.add_boolean(
        file=ifc4_file,
        first_item=outer_sphere,
        second_items=[inner_sphere, subtracting_cylinder],
        operator="DIFFERENCE",
    )[-1]
    dome_representation = ifcplus.api.geometry.add_csg_solid(
        boolean_result_or_primitive=hollow_sphere,
    )
    dome_representation_type = ifcopenshell.util.representation.guess_type(
        items=[dome_representation]
    )
    dome_representation_shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, dome_representation_type),
        items=[dome_representation],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=dome,
        representation=dome_representation_shape_model,
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[dome],
        relating_object=element,
    )
    ifcplus.api.placement.edit_object_placement(
        product=dome,
        repositioned_origin=(0.0, 0.0, cylinder_height),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=True,
    )
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[dome],
        material=material,
    )

    return element


def create_reactor_box(
    ifc4_file: ifcopenshell.file,
    length: float = 20.0,
    width: float = 20.0,
    height: float = 15.0,
    element: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    parent: ifcopenshell.entity_instance | None = None,
    place_object_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:

    if element is None:
        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcEnergyConversionDevice",
            name=name,
        )

    element_representation = ifcplus.api.geometry.add_block(
        ifc4_file=ifc4_file,
        length=length,
        width=width,
        height=height,
    )
    element_representation_type = ifcopenshell.util.representation.guess_type(
        items=[element_representation]
    )
    element_shape_model = ifcplus.api.geometry.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type=cast(str, element_representation_type),
        items=[element_representation],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=element_shape_model,
    )
    if isinstance(parent, ifcopenshell.entity_instance):
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[element],
            relating_structure=parent,
        )
    ifcplus.api.placement.edit_object_placement(
        product=element,
        repositioned_origin=(0.0, 0.0, 0.0),
        repositioned_z_axis=(0.0, 0.0, 1.0),
        repositioned_x_axis=(1.0, 0.0, 0.0),
        place_object_relative_to_parent=place_object_relative_to_parent,
    )

    return element
