# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import bim2fem.ifcplus.api.project
from tests.conftest import OUTPUT_DIR_FOR_NUCLEAR
import bim2fem.ifcplus.api.nuclear
import bim2fem.ifcplus.util.nuclear
import ifcopenshell.validate
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.material
from typing import cast
import ifcopenshell
from pprint import pprint
import ifcopenshell.api.system
import bim2fem.ifcplus.util.geometry
import numpy as np


class TestCreateNuclearPowerPlantEquipment:

    def test_create_nuclear_reactor_containment_structure(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=building,
            place_object_relative_to_parent=True,
        )

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.nuclear.create_nuclear_reactor_containment_structure(
            ifc4_file=ifc4_file,
            material=cast(ifcopenshell.entity_instance, concrete_material),
            name="Nuclear Reactor Containment Structure",
            parent=building,
            place_object_relative_to_parent=True,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR / "nuclear_reactor_containment_structure.ifc"
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
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

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=building,
            place_object_relative_to_parent=True,
        )

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.nuclear.create_nuclear_reactor_containment_structure(
            ifc4_file=ifc4_file,
            material=cast(ifcopenshell.entity_instance, concrete_material),
            name="Nuclear Reactor Containment Structure",
            parent=building,
            place_object_relative_to_parent=True,
        )

        reactor_box_length = 15.0
        reactor_box_width = 19.0
        reactor_box_height = 14.0

        reactor_box = bim2fem.ifcplus.api.nuclear.create_reactor_box(
            ifc4_file=ifc4_file,
            length=reactor_box_length,
            width=reactor_box_width,
            height=reactor_box_height,
            name="Reactor Box",
            parent=building,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.placement.edit_object_placement(
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
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_reactor_pressure_vessel(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
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
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=site,
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        primary_coolant_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        primary_coolant_system.Name = "PCS"
        primary_coolant_system.LongName = "Primary Coolant System"
        primary_coolant_system.PredefinedType = "HEATING"

        rpv_1 = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=1.0,
            name="Reactor Pressure Vessel #1",
            parent=site,
            reactor_coolant_system=primary_coolant_system,
            place_object_relative_to_parent=True,
        )
        bbox_for_rpv_1 = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=rpv_1,
        )
        x_dim_for_rpv_1, y_dim_for_rpv_1, z_dim_for_rpv_1 = bbox_for_rpv_1.dimensions
        assert np.round(x_dim_for_rpv_1, 1) == 6.0
        assert np.round(y_dim_for_rpv_1, 1) == 5.0
        assert np.round(z_dim_for_rpv_1, 1) == 12.5

        scaling_factor_based_on_reduced_thermal_capacity = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_reactor_pressure_vessel(
                thermal_capacity=500e6,  # Wth
            )
        )
        rpv_2 = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor_based_on_reduced_thermal_capacity,
            name="Reactor Pressure Vessel #2",
            parent=site,
            reactor_coolant_system=primary_coolant_system,
            place_object_relative_to_parent=True,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=rpv_2,
            repositioned_origin=(15.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )
        bbox_for_rpv_2 = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=rpv_2,
        )
        x_dim_for_rpv_2, y_dim_for_rpv_2, z_dim_for_rpv_2 = bbox_for_rpv_2.dimensions
        assert np.round(x_dim_for_rpv_2, 1) == 3.6
        assert np.round(y_dim_for_rpv_2, 1) == 2.6
        assert np.round(z_dim_for_rpv_2, 1) == 6.5

        output_path = str(OUTPUT_DIR_FOR_NUCLEAR / "reactor_pressure_vessels.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
