# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
from typing import Literal
import inlbim.util.file
import ifcopenshell.api.attribute
import ifcopenshell.api.profile
import numpy as np
import pickle
import os
import ifcopenshell.api.pset
import inlbim.util.unit
from inlbim import REGION

PARAMETERIZED_PROFILE_CLASSES = Literal[
    "IfcRectangleProfileDef",
    "IfcRectangleHollowProfileDef",
    "IfcCircleProfileDef",
    "IfcCircleHollowProfileDef",
    "IfcIShapeProfileDef",
    "IfcLShapeProfileDef",
    "IfcUShapeProfileDef",
    "IfcTShapeProfileDef",
]

TARGET_LENGTHS = {
    "IfcRectangleProfileDef": 2,
    "IfcRectangleHollowProfileDef": 5,
    "IfcCircleProfileDef": 1,
    "IfcCircleHollowProfileDef": 2,
    "IfcIShapeProfileDef": 7,
    "IfcLShapeProfileDef": 6,
    "IfcUShapeProfileDef": 7,
    "IfcTShapeProfileDef": 9,
}


def extend_list_to_length(lst: list, target_length: int) -> list:
    while len(lst) < target_length:
        lst.append(None)
    return lst


def add_parameterized_profile(
    ifc4_file: ifcopenshell.file,
    profile_class: PARAMETERIZED_PROFILE_CLASSES,
    dimensions: list[float | None],
    profile_name: str | None = None,
    check_for_duplicate: bool = False,
    calculate_mechanical_properties: bool = False,
) -> ifcopenshell.entity_instance:

    precision = inlbim.util.file.get_precision_of_project(ifc4_file=ifc4_file)

    dimensions = extend_list_to_length(
        lst=dimensions, target_length=TARGET_LENGTHS[profile_class]
    )

    if check_for_duplicate:
        dimensions_array = np.array([dim if dim else 0 for dim in dimensions])
        old_profiles = ifc4_file.by_type(type=profile_class, include_subtypes=False)
        for old_profile in old_profiles:
            old_profile_class = old_profile.is_a()
            classes_match = old_profile_class == profile_class
            if not classes_match:
                continue
            old_dimensions = list(old_profile.get_info().values())[5:]
            if len(dimensions) != len(old_dimensions):
                exit("unexpected behavior")
            old_dimensions_array = np.array(
                [dim if dim else 0 for dim in old_dimensions]
            )
            dims_are_close_in_value = True
            for dim, old_dim in zip(dimensions_array, old_dimensions_array):
                difference = abs(dim - old_dim)
                if difference > precision:
                    dims_are_close_in_value = False
                    break
            if dims_are_close_in_value:
                return old_profile

    profile = ifcopenshell.api.profile.add_parameterized_profile(
        file=ifc4_file,
        ifc_class=profile_class,
    )

    def join_profile_dims_into_string(profile_dims: list):
        return "x".join(
            str(np.round(x * 1000, 1)) if x is not None else "0" for x in profile_dims
        )

    if profile_class == "IfcRectangleProfileDef":
        if not profile_name:
            profile_name = "R_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "XDim": dimensions[0],
                "YDim": dimensions[1],
            },
        )

    elif profile_class == "IfcRectangleHollowProfileDef":
        if not profile_name:
            profile_name = "RH_" + join_profile_dims_into_string(
                profile_dims=dimensions
            )
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "XDim": dimensions[0],
                "YDim": dimensions[1],
                "WallThickness": dimensions[2],
                "InnerFilletRadius": dimensions[3],
                "OuterFilletRadius": dimensions[4],
            },
        )

    elif profile_class == "IfcCircleProfileDef":
        if not profile_name:
            profile_name = "C_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "Radius": dimensions[0],
            },
        )

    elif profile_class == "IfcCircleHollowProfileDef":
        if not profile_name:
            profile_name = "CH_" + join_profile_dims_into_string(
                profile_dims=dimensions
            )
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "Radius": dimensions[0],
                "WallThickness": dimensions[1],
            },
        )

    elif profile_class == "IfcIShapeProfileDef":
        if not profile_name:
            profile_name = "I_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "OverallWidth": dimensions[0],
                "OverallDepth": dimensions[1],
                "WebThickness": dimensions[2],
                "FlangeThickness": dimensions[3],
                "FilletRadius": dimensions[4],
                "FlangeEdgeRadius": dimensions[5],
                "FlangeSlope": dimensions[6],
            },
        )

    elif profile_class == "IfcLShapeProfileDef":
        if not profile_name:
            profile_name = "L_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "Depth": dimensions[0],
                "Width": dimensions[1],
                "Thickness": dimensions[2],
                "FilletRadius": dimensions[3],
                "EdgeRadius": dimensions[4],
                "LegSlope": dimensions[5],
            },
        )

    elif profile_class == "IfcUShapeProfileDef":
        if not profile_name:
            profile_name = "U_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "Depth": dimensions[0],
                "FlangeWidth": dimensions[1],
                "WebThickness": dimensions[2],
                "FlangeThickness": dimensions[3],
                "FilletRadius": dimensions[4],
                "EdgeRadius": dimensions[5],
                "FlangeSlope": dimensions[6],
            },
        )

    elif profile_class == "IfcTShapeProfileDef":
        if not profile_name:
            profile_name = "T_" + join_profile_dims_into_string(profile_dims=dimensions)
        ifcopenshell.api.attribute.edit_attributes(
            file=ifc4_file,
            product=profile,
            attributes={
                "ProfileType": "AREA",
                "ProfileName": profile_name,
                "Depth": dimensions[0],
                "FlangeWidth": dimensions[1],
                "WebThickness": dimensions[2],
                "FlangeThickness": dimensions[3],
                "FilletRadius": dimensions[4],
                "FlangeEdgeRadius": dimensions[5],
                "WebEdgeRadius": dimensions[6],
                "WebSlope": dimensions[7],
                "FlangeSlope": dimensions[8],
            },
        )

    if calculate_mechanical_properties:

        sect_data = None
        if profile_class == "IfcLShapeProfileDef":
            sect_data = calculate_section_data_for_l_shape(profile=profile)
        elif profile_class == "IfcRectangleProfileDef":
            sect_data = calculate_section_data_for_rect_shape(profile=profile)
        elif profile_class == "IfcRectangleHollowProfileDef":
            sect_data = calculate_section_data_for_rect_hollow_shape(profile=profile)
        elif profile_class == "IfcUShapeProfileDef":
            sect_data = calculate_section_data_for_u_shape(profile=profile)
        elif profile_class == "IfcIShapeProfileDef":
            sect_data = calculate_section_data_for_i_shape(profile=profile)
        elif profile_class == "IfcCircleProfileDef":
            sect_data = calculate_section_data_for_circle_shape(profile=profile)
        elif profile_class == "IfcCircleHollowProfileDef":
            sect_data = calculate_section_data_for_circle_hollow_shape(profile=profile)
        elif profile_class == "IfcTShapeProfileDef":
            sect_data = calculate_section_data_for_t_shape(profile=profile)

        if isinstance(sect_data, dict):
            pset = ifcopenshell.api.pset.add_pset(
                file=ifc4_file,
                product=profile,
                name="Pset_ProfileMechanical",
            )
            ifcopenshell.api.pset.edit_pset(
                file=ifc4_file,
                pset=pset,
                properties={
                    "CentreOfGravityInX": sect_data["CentreOfGravityInX"],
                    "CentreOfGravityInY": sect_data["CentreOfGravityInY"],
                    "CrossSectionArea": sect_data["CrossSectionArea"],
                    "MomentOfInertiaY": sect_data["MomentOfInertiaY"],
                    "MomentOfInertiaZ": sect_data["MomentOfInertiaZ"],
                    "TorsionalConstantX": sect_data["TorsionalConstantX"],
                },
            )

    return profile


