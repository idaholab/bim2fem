# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell
import ifcopenshell.api.spatial
import ifcopenshell.api.owner


def assign_object_v2(
    products: list[ifcopenshell.entity_instance],
    relating_object: ifcopenshell.entity_instance,
    place_relative_to_parent: bool = True,
) -> ifcopenshell.entity_instance | None:
    """Assigns object as an aggregate to the products"""

    file = relating_object.file

    if not products:
        return

    products_set = set(products)
    is_decomposed_by = next(
        (i for i in relating_object.IsDecomposedBy if i.is_a("IfcRelAggregates")), None
    )

    previous_aggregates_rels: set[ifcopenshell.entity_instance] = set()
    products_without_aggregates: list[ifcopenshell.entity_instance] = []
    products_with_aggregates: list[ifcopenshell.entity_instance] = []

    # check if there is anything to change
    for product in products_set:
        product_rel = next(iter(product.Decomposes), None)

        if product_rel is None:
            products_without_aggregates.append(product)
            continue

        # either is_decomposed_by is None or product is part of different rel
        if product_rel != is_decomposed_by:
            previous_aggregates_rels.add(product_rel)
            products_with_aggregates.append(product)

        # products with already assigned aggregates will be skipped

    products_to_change = products_without_aggregates + products_with_aggregates
    # nothing to change
    if not products_to_change:
        return is_decomposed_by

    # can be either only aggregated or only contained at the same time
    # some product might not be able to have a container
    possibly_contained_products = [
        p for p in products_without_aggregates if hasattr(p, "ContainedInStructure")
    ]
    ifcopenshell.api.spatial.unassign_container(
        file, products=possibly_contained_products
    )

    # unassign elements from previous aggregates
    for decomposes in previous_aggregates_rels:
        related_objects = set(decomposes.RelatedObjects) - products_set
        if related_objects:
            decomposes.RelatedObjects = list(related_objects)
            ifcopenshell.api.owner.update_owner_history(file, element=decomposes)
        else:
            history = decomposes.OwnerHistory
            file.remove(decomposes)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # assign elements to a new aggregate
    if is_decomposed_by:
        is_decomposed_by.RelatedObjects = list(
            set(is_decomposed_by.RelatedObjects) | products_set
        )
        ifcopenshell.api.owner.update_owner_history(file, element=is_decomposed_by)
    else:
        is_decomposed_by = file.create_entity(
            "IfcRelAggregates",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": list(products_set),
                "RelatingObject": relating_object,
            }
        )

    # localize placement relative to a new container for affected products
    if place_relative_to_parent:
        for product in products_to_change:
            placement = getattr(product, "ObjectPlacement", None)
            if placement and placement.is_a("IfcLocalPlacement"):
                placement_rel_to = getattr(relating_object, "ObjectPlacement", None)
                placement.PlacementRelTo = placement_rel_to

    return is_decomposed_by
