# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")),
)


from bim2glb import current_time
import time
import chime
import bim2glb.convert_ifc_to_glb


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_input_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "files",
            "small_structure_RV.ifc",
        )
    )
    # Get GLB output filename
    glb_output_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "small_structure_RV.glb",
        )
    )

    # Convert from IFC to GLB
    bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
        ifc_input_filename=ifc_input_fname,
        glb_output_filename=glb_output_fname,
        store_metadata_in_glb_nodes=True,
        store_metadata_in_json=True,
        flatten_metadata=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
