# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved


import ifcopenshell.util.pset


def get_names_of_applicable_property_sets(ifc_class: str) -> list[str]:
    """
    pset_names = inlbim.util.pset.get_names_of_applicable_property_sets(ifc_class="IfcBeam")

    pset_qto = ifcopenshell.util.pset.PsetQto(schema_identifier="IFC4")

    for pset_name in pset_names:
        pset = pset_qto.get_by_name(name=pset_name)
        assert isinstance(pset, ifcopenshell.entity_instance)
        property_templates = pset.HasPropertyTemplates
        print(f"\n{pset.Name}")
        for property_template in property_templates:
            print(f"\t{property_template.Name}")
    """

    pset_qto = ifcopenshell.util.pset.PsetQto(schema_identifier="IFC4")

    pset_templates = pset_qto.get_applicable(ifc_class=ifc_class)

    pset_names = [pset_template.Name for pset_template in pset_templates]

    return pset_names


def property_set_is_applicable(pset_name: str, ifc_class: str) -> bool:

    names_of_applicable_psets = get_names_of_applicable_property_sets(
        ifc_class=ifc_class
    )

    return pset_name in names_of_applicable_psets
