# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.material
import ifcopenshell.api.structural
import inlbim.api.representation
import inlbim.util.geometry
import inlbim.util.structural
import inlbim.util.file
import ifcopenshell.api.project
import inlbim.api.material
import inlbim.api.product
import math
import numpy as np
import inlbim.api.structural
import ifcopenshell.util.element


def add_structural_analysis_model(
    ifc4_file: ifcopenshell.file,
    name: str | None = None,
    predefined_type: str | None = "LOADING_3D",
):
    """Create IfcStructuralAnalysisModel"""

    structural_analysis_model = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcStructuralAnalysisModel",
        name=name,
        predefined_type=predefined_type,
    )

    shared_placement = ifc4_file.createIfcLocalPlacement()
    shared_placement.RelativePlacement = ifc4_file.createIfcAxis2Placement3D(
        ifc4_file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
        ifc4_file.createIfcDirection((0.0, 0.0, 1.0)),
        ifc4_file.createIfcDirection((1.0, 0.0, 0.0)),
    )
    structural_analysis_model.SharedPlacement = shared_placement

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    ifcopenshell.api.project.assign_declaration(
        file=ifc4_file,
        definitions=[structural_analysis_model],
        relating_context=project,
    )

    return structural_analysis_model


def create_3pt_structural_curve_member(
    p1: tuple[float, float, float],
    p2: tuple[float, float, float],
    p3: tuple[float, float, float],
    profile_def: ifcopenshell.entity_instance,
    material: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    structural_curve_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    corresponding_product: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:
    """Create 3pt IfcStructuralCurveMember"""

    # Get IFC4 File
    ifc4_file = profile_def.file

    # Create StructuralCurveMember
    if structural_curve_member is None:
        structural_curve_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStructuralCurveMember",
            name=name,
            predefined_type="NOTDEFINED",
        )
        if name is None:
            name = f"FrameMember-{structural_curve_member.id()}"
            structural_curve_member.Name = name

    # Assign StructuralCurveMember to StructuralAnalysisModel
    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_curve_member],
        structural_analysis_model=structural_analysis_model,
    )
    structural_curve_member.ObjectPlacement = structural_analysis_model.SharedPlacement

    # Add Axis (aka Z-axis orientation) attribute
    z_axis = np.array(p3) - np.array(p1)
    structural_curve_member.Axis = ifc4_file.createIfcDirection(
        tuple([float(val) for val in z_axis])
    )

    # Create Vertex Points
    vertex_points = []
    for point in [p1, p2]:
        vertex_points.append(
            inlbim.api.representation.add_vertex_point(
                ifc4_file=ifc4_file, point_coordinates=point
            )
        )

    # Add and assign representation
    representation_item = inlbim.api.representation.add_edge(
        edge_start=vertex_points[0],
        edge_end=vertex_points[1],
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type="Edge",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_curve_member,
        representation=shape_model,
    )

    # Add and Assign MaterialProfileSetUsage
    material_profile_set = (
        inlbim.api.material.add_material_profile_set_with_single_material_profile(
            material=material,
            profile=profile_def,
            check_for_duplicate=True,
        )
    )
    material_profile_set_usage = ifc4_file.create_entity(
        type="IfcMaterialProfileSetUsage"
    )
    material_profile_set_usage.ForProfileSet = material_profile_set
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[structural_curve_member],
        material=material_profile_set_usage,
    )

    # Add and Assign StructuralPointConnections
    for vertex_point in vertex_points:
        structural_point_connection = create_structural_point_connection(
            vertex_point=vertex_point,
            structural_analysis_model=structural_analysis_model,
            name=None,
        )
        ifcopenshell.api.structural.add_structural_member_connection(
            file=ifc4_file,
            relating_structural_member=structural_curve_member,
            related_structural_connection=structural_point_connection,
        )

    # Assign to corresponding IfcProduct
    if corresponding_product:
        inlbim.api.product.assign_product(
            file=ifc4_file,
            objects=[structural_curve_member],
            product=corresponding_product,
        )

    return structural_curve_member


