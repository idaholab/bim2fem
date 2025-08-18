# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")),
)


from inlbim import current_time
import time
import chime
import ifcopenshell
import ifcopenshell.util.selector
from pprint import pprint


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Get IFC input filename
    ifc_input_fname = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "files",
            "small_structure_RV.ifc",
        )
    )

    # Open IFC
    ifc4_file = ifcopenshell.open(path=ifc_input_fname)
    assert isinstance(ifc4_file, ifcopenshell.file)

    # Facet type: entity
    all_products = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="IfcProduct",
        elements=None,
    )
    print("\nall_products:")
    pprint(all_products)

    # Facet type: entity
    all_elements = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="IfcElement",
        elements=None,
    )
    print("\nall_elements:")
    pprint(all_elements)

    # Facet type: entity
    columns_by_class = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="IfcColumn",
        elements=None,
    )
    print("\ncolumns_by_class:")
    pprint(columns_by_class)

    # Facet type: instance
    first_column_by_guid = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="0Nyvg_TCX6xgWDWlZ1DObW",
        elements=None,
    )
    print("\nfirst_column_by_guid:")
    pprint(first_column_by_guid)

    # Facet type: attribute
    first_column_by_name_attribute = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="Name = Column-159",
        elements=None,
    )
    print("\nfirst_column_by_name_attribute:")
    pprint(first_column_by_name_attribute)

    # Facet type: type  # S355 HE140A
    products_by_type = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query='type = "S355 HE140A"',
        elements=None,
    )
    print("\nproducts_by_type:")
    pprint(products_by_type)

    # Facet type: material  # S355
    products_by_mat = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="material = S355",
        elements=None,
    )
    print("\nproducts_by_mat:")
    pprint(products_by_mat)

    # Facet type: parent
    products_by_parent = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="parent = Building-01",
        elements=None,
    )
    print("\nproducts_by_parent:")
    pprint(products_by_parent)

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
