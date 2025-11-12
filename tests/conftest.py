# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import pytest
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial
import ifcopenshell.api.system
import ifcplus.api.project
import ifcplus.api.placement
from pathlib import Path

TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"
INPUT_DIR = FIXTURES_DIR / "input"
EXPECTED_DIR = FIXTURES_DIR / "expected"

OUTPUT_DIR = TEST_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_GEOMETRY = OUTPUT_DIR / "geometry"
OUTPUT_DIR_FOR_GEOMETRY.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT = OUTPUT_DIR / "distribution_element"
OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_SYSTEM = OUTPUT_DIR / "system"
OUTPUT_DIR_FOR_SYSTEM.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_NUCLEAR = OUTPUT_DIR / "nuclear"
OUTPUT_DIR_FOR_NUCLEAR.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_BUILT_ELEMENT = OUTPUT_DIR / "built_element"
OUTPUT_DIR_FOR_BUILT_ELEMENT.mkdir(exist_ok=True)


@pytest.fixture
def empty_ifc_file() -> ifcopenshell.file:
    """Create a minimal valid IFC file"""

    ifc4_file = ifcplus.api.project.create_ifc4_file(
        model_view_definition="ReferenceView_V1.2",
        precision=1e-4,
    )

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    site = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSite",
        name="Site-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[site],
        relating_object=project,
    )
    ifcplus.api.placement.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    return ifc4_file


@pytest.fixture
def ifc_file_with_one_element() -> ifcopenshell.file:
    """Create a minimal valid IFC file with one element"""

    ifc4_file = ifcplus.api.project.create_ifc4_file(
        model_view_definition="ReferenceView_V1.2",
        precision=1e-4,
    )

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    site = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSite",
        name="Site-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[site],
        relating_object=project,
    )
    ifcplus.api.placement.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuildingElementProxy",
        name="Element-01",
        predefined_type=None,
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[element],
        relating_structure=site,
    )
    ifcplus.api.placement.edit_object_placement(
        product=element,
        place_object_relative_to_parent=True,
    )

    return ifc4_file


@pytest.fixture
def ifc_file_with_ventilation_distribution_system() -> ifcopenshell.file:
    """Create a minimal valid IFC file with a ventilation IfcDisbributionSystem"""

    ifc4_file = ifcplus.api.project.create_ifc4_file(
        model_view_definition="ReferenceView_V1.2",
        precision=1e-4,
    )

    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    site = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcSite",
        name="Site-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[site],
        relating_object=project,
    )
    ifcplus.api.placement.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
    distribution_system.Name = "CVS"
    distribution_system.LongName = "Central Ventilation System"
    distribution_system.PredefinedType = "VENTILATION"

    return ifc4_file
