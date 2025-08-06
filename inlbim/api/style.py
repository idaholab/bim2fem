# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

from typing import Union
import ifcopenshell
import ifcopenshell.util.representation
import ifcopenshell.api.style
import random

RGB_TRIPLET = Union[tuple[float, float, float]]


def generate_random_rgb():
    """Generates a random RGB triplet."""
    r = random.randint(0, 255) / 255
    g = random.randint(0, 255) / 255
    b = random.randint(0, 255) / 255
    return (r, g, b)


def assign_color_to_element(
    element: ifcopenshell.entity_instance,
    rgb_triplet: RGB_TRIPLET,
    transparency: float = 0.0,
    # subcontext: REPRESENTATION_IDENTIFIER = "Body",
) -> ifcopenshell.entity_instance:
    """Assign color to the representation of an IfcElement"""

    shape_representation = ifcopenshell.util.representation.get_representation(
        element=element,
        context="Model",
        # subcontext=subcontext,
    )
    assert isinstance(shape_representation, ifcopenshell.entity_instance)

    style = ifcopenshell.api.style.add_style(file=element.file)
    ifcopenshell.api.style.add_surface_style(
        file=element.file,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={
            "SurfaceColour": {
                "Name": None,
                "Red": rgb_triplet[0],
                "Green": rgb_triplet[1],
                "Blue": rgb_triplet[2],
            },
            "Transparency": transparency,  # 0 is opaque, 1 is transparent
        },
    )
    ifcopenshell.api.style.assign_representation_styles(
        file=element.file,
        shape_representation=shape_representation,
        styles=[style],
    )

    return style


def assign_color_to_material(
    material: ifcopenshell.entity_instance,
    rgb_triplet: RGB_TRIPLET,
    transparency: float = 0.0,
) -> ifcopenshell.entity_instance:
    """Assign color to an IfcMaterial"""

    body_subcontext = ifcopenshell.util.representation.get_context(
        ifc_file=material.file,
        context="Model",
        subcontext="Body",
    )
    assert isinstance(body_subcontext, ifcopenshell.entity_instance)

    style = ifcopenshell.api.style.add_style(file=material.file)
    ifcopenshell.api.style.add_surface_style(
        file=material.file,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={
            "SurfaceColour": {
                "Name": None,
                "Red": rgb_triplet[0],
                "Green": rgb_triplet[1],
                "Blue": rgb_triplet[2],
            },
            "Transparency": transparency,  # 0 is opaque, 1 is transparent
        },
    )
    ifcopenshell.api.style.assign_material_style(
        file=material.file, material=material, style=style, context=body_subcontext
    )

    return style
