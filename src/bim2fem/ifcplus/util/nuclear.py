# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


def get_scaling_factor_for_reactor_pressure_vessel(
    thermal_capacity: float = 3500.0e6,  # Wth
) -> float:

    baseline_thermal_capacity = 3500e6  # Wth

    scaling_factor = (thermal_capacity / baseline_thermal_capacity) ** (1 / 3)

    return scaling_factor


def get_scaling_factor_for_steam_generator(
    thermal_capacity: float = 3500.0e6,  # Wth
) -> float:

    baseline_thermal_capacity = 3500e6  # Wth

    scaling_factor = (thermal_capacity / baseline_thermal_capacity) ** (1 / 3)

    return scaling_factor


def get_scaling_factor_for_reactor_coolant_pump(
    flow_rate: float = 5.5,  # m^3/s
) -> float:

    baseline_flow_rate = 5.5

    scaling_factor = (flow_rate / baseline_flow_rate) ** (1 / 3)

    return scaling_factor
