# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
from tests.conftest import OUTPUT_DIR_FOR_CONVERT, INPUT_DIR
from typing import cast
from pprint import pprint
from bim2fem.core.convert.convert_frame_structure_to_fem import (
    convert_frame_structure_to_fem,
)


class TestConvertFrameStructureToFEM:

    def test_convert_simple_structure_to_fem(
        self,
    ):

        ifc4_rv_file = ifcopenshell.open(
            path=str(INPUT_DIR / "simple_structure_RV.ifc"),
        )
        ifc4_rv_file = cast(ifcopenshell.file, ifc4_rv_file)

        ifc4sav_file = convert_frame_structure_to_fem(
            ifc4_source_file=ifc4_rv_file,
            element_deselection_query=None,
            region="Europe",
        )

        output_path = str(
            OUTPUT_DIR_FOR_CONVERT / "simple_structure_RV_converted_to_SAV.ifc"
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4sav_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_convert_revit_steel_construction_rv_to_fem(
        self,
    ):

        ifc4_rv_file = ifcopenshell.open(
            path=str(INPUT_DIR / "SteelConstruction_RV.ifc"),
        )
        ifc4_rv_file = cast(ifcopenshell.file, ifc4_rv_file)

        ifc4sav_file = convert_frame_structure_to_fem(
            ifc4_source_file=ifc4_rv_file,
            element_deselection_query='type *= "Footing"',
            region="Europe",
        )

        output_path = str(
            OUTPUT_DIR_FOR_CONVERT / "SteelConstruction_RV_converted_to_SAV.ifc"
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4sav_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_convert_revit_steel_construction_dtv_to_fem(
        self,
    ):

        ifc4_rv_file = ifcopenshell.open(
            path=str(INPUT_DIR / "SteelConstruction_DTV.ifc"),
        )
        ifc4_rv_file = cast(ifcopenshell.file, ifc4_rv_file)

        ifc4sav_file = convert_frame_structure_to_fem(
            ifc4_source_file=ifc4_rv_file,
            element_deselection_query='type *= "Footing"',
            region="Europe",
        )

        output_path = str(
            OUTPUT_DIR_FOR_CONVERT / "SteelConstruction_DTV_converted_to_SAV.ifc"
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4sav_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
