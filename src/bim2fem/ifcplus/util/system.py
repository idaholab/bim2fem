# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell.util.placement


def get_port_location(
    distribution_port: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:
    """Get IfcDistributionPort Location in Global Coordinates"""
    port_local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=distribution_port.ObjectPlacement
        )
    )
    port_origin = tuple(
        [float(row[3]) for row in port_local_placement_in_global_coordinates[0:-1]]
    )
    assert len(port_origin) == 3
    return port_origin


def get_port_z_axis(
    distribution_port: ifcopenshell.entity_instance,
) -> tuple[float, float, float]:
    """Get IfcDistributionPort Location in Global Coordinates"""
    port_local_placement_in_global_coordinates = (
        ifcopenshell.util.placement.get_local_placement(
            placement=distribution_port.ObjectPlacement
        )
    )
    port_z_axis = tuple(
        [float(row[2]) for row in port_local_placement_in_global_coordinates[0:-1]]
    )
    assert len(port_z_axis) == 3
    return port_z_axis