def create_npt_structural_surface_member(
    outer_profile: list[tuple[float, float, float]],  # Global XYZ
    inner_profiles: list[list[tuple[float, float, float]]],  # Global XYZ
    thickness: float,
    material: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    structural_surface_member: ifcopenshell.entity_instance | None = None,
    name: str | None = None,
    corresponding_product: ifcopenshell.entity_instance | None = None,
) -> ifcopenshell.entity_instance:
    """Create npt IfcStructuralSurfaceMember"""

    # Get IFC4 File
    ifc4_file = material.file

    # Create StructuralCurveMember
    if structural_surface_member is None:
        structural_surface_member = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcStructuralSurfaceMember",
            name=name,
            predefined_type="NOTDEFINED",
        )
    if name is None and structural_surface_member.Name is None:
        name = f"StructuralSurfaceMember-{structural_surface_member.id()}"
        structural_surface_member.Name = name

    # Assign StructuralSurfaceMember to StructuralAnalysisModel
    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_surface_member],
        structural_analysis_model=structural_analysis_model,
    )
    structural_surface_member.ObjectPlacement = (
        structural_analysis_model.SharedPlacement
    )

    # Assign thickness
    structural_surface_member.Thickness = thickness

    # Create Vertex Points of Outer Profile
    vertex_points_of_outer_profile = []
    for point in outer_profile:
        vertex_points_of_outer_profile.append(
            inlbim.api.representation.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=point,
            )
        )

    # Create Vertex Points of Inner Profiles
    vertex_points_of_inner_profiles = []
    for inner_profile in inner_profiles:
        vertex_points_of_inner_profile = []
        for point in inner_profile:
            vertex_points_of_inner_profile.append(
                inlbim.api.representation.add_vertex_point(
                    ifc4_file=ifc4_file,
                    point_coordinates=point,
                )
            )
        vertex_points_of_inner_profiles.append(vertex_points_of_inner_profile)

    # Add and assign representation
    representation_item = inlbim.api.representation.add_face_surface(
        vertex_points_of_outer_bound=vertex_points_of_outer_profile,
        vertex_points_of_inner_bounds=vertex_points_of_inner_profiles,
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type="Face",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_surface_member,
        representation=shape_model,
    )

    # Add and Assign MaterialLayerSetUsage
    material_layer_set = inlbim.api.material.add_material_layer_set(
        materials=[material],
        thicknesses=[thickness],
        name=None,
        check_for_duplicate=True,
    )
    material_layer_set_usage = ifc4_file.create_entity(type="IfcMaterialLayerSetUsage")
    material_layer_set_usage.ForLayerSet = material_layer_set
    material_layer_set_usage.LayerSetDirection = "AXIS3"
    material_layer_set_usage.DirectionSense = "POSITIVE"
    material_layer_set_usage.OffsetFromReferenceLine = -thickness / 2
    ifcopenshell.api.material.assign_material(
        file=ifc4_file,
        products=[structural_surface_member],
        material=material_layer_set_usage,
    )

    # Add and Assign StructuralPointConnections
    for vertex_point in vertex_points_of_outer_profile:
        structural_point_connection = create_structural_point_connection(
            vertex_point=vertex_point,
            structural_analysis_model=structural_analysis_model,
            name=None,
        )
        ifcopenshell.api.structural.add_structural_member_connection(
            file=ifc4_file,
            relating_structural_member=structural_surface_member,
            related_structural_connection=structural_point_connection,
        )
    for vertex_points_of_inner_profile in vertex_points_of_inner_profiles:
        for vertex_point in vertex_points_of_inner_profile:
            structural_point_connection = create_structural_point_connection(
                vertex_point=vertex_point,
                structural_analysis_model=structural_analysis_model,
                name=None,
            )
            ifcopenshell.api.structural.add_structural_member_connection(
                file=ifc4_file,
                relating_structural_member=structural_surface_member,
                related_structural_connection=structural_point_connection,
            )

    # Assign to corresponding IfcProduct
    if corresponding_product:
        inlbim.api.product.assign_product(
            file=ifc4_file,
            objects=[structural_surface_member],
            product=corresponding_product,
        )

    return structural_surface_member