def add_profile_from_standard_library(
    ifc4_file: ifcopenshell.file,
    # section_libraries: list[str],  # ["Euro", "BSShapes2006"] | ["AISC14"]
    region: REGION,
    profile_name: str,  # L8X4X7/8, ILS100
    check_for_duplicate: bool = False,
) -> ifcopenshell.entity_instance | None:
    """Load IfcParameterizedProfileDef from library"""

    if check_for_duplicate:
        old_profiles = ifc4_file.by_type(type="IfcProfileDef", include_subtypes=True)
        for old_profile in old_profiles:
            names_match = str(old_profile.ProfileName).upper() == profile_name.upper()
            if names_match:
                return old_profile

    if region == "Europe":
        section_libraries = ["BSShapes2006", "Euro"]
    elif region == "UnitedStates":
        section_libraries = ["AISC14", "SJIJoists"]
    else:
        return None

    # given_section_libraries_are_valid = all(
    #     [sl in SECTION_LIBRARIES for sl in section_libraries]
    # )
    # if not given_section_libraries_are_valid:
    #     return None

    matching_section_category_label = None
    matching_section_data_dictionary = None
    for section_library in section_libraries:
        section_library_file_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "property_libraries",
            "sections",
            f"{section_library}.pkl",
        )
        with open(section_library_file_path, "rb") as file:
            section_library_data = pickle.load(file)
        for (
            section_category_label,
            section_category_dictionary,
        ) in section_library_data.items():
            section_data_dictionary = section_category_dictionary.get(profile_name)
            if section_data_dictionary:
                matching_section_data_dictionary = section_data_dictionary
                matching_section_category_label = section_category_label
                break
        if matching_section_data_dictionary:
            break
    if not isinstance(matching_section_data_dictionary, dict):
        return None

    if matching_section_category_label == "STEEL_ANGLE":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["Depth"],
            matching_section_data_dictionary["Width"],
            matching_section_data_dictionary["Thickness"],
            matching_section_data_dictionary["FilletRadius"],
            matching_section_data_dictionary["EdgeRadius"],
            matching_section_data_dictionary["LegSlope"],
        ]
    elif matching_section_category_label == "STEEL_BOX":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["XDim"],
            matching_section_data_dictionary["YDim"],
            matching_section_data_dictionary["WallThickness"],
            matching_section_data_dictionary["InnerFilletRadius"],
            matching_section_data_dictionary["OuterFilletRadius"],
        ]
    elif matching_section_category_label == "STEEL_CHANNEL":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["Depth"],
            matching_section_data_dictionary["FlangeWidth"],
            matching_section_data_dictionary["WebThickness"],
            matching_section_data_dictionary["FlangeThickness"],
            matching_section_data_dictionary["FilletRadius"],
            matching_section_data_dictionary["EdgeRadius"],
            matching_section_data_dictionary["FlangeSlope"],
        ]
    elif matching_section_category_label == "STEEL_I_SECTION":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["OverallWidth"],
            matching_section_data_dictionary["OverallDepth"],
            matching_section_data_dictionary["WebThickness"],
            matching_section_data_dictionary["FlangeThickness"],
            matching_section_data_dictionary["FilletRadius"],
            matching_section_data_dictionary["FlangeEdgeRadius"],
            matching_section_data_dictionary["FlangeSlope"],
        ]
    elif matching_section_category_label == "STEEL_PIPE":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["Radius"],
            matching_section_data_dictionary["WallThickness"],
        ]
    elif matching_section_category_label == "STEEL_TEE":
        ifc_class = matching_section_data_dictionary["IfcClass"]
        dimensions = [
            matching_section_data_dictionary["Depth"],
            matching_section_data_dictionary["FlangeWidth"],
            matching_section_data_dictionary["WebThickness"],
            matching_section_data_dictionary["FlangeThickness"],
            matching_section_data_dictionary["FilletRadius"],
            matching_section_data_dictionary["FlangeEdgeRadius"],
            matching_section_data_dictionary["WebEdgeRadius"],
            matching_section_data_dictionary["WebSlope"],
            matching_section_data_dictionary["FlangeSlope"],
        ]
    elif (
        matching_section_category_label == "JOIST_STANDARD"
        or matching_section_category_label == "JOIST_STANDARD"
    ):
        ifc_class = "IfcRectangleProfileDef"
        ydim = matching_section_data_dictionary["Depth"]
        iyy = matching_section_data_dictionary["MomentOfInertiaY"]
        xdim = iyy * 12 / ydim**3
        xdim = inlbim.util.unit.convert_unit_of_value(value=xdim, conversion_factor=1)
        dimensions = [
            xdim,
            ydim,
        ]

    section_from_library = add_parameterized_profile(
        ifc4_file=ifc4_file,
        profile_class=ifc_class,
        dimensions=dimensions,
        profile_name=profile_name,
        check_for_duplicate=True,
    )

    if matching_section_category_label in [
        "STEEL_ANGLE",
        "STEEL_BOX",
        "STEEL_CHANNEL",
        "STEEL_I_SECTION",
        "STEEL_PIPE",
        "STEEL_TEE",
    ]:
        pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=section_from_library,
            name="Pset_ProfileMechanical",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=pset,
            properties={
                "CentreOfGravityInX": matching_section_data_dictionary[
                    "CentreOfGravityInX"
                ],
                "CentreOfGravityInY": matching_section_data_dictionary[
                    "CentreOfGravityInY"
                ],
                "CrossSectionArea": matching_section_data_dictionary[
                    "CrossSectionArea"
                ],
                "MomentOfInertiaY": matching_section_data_dictionary[
                    "MomentOfInertiaY"
                ],
                "MomentOfInertiaZ": matching_section_data_dictionary[
                    "MomentOfInertiaZ"
                ],
                "TorsionalConstantX": matching_section_data_dictionary[
                    "TorsionalConstantX"
                ],
            },
        )
    elif (
        matching_section_category_label == "JOIST_STANDARD"
        or matching_section_category_label == "JOIST_STANDARD"
    ):
        pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=section_from_library,
            name="Pset_ProfileMechanical",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=pset,
            properties={
                "MomentOfInertiaY": matching_section_data_dictionary[
                    "MomentOfInertiaY"
                ],
            },
        )

    return section_from_library


