# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.util.placement
from typing import Iterable
import numpy as np
import ifcopenshell.util.element
import ifcopenshell
import ifcopenshell.api.geometry


def edit_object_placement(
    product: ifcopenshell.entity_instance,
    repositioned_origin: Iterable[float] = (0, 0, 0),
    repositioned_z_axis: Iterable[float] = (0, 0, 1),
    repositioned_x_axis: Iterable[float] = (1, 0, 0),
    should_transform_children: bool = False,
    place_object_relative_to_parent: bool = False,
):
    """Edit the object placement matrix of an IfcProduct. Allows for transformation
    relative to parent entity."""

    matrix_for_global_placement = ifcopenshell.util.placement.a2p(
        o=repositioned_origin,
        z=repositioned_z_axis,
        x=repositioned_x_axis,
    )

    if place_object_relative_to_parent:
        parent = ifcopenshell.util.element.get_parent(element=product)
        parent_exists = isinstance(parent, ifcopenshell.entity_instance)
        if parent_exists:
            parent_is_a_project_entity = parent.is_a("IfcProject")
            if not parent_is_a_project_entity:
                matrix_for_parent_placement = (
                    ifcopenshell.util.placement.get_local_placement(
                        parent.ObjectPlacement
                    )
                )
                matrix_for_global_placement = np.dot(
                    matrix_for_parent_placement,
                    matrix_for_global_placement,
                )

    ifcopenshell.api.geometry.edit_object_placement(
        file=product.file,
        product=product,
        matrix=matrix_for_global_placement,
        should_transform_children=should_transform_children,
    )
