# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import bim2fem.ifcplus.util.material
import bim2fem.ifcplus.api.material
from bim2fem.ifcplus import REGION
import ifcopenshell.api.root
import ifcopenshell
import bim2fem.ifcplus.util.material
import bim2fem.ifcplus.api.material
import ifcopenshell.api.root
import bim2fem.ifcplus.api.structural
import numpy as np
from bim2fem.core.geom_helpers import TriangularMesh
import ifcopenshell.api.spatial
import bim2fem.ifcplus.api.element_type
import ifcopenshell.api.type
import bim2fem.ifcplus.util.project
from typing import cast


def convert_planar_wall_or_slab_to_structural_surface_members(
    planar_wall_or_slab_from_source_file: ifcopenshell.entity_instance,
    ifc4_destination_file: ifcopenshell.file,
    region: REGION,
    structural_analysis_model: ifcopenshell.entity_instance,
) -> list[ifcopenshell.entity_instance] | None:

    planar_building_element_copied_to_destination_file = (
        ifcopenshell.api.root.create_entity(
            file=ifc4_destination_file,
            ifc_class=planar_wall_or_slab_from_source_file.is_a(),
            name=planar_wall_or_slab_from_source_file.Name,
        )
    )
    planar_building_element_copied_to_destination_file.GlobalId = (
        planar_wall_or_slab_from_source_file.GlobalId
    )

    site = ifc4_destination_file.by_type(type="IfcSite", include_subtypes=False)[0]
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_destination_file,
        products=[planar_building_element_copied_to_destination_file],
        relating_structure=site,
    )

    material_names_from_destination_file = list(
        {
            material.Name
            for material in ifc4_destination_file.by_type(
                type="IfcMaterial",
                include_subtypes=False,
            )
        }
    )
    standard_material_name = bim2fem.ifcplus.util.material.get_best_matching_standard_material_from_element_metadata(
        element=planar_wall_or_slab_from_source_file,
        region=region,
        other_material_names=material_names_from_destination_file,
    )
    if standard_material_name is None:
        if region == "Europe":
            standard_material_name = "S355"
        elif region == "UnitedStates":
            standard_material_name = "A36"
        else:
            standard_material_name = "S355"

    material = bim2fem.ifcplus.api.material.add_material_from_standard_library(
        ifc4_file=ifc4_destination_file,
        region=region,
        material_name=standard_material_name,
        check_for_duplicate=True,
    )
    material = cast(ifcopenshell.entity_instance, material)

    triangular_mesh = TriangularMesh.from_ifc_element(
        element=planar_wall_or_slab_from_source_file
    )

    indices_of_all_faces = [_ for _ in range(len(triangular_mesh.faces))]
    areas_of_all_faces = []
    for index_of_face in indices_of_all_faces:
        area_of_face = triangular_mesh.calculate_area_of_face(face_index=index_of_face)
        areas_of_all_faces.append(area_of_face)
    index_of_largest_face_in_group_1 = areas_of_all_faces.index(max(areas_of_all_faces))

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

    areas_of_faces_in_group_2 = []
    for index_of_face in indices_of_faces_in_group_2:
        area_of_face = triangular_mesh.calculate_area_of_face(face_index=index_of_face)
        areas_of_faces_in_group_2.append(area_of_face)
    index_of_largest_face_in_group_2 = indices_of_faces_in_group_2[
        areas_of_faces_in_group_2.index(max(areas_of_faces_in_group_2))
    ]

    numeric_scale = bim2fem.ifcplus.util.project.get_numeric_scale_of_project(
        ifc4_file=ifc4_destination_file
    )

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

    material_layer_set = bim2fem.ifcplus.api.material.add_material_layer_set(
        materials=[material],
        thicknesses=[thickness],
        name=None,
        check_for_duplicate=True,
    )
    element_type = (
        bim2fem.ifcplus.api.element_type.add_element_type_for_material_layer_set(
            ifc_class=planar_building_element_copied_to_destination_file.is_a()
            + "Type",
            material_layer_set=material_layer_set,
            name=material_layer_set.LayerSetName,
            check_for_duplicate=True,
        )
    )
    ifcopenshell.api.type.assign_type(
        file=ifc4_destination_file,
        related_objects=[planar_building_element_copied_to_destination_file],
        relating_type=element_type,
    )

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
        bim2fem.ifcplus.api.structural.create_structural_surface_member(
            outer_profile=translated_coordinates_of_face_in_group_1,
            inner_profiles=[],
            thicknesses=[thickness],
            materials=[material],
            structural_analysis_model=structural_analysis_model,
            product_assigned_to=planar_building_element_copied_to_destination_file,
        )
        structural_items.append(structural_items)

    return structural_items