def calculate_section_data_for_l_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcLShapeProfileDef"""

    assert profile.is_a("IfcLShapeProfileDef")

    d = profile.Depth
    b = profile.Width
    t = profile.Thickness
    bases = [t, b]
    heights = [d - t, t]
    areas = [base * height for base, height in zip(bases, heights)]
    x_bars = [t / 2, b / 2]
    y_bars = [t + (d - t) / 2, t / 2]
    x_bar = sum([x_bar_i * area_i for x_bar_i, area_i in zip(x_bars, areas)]) / sum(
        areas
    )
    y_bar = sum([y_bar_i * area_i for y_bar_i, area_i in zip(y_bars, areas)]) / sum(
        areas
    )
    Ixs = [
        1 / 12 * base_i * height_i**3 + area_i * (y_i - y_bar) ** 2
        for base_i, height_i, area_i, y_i in zip(bases, heights, areas, y_bars)
    ]
    Iys = [
        1 / 12 * height_i * base_i**3 + area_i * (x_i - x_bar) ** 2
        for base_i, height_i, area_i, x_i in zip(bases, heights, areas, x_bars)
    ]

    d_prime = d - t / 2
    b_prime = b - t / 2
    j = 1 / 3 * (d_prime + b_prime) * t**3

    sect_data = {
        "CentreOfGravityInX": -1 * (b / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d / 2 - y_bar),
        "CrossSectionArea": (b * t) + (d * t) - (t * t),
        "MomentOfInertiaY": sum(Ixs),
        "MomentOfInertiaZ": sum(Iys),
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_rect_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcRectangleProfileDef"""

    assert profile.is_a("IfcRectangleProfileDef")

    xdim = profile.XDim
    ydim = profile.YDim
    area = xdim * ydim
    x_bar = xdim / 2
    y_bar = ydim / 2
    Ix = 1 / 12 * xdim * ydim**3
    Iy = 1 / 12 * ydim * xdim**3

    if xdim < ydim:
        a = ydim
        b = xdim
    else:
        a = xdim
        b = ydim
    j = a * b**3 / 16 * (16 / 3 - 3.36 * b / a * (1 - b**4 / 12 / a**4))

    sect_data = {
        "CentreOfGravityInX": -1 * (xdim / 2 - x_bar),
        "CentreOfGravityInY": -1 * (ydim / 2 - y_bar),
        "CrossSectionArea": area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_rect_hollow_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcRectangleHollowProfileDef"""

    assert profile.is_a("IfcRectangleHollowProfileDef")

    b = profile.XDim
    h = profile.YDim
    t = profile.WallThickness
    area = 2 * t * (b + h - 2 * t)
    x_bar = b / 2
    y_bar = h / 2
    Ix = 1 / 12 * (b * h**3 - (b - 2 * t) * (h - 2 * t) ** 3)
    Iy = 1 / 12 * (h * b**3 - (h - 2 * t) * (b - 2 * t) ** 3)

    Rc = 1.5 * t
    Ap = (h - t) * (b - t) - Rc**2 * (4 - np.pi)
    p = 2 * ((h - t) + (b - t)) - 2 * Rc * (4 - np.pi)
    j = 4 * Ap**2 * t / p

    sect_data = {
        "CentreOfGravityInX": -1 * (b / 2 - x_bar),
        "CentreOfGravityInY": -1 * (h / 2 - y_bar),
        "CrossSectionArea": area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_u_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcUShapeProfileDef"""

    assert profile.is_a("IfcUShapeProfileDef")

    d = profile.Depth
    b = profile.FlangeWidth
    tw = profile.WebThickness
    tf = profile.FlangeThickness

    x_bars = [tw / 2, b / 2, b / 2]
    y_bars = [d / 2, tf / 2, d - tf / 2]
    areas = [tw * (d - 2 * tf), b * tf, b * tf]

    total_area = sum(areas)

    x_bar = (
        sum([x_bar_i * area_i for x_bar_i, area_i in zip(x_bars, areas)]) / total_area
    )
    y_bar = (
        sum([y_bar_i * area_i for y_bar_i, area_i in zip(y_bars, areas)]) / total_area
    )

    Ixs = [
        1 / 12 * tw * (d - 2 * tf) ** 3,
        1 / 12 * b * tf**3,
        1 / 12 * b * tf**3,
    ]
    Ix = sum(
        [
            Ix_i + A_i * (y_bar_i - y_bar) ** 2
            for Ix_i, A_i, y_bar_i in zip(Ixs, areas, y_bars)
        ]
    )

    Iys = [
        1 / 12 * (d - 2 * tf) * tw**3,
        1 / 12 * tf * b**3,
        1 / 12 * tf * b**3,
    ]
    Iy = sum(
        [
            Iy_i + A_i * (x_bar_i - x_bar) ** 2
            for Iy_i, A_i, x_bar_i in zip(Iys, areas, x_bars)
        ]
    )

    b_prime = b - tw / 2
    d_prime = d - tf
    j = 1 / 3 * (2 * b_prime * tf**3 + d_prime * tw**3)

    sect_data = {
        "CentreOfGravityInX": -1 * (b / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d / 2 - y_bar),
        "CrossSectionArea": total_area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_i_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcIShapeProfileDef"""

    assert profile.is_a("IfcIShapeProfileDef")

    d = profile.OverallDepth
    b = profile.OverallWidth
    tw = profile.WebThickness
    tf = profile.FlangeThickness

    x_bars = [b / 2, b / 2, b / 2]
    y_bars = [d / 2, tf / 2, d - tf / 2]
    areas = [tw * (d - 2 * tf), b * tf, b * tf]

    total_area = sum(areas)

    x_bar = (
        sum([x_bar_i * area_i for x_bar_i, area_i in zip(x_bars, areas)]) / total_area
    )
    y_bar = (
        sum([y_bar_i * area_i for y_bar_i, area_i in zip(y_bars, areas)]) / total_area
    )

    Ixs = [
        1 / 12 * tw * (d - 2 * tf) ** 3,
        1 / 12 * b * tf**3,
        1 / 12 * b * tf**3,
    ]
    Ix = sum(
        [
            Ix_i + A_i * (y_bar_i - y_bar) ** 2
            for Ix_i, A_i, y_bar_i in zip(Ixs, areas, y_bars)
        ]
    )

    Iys = [
        1 / 12 * (d - 2 * tf) * tw**3,
        1 / 12 * tf * b**3,
        1 / 12 * tf * b**3,
    ]
    Iy = sum(
        [
            Iy_i + A_i * (x_bar_i - x_bar) ** 2
            for Iy_i, A_i, x_bar_i in zip(Iys, areas, x_bars)
        ]
    )

    j = 1 / 3 * (2 * b * tf**3 + (d - tf) * tw**3)

    sect_data = {
        "CentreOfGravityInX": -1 * (b / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d / 2 - y_bar),
        "CrossSectionArea": total_area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_circle_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcCircleProfileDef"""

    assert profile.is_a("IfcCircleProfileDef")

    r = profile.Radius
    d = r * 2

    area = np.pi * r**2

    x_bar = d / 2
    y_bar = d / 2

    Ix = 1 / 4 * np.pi * r**4

    Iy = 1 / 4 * np.pi * r**4

    j = 1 / 2 * np.pi * r**4

    sect_data = {
        "CentreOfGravityInX": -1 * (d / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d / 2 - y_bar),
        "CrossSectionArea": area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_circle_hollow_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcCircleHollowProfileDef"""

    assert profile.is_a("IfcCircleHollowProfileDef")

    r_o = profile.Radius
    t = profile.WallThickness
    r_i = r_o - t
    d_o = r_o * 2

    area = np.pi * (r_o**2 - r_i**2)

    x_bar = d_o / 2
    y_bar = d_o / 2

    Ix = 1 / 4 * np.pi * (r_o**4 - r_i**4)

    Iy = 1 / 4 * np.pi * (r_o**4 - r_i**4)

    j = 1 / 2 * np.pi * (r_o**4 - r_i**4)

    sect_data = {
        "CentreOfGravityInX": -1 * (d_o / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d_o / 2 - y_bar),
        "CrossSectionArea": area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def calculate_section_data_for_t_shape(
    profile: ifcopenshell.entity_instance,
) -> dict:
    """Calculate section properties for an IfcTShapeProfileDef"""

    assert profile.is_a("IfcTShapeProfileDef")

    d = profile.Depth
    b = profile.FlangeWidth
    tw = profile.WebThickness
    tf = profile.FlangeThickness

    d_prime = d - tf

    x_bars = [b / 2, b / 2]
    y_bars = [d_prime / 2, d - tf / 2]
    areas = [tw * d_prime, b * tf]

    total_area = sum(areas)

    x_bar = (
        sum([x_bar_i * area_i for x_bar_i, area_i in zip(x_bars, areas)]) / total_area
    )
    y_bar = (
        sum([y_bar_i * area_i for y_bar_i, area_i in zip(y_bars, areas)]) / total_area
    )

    Ixs = [
        1 / 12 * tw * d_prime**3,
        1 / 12 * b * tf**3,
    ]
    Ix = sum(
        [
            Ix_i + A_i * (y_bar_i - y_bar) ** 2
            for Ix_i, A_i, y_bar_i in zip(Ixs, areas, y_bars)
        ]
    )

    Iys = [
        1 / 12 * d_prime * tw**3,
        1 / 12 * tf * b**3,
    ]
    Iy = sum(
        [
            Iy_i + A_i * (x_bar_i - x_bar) ** 2
            for Iy_i, A_i, x_bar_i in zip(Iys, areas, x_bars)
        ]
    )

    j = 1 / 3 * (b * tf**3 + d_prime * tw**3)

    sect_data = {
        "CentreOfGravityInX": -1 * (b / 2 - x_bar),
        "CentreOfGravityInY": -1 * (d / 2 - y_bar),
        "CrossSectionArea": total_area,
        "MomentOfInertiaY": Ix,
        "MomentOfInertiaZ": Iy,
        "TorsionalConstantX": j,
    }

    return sect_data


def add_arbitrary_profile_with_or_without_voids(
    file: ifcopenshell.file,
    outer_profile: list[tuple[float, float]],
    inner_profiles: list[list[tuple[float, float]]],
    name: str | None = None,
) -> ifcopenshell.entity_instance:
    """Adds a new arbitrary polyline-based profile with voids

    Example:

    .. code:: python

        # A 400mm by 400mm square with a 200mm by 200mm hole in it.
        square_with_hole = ifcopenshell.api.profile.add_arbitrary_profile_with_voids(model,
            outer_profile=[(0., 0.), (.4, 0.), (.4, .4), (0., .4), (0., 0.)],
            inner_profiles=[[(0.1, 0.1), (0.3, 0.1), (0.3, 0.3), (0.1, 0.3), (0.1, 0.1)]],
            name="SK01 Hole Profile")
    """

    outer_ifc_points = file.create_entity("IfcCartesianPointList2D", outer_profile)
    outer_curve = file.create_entity("IfcIndexedPolyCurve", outer_ifc_points)

    profile_has_voids = len(inner_profiles) > 0

    if profile_has_voids:

        inner_curves = []
        for inner_profile in inner_profiles:
            inner_ifc_points = file.create_entity(
                "IfcCartesianPointList2D", inner_profile
            )
            inner_curve = file.create_entity("IfcIndexedPolyCurve", inner_ifc_points)
            inner_curves.append(inner_curve)

        return file.create_entity(
            "IfcArbitraryProfileDefWithVoids", "AREA", name, outer_curve, inner_curves
        )

    else:
        return file.create_entity(
            "IfcArbitraryClosedProfileDef", "AREA", name, outer_curve
        )
