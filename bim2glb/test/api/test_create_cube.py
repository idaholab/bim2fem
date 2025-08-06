# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

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
import bim2glb.api
import numpy as np


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Add GLB File
    glb_file = bim2glb.api.create_gltf()

    # Add Building
    index_for_node_for_building = bim2glb.api.create_node(
        gltf=glb_file,
        name="Building",
    )
    bim2glb.api.assign_node_to_scene(
        gltf=glb_file,
        index_of_node=index_for_node_for_building,
    )

    # Create Cube
    index_for_node_for_box = bim2glb.api.create_node(
        gltf=glb_file,
        name="Box",
    )
    bim2glb.api.assign_node_as_aggregate_to_other_nodes(
        gltf=glb_file,
        index_for_parent_node=index_for_node_for_building,
        indices_for_child_nodes=[index_for_node_for_box],
    )

    # Define points and triangles for a generic cube
    points = np.array(
        [
            (-0.5 + 0.5, -0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, -0.5 + 0.5, 0.5 + 0.5),
            (-0.5 + 0.5, 0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, 0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, -0.5 + 0.5, -0.5 + 0.5),
            (-0.5 + 0.5, -0.5 + 0.5, -0.5 + 0.5),
            (0.5 + 0.5, 0.5 + 0.5, -0.5 + 0.5),
            (-0.5 + 0.5, 0.5 + 0.5, -0.5 + 0.5),
        ],
        dtype="float32",
    )
    triangles = np.array(
        [
            [0, 1, 2],
            [3, 2, 1],
            [1, 0, 4],
            [5, 4, 0],
            [3, 1, 6],
            [4, 6, 1],
            [2, 3, 7],
            [6, 7, 3],
            [0, 2, 5],
            [7, 5, 2],
            [5, 7, 4],
            [6, 4, 7],
        ],
        dtype="uint8",
    )

    # Add Cube Representation
    index_for_mesh = bim2glb.api.create_mesh(
        gltf=glb_file,
        sets_of_triangles_for_primitives=[triangles],
        sets_of_points_for_primitives=[points],
        name="Box",
    )
    index_for_material = bim2glb.api.create_material(
        name=None,
        gltf=glb_file,
        rgb_triplet=[0.0, 0.0, 1.0],
    )
    bim2glb.api.assign_materials_to_mesh(
        gltf=glb_file,
        index_for_mesh=index_for_mesh,
        indices_of_materials_for_primitives=[index_for_material],
    )
    bim2glb.api.assign_mesh_to_node(
        gltf=glb_file,
        index_for_node=index_for_node_for_box,
        index_for_mesh=index_for_mesh,
    )

    # Show global coords via boxes
    bim2glb.api.create_shapes_representing_cartesian_coordinate_axes(gltf=glb_file)

    # Write GLB file
    glb_output_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "test_create_cube.glb",
        )
    )
    glb_file.save(fname=glb_output_fname)

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
