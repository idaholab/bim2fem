# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.util.representation


def get_single_extruded_area_solid_representation(
    element: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:

    body_representation = ifcopenshell.util.representation.get_representation(
        element=element,
        context="Model",
        subcontext="Body",
        target_view="MODEL_VIEW",
    )
    if body_representation:
        body_representation = ifcopenshell.util.representation.resolve_representation(
            representation=body_representation
        )
        if body_representation.RepresentationType == "SweptSolid":
            if len(body_representation.Items) != 1:
                return None
            representation_item = body_representation.Items[0]
            if representation_item.is_a("IfcExtrudedAreaSolid"):
                return representation_item

    return None


def get_local_origin_and_axes_of_extruded_area_solid(
    extruded_area_solid: ifcopenshell.entity_instance,
) -> tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]:

    pos = extruded_area_solid.Position

    local_origin = pos.Location.Coordinates

    if pos.Axis is None:
        local_z_axis = (0.0, 0.0, 1.0)
    else:
        local_z_axis = pos.Axis.DirectionRatios

    if pos.RefDirection is None:
        local_x_axis = (1.0, 0.0, 0.0)
    else:
        local_x_axis = pos.RefDirection.DirectionRatios

    return local_origin, local_z_axis, local_x_axis
