# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to merge two IFC files"""

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.representation
import ifcopenshell.api.style
import ifcopenshell.api.aggregate


def add_source_style_to_destination_file(
    destination_file: ifcopenshell.file, source_style: ifcopenshell.entity_instance
) -> ifcopenshell.entity_instance:
    """Add source IfcSurfaceStyle to destination IFC file"""

    destination_styles = destination_file.by_type(
        type="IfcSurfaceStyle", include_subtypes=False
    )
    for destination_style in destination_styles:
        names_match = destination_style.Name == source_style.Name
        sides_match = destination_style.Side == source_style.Side
        # TODO: Need more thorough comparison of destination_style.Styles and
        # source_style.Styles
        count_of_styles_match = len(destination_style.Styles) == len(
            source_style.Styles
        )
        if all([names_match, sides_match, count_of_styles_match]):
            return destination_style

    return destination_file.add(inst=source_style)


def copy_and_assign_surface_styles_from_source_to_destination_entity(
    source_entity: ifcopenshell.entity_instance,
    destination_entity: ifcopenshell.entity_instance,
):
    """Copy and assign IfcSurfaceStyles from the Source IFC entity to the Destination
    IFC entity"""

    # Get each Item and its SurfaceStyles in the Source and Destination entities.
    # There should be no existing SurfaceStyles for the Items of the Destination
    # entity b/c they should have been lost when the Destination entity was originally
    # created from the Source entity.
    styles_for_each_item_in_source_entity = {}
    styles_for_each_item_in_destination_entity = {}
    for entity, styles_for_each_item_in_entity in zip(
        [
            source_entity,
            destination_entity,
        ],
        [
            styles_for_each_item_in_source_entity,
            styles_for_each_item_in_destination_entity,
        ],
    ):

        # SurfaceStyles for Material
        materials = ifcopenshell.util.element.get_materials(element=entity)
        for material in materials:
            for material_definition_representation in material.HasRepresentation or []:
                for (
                    representation
                ) in material_definition_representation.Representations:
                    for item in representation.Items:
                        styles_for_each_item_in_entity[item.id()] = []
                        styles_for_each_item_in_entity[item.id()].extend(
                            [s for s in item.Styles if s.is_a("IfcSurfaceStyle")]
                        )

        # SurfaceStyles for Physical Representation
        shape_representation_for_entity = (
            ifcopenshell.util.representation.get_representation(
                entity, "Model", "Body", "MODEL_VIEW"
            )
        )
        if not shape_representation_for_entity:
            continue
        queue = list(shape_representation_for_entity.Items)
        while queue:
            item = queue.pop()
            styles_for_each_item_in_entity[item.id()] = []
            if item.is_a("IfcMappedItem"):
                queue.extend(item.MappingSource.MappedRepresentation.Items)
            if item.is_a("IfcBooleanResult"):
                queue.append(item.FirstOperand)
                queue.append(item.SecondOperand)
            if item.StyledByItem:
                styles_for_each_item_in_entity[item.id()].extend(
                    [
                        s
                        for s in item.StyledByItem[0].Styles
                        if s.is_a("IfcSurfaceStyle")
                    ]
                )

    # Check that the Item count is the same for each entity. If the Destination
    # entity was properly created from the Source entity, then this check should never
    # be violated.
    count_of_items_match_for_each_entity = len(
        styles_for_each_item_in_source_entity
    ) == len(styles_for_each_item_in_destination_entity)
    if not count_of_items_match_for_each_entity:
        return

    # Create IfcSurfaceStyles for the Destination entity
    for source_item_id, destination_item_id in zip(
        styles_for_each_item_in_source_entity.keys(),
        styles_for_each_item_in_destination_entity,
    ):
        source_styles = styles_for_each_item_in_source_entity[source_item_id]
        destination_styles = []
        for source_style in source_styles:
            # destination_style = destination_entity.file.add(inst=source_style)
            destination_style = add_source_style_to_destination_file(
                destination_file=destination_entity.file, source_style=source_style
            )
            destination_styles.append(destination_style)
        styles_for_each_item_in_destination_entity[destination_item_id] = (
            destination_styles
        )

    # Assign the IfcSurfaceStyles to the corresponding Items for the Destination entity
    for (
        destination_item_id,
        destination_styles,
    ) in styles_for_each_item_in_destination_entity.items():
        destination_item = destination_entity.file.by_id(id=destination_item_id)
        for destination_style in destination_styles:
            ifcopenshell.api.style.assign_item_style(
                file=destination_entity.file,
                item=destination_item,
                style=destination_style,
            )


def nest_undeclared_products_under_project(ifc4_file: ifcopenshell.file):

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    products = ifc4_file.by_type(type="IfcProduct", include_subtypes=True)

    undeclared_products = []
    for product in products:
        parent_ifc_product = ifcopenshell.util.element.get_parent(element=product)
        if parent_ifc_product is None:
            undeclared_products.append(product)

    if len(undeclared_products) > 0:
        for undeclared_product in undeclared_products:
            print("\t" + undeclared_product.to_string())
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=undeclared_products,
            relating_object=project,
        )


def merge_projects(
    destination_ifc4_file: ifcopenshell.file,
    source_ifc4_files: list[ifcopenshell.file],
    nest_undeclared_products_under_projects_before_merge: bool = False,
) -> ifcopenshell.file:

    if nest_undeclared_products_under_projects_before_merge:
        for ifc4_file in [destination_ifc4_file] + source_ifc4_files:
            nest_undeclared_products_under_project(ifc4_file=ifc4_file)

    for source_ifc4_file in source_ifc4_files:
        destination_ifc4_file = merge_two_projects(
            destination_ifc4_file=destination_ifc4_file,
            source_ifc4_file=source_ifc4_file,
        )

    return destination_ifc4_file


def merge_two_projects(
    destination_ifc4_file: ifcopenshell.file,
    source_ifc4_file: ifcopenshell.file,
) -> ifcopenshell.file:

    # Get IfcProjects for destination and source IFC4 Files
    destination_project = destination_ifc4_file.by_type("IfcProject")[0]
    source_project = destination_ifc4_file.add(
        inst=source_ifc4_file.by_type("IfcProject")[0]
    )

    # Cycle through IfcRoots in the source IFC4 File
    # IfcRoots include IfcProject, IfcBeam, IfcBuilding, IfcBuildingStorey,
    # IfcSite, IfcBeamType, IfcRelAssociatesMaterial,
    # IfcRelContainedInSpatialStructure, IfcRelAggregates, IfcRelDefinesByType, etc.
    for root_inst_in_source in source_ifc4_file.by_type(
        type="IfcRoot", include_subtypes=True
    ):

        # Add IfcRoot from source to destination IFC4 File
        root_inst_in_destination = destination_ifc4_file.add(inst=root_inst_in_source)

        # Copy and assign IfcSurfaceStyles from the Source IFC entity to the
        # Destination IFC entity
        copy_and_assign_surface_styles_from_source_to_destination_entity(
            source_entity=root_inst_in_source,
            destination_entity=root_inst_in_destination,
        )

    # Entities Referencing Source Project include IfcRelAggregates, IfcRelDeclares, etc.
    for entity_referencing_source_project in destination_ifc4_file.get_inverse(
        inst=source_project
    ):
        ifcopenshell.util.element.replace_attribute(
            element=entity_referencing_source_project,
            old=source_project,
            new=destination_project,
        )

    # Remove the source project from the destination IFC4 File
    destination_ifc4_file.remove(inst=source_project)

    return destination_ifc4_file
