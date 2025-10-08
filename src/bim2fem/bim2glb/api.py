# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

from pygltflib import (
    GLTF2,
    Scene,
    Buffer,
    Node,
    BufferView,
    ELEMENT_ARRAY_BUFFER,
    ARRAY_BUFFER,
    Accessor,
    UNSIGNED_BYTE,
    UNSIGNED_SHORT,
    UNSIGNED_INT,
    SCALAR,
    FLOAT,
    VEC3,
    Mesh,
    Primitive,
    Attributes,
    Material,
    PbrMetallicRoughness,
)
import numpy as np
import bim2glb.util


def create_material(
    gltf: GLTF2,
    name: str | None = None,
    rgb_triplet: list[float] = [1, 1, 1],
    check_for_duplicate: bool = True,
) -> int:
    """Create Material for GLTF2 Object"""

    if check_for_duplicate:
        for old_material_index, old_material in enumerate(gltf.materials):
            if not isinstance(old_material, Material):
                continue
            old_material_name = old_material.name
            if not old_material_name == name:
                continue
            if not isinstance(old_material.pbrMetallicRoughness, PbrMetallicRoughness):
                continue
            if not isinstance(old_material.pbrMetallicRoughness.baseColorFactor, list):
                continue
            old_rgb_triplet = old_material.pbrMetallicRoughness.baseColorFactor[0:3]
            l2_norm = np.round(
                np.linalg.norm(np.array(rgb_triplet) - np.array(old_rgb_triplet)),
                2,
            )
            if l2_norm != 0.0:
                continue
            return old_material_index

    material = Material(
        alphaMode="MASK",
        name=name,
        pbrMetallicRoughness=PbrMetallicRoughness(baseColorFactor=rgb_triplet + [1]),
    )
    gltf.materials += [material]
    material_index = len(gltf.materials) - 1

    return material_index


def create_shapes_representing_cartesian_coordinate_axes(gltf: GLTF2):
    """Create an arrangment of cube shapes that indicate the direction of the
    cartesian coordinate system.

    X Axis -> Red
    Y Axis -> Green
    Z Axis -> Blue
    """

    index_for_node_for_axes_at_origin = create_node(gltf=gltf, name="Axes at Origin")

    assign_node_to_scene(
        gltf=gltf,
        index_of_node=index_for_node_for_axes_at_origin,
    )

    sets_of_triangles_for_each_primitive = []
    sets_of_points_for_each_primitive = []
    indices_of_materials = []

    for delta, rgb_triplet in zip(
        [
            [0, 0, 0],
            [1.5, 0, 0],
            [2.5, 0, 0],
            [3.5, 0, 0],
            [0, 1.5, 0],
            [0, 2.5, 0],
            [0, 3.5, 0],
            [0, 0, 1.5],
            [0, 0, 2.5],
            [0, 0, 3.5],
        ],
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0],
        ],
    ):
        delta_x = delta[0]
        delta_y = delta[1]
        delta_z = delta[2]

        points = np.array(
            [
                [-0.5 + delta_x, -0.5 + delta_y, 0.5 + delta_z],
                [0.5 + delta_x, -0.5 + delta_y, 0.5 + delta_z],
                [-0.5 + delta_x, 0.5 + delta_y, 0.5 + delta_z],
                [0.5 + delta_x, 0.5 + delta_y, 0.5 + delta_z],
                [0.5 + delta_x, -0.5 + delta_y, -0.5 + delta_z],
                [-0.5 + delta_x, -0.5 + delta_y, -0.5 + delta_z],
                [0.5 + delta_x, 0.5 + delta_y, -0.5 + delta_z],
                [-0.5 + delta_x, 0.5 + delta_y, -0.5 + delta_z],
            ],
            dtype="float32",
        )

        sets_of_points_for_each_primitive.append(points)

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

        sets_of_triangles_for_each_primitive.append(triangles)

        index_for_material = create_material(
            name=None,
            gltf=gltf,
            rgb_triplet=rgb_triplet,
        )

        indices_of_materials.append(index_for_material)

    index_for_mesh_for_axes_at_origin = create_mesh(
        gltf=gltf,
        sets_of_triangles_for_primitives=sets_of_triangles_for_each_primitive,
        sets_of_points_for_primitives=sets_of_points_for_each_primitive,
        name="Axes at Origin",
    )

    assign_materials_to_mesh(
        gltf=gltf,
        index_for_mesh=index_for_mesh_for_axes_at_origin,
        indices_of_materials_for_primitives=indices_of_materials,
    )

    assign_mesh_to_node(
        gltf=gltf,
        index_for_node=index_for_node_for_axes_at_origin,
        index_for_mesh=index_for_mesh_for_axes_at_origin,
    )


def create_node(
    gltf: GLTF2,
    name: str | None = None,
) -> int:
    """Create Node for GLTF2 Object"""

    node = Node(name=name)
    gltf.nodes += [node]
    node_index = len(gltf.nodes) - 1

    return node_index


def assign_node_to_scene(
    gltf: GLTF2,
    index_of_node: int,
):
    """Assigns node to scene"""
    scene = gltf.scenes[gltf.scene]
    if scene.nodes:
        if index_of_node not in scene.nodes:
            scene.nodes.append(index_of_node)
    else:
        scene.nodes = [index_of_node]


def create_gltf() -> GLTF2:
    """Create GLTF2 object that is empty except for a single Scene namded "Root" """
    gltf = GLTF2()
    gltf.scenes.append(Scene(name="Root"))
    gltf.scene = 0
    gltf.buffers.append(Buffer(byteLength=0))
    gltf.set_binary_blob(bytes())
    return gltf


