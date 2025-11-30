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
import ifcopenshell.api.pset.add_pset
import pytest
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

    @pytest.mark.parametrize("thermal_power_capacity", [3500e6, 500e6])
    def test_create_reactor_pressure_vessel(
        self,
        thermal_power_capacity,
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

        scaling_factor = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_steam_generator(
                thermal_capacity=thermal_power_capacity
            )
        )

        rpv = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor,
            parent=site,
            reactor_coolant_system=rcs,
            place_object_relative_to_parent=True,
        )
        rpv.Name = "RPV-1"
        rpv.Description = "Reactor Pressure Vessel Unit 1"

        rpv_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=rpv,
            name="INL_ReactorPressureVesselCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=rpv_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity,  # Wth
            },
            pset_template=inl_pset_template,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / f"reactor_pressure_vessel_{int(thermal_power_capacity * 1e-6)}_MWth.ifc"
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

    @pytest.mark.parametrize("thermal_power_capacity", [3500e6, 500e6])
    def test_create_steam_generator(
        self,
        thermal_power_capacity,
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

        scs = ifcopenshell.api.system.add_system(file=ifc4_file)
        scs.Name = "SCS"
        scs.LongName = "Secondary Coolant System"
        scs.PredefinedType = "USERDEFINED"
        scs.ObjectType = "COOLING"

        scaling_factor = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_steam_generator(
                thermal_capacity=thermal_power_capacity
            )
        )

        sg = bim2fem.ifcplus.api.nuclear.create_steam_generator(
            ifc4_file=ifc4_file,
            scaling_factor_for_size=scaling_factor,
            parent=site,
            reactor_coolant_system=rcs,
            secondary_coolant_system=scs,
            place_object_relative_to_parent=True,
        )

        sg_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=sg,
            name="INL_SteamGeneratorCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=sg_pset,
            properties={
                "ThermalPowerCapacity": thermal_power_capacity,  # Wth
            },
            pset_template=inl_pset_template,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / f"steam_generator_{int(thermal_power_capacity * 1e-6)}_MWth.ifc"
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

    @pytest.mark.parametrize("flow_rate", [5.5, 0.79])
    def test_create_reactor_coolant_pump(
        self,
        flow_rate,
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

        scale_factor = (
            bim2fem.ifcplus.util.nuclear.get_scaling_factor_for_reactor_coolant_pump(
                flow_rate=flow_rate
            )
        )

        rcp = bim2fem.ifcplus.api.nuclear.create_reactor_coolant_pump(
            ifc4_file=ifc4_file,
            scale_factor=scale_factor,
            parent=site,
            reactor_coolant_system=rcs,
            place_object_relative_to_parent=True,
        )

        rcp_pset = ifcopenshell.api.pset.add_pset(
            file=ifc4_file,
            product=rcp,
            name="INL_ReactorCoolantPumpCommon",
        )
        ifcopenshell.api.pset.edit_pset(
            file=ifc4_file,
            pset=rcp_pset,
            properties={
                "FlowRate": flow_rate,  # m^3/s
            },
            pset_template=inl_pset_template,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / f"reactor_coolant_pump_{np.round(flow_rate, 2)}_cumecs.ifc"
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
