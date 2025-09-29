# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

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
import bim2fem.convert_piping_to_fem
import inlbim.api.file
import ifcopenshell


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_input_filename = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "files",
            "small_piping_with_two_bends.ifc",
        )
    )

    # Open IFC4 Source File
    ifc4_source_file = ifcopenshell.open(path=ifc_input_filename)
    assert isinstance(ifc4_source_file, ifcopenshell.file)

    # Get IFC output filename
    ifc_output_filename = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "small_piping_with_two_bends_SAV.ifc",
        )
    )

    # Convert architectural IFC to structural IFC
    ifc4_sav_file = bim2fem.convert_piping_to_fem.convert_piping_from_reference_view_to_structural_analysis_view(
        ifc4_source_file=ifc4_source_file,
        element_deselection_query=None,
        region="Europe",
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_sav_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                ifc_output_filename,
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