def create_primitive(
    gltf: GLTF2,
    triangles: np.ndarray,
    points: np.ndarray,
) -> Primitive:
    """Create Primitive for GLTF2 object"""

    def is_multiple_of_4(number: int) -> bool:
        """
        Checks if a number is a multiple of 4.

        Args:
            number: The number to check.

        Returns:
            True if the number is a multiple of 4, False otherwise.
        """
        return number % 4 == 0

    def align_to_4_bytes(binary_blob):
        """Ensures that binary data is 4-byte aligned by adding padding if necessary."""
        length = len(binary_blob)
        padding_needed = (4 - (length % 4)) % 4  # Compute how many bytes to add
        return binary_blob + (b"\x00" * padding_needed)  # Append zero bytes

    triangles_binary_blob = align_to_4_bytes(triangles.flatten().tobytes())
    points_binary_blob = align_to_4_bytes(points.tobytes())

    byteOffset_for_triangles = gltf.buffers[0].byteLength
    byteLength_for_triangles = len(triangles_binary_blob)
    byteOffset_for_points = byteOffset_for_triangles + byteLength_for_triangles
    byteLength_for_points = len(points_binary_blob)

    for byteValue in [
        byteOffset_for_triangles,
        byteLength_for_triangles,
        byteOffset_for_points,
        byteLength_for_points,
    ]:
        if not is_multiple_of_4(byteValue):
            exit("byte data must be in multiples of 4 for GLB to read properly")

    buffer_view_for_triangles = BufferView(
        buffer=0,
        byteOffset=byteOffset_for_triangles,
        byteLength=byteLength_for_triangles,
        target=ELEMENT_ARRAY_BUFFER,
    )
    buffer_view_for_points = BufferView(
        buffer=0,
        byteOffset=byteOffset_for_points,
        byteLength=byteLength_for_points,
        target=ARRAY_BUFFER,
    )

    gltf.bufferViews += [buffer_view_for_triangles, buffer_view_for_points]
    buffer_view_index_for_triangles = len(gltf.bufferViews) - 2
    buffer_view_index_for_points = len(gltf.bufferViews) - 1

    if triangles.dtype == "uint8":
        dtype_for_triangles = UNSIGNED_BYTE
    elif triangles.dtype == "uint16":
        dtype_for_triangles = UNSIGNED_SHORT
    elif triangles.dtype == "uint32":
        dtype_for_triangles = UNSIGNED_INT
    else:
        dtype_for_triangles = UNSIGNED_INT

    accessor_for_triangles = Accessor(
        bufferView=buffer_view_index_for_triangles,
        componentType=dtype_for_triangles,
        # componentType=UNSIGNED_INT,
        count=triangles.size,
        type=SCALAR,
        max=[int(triangles.max())],
        min=[int(triangles.min())],
    )
    accessor_for_points = Accessor(
        bufferView=buffer_view_index_for_points,
        componentType=FLOAT,
        count=len(points),
        type=VEC3,
        max=points.max(axis=0).tolist(),
        min=points.min(axis=0).tolist(),
    )

    gltf.accessors += [accessor_for_triangles, accessor_for_points]
    accessor_index_for_triangles = len(gltf.accessors) - 2
    accessor_index_for_points = len(gltf.accessors) - 1

    primitive = Primitive(
        attributes=Attributes(POSITION=accessor_index_for_points),
        indices=accessor_index_for_triangles,
    )

    gltf.buffers[0].byteLength = (
        gltf.buffers[0].byteLength + byteLength_for_triangles + byteLength_for_points
    )

    gltf._glb_data = gltf._glb_data + triangles_binary_blob + points_binary_blob

    return primitive


def create_mesh(
    gltf: GLTF2,
    sets_of_triangles_for_primitives: list[np.ndarray],
    sets_of_points_for_primitives: list[np.ndarray],
    name: str | None = None,
) -> int:
    """Create Mesh for GLTF2 Object"""

    mesh = Mesh(name=name if name else None, primitives=[])

    for triangles_for_primitive, points_for_primitive in zip(
        sets_of_triangles_for_primitives, sets_of_points_for_primitives
    ):
        primitive = create_primitive(
            gltf=gltf,
            triangles=triangles_for_primitive,
            points=points_for_primitive,
        )
        mesh.primitives.append(primitive)

    gltf.meshes += [mesh]
    index_for_mesh = len(gltf.meshes) - 1

    return index_for_mesh


def assign_mesh_to_node(
    gltf: GLTF2,
    index_for_node: int,
    index_for_mesh: int,
):
    """Assigns mesh to node"""

    node = gltf.nodes[index_for_node]
    node.mesh = index_for_mesh


def assign_materials_to_mesh(
    gltf: GLTF2,
    indices_of_materials_for_primitives: list[int],
    index_for_mesh: int,
):
    """Assigns materials to primitives of mesh"""

    mesh = gltf.meshes[index_for_mesh]

    if len(indices_of_materials_for_primitives) != len(mesh.primitives):
        return

    for index_of_material, primitive in zip(
        indices_of_materials_for_primitives, mesh.primitives
    ):
        primitive.material = index_of_material


def set_node_matrix(node: Node, matrix_array: np.ndarray):
    if bim2glb.util.is_identity_matrix(matrix_array=matrix_array):
        node.matrix = None
    else:
        node.matrix = matrix_array.T.flatten().tolist()


def assign_node_as_aggregate_to_other_nodes(
    gltf: GLTF2,
    index_for_parent_node: int,
    indices_for_child_nodes: list[int],
):
    parent_node = gltf.nodes[index_for_parent_node]

    if isinstance(parent_node.children, list):
        for index_for_child_node in indices_for_child_nodes:
            if index_for_child_node not in parent_node.children:
                parent_node.children.append(index_for_child_node)

    else:
        parent_node.children = indices_for_child_nodes
