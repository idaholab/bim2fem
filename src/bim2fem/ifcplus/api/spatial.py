import ifcopenshell
import ifcopenshell.guid
import ifcopenshell.api.owner
import ifcopenshell.api.aggregate
import ifcopenshell.util.element
from typing import Union


def assign_container_v2(
    products: list[ifcopenshell.entity_instance],
    relating_structure: ifcopenshell.entity_instance,
    place_relative_to_parent: bool = True,
) -> Union[ifcopenshell.entity_instance, None]:
    """Assigns products to be contained hierarchically in a space"""

    file = relating_structure.file

    if not products:
        return

    products_set = set(products)
    structure_rel = next(iter(relating_structure.ContainsElements), None)

    previous_containers_rels: set[ifcopenshell.entity_instance] = set()
    products_without_containers: list[ifcopenshell.entity_instance] = []
    products_with_containers: list[ifcopenshell.entity_instance] = []

    # check if there is anything to change
    for product in products_set:
        product_rel = next(iter(product.ContainedInStructure), None)

        if product_rel is None:
            products_without_containers.append(product)
            continue

        # either structure_rel is None or product is part of different rel
        if product_rel != structure_rel:
            previous_containers_rels.add(product_rel)
            products_with_containers.append(product)

        # products with already assigned containers will be skipped

    products_to_change = products_without_containers + products_with_containers
    # nothing to change
    if not products_to_change:
        return structure_rel

    # can be either only aggregated or only contained at the same time
    ifcopenshell.api.aggregate.unassign_object(
        file, products=products_without_containers
    )

    # unassign elements from previous containers
    for rel in previous_containers_rels:
        related_elements = set(rel.RelatedElements) - products_set
        if related_elements:
            rel.RelatedElements = list(related_elements)
            ifcopenshell.api.owner.update_owner_history(file, element=rel)
        else:
            history = rel.OwnerHistory
            file.remove(rel)
            if history:
                ifcopenshell.util.element.remove_deep2(file, history)

    # assign elements to a new container
    if structure_rel:
        structure_rel.RelatedElements = list(
            set(structure_rel.RelatedElements) | products_set
        )
        ifcopenshell.api.owner.update_owner_history(file, element=structure_rel)
    else:
        structure_rel = file.create_entity(
            "IfcRelContainedInSpatialStructure",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedElements": list(products_set),
                "RelatingStructure": relating_structure,
            }
        )

    # localize placement relative to a new container for affected products
    if place_relative_to_parent:
        for product in products_to_change:
            placement = getattr(product, "ObjectPlacement", None)
            if placement and placement.is_a("IfcLocalPlacement"):
                placement_rel_to = getattr(relating_structure, "ObjectPlacement", None)
                placement.PlacementRelTo = placement_rel_to

    return structure_rel
