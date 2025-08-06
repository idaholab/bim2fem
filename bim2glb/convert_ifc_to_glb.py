# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to convert IFC to GLB"""


import os
from pygltflib import GLTF2, Material
import numpy as np
import ifcopenshell
import ifcopenshell.util.element
import multiprocessing
import subprocess
import json
import bim2glb.util
import bim2glb.api

IFCCONVERT_WINDOWS_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "ifc_convert",
        "windows",
        "IfcConvert.exe",
    )
)

IFCCONVERT_LINUX_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "ifc_convert",
        "linux",
        "IfcConvert",
    )
)

IFCCONVERT_MAC_FILE_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "ifc_convert",
        "macOS",
        "IfcConvert",
    )
)


def convert_ifc_to_glb_using_ifcconvert_executable(
    ifc_input_filename: str,
    glb_output_filename: str,
) -> str:
    """Convert IFC to GLB using IfcConvert Executable"""

    current_os = bim2glb.util.get_os()
    print(f"current_os: {current_os}")
    if current_os == "Linux":
        ifcconvert_file_path = IFCCONVERT_LINUX_FILE_PATH
    elif current_os == "Windows":
        ifcconvert_file_path = IFCCONVERT_WINDOWS_FILE_PATH
    else:
        exit("incompatible OS")
    print(f"ifcconvert_file_path exists: {os.path.exists(ifcconvert_file_path)}")

    # Remove duplicate GLBs
    if os.path.exists(glb_output_filename):
        os.remove(glb_output_filename)

    # Run IfcConvert
    subprocess.run(
        [
            ifcconvert_file_path,
            "-j",
            f"{multiprocessing.cpu_count()+1}",
            "--use-element-guids",
            "--weld-vertices",
            "--center-model",
            ifc_input_filename,
            glb_output_filename,
        ]
    )

    return glb_output_filename


def traverse_nodes_and_correct_local_transforms(
    gltf: GLTF2,
    node_index: int,
    depth: int = 0,
):
    """Recursively traverses the node hierarchy and correct the local 4x4
    transformation matrices."""
    node = gltf.nodes[node_index]
    assert node.extras
    node.extras["depth"] = depth
    ancestors_from_parent_to_progenitor = bim2glb.util.get_ancestors_of_node(
        gltf=gltf, index_of_child_node=node_index
    )
    new_local_4x4_transform = bim2glb.util.get_node_matrix_array(node=node)
    for ancestor_node_index in ancestors_from_parent_to_progenitor[::-1]:
        ancestor_node = gltf.nodes[ancestor_node_index]
        ancestor_local_4x4_transform = bim2glb.util.get_node_matrix_array(
            node=ancestor_node
        )
        new_local_4x4_transform = np.dot(
            bim2glb.util.inverse_matrix(ancestor_local_4x4_transform),
            new_local_4x4_transform,
        )
    bim2glb.api.set_node_matrix(node=node, matrix_array=new_local_4x4_transform)

    # # Print Node information
    # indent = "  " * depth * 4  # Indentation for visualizing hierarchy
    # print(
    #     " - ".join(
    #         [
    #             f"{indent}{node_index}",
    #             f"{node.extras['Class']}{node.extras['Name']}",
    #             "".join(
    #                 [
    #                     "ancestors_from_parent_to_progenitor: ",
    #                     f"{ancestors_from_parent_to_progenitor}",
    #                 ]
    #             ),
    #         ]
    #     )
    # )

    # Recursively traverse children (if any)
    if node.children:
        for child_index in node.children:
            traverse_nodes_and_correct_local_transforms(gltf, child_index, depth + 1)


def incorporate_ifc_hierarchy_into_glb(
    gltf: GLTF2,
    ifc_file: ifcopenshell.file,
):
    """Incorporate IFC hierarchy into GLB after running IfcConvert"""

    # Map Node Indicies to IFC GlobalIds
    indices_of_nodes_by_ifc_guid = {}
    for index_of_node, node in enumerate(gltf.nodes):
        indices_of_nodes_by_ifc_guid[node.name] = index_of_node

    # Empty the scene
    gltf.scenes[0].nodes = []

    # Establish IFC Child/Parent relationships in Metadata
    for index_for_child_node, child_node in enumerate(gltf.nodes):

        # Get child and parent IfcProducts
        assert isinstance(child_node.name, str)
        child_ifc_product = ifc_file.by_guid(guid=child_node.name)
        parent_ifc_product = ifcopenshell.util.element.get_parent(
            element=child_ifc_product
        )

        # Case 1: Parent Exists
        if isinstance(parent_ifc_product, ifcopenshell.entity_instance):

            # Get Index for Parent Node
            index_for_parent_node = indices_of_nodes_by_ifc_guid[
                parent_ifc_product.GlobalId
            ]

            # Update Parent of Child
            assert child_node.extras
            child_node.extras["parent"] = index_for_parent_node

            # Update Children of Parent
            parent_node = gltf.nodes[index_for_parent_node]
            if parent_node.children is None:
                parent_node.children = [index_for_child_node]
            else:
                parent_node.children.append(index_for_child_node)

        # Case: 2 Parent DNE
        else:

            # Update Parent of Child
            assert child_node.extras
            child_node.extras["parent"] = None

            # Update depth=0 Nodes (ideally, IfcProject should only be here)
            gltf.scenes[0].nodes.append(index_for_child_node)

    # Traverse the graph and update the local transformations
    for index_of_progenitor_node in gltf.scenes[0].nodes:
        traverse_nodes_and_correct_local_transforms(
            gltf=gltf, node_index=index_of_progenitor_node
        )


