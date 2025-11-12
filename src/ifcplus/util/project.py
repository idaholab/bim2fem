# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.util.representation
import numpy as np
from typing import cast


def get_precision_of_project(
    ifc4_file: ifcopenshell.file,
) -> float:

    geometric_representation_context = ifcopenshell.util.representation.get_context(
        ifc_file=ifc4_file,
        context="Model",
    )
    model_precision = cast(
        ifcopenshell.entity_instance, geometric_representation_context
    ).Precision

    return model_precision


def get_numeric_scale_of_project(
    ifc4_file: ifcopenshell.file,
) -> int:

    precision = get_precision_of_project(ifc4_file=ifc4_file)
    numeric_scale = int(-1 * np.log10(precision))

    return numeric_scale
