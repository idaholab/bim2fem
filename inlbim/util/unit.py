# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import math
from typing import Literal


def round_to_sig_digits(value: float, digits: int) -> float:
    """Round to significant digits

    Args:
        value (float): _description_
        digits (int): _description_

    Returns:
        float: _description_

    Example:

    .. code:: python

        number = 12345.6789
        significant_digits = 3

        rounded_number = round_to_sig_digits(number, significant_digits)
        print(f"{number} rounded to {significant_digits} significant digits is {rounded_number}")
    """
    if value == 0:
        return 0
    else:
        # Calculate the factor to scale the number
        factor = math.pow(10, digits - int(math.floor(math.log10(abs(value)))) - 1)
        # Round the number using the factor
        return round(value * factor) / factor


def count_significant_digits(value: float) -> int:
    """_summary_

    Args:
        value (float): _description_

    Returns:
        int: _description_

    Example:

    .. code:: python

        number1 = 12345.6789
        number2 = 0.0012345
        number3 = 1000
        number4 = 0.000

        print(f"{number1} has {count_significant_digits(number1)} significant digits")
        print(f"{number2} has {count_significant_digits(number2)} significant digits")
        print(f"{number3} has {count_significant_digits(number3)} significant digits")
        print(f"{number4} has {count_significant_digits(number4)} significant digits")
    """
    if value == 0:
        return 1  # Zero is considered to have one significant digit
    else:
        # Convert the number to a string and remove the decimal point
        value_str = f"{value:.15g}"  # Use scientific notation to handle very small/large numbers
        value_str = value_str.replace(".", "").replace("-", "").replace("e", "")

        # Count the number of digits, ignoring leading zeros
        significant_digits = len(value_str.lstrip("0"))
        return significant_digits


def convert_unit_of_value(
    value: float, conversion_factor: float, use_sig_figs: bool = False
) -> float:
    """Convert unit of given value

    Args:
        value (float): _description_
        conversion_factor (float): _description_

    Returns:
        float: _description_
    """

    if use_sig_figs:

        sig_figs = count_significant_digits(value=value)

        converted_value = round_to_sig_digits(
            value=value * conversion_factor, digits=sig_figs
        )

        return converted_value

    else:
        return value * conversion_factor


UNIT_OF_LENGTH = Literal[
    "millimeter",
    "centimeter",
    "decimeter",
    "meter",
    "kilometer",
    "inch",
    "foot",
    "yard",
    "mile",
    "nautical mile",
    "micron",
    "nanometer",
    "angstrom",
]

conversion_factors_to_meters = {
    "millimeter": 0.001,
    "centimeter": 0.01,
    "decimeter": 0.1,
    "meter": 1.0,
    "kilometer": 1000.0,
    "inch": 0.0254,
    "foot": 0.3048,
    "yard": 0.9144,
    "mile": 1609.34,
    "nautical mile": 1852.0,
    "micron": 1e-6,
    "nanometer": 1e-9,
    "angstrom": 1e-10,
}


def get_conversion_factor_to_meters(given_unit: UNIT_OF_LENGTH) -> float:
    return conversion_factors_to_meters[given_unit]
