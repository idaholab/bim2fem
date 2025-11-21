# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcplus.api.project
from tests.conftest import OUTPUT_DIR_FOR_NUCLEAR
import ifcplus.api.nuclear
import ifcopenshell.validate
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcplus.api.placement
import ifcplus.api.material
from typing import cast
import ifcopenshell
from pprint import pprint


class TestCreateNuclearPowerPlant:

    def test_create_nuclear_reactor_containment_structure(
        self,
    ):

        ifc4_file = ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

        building = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuilding",
            name="Reactor Building",
        )
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=[building],
            relating_object=project,
        )
        ifcplus.api.placement.edit_object_placement(
            product=building,
            place_object_relative_to_parent=True,
        )

        concrete_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )

        ifcplus.api.nuclear.create_nuclear_reactor_containment_structure(
            ifc4_file=ifc4_file,
            material=cast(ifcopenshell.entity_instance, concrete_material),
            name="Nuclear Reactor Containment Structure",
            parent=building,
            place_object_relative_to_parent=True,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR / "nuclear_reactor_containment_structure.ifc"
        )
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_reactor_containment_structure_with_reactor_box(
        self,
    ):

        ifc4_file = ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

        building = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuilding",
            name="Reactor Building",
        )
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=[building],
            relating_object=project,
        )
        ifcplus.api.placement.edit_object_placement(
            product=building,
            place_object_relative_to_parent=True,
        )

        concrete_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )

        ifcplus.api.nuclear.create_nuclear_reactor_containment_structure(
            ifc4_file=ifc4_file,
            material=cast(ifcopenshell.entity_instance, concrete_material),
            name="Nuclear Reactor Containment Structure",
            parent=building,
            place_object_relative_to_parent=True,
        )

        reactor_box_length = 15.0
        reactor_box_width = 19.0
        reactor_box_height = 14.0

        reactor_box = ifcplus.api.nuclear.create_reactor_box(
            ifc4_file=ifc4_file,
            length=reactor_box_length,
            width=reactor_box_width,
            height=reactor_box_height,
            name="Reactor Box",
            parent=building,
            place_object_relative_to_parent=True,
        )

        ifcplus.api.placement.edit_object_placement(
            product=reactor_box,
            repositioned_origin=(
                -reactor_box_length / 2.0,
                -reactor_box_width / 2.0,
                0.0,
            ),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / "reactor_containment_structure_with_reactor_box.ifc"
        )
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
