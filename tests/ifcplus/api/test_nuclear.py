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
import ifcopenshell.api.pset.add_pset


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

        inl_pset_template = (
            bim2fem.ifcplus.api.nuclear.create_INL_nuclear_property_set_templte(
                ifc4_file=ifc4_file,
            )
        )

        rcs_1 = ifcopenshell.api.system.add_system(file=ifc4_file)
        rcs_1.Name = "RCS #1"
        rcs_1.LongName = "Reactor Coolant System #1"
        rcs_1.PredefinedType = "HEATING"

        thermal_power_capacity_of_rpv_1 = 3500e6
        scaling_factor_for_rpv_1 = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_steam_generator(
                thermal_capacity=thermal_power_capacity_of_rpv_1  # Wth
            )
        )
        rpv_1 = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor_for_rpv_1,
            name="Reactor Pressure Vessel #1",
            parent=site,
            reactor_coolant_system=rcs_1,
            place_object_relative_to_parent=True,
        )

        bbox_for_rpv_1 = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=rpv_1,
        )
        x_dim_for_rpv_1, y_dim_for_rpv_1, z_dim_for_rpv_1 = bbox_for_rpv_1.dimensions
        assert np.round(x_dim_for_rpv_1, 1) == 6.0
        assert np.round(y_dim_for_rpv_1, 1) == 5.0
        assert np.round(z_dim_for_rpv_1, 1) == 12.5

        rpv_1_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=rpv_1,
            name="INL_ReactorPressureVesselCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=rpv_1_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity_of_rpv_1,  # Wth
            },
            pset_template=inl_pset_template,
        )

        rcs_2 = ifcopenshell.api.system.add_system(file=ifc4_file)
        rcs_2.Name = "RCS #2"
        rcs_2.LongName = "Reactor Coolant System #2"
        rcs_2.PredefinedType = "HEATING"

        thermal_power_capacity_of_rpv_2 = 500e6
        scaling_factor_for_rpv_2 = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_reactor_pressure_vessel(
                thermal_capacity=thermal_power_capacity_of_rpv_2,  # Wth
            )
        )
        rpv_2 = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor_for_rpv_2,
            name="Reactor Pressure Vessel #2",
            parent=site,
            reactor_coolant_system=rcs_2,
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

        rpv_2_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=rpv_2,
            name="INL_ReactorPressureVesselCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=rpv_2_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity_of_rpv_2,  # Wth
            },
            pset_template=inl_pset_template,
        )

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

    def test_create_steam_generator(
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

        inl_pset_template = (
            bim2fem.ifcplus.api.nuclear.create_INL_nuclear_property_set_templte(
                ifc4_file=ifc4_file,
            )
        )

        rcs = ifcopenshell.api.system.add_system(file=ifc4_file)
        rcs.Name = "RCS"
        rcs.LongName = "Reactor Coolant System"
        rcs.PredefinedType = "HEATING"

        scs_1 = ifcopenshell.api.system.add_system(file=ifc4_file)
        scs_1.Name = "SCS #1"
        scs_1.LongName = "Secondary Coolant System #1"
        scs_1.PredefinedType = "USERDEFINED"
        scs_1.ObjectType = "COOLING"

        thermal_power_capacity_of_sg_1 = 3500e6
        scaling_factor_for_sg_1 = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_steam_generator(
                thermal_capacity=thermal_power_capacity_of_sg_1  # Wth
            )
        )
        sg_1 = bim2fem.ifcplus.api.nuclear.create_steam_generator(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor_for_sg_1,
            name="Steam Generator #1",
            parent=site,
            reactor_coolant_system=rcs,
            secondary_coolant_system=scs_1,
            place_object_relative_to_parent=True,
        )
        bbox_for_sg_1 = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=sg_1,
        )
        x_dim_for_sg_1, y_dim_for_sg_1, z_dim_for_sg_1 = bbox_for_sg_1.dimensions
        assert np.round(x_dim_for_sg_1, 1) == 3.8
        assert np.round(y_dim_for_sg_1, 1) == 3.5
        assert np.round(z_dim_for_sg_1, 1) == 21.5

        sg_1_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=sg_1,
            name="INL_SteamGeneratorCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=sg_1_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity_of_sg_1,  # Wth
            },
            pset_template=inl_pset_template,
        )

        scs_2 = ifcopenshell.api.system.add_system(file=ifc4_file)
        scs_2.Name = "SCS #2"
        scs_2.LongName = "Secondary Coolant System #2"
        scs_2.PredefinedType = "USERDEFINED"
        scs_2.ObjectType = "COOLING"

        thermal_power_capacity_of_sg_2 = 500e6
        scaling_factor_for_sg_2 = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_steam_generator(
                thermal_capacity=thermal_power_capacity_of_sg_2,  # Wth
            )
        )
        sg_2 = bim2fem.ifcplus.api.nuclear.create_steam_generator(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor_for_sg_2,
            name="Steam Generator #2",
            parent=site,
            reactor_coolant_system=rcs,
            secondary_coolant_system=scs_2,
            place_object_relative_to_parent=True,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=sg_2,
            repositioned_origin=(15.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )
        bbox_for_sg_2 = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=sg_2,
        )
        x_dim_for_sg_2, y_dim_for_sg_2, z_dim_for_sg_2 = bbox_for_sg_2.dimensions
        assert np.round(x_dim_for_sg_2, 1) == 2.2
        assert np.round(y_dim_for_sg_2, 1) == 1.8
        assert np.round(z_dim_for_sg_2, 1) == 11.5

        sg_2_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=sg_2,
            name="INL_SteamGeneratorCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=sg_2_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity_of_sg_2,  # Wth
            },
            pset_template=inl_pset_template,
        )

        output_path = str(OUTPUT_DIR_FOR_NUCLEAR / "steam_generators.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
