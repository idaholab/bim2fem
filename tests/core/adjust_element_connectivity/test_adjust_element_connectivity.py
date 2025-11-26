# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
from tests.conftest import OUTPUT_DIR_FOR_SNAP, INPUT_DIR
from typing import cast
from pprint import pprint
from bim2fem.core.adjust_element_connectivity.adjust_element_connectivity_of_frame_structure import (
    adjust_element_connectivity_of_frame_structure,
)


class TestAdjustElementConnectivityOfFrameStructure:

    def test_adjust_element_connectivity_of_revit_steel_construction(
        self,
    ):

        ifc4_sav_file_original = ifcopenshell.open(
            path=str(INPUT_DIR / "SteelConstruction_RV_converted_to_SAV.ifc"),
        )
        ifc4_sav_file_original = cast(ifcopenshell.file, ifc4_sav_file_original)

        ifc4sav_file_snapped = adjust_element_connectivity_of_frame_structure(
            ifc4_sav_file=ifc4_sav_file_original,
            execute_snap_frame_members=True,
            execute_snap_floor_beam_systems=True,
            execute_snap_walls_to_slabs=True,
            execute_snap_walls_to_walls=True,
            execute_snap_beams_to_walls=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_SNAP / "SteelConstruction_RV_converted_to_SAV_snapped.ifc"
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4sav_file_snapped,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