def create_structural_point_connection(
    vertex_point: ifcopenshell.entity_instance,
    structural_analysis_model: ifcopenshell.entity_instance,
    name: str | None = None,
) -> ifcopenshell.entity_instance:
    """Create IfcStructuralPointConnection"""

    # Get IFC4 File
    ifc4_file = vertex_point.file

    # Create IfcStructuralPointConnection
    structural_point_connection = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcStructuralPointConnection",
        name=name,
    )
    if name is None:
        name = f"Node-{structural_point_connection.id()}"
        structural_point_connection.Name = name

    # Assign StructuralCurveMember to StructuralAnalysisModel
    ifcopenshell.api.structural.assign_structural_analysis_model(
        file=structural_analysis_model.file,
        products=[structural_point_connection],
        structural_analysis_model=structural_analysis_model,
    )
    structural_point_connection.ObjectPlacement = (
        structural_analysis_model.SharedPlacement
    )

    # Add and assign representation
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcTopologyRepresentation",
        representation_identifier="Reference",
        representation_type="Vertex",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[vertex_point],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=structural_point_connection,
        representation=shape_model,
    )

    return structural_point_connection


def merge_all_coincident_structural_point_connections(
    ifc4sav_file: ifcopenshell.file,
):

    # Get Model Precision
    model_precision = inlbim.util.file.get_precision_of_project(ifc4_file=ifc4sav_file)

    # Set up node groups
    node_groups = {}
    num_x_divisions = 8
    num_y_divisions = 8
    num_z_divisions = 8
    for x_group_num in range(num_x_divisions):
        for y_group_num in range(num_y_divisions):
            for z_group_num in range(num_z_divisions):
                group_key = f"{x_group_num}{y_group_num}{z_group_num}"
                node_groups[group_key] = []
    all_nodes = ifc4sav_file.by_type(
        type="IfcStructuralPointConnection", include_subtypes=False
    )

    # Get parameters for equations used to group nodes
    x_vals = set()
    y_vals = set()
    z_vals = set()
    for node in all_nodes:
        coordinates_of_node = (
            inlbim.util.structural.get_coordinates_of_structural_point_connection(
                structural_point_connection=node,
            )
        )
        x_vals.add(coordinates_of_node[0])
        y_vals.add(coordinates_of_node[1])
        z_vals.add(coordinates_of_node[2])
    x_val_min = min(x_vals) - 1
    x_val_max = max(x_vals) + 1
    slope_for_x = num_x_divisions / (x_val_max - x_val_min)
    y_val_min = min(y_vals) - 1
    y_val_max = max(y_vals) + 1
    slope_for_y = num_y_divisions / (y_val_max - y_val_min)
    z_val_min = min(z_vals) - 1
    z_val_max = max(z_vals) + 1
    slope_for_z = num_z_divisions / (z_val_max - z_val_min)

    # Sort the nodes into groups
    for node in all_nodes:
        coordinates_of_node = (
            inlbim.util.structural.get_coordinates_of_structural_point_connection(
                structural_point_connection=node,
            )
        )
        x_val = coordinates_of_node[0]
        x_group_num = math.floor(slope_for_x * x_val + -slope_for_x * x_val_min)
        y_val = coordinates_of_node[1]
        y_group_num = math.floor(slope_for_y * y_val + -slope_for_y * y_val_min)
        z_val = coordinates_of_node[2]
        z_group_num = math.floor(slope_for_z * z_val + -slope_for_z * z_val_min)
        group_key = f"{x_group_num}{y_group_num}{z_group_num}"
        node_groups[group_key].append(node)

    # Sanity Check
    count_of_nodes_in_groups = 0
    for node_group in node_groups.values():
        count_of_nodes_in_groups += len(node_group)
    if count_of_nodes_in_groups != len(all_nodes):
        exit("Not all nodes accounted for. Aborting.")

    # Merge Nodes
    all_merged_nodes = []
    for node_group in node_groups.values():
        trial_nodes = node_group
        merged_nodes = []
        for trial_node in trial_nodes:
            trial_node_is_unique = True
            for merged_node in merged_nodes:
                nodes_are_coincident = inlbim.util.structural.two_structural_point_connections_are_coincident(
                    structural_point_connection_1=merged_node,
                    structural_point_connection_2=trial_node,
                    tolerance=model_precision,
                )
                if nodes_are_coincident:
                    trial_node_is_unique = False
                    merge_two_structural_point_connections_together(
                        replacing_structural_point_connection=merged_node,
                        replaced_structural_point_connection=trial_node,
                    )
                    break
            if trial_node_is_unique:
                merged_nodes.append(trial_node)
                all_merged_nodes.append(trial_node)

    return ifc4sav_file