def convert_ifc_to_glb(
    ifc_input_filename: str,
    glb_output_filename: str,
    show_global_coordinate_system_axes: bool = False,
    delete_intermediate_glb_file: bool = True,
    store_metadata_in_glb_nodes: bool = False,
    store_metadata_in_json: bool = False,
    flatten_metadata: bool = False,
) -> str:
    """Convert IFC to GLB"""

    # Convert to temporary intermediate GLB using IfcConvert
    temp_glb_output_filename = convert_ifc_to_glb_using_ifcconvert_executable(
        ifc_input_filename=ifc_input_filename,
        glb_output_filename=glb_output_filename.replace(".glb", "_temp.glb"),
    )

    # Load temp GLB to GLTF2 object for inspection and editing
    glb_file = GLTF2.load(fname=temp_glb_output_filename)
    assert isinstance(glb_file, GLTF2)
    assert glb_file.scenes[0].nodes

    # Open IFC File
    ifc_file = ifcopenshell.open(path=ifc_input_filename)
    assert isinstance(ifc_file, ifcopenshell.file)

    # Get IFC Parent Mapping
    family_info_by_ifc_guid = bim2glb.util.get_parent_mapping_of_ifc_entities(
        ifc_file=ifc_file
    )

    # Get the GlobalIds of IfcEntities that are already in the scene as GLB Nodes
    ifc_guids_of_products_already_in_the_scene = [node.name for node in glb_file.nodes]

    # Get the GlobalIds of IfcEntities that are not yet in the scene as GLB Nodes
    project = ifc_file.by_type(type="IfcProject", include_subtypes=False)[0]
    products = ifc_file.by_type(type="IfcProduct", include_subtypes=True)
    ifc_entities = [project] + products
    ifc_guids_of_desireable_entities_not_yet_in_the_scene = []
    for ifc_entity in ifc_entities:

        ifc_entity_is_already_in_the_scene = (
            ifc_entity.GlobalId in ifc_guids_of_products_already_in_the_scene
        )
        if ifc_entity_is_already_in_the_scene:
            continue

        if ifc_entity.is_a("IfcOpeningElement"):
            continue

        count_of_children = len(
            family_info_by_ifc_guid[ifc_entity.GlobalId]["children"]
        )
        ifc_entity_has_no_children = count_of_children == 0
        if ifc_entity_has_no_children:
            continue

        ifc_guids_of_desireable_entities_not_yet_in_the_scene.append(
            ifc_entity.GlobalId
        )

    # Create Nodes for desireable IFC entities not yet in the Scene
    for ifc_guid in ifc_guids_of_desireable_entities_not_yet_in_the_scene:
        ifc_entity = ifc_file.by_guid(guid=ifc_guid)
        index_of_node = bim2glb.api.create_node(gltf=glb_file, name=ifc_entity.GlobalId)
        glb_file.scenes[0].nodes.append(index_of_node)

    # Scrape IFC Metadata into each Node
    for node in glb_file.nodes:
        assert node.name
        ifc_entity = ifc_file.by_guid(guid=ifc_guid)
        node.extras = {
            "Class": ifc_entity.is_a(),
            "GlobalId": ifc_entity.GlobalId,
            "Name": ifc_entity.Name,
            "Description": ifc_entity.Description,
        }

    # Incorporate IFC Hierarchy into GLB
    incorporate_ifc_hierarchy_into_glb(gltf=glb_file, ifc_file=ifc_file)

    # Alpha cutoff is supported only for 'MASK' alpha mode.
    for material in glb_file.materials:
        assert isinstance(material, Material)
        if isinstance(material.alphaCutoff, float):
            material.alphaMode = "MASK"

    # Show global coords via boxes
    if show_global_coordinate_system_axes:
        bim2glb.api.create_shapes_representing_cartesian_coordinate_axes(gltf=glb_file)

    # Store Metadata
    metadata_requested = any([store_metadata_in_glb_nodes, store_metadata_in_json])
    if metadata_requested:
        metadata_for_all_nodes = bim2glb.util.get_ifc_metadata_for_all_nodes(
            glb_file=glb_file, ifc_file=ifc_file, flatten_metadata=flatten_metadata
        )
        if store_metadata_in_glb_nodes:
            for index_for_node, node in enumerate(glb_file.nodes):
                node.extras = metadata_for_all_nodes[index_for_node]
        if store_metadata_in_json:
            json_output_filename = glb_output_filename.replace(".glb", "_metadata.json")
            with open(json_output_filename, "w") as json_file:
                json.dump(list(metadata_for_all_nodes.values()), json_file, indent=2)

    # Write to file
    glb_file.save(fname=glb_output_filename)

    # Remove Intermediate GLB file
    if delete_intermediate_glb_file:
        if os.path.exists(temp_glb_output_filename):
            os.remove(temp_glb_output_filename)

    return glb_output_filename
