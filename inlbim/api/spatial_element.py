# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
from typing import Iterable
import inlbim.api.profile
import ifcopenshell
import ifcopenshell.api.geometry
import inlbim.api.geometry
import inlbim.api.profile
import inlbim.api.representation
import ifcopenshell.api.root
import ifcopenshell.api.aggregate


def create_arbitrary_solid_space_with_or_without_voids(
    ifc4_file: ifcopenshell.file,
    outer_profile: list[tuple[float, float]],
    inner_profiles: list[list[tuple[float, float]]],
    height: float,
    origin: Iterable[float] = (0, 0, 0),
    z_axis: Iterable[float] = (0, 0, 1),
    x_axis: Iterable[float] = (1, 0, 0),
    space: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    structure_contained_in: ifcopenshell.entity_instance | None = None,
    should_transform_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for an IfcSpace representated by a solid body
    extruded from an arbitrary profile, and then automatically assign it.
    """

    # Create Space
    if space is None:
        space = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSpace",
            name=name,
        )

    # Aggregation relationship
    if isinstance(structure_contained_in, ifcopenshell.entity_instance):
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=[space],
            relating_object=structure_contained_in,
        )
        inlbim.api.geometry.edit_object_placement(
            product=space,
            place_object_relative_to_parent=should_transform_relative_to_parent,
        )

    # Add Profile
    profile = inlbim.api.profile.add_arbitrary_profile_with_or_without_voids(
        file=ifc4_file,
        outer_profile=outer_profile,
        inner_profiles=inner_profiles,
        name=None,
    )

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile,
        extrusion_depth=height,
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="SweptSolid",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=space,
        representation=shape_model,
    )

    # Edit Placement
    inlbim.api.geometry.edit_object_placement(
        product=space,
        repositioned_origin=origin,
        repositioned_z_axis=z_axis,
        repositioned_x_axis=x_axis,
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    return space


def create_rectangular_solid_space(
    ifc4_file: ifcopenshell.file,
    length: float,
    width: float,
    height: float,
    repositioned_origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    repositioned_z_axis: tuple[float, float, float] = (0.0, 0.0, 1.0),
    repositioned_x_axis: Iterable[float] = (1, 0, 0),
    space: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    spatial_element: ifcopenshell.entity_instance | None = None,
    should_transform_relative_to_parent: bool = False,
) -> ifcopenshell.entity_instance:
    """
    Add a geometric representation for an IfcSpace representated by a solid body
    extruded from a rectangular profile, and then automatically assign it.
    """

    # Create Space
    if space is None:
        space = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSpace",
            name=name,
        )

    # Aggregation relationship
    if isinstance(spatial_element, ifcopenshell.entity_instance):
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=[space],
            relating_object=spatial_element,
        )
        inlbim.api.geometry.edit_object_placement(
            product=space,
            place_object_relative_to_parent=should_transform_relative_to_parent,
        )

    # Add Profile
    profile = inlbim.api.profile.add_arbitrary_profile_with_or_without_voids(
        file=ifc4_file,
        outer_profile=[
            (0.0, 0.0),
            (0.0 + length, 0.0),
            (0.0 + length, 0.0 + width),
            (0.0, 0.0 + width),
            (0.0, 0.0),
        ],
        inner_profiles=[],
        name=None,
    )

    # Add and assign representation
    representation_item = inlbim.api.representation.add_extruded_area_solid(
        ifc4_file=ifc4_file,
        profile=profile,
        extrusion_depth=height,
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="SweptSolid",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=space,
        representation=shape_model,
    )

    # Edit Placement
    inlbim.api.geometry.edit_object_placement(
        product=space,
        repositioned_origin=repositioned_origin,
        repositioned_z_axis=repositioned_z_axis,
        repositioned_x_axis=repositioned_x_axis,
        place_object_relative_to_parent=should_transform_relative_to_parent,
    )

    return space
