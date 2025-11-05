# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell.util.placement
import ifcplus.util.geometry


def get_port_location(
    distribution_port: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:
    """Get IfcDistributionPort Location in Global Coordinates"""
    port_local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=distribution_port.ObjectPlacement
        )
    )
    x_val = float(port_local_placement_in_global_coordinates[0][3])
    y_val = float(port_local_placement_in_global_coordinates[1][3])
    z_val = float(port_local_placement_in_global_coordinates[2][3])

    return x_val, y_val, z_val


def get_port_z_axis(
    distribution_port: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:
    """Get IfcDistributionPort Z-Axis in Global Coordinates. The Z-axis points in the
    direction of flow."""

    port_local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=distribution_port.ObjectPlacement
        )
    )
    val_1 = float(port_local_placement_in_global_coordinates[0][2])
    val_2 = float(port_local_placement_in_global_coordinates[1][2])
    val_3 = float(port_local_placement_in_global_coordinates[2][2])

    port_z_axis = ifcplus.util.geometry.unit_normalize_vector(
        vector=(val_1, val_2, val_3)
    )

    return port_z_axis
