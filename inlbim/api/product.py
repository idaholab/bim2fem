# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell
import ifcopenshell.api.owner
import ifcopenshell.guid


def assign_product(
    file: ifcopenshell.file,
    objects: list[ifcopenshell.entity_instance],
    product: ifcopenshell.entity_instance,
) -> ifcopenshell.entity_instance | None:
    """Assigns objects to a product

    If an object is already assigned to the product, it will not be assigned
    twice.

    :param objects: A list of IfcObjects to assign to the product
    :param product: The IfcProduct to assign the objects to
    :return: The IfcRelAssignsToProduct relationship
        or `None` if `objects` was empty list.

    Example:

    .. code:: python

        product = ifcopenshell.api.root.create_entity(file, "IfcBeam")
        ifcopenshell.api.product.assign_product(file,
            objects=model.by_type("IfcStructuralCurveMember"), product=product)
    """
    if not objects:
        return

    referenced_by: tuple[ifcopenshell.entity_instance, ...]
    if not (referenced_by := product.ReferencedBy):
        return file.create_entity(
            "IfcRelAssignsToProduct",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "OwnerHistory": ifcopenshell.api.owner.create_owner_history(file),
                "RelatedObjects": objects,
                "RelatingProduct": product,
            },
        )
    rel = referenced_by[0]
    related_objects = set(rel.RelatedObjects) or set()
    objects_set = set(objects)
    if objects_set.issubset(related_objects):
        return rel
    rel.RelatedObjects = list(related_objects | objects_set)
    ifcopenshell.api.owner.update_owner_history(file=file, element=rel)
    return rel
