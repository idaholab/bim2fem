# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.util.representation
import numpy as np


def get_precision_of_project(
    ifc4_file: ifcopenshell.file,
) -> float:

    # Get Model Precision
    geometric_representation_context = ifcopenshell.util.representation.get_context(
        ifc_file=ifc4_file, context="Model"
    )
    assert geometric_representation_context
    model_precision = geometric_representation_context.Precision

    return model_precision


def get_numeric_scale_of_project(
    ifc4_file: ifcopenshell.file,
) -> int:

    # Get Precision
    precision = get_precision_of_project(ifc4_file=ifc4_file)

    # Get Numeric Scale (the maximum number of decimal places)
    numeric_scale = int(-1 * np.log10(precision))

    return numeric_scale