def merge_two_structural_point_connections_together(
    replacing_structural_point_connection: ifcopenshell.entity_instance,
    replaced_structural_point_connection: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance:

    # Get IFC File
    ifc4sav_file = replacing_structural_point_connection.file

    # Replace structural connections
    assert isinstance(
        replaced_structural_point_connection.ConnectsStructuralMembers, tuple
    )
    for (
        rel_connects_structural_member
    ) in replaced_structural_point_connection.ConnectsStructuralMembers:
        rel_connects_structural_member.RelatedStructuralConnection = (
            replacing_structural_point_connection
        )

    # Replace VertexPoint
    replacing_vertex_point = (
        inlbim.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=replacing_structural_point_connection,
        )
    )
    replaced_vertex_point = (
        inlbim.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=replaced_structural_point_connection,
        )
    )
    assert isinstance(replaced_vertex_point, ifcopenshell.entity_instance)
    entities_refercing_replaced_vertex_point = ifc4sav_file.get_inverse(
        inst=replaced_vertex_point
    )
    for entity in entities_refercing_replaced_vertex_point:
        if not isinstance(entity, ifcopenshell.entity_instance):
            continue
        if entity.is_a() == "IfcEdge":
            if entity.EdgeStart == replaced_vertex_point:
                entity.EdgeStart = replacing_vertex_point
                continue
            elif entity.EdgeEnd == replaced_vertex_point:
                entity.EdgeEnd = replacing_vertex_point
                continue

    # Get replaced CartesianPoint
    replaced_cartesian_point = replaced_vertex_point.VertexGeometry

    # Get replaced ProductDefinitionShape
    replaced_product_definition_shape = (
        replaced_structural_point_connection.Representation
    )

    # Get replaced Topologyrepresentation
    assert isinstance(replaced_product_definition_shape, ifcopenshell.entity_instance)
    assert isinstance(replaced_product_definition_shape.Representations, tuple)
    replaced_topology_representation = (
        replaced_product_definition_shape.Representations[0]
    )

    # Get replaced OwnerHistory
    ifc4_file = replaced_structural_point_connection.file
    owner_history_of_replaced_structural_point_connection = (
        replaced_structural_point_connection.OwnerHistory
    )
    total_inverses_for_owner_history_of_replaced_structural_point_connection = (
        ifc4_file.get_total_inverses(
            inst=owner_history_of_replaced_structural_point_connection
        )
    )
    if total_inverses_for_owner_history_of_replaced_structural_point_connection == 1:
        replaced_owner_history = owner_history_of_replaced_structural_point_connection
    else:
        replaced_owner_history = None

    # Remove replaced entities
    for replaced_entity in [
        replaced_cartesian_point,
        replaced_vertex_point,
        replaced_topology_representation,
        replaced_product_definition_shape,
        replaced_owner_history,
        replaced_structural_point_connection,
    ]:
        if isinstance(replaced_entity, ifcopenshell.entity_instance):
            ifc4sav_file.remove(inst=replaced_entity)

    return replacing_structural_point_connection


def translate_structural_point_connection(
    structural_point_connection: ifcopenshell.entity_instance,
    translation: tuple[float, float, float],
):

    vertex_point = (
        inlbim.util.structural.get_vertex_point_of_structural_point_connection(
            structural_point_connection=structural_point_connection
        )
    )

    old_coordinates = (
        inlbim.util.structural.get_coordinates_of_structural_point_connection(
            structural_point_connection=structural_point_connection
        )
    )

    new_coordinates = (
        old_coordinates[0] + translation[0],
        old_coordinates[1] + translation[1],
        old_coordinates[2] + translation[2],
    )

    old_cartesian_point = vertex_point.VertexGeometry

    ifc4_sav_file = structural_point_connection.file

    count_of_references_to_old_cartesian_point = ifc4_sav_file.get_total_inverses(
        inst=old_cartesian_point
    )

    safe_to_edit_old_cartesian_point = count_of_references_to_old_cartesian_point == 1

    if safe_to_edit_old_cartesian_point:
        old_cartesian_point.Coordinates = new_coordinates

    else:
        new_cartesian_point = ifc4_sav_file.createIfcCartesianPoint(new_coordinates)
        vertex_point.VertexGeometry = new_cartesian_point


