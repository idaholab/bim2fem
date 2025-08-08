# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)


from bim2fem import current_time
import time
import chime
import inlbim.api.file
import ifcopenshell
from bim2fem.adjust_element_connectivity_of_fem import (
    adjust_element_connectivity_of_ifc4_sav_file,
)


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_sav_filepath = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "convert_ifc_to_fem",
            "test_convert_SteelConstruction_RV_to_fem.ifc",
        )
    )

    # Open IFC4 Source File
    ifc4_sav_file = ifcopenshell.open(path=ifc_sav_filepath)
    assert isinstance(ifc4_sav_file, ifcopenshell.file)

    # Execute
    snapped_ifc4sav__file = adjust_element_connectivity_of_ifc4_sav_file(
        ifc4_sav_file=ifc4_sav_file,
        execute_snap_frame_members=True,
        execute_snap_floor_beam_systems=True,
        execute_snap_walls_to_slabs=False,
        execute_snap_beams_to_walls=False,
    )

    # Write to disk
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=snapped_ifc4sav__file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_adjust_element_connectivity_of_SteelConstruction_RV_fem.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
