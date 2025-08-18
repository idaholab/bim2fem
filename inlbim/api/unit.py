# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
from typing import Literal

UNIT_TYPE = Literal[
    "ABSORBEDDOSEUNIT",
    "AMOUNTOFSUBSTANCEUNIT",
    "AREAUNIT",
    "DOSEEQUIVALENTUNIT",
    "ELECTRICCAPACITANCEUNIT",
    "ELECTRICCHARGEUNIT",
    "ELECTRICCONDUCTANCEUNIT",
    "ELECTRICCURRENTUNIT",
    "ELECTRICRESISTANCEUNIT",
    "ELECTRICVOLTAGEUNIT",
    "ENERGYUNIT",
    "FORCEUNIT",
    "FREQUENCYUNIT",
    "ILLUMINANCEUNIT",
    "INDUCTANCEUNIT",
    "LENGTHUNIT",
    "LUMINOUSFLUXUNIT",
    "LUMINOUSINTENSITYUNIT",
    "MAGNETICFLUXDENSITYUNIT",
    "MAGNETICFLUXUNIT",
    "MASSUNIT",
    "PLANEANGLEUNIT",
    "POWERUNIT",
    "PRESSUREUNIT",
    "RADIOACTIVITYUNIT",
    "SOLIDANGLEUNIT",
    "THERMODYNAMICTEMPERATUREUNIT",
    "TIMEUNIT",
    "VOLUMEUNIT",
]

DERIVED_UNIT_TYPE = Literal[
    "ACCELERATIONUNIT",
    "ANGULARVELOCITYUNIT",
    "AREADENSITYUNIT",
    "COMPOUNDPLANEANGLEUNIT",
    "CURVATUREUNIT",
    "DYNAMICVISCOSITYUNIT",
    "HEATFLUXDENSITYUNIT",
    "HEATINGVALUEUNIT",
    "INTEGERCOUNTRATEUNIT",
    "IONCONCENTRATIONUNIT",
    "ISOTHERMALMOISTURECAPACITYUNIT",
    "KINEMATICVISCOSITYUNIT",
    "LINEARFORCEUNIT",
    "LINEARMOMENTUNIT",
    "LINEARSTIFFNESSUNIT",
    "LINEARVELOCITYUNIT",
    "LUMINOUSINTENSITYDISTRIBUTIONUNIT",
    "MASSDENSITYUNIT",
    "MASSFLOWRATEUNIT",
    "MASSPERLENGTHUNIT",
    "MODULUSOFELASTICITYUNIT",
    "MODULUSOFLINEARSUBGRADEREACTIONUNIT",
    "MODULUSOFROTATIONALSUBGRADEREACTIONUNIT",
    "MODULUSOFSUBGRADEREACTIONUNIT",
    "MOISTUREDIFFUSIVITYUNIT",
    "MOLECULARWEIGHTUNIT",
    "MOMENTOFINERTIAUNIT",
    "PHUNIT",
    "PLANARFORCEUNIT",
    "ROTATIONALFREQUENCYUNIT",
    "ROTATIONALMASSUNIT",
    "ROTATIONALSTIFFNESSUNIT",
    "SECTIONAREAINTEGRALUNIT",
    "SECTIONMODULUSUNIT",
    "SHEARMODULUSUNIT",
    "SOUNDPOWERLEVELUNIT",
    "SOUNDPOWERUNIT",
    "SOUNDPRESSURELEVELUNIT",
    "SOUNDPRESSUREUNIT",
    "SPECIFICHEATCAPACITYUNIT",
    "TEMPERATUREGRADIENTUNIT",
    "TEMPERATURERATEOFCHANGEUNIT",
    "THERMALADMITTANCEUNIT",
    "THERMALCONDUCTANCEUNIT",
    "THERMALEXPANSIONCOEFFICIENTUNIT",
    "THERMALRESISTANCEUNIT",
    "THERMALTRANSMITTANCEUNIT",
    "TORQUEUNIT",
    "VAPORPERMEABILITYUNIT",
    "VOLUMETRICFLOWRATEUNIT",
    "WARPINGCONSTANTUNIT",
    "WARPINGMOMENTUNIT",
]


SI_PREFIX = Literal[
    "ATTO",
    "CENTI",
    "DECA",
    "DECI",
    "EXA",
    "FEMTO",
    "GIGA",
    "HECTO",
    "KILO",
    "MEGA",
    "MICRO",
    "MILLI",
    "NANO",
    "PETA",
    "PICO",
    "TERA",
    None,
]

SI_UNIT_NAME = Literal[
    "AMPERE",
    "BECQUEREL",
    "CANDELA",
    "COULOMB",
    "CUBIC_METRE",
    "DEGREE_CELSIUS",
    "FARAD",
    "GRAM",
    "GRAY",
    "HENRY",
    "HERTZ",
    "JOULE",
    "KELVIN",
    "LUMEN",
    "LUX",
    "METRE",
    "MOLE",
    "NEWTON",
    "OHM",
    "PASCAL",
    "RADIAN",
    "SECOND",
    "SIEMENS",
    "SIEVERT",
    "SQUARE_METRE",
    "STERADIAN",
    "TESLA",
    "VOLT",
    "WATT",
    "WEBER",
]


def add_si_unit(
    ifc4_file: ifcopenshell.file,
    si_unit_type: UNIT_TYPE,
    si_unit_name: SI_UNIT_NAME,
    prefix: SI_PREFIX | None = None,
) -> ifcopenshell.entity_instance:
    """Add IfcSIUnit
    https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcSIUnit.htm
    """

    si_unit = ifc4_file.create_entity(
        type="IfcSIUnit",
        UnitType=si_unit_type,
        Prefix=prefix,
        Name=si_unit_name,
    )

    return si_unit


def add_derived_unit(
    ifc4_file: ifcopenshell.file,
    unit_type: DERIVED_UNIT_TYPE,
) -> ifcopenshell.entity_instance | None:
    """Add IfcDerivedUnit
    https://standards.buildingsmart.org/IFC/RELEASE/IFC4_3/HTML/lexical/IfcDerivedUnit.htm
    """
    base_si_units = {
        f"{si_unit.UnitType}": si_unit
        for si_unit in ifc4_file.by_type(type="IfcSIUnit", include_subtypes=False)
    }

    if unit_type == "MASSDENSITYUNIT":
        units = [base_si_units["MASSUNIT"], base_si_units["LENGTHUNIT"]]
        exponents = [1, -3]
    elif unit_type == "MODULUSOFELASTICITYUNIT":
        units = [base_si_units["FORCEUNIT"], base_si_units["LENGTHUNIT"]]
        exponents = [1, -2]
    else:
        return None

    elements = []
    for unit, integer in zip(units, exponents):
        element = ifc4_file.create_entity(
            type="IfcDerivedUnitElement",
            Unit=unit,
            Exponent=integer,
        )
        elements.append(element)

    derived_unit = ifc4_file.create_entity(
        type="IfcDerivedUnit",
        Elements=elements,
        UnitType=unit_type,
    )

    return derived_unit
