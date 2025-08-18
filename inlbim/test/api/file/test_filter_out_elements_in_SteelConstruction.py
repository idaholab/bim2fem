# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys

# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")),
)


from inlbim import current_time
import time
import chime
import ifcopenshell
import inlbim.api.file


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_input_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "files",
            "SteelConstruction_DTV.ifc",
        )
    )

    # Open IFC
    ifc4_file = ifcopenshell.open(path=ifc_input_fname)
    assert isinstance(ifc4_file, ifcopenshell.file)

    # Filter out elements
    ifc4_file = inlbim.api.file.filter_out_elements(
        ifc4_file=ifc4_file,
        selection_query="IfcColumn, IfcSlab, IfcWall, IfcBeam, IfcMember, IfcElementAssembly, IfcOpeningElement",
        deselection_query='type = "M_Footing-Rectangular:1800 x 1200 x 450mm"',
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_filter_out_elements_in_SteelConstruction.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