def divide_structural_curve_member(
    structural_curve_member: ifcopenshell.entity_instance,
    division_locations_as_proportions_of_length: list[float],
) -> list[ifcopenshell.entity_instance]:

    # Check number of divisions
    if len(division_locations_as_proportions_of_length) == 0:
        return [structural_curve_member]

    # Validate the input list to ensure all division locations are between 0.0 and 1.0 (exclusive)
    if all(0.0 < num < 1.0 for num in division_locations_as_proportions_of_length):
        # Sort the list in ascending order
        division_locations_as_proportions_of_length = sorted(
            division_locations_as_proportions_of_length
        )
    else:
        raise ValueError(
            "All elements in the list must be between 0.0 and 1.0 (exclusive)"
        )

    # Get various parameters
    original_start_point, original_end_point, original_orientation_point = (
        inlbim.util.structural.get_coordinates_of_points_of_linear_structural_curve_member(
            linear_structural_curve_member=structural_curve_member
        )
    )
    length_of_original_member = float(
        np.linalg.norm(np.array(original_end_point) - np.array(original_start_point))
    )
    direction_vector = (
        inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=original_start_point,
            p2=original_end_point,
        )
    )
    local_orientation_axis_in_global_coordinates = (
        inlbim.util.geometry.calculate_unit_direction_vector_between_two_points(
            p1=original_start_point,
            p2=original_orientation_point,
        )
    )

    # Get assigned product
    assigned_product = inlbim.util.structural.get_assigned_product_of_structural_item(
        structural_item=structural_curve_member
    )

    # Get ProfileDef and Material
    material_profile_set = ifcopenshell.util.element.get_material(
        element=structural_curve_member,
        should_skip_usage=True,
    )
    assert isinstance(material_profile_set, ifcopenshell.entity_instance)
    profile_def = material_profile_set.MaterialProfiles[0].Profile
    material = material_profile_set.MaterialProfiles[0].Material

    structural_analysis_model = (
        inlbim.util.structural.get_structural_analysis_model_of_structural_item(
            structural_item=structural_curve_member
        )
    )
    assert structural_analysis_model

    new_end_points = []
    for (
        division_location_as_proportion_of_length
    ) in division_locations_as_proportions_of_length + [1.0]:
        new_end_point = tuple(
            float(val)
            for val in (
                np.array(original_start_point)
                + np.array(direction_vector)
                * division_location_as_proportion_of_length
                * length_of_original_member
            ).tolist()
        )
        assert len(new_end_point) == 3
        new_end_points.append(new_end_point)

    new_structural_curve_members = []
    new_start_point = original_start_point
    for index, new_end_point in enumerate(new_end_points):
        new_orientation_point = tuple(
            float(val)
            for val in (
                np.array(new_start_point)
                + np.array(local_orientation_axis_in_global_coordinates) * 1.0
            ).tolist()
        )
        assert len(new_orientation_point) == 3

        if index == 0:
            translation = tuple(
                float(val)
                for val in (
                    np.array(new_end_point) - np.array(original_end_point)
                ).tolist()
            )
            assert len(translation) == 3
            second_node_of_structural_curve_member = inlbim.util.structural.get_ordered_structural_point_connections_of_linear_structural_curve_member(
                linear_structural_curve_member=structural_curve_member
            )[
                1
            ]
            translate_structural_point_connection(
                structural_point_connection=second_node_of_structural_curve_member,
                translation=translation,
            )
            new_structural_curve_members.append(structural_curve_member)
        else:
            new_structural_curve_member = (
                inlbim.api.structural.create_3pt_structural_curve_member(
                    p1=new_start_point,
                    p2=new_end_point,
                    p3=new_orientation_point,
                    profile_def=profile_def,
                    material=material,
                    structural_analysis_model=structural_analysis_model,
                    corresponding_product=assigned_product,
                )
            )
            new_structural_curve_members.append(new_structural_curve_member)

        new_start_point = new_end_point

    return new_structural_curve_members
