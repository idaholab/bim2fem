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
import inlbim.api.file
import ifcopenshell
import bim2fem.recreate_fem_with_3d_body_shape_representation
import bim2glb.convert_ifc_to_glb


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_sav_filepath = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "convert_ifc_to_fem",
            "test_convert_slab_to_fem.ifc",
        )
    )

    # Open IFC4 Source File
    ifc4_sav_file = ifcopenshell.open(path=ifc_sav_filepath)
    assert isinstance(ifc4_sav_file, ifcopenshell.file)

    # Execute for Extruded View
    ifc_arch_extruded_file_path = inlbim.api.file.write_to_ifc_spf(
        ifc4_file=bim2fem.recreate_fem_with_3d_body_shape_representation.recreate_ifc4_sav_with_3d_body_shape_representation(
            ifc4_sav_file=ifc4_sav_file,
            view_option="Extruded",
        ),
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_recreate_slab_fem_with_3d_extrusion_representation.ifc",
            )
        ),
        add_annotations=True,
    )

    # Convert from IFC to GLB
    bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
        ifc_input_filename=ifc_arch_extruded_file_path,
        glb_output_filename=ifc_arch_extruded_file_path.replace(".ifc", ".glb"),
        store_metadata_in_glb_nodes=True,
        store_metadata_in_json=False,
    )

    # Execute for 3D Wireframe View
    ifc_arch_wireframe_file_path = inlbim.api.file.write_to_ifc_spf(
        ifc4_file=bim2fem.recreate_fem_with_3d_body_shape_representation.recreate_ifc4_sav_with_3d_body_shape_representation(
            ifc4_sav_file=ifc4_sav_file,
            view_option="Wireframe_3D",
        ),
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_recreate_slab_fem_with_3d_wireframe_representation.ifc",
            )
        ),
        add_annotations=True,
    )

    # Convert from IFC to GLB
    bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
        ifc_input_filename=ifc_arch_wireframe_file_path,
        glb_output_filename=ifc_arch_wireframe_file_path.replace(".ifc", ".glb"),
        store_metadata_in_glb_nodes=True,
        store_metadata_in_json=False,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
