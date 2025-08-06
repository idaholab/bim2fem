# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved


from pygltflib import GLTF2, Node
import numpy as np
import ifcopenshell
import ifcopenshell.util.element
import platform


def get_os():
    """
    Checks and returns the operating system name.
    Returns "Windows" or "Linux" or "macOS" or "other".
    """
    os_name = platform.system()
    if os_name == "Windows":
        return "Windows"
    elif os_name == "Linux":
        return "Linux"
    elif os_name == "Darwin":
        return "macOS"
    else:
        return "Other"


def get_ancestors_of_node(gltf: GLTF2, index_of_child_node: int) -> list[int]:
    """Get ancestor Nodes of given Node from the immediate parent to the progenitor"""
    indices_of_ancestor_nodes = []
    while True:
        child_node = gltf.nodes[index_of_child_node]
        assert child_node.extras
        index_of_parent_node = child_node.extras["parent"]
        if index_of_parent_node is None:
            break
        indices_of_ancestor_nodes.append(index_of_parent_node)
        index_of_child_node = index_of_parent_node

    return indices_of_ancestor_nodes


def get_node_matrix_array(node: Node) -> np.ndarray:
    """Get the transformation matrix array of a node"""
    if node.matrix:
        return np.array(node.matrix, dtype=np.float32).reshape(4, 4).T
    else:
        # Default identity matrix if no transformation is provided
        return np.identity(4).astype(np.float32)


def get_parent_mapping_of_ifc_entities(ifc_file: ifcopenshell.file) -> dict:

    project = ifc_file.by_type(type="IfcProject", include_subtypes=False)[0]
    products = ifc_file.by_type(type="IfcProduct", include_subtypes=True)
    ifc_entities = [project] + products

    family_info_by_ifc_guid = {}
    for child in ifc_entities:
        family_info_by_ifc_guid[child.GlobalId] = {
            "parent": None,
            "children": [],
        }

    for child in [project] + products:
        parent = ifcopenshell.util.element.get_parent(element=child)
        parent_exists = isinstance(parent, ifcopenshell.entity_instance)
        if parent_exists:
            family_info_by_ifc_guid[child.GlobalId]["parent"] = parent.GlobalId
            family_info_by_ifc_guid[parent.GlobalId]["children"].append(child.GlobalId)

    return family_info_by_ifc_guid


def inverse_matrix(matrix) -> np.ndarray:
    """Compute the inverse of a 4x4 transformation matrix."""
    return np.linalg.inv(matrix).astype(np.float32)


def is_identity_matrix(matrix_array: np.ndarray) -> bool:
    """
    Checks if a given matrix is an identity matrix.

    Args:
        matrix: A list of lists representing the matrix.

    Returns:
        True if the matrix is an identity matrix, False otherwise.
    """
    rows = len(matrix_array)
    if rows == 0:
        return False
    cols = len(matrix_array[0])
    if rows != cols:
        return False

    for i in range(rows):
        for j in range(cols):
            if i == j:
                if matrix_array[i][j] != 1:
                    return False
            else:
                if matrix_array[i][j] != 0:
                    return False
    return True


def get_ifc_metadata_for_all_nodes(
    glb_file: GLTF2, ifc_file: ifcopenshell.file, flatten_metadata: bool = False
) -> dict:

    # Initialize dictionary to store metadata as JSON strings for each node
    metadata_for_all_nodes = {}

    # Create Metadata for each node
    for index_for_node, node in enumerate(glb_file.nodes):

        # Get IFC Entity for Parent Node
        assert node.extras
        index_of_parent_node = node.extras["parent"]
        if isinstance(index_of_parent_node, int):
            parent_node = glb_file.nodes[index_of_parent_node]
            assert isinstance(parent_node.name, str)
            parent_ifc_entity = ifc_file.by_guid(guid=parent_node.name)
            parent_id = parent_ifc_entity.GlobalId
        else:
            parent_id = None

        # Get IFC Entity for Node
        assert isinstance(node.name, str)
        ifc_entity = ifc_file.by_guid(guid=node.name)

        # Get depth
        depth = node.extras.get("depth")

        # Get PropertySets and QuantityTakeOffSets
        psets_and_qtos = ifcopenshell.util.element.get_psets(element=ifc_entity)
        if flatten_metadata:
            flattened_psets_and_qtos = {}
            for property_set_name, property_set_data in psets_and_qtos.items():
                for property_name, property_value in property_set_data.items():
                    flattened_psets_and_qtos[f"{property_set_name}/{property_name}"] = (
                        str(property_value)
                    )
            psets_and_qtos = flattened_psets_and_qtos

        # Build  metadata
        metadata = {
            "name": str(ifc_entity.Name),
            "class": ifc_entity.is_a(),
            "guid": ifc_entity.GlobalId,
            "parent_guid": str(parent_id),
            "depth": depth,
            "psets_and_qtos": psets_and_qtos,
            # "UNIQUE_ID": '"94073b9e-1483-4f6a-a624-384ed1a3dd7d-0063e7ff"',
            # "Identity Data/Edited by": '""',
            # "Identity Data/Workset": '"2038"',
            # "Other/Category": '"Generic Models"',
            # "Other/Family and Type": '"3D-Base Plate DOOR 1 : 3D-Base Plate DOOR 1"',
            # "Phasing/Phase Created": '"Loading Dock (OdBmProjectPhase)"',
            # "Constraints/Level": '"LOADING DOCK (OdBmLevel)"',
            # "Constraints/Work Plane": '"Level : LOADING DOCK"',
            # "Constraints/Schedule Level": '"LOADING DOCK (OdBmLevel)"',
            # "Constraints/Host": '"Foundation Slab : 30\\" Foundation Slab"',
            # "Constraints/Elevation from Level": '"0.000000000000"',
            # "Id": "1184",
        }

        # Save the Metadata as string for later
        metadata_for_all_nodes[index_for_node] = metadata

    return metadata_for_all_nodes
