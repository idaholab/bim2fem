# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import inlbim.util.material
import inlbim.api.material
from inlbim import REGION
import ifcopenshell.api.root
import ifcopenshell
import inlbim.util.material
import inlbim.api.material
import ifcopenshell.api.root
import inlbim.api.structural
import numpy as np
from inlbim.util.geometry import TriangularMesh
import ifcopenshell.api.spatial
import inlbim.api.element_type
import ifcopenshell.api.type
import ifcopenshell.api.project
import inlbim.util.file


def convert_planar_slab_or_wall_to_structural_item(
    slab_or_wall_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance] | None:

    print("\tconvert_planar_slab_or_wall_to_structural_item()")
    print(f"\tslab_or_wall_from_source_file: {slab_or_wall_from_source_file}")
    print(f"\tregion: {region}")
    print(f"\tstructural_analysis_model: {structural_analysis_model}")

    # Add Slab/Wall to destination file with the original IfcGlobalId
    if slab_or_wall_from_source_file.is_a("IfcWall"):
        element_class = "IfcWall"
    elif slab_or_wall_from_source_file.is_a("IfcSlab"):
        element_class = "IfcSlab"
    else:
        return None
    slab_or_wall_copied_to_destination_file = ifcopenshell.api.root.create_entity(
        file=ifc4_destination_file,
        ifc_class=element_class,
        name=slab_or_wall_from_source_file.Name,
    )
    site = ifc4_destination_file.by_type(type="IfcSite", include_subtypes=False)[0]
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_destination_file,
        products=[slab_or_wall_copied_to_destination_file],
        relating_structure=site,
    )

    # Get best matching standard material name, if it exists
    material_names_from_destination_file = list(
        {
            material.Name
            for material in ifc4_destination_file.by_type(
                type="IfcMaterial",
                include_subtypes=False,
            )
        }
    )
    standard_material_name = (
        inlbim.util.material.get_best_matching_standard_material_from_element_metadata(
            element=slab_or_wall_from_source_file,
            region=region,
            other_material_names=material_names_from_destination_file,
        )
    )
    if standard_material_name is None:
        if region == "Europe":
            standard_material_name = "S355"
        elif region == "UnitedStates":
            standard_material_name = "A36"
        else:
            standard_material_name = "S355"
    print(f"\tstandard_material_name: {standard_material_name}")

    # Create the standard material
    material = inlbim.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    assert isinstance(material, ifcopenshell.entity_instance)

    # Triangular Mesh
    triangular_mesh = TriangularMesh.from_ifc_element(
        element=slab_or_wall_from_source_file
    )
    # triangular_mesh.plot_all()

    # Get largest face
    indices_of_all_faces = [_ for _ in range(len(triangular_mesh.faces))]
    areas_of_all_faces = []
    for index_of_face in indices_of_all_faces:
        area_of_face = triangular_mesh.calculate_area_of_face(face_index=index_of_face)
        areas_of_all_faces.append(area_of_face)
    index_of_largest_face_in_group_1 = areas_of_all_faces.index(max(areas_of_all_faces))

    # Get faces coplanar to largest face
    indices_of_faces_in_group_1 = []
    indices_of_faces_in_group_2 = []
    for index_of_trial_face in indices_of_all_faces:
        faces_are_coplanar = triangular_mesh.are_faces_coplanar(
            index_of_face1=index_of_trial_face,
            index_of_face2=index_of_largest_face_in_group_1,
        )
        if faces_are_coplanar:
            indices_of_faces_in_group_1.append(index_of_trial_face)
        else:
            indices_of_faces_in_group_2.append(index_of_trial_face)
    # triangular_mesh.plot_faces_3d(
    #     faces_as_tuples_with_coordinates=triangular_mesh.get_coordinates_of_faces(
    #         indices_of_faces=indices_of_faces_in_group_1
    #     )
    # )

    # Get largest face in group 2
    areas_of_faces_in_group_2 = []
    for index_of_face in indices_of_faces_in_group_2:
        area_of_face = triangular_mesh.calculate_area_of_face(face_index=index_of_face)
        areas_of_faces_in_group_2.append(area_of_face)
    index_of_largest_face_in_group_2 = indices_of_faces_in_group_2[
        areas_of_faces_in_group_2.index(max(areas_of_faces_in_group_2))
    ]

    # Get numeric scale of project (for rounding thickness to a reasonable number)
    numeric_scale = inlbim.util.file.get_numeric_scale_of_project(
        ifc4_file=ifc4_destination_file
    )

    # Calculate distance between largest face in group 1 and largest face in group 2
    normal_vector_of_group_1 = triangular_mesh.calculate_normal_vector_of_face(
        face_index=index_of_largest_face_in_group_1
    )
    point_from_group_1 = triangular_mesh.get_coordinates_of_faces(
        indices_of_faces=[index_of_largest_face_in_group_1]
    )[0][0]
    point_from_group_2 = triangular_mesh.get_coordinates_of_faces(
        indices_of_faces=[index_of_largest_face_in_group_2]
    )[0][0]
    vector_from_point_in_group_2_to_point_in_group_1 = np.array(
        point_from_group_1
    ) - np.array(point_from_group_2)
    thickness = float(
        np.round(
            np.dot(
                vector_from_point_in_group_2_to_point_in_group_1,
                normal_vector_of_group_1,
            ),
            numeric_scale,
        )
    )

    # Add and assign Type
    if slab_or_wall_copied_to_destination_file.is_a("IfcSlab"):
        element_type_class = "IfcSlabType"
    elif slab_or_wall_copied_to_destination_file.is_a("IfcWall"):
        element_type_class = "IfcWallType"
    else:
        element_type_class = "IfcPlateType"
    element_type = inlbim.api.element_type.add_slab_or_wall_or_plate_element_type(
        ifc_class=element_type_class,
        materials=[material],
        thicknesses=[thickness],
        check_for_duplicate=True,
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[slab_or_wall_copied_to_destination_file],
        relating_type=element_type,
    )

    # Declare Type on Project
    project = ifc4_destination_file.by_type(type="IfcProject", include_subtypes=False)[
        0
    ]
    ifcopenshell.api.project.assign_declaration(
        file=ifc4_destination_file,
        definitions=[element_type],
        relating_context=project,
    )

    # Create StructuralItem
    structural_items = []
    for index_of_face_in_group_1 in indices_of_faces_in_group_1:
        coordinates_of_face_in_group_1 = triangular_mesh.get_coordinates_of_faces(
            indices_of_faces=[index_of_face_in_group_1]
        )[0]
        translated_coordinates_of_face_in_group_1 = []
        for point in coordinates_of_face_in_group_1:
            translated_point = tuple(
                val
                for val in (
                    np.array(point)
                    + -1 * np.array(normal_vector_of_group_1) * thickness / 2.0
                ).tolist()
            )
            translated_coordinates_of_face_in_group_1.append(translated_point)
        inlbim.api.structural.create_npt_structural_surface_member(
            outer_profile=translated_coordinates_of_face_in_group_1,
            inner_profiles=[],
            thickness=thickness,
            material=material,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=slab_or_wall_copied_to_destination_file,
        )
        structural_items.append(structural_items)

    return structural_items
