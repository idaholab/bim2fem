# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell.util.system
import bim2fem.ifcplus.api.project
from tests.conftest import OUTPUT_DIR_FOR_NUCLEAR
import bim2fem.ifcplus.api.nuclear
import ifcopenshell.validate
import ifcopenshell.api.root
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.material
from typing import cast
import ifcopenshell
from pprint import pprint
import ifcopenshell.api.system
import pytest
import numpy as np
import ifcopenshell.util.element
import json
import ifcopenshell.api.system
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial
import bim2fem.ifcplus.api.system
import bim2fem.ifcplus.util.geometry


class TestCreateNuclearPowerPlant:

    def test_create_pressurized_reactor_containment_structure(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )
        concrete_material = cast(ifcopenshell.entity_instance, concrete_material)

        reactor_containment_building = bim2fem.ifcplus.api.nuclear.create_pressurized_reactor_containment_structure(
            ifc4_file=ifc4_file,
            radius=20.0,
            height=73.0,
            thickness=1.0,
            material=concrete_material,
            location=(1.0, 1.0, 0.0),
        )
        reactor_containment_building.Name = "Nuclear Reactor Containment Structure"
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[reactor_containment_building],
            relating_object=site,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR / "pressurized_reactor_containment_structure.ifc"
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

    def test_create_simplified_rectangular_hall(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )
        concrete_material = cast(
            ifcopenshell.entity_instance,
            concrete_material,
        )

        simplified_rectangular_hall = (
            bim2fem.ifcplus.api.nuclear.create_simplified_rectangular_hall_building(
                ifc4_file=ifc4_file,
                length=60.0,
                width=30.0,
                height=20.0,
                material=concrete_material,
                location=(1.0, 1.0, 0.0),
                z_axis=(0.0, 0.0, 1.0),
                x_axis=(1.0, 0.0, 0.0),
            )
        )
        simplified_rectangular_hall.Name = "Rectangular Hall"
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[simplified_rectangular_hall],
            relating_object=site,
        )

        output_path = str(OUTPUT_DIR_FOR_NUCLEAR / "simplified_rectangular_hall.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_pressurized_reactor_containment_structure_with_reactor_box(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )
        concrete_material = cast(ifcopenshell.entity_instance, concrete_material)

        reactor_containment_building = bim2fem.ifcplus.api.nuclear.create_pressurized_reactor_containment_structure(
            ifc4_file=ifc4_file,
            radius=20.0,
            height=73.0,
            thickness=1.0,
            material=concrete_material,
            location=(1.0, 1.0, 0.0),
        )
        reactor_containment_building.Name = "Nuclear Reactor Containment Structure"
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[reactor_containment_building],
            relating_object=site,
        )

        reactor_box = bim2fem.ifcplus.api.nuclear.create_reactor_box(
            ifc4_file=ifc4_file,
            length=20.0,
            width=20.0,
            height=15.0,
            location=(10.0, 10.0, 3.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[reactor_box],
            relating_structure=reactor_containment_building,
        )

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / "pressurized_reactor_containment_structure_with_reactor_box.ifc"
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

    @pytest.mark.parametrize(
        "thermal_power_capacity, num_loops", [(3500e6, 4), (500e6, 1)]
    )
    def test_create_reactor_pressure_vessel(
        self,
        thermal_power_capacity: float,
        num_loops: int,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        rcs = ifcopenshell.api.system.add_system(file=ifc4_file)
        rcs.Name = "RCS"
        rcs.LongName = "Reactor Coolant System"
        rcs.PredefinedType = "HEATING"

        rpv = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            thermal_power_capacity=thermal_power_capacity,
            reactor_coolant_system=rcs,
            num_loops=num_loops,
            location=(1.0, 1.0, 0.0),
        )
        rpv.Name = "RPV-1"
        rpv.Description = "Reactor Pressure Vessel Unit 1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[rpv],
            relating_structure=site,
        )

        if thermal_power_capacity == 3500e6 and num_loops == 4:
            bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
                product=rpv,
            )
            bbox_dict = bbox.to_dict()
            assert bbox_dict["min"] == (2.0, 2.0, 0.0)
            assert bbox_dict["max"] == (8.0, 8.0, 12.5)

        output_path = str(
            OUTPUT_DIR_FOR_NUCLEAR
            / f"reactor_pressure_vessel_{int(thermal_power_capacity * 1e-6)}_MWth_{num_loops}_loop.ifc"
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

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
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

        sg = bim2fem.ifcplus.api.nuclear.create_steam_generator(
            ifc4_file=ifc4_file,
            thermal_power_capacity=thermal_power_capacity,
            reactor_coolant_system=rcs,
            secondary_coolant_system=scs,
        )
        sg.Name = "SG-1A"
        sg.Description = "Steam Generator for Loop A of Unit 1"
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=sg,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[sg],
            relating_structure=site,
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

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        rcs = ifcopenshell.api.system.add_system(file=ifc4_file)
        rcs.Name = "RCS"
        rcs.LongName = "Reactor Coolant System"
        rcs.PredefinedType = "HEATING"

        rcp = bim2fem.ifcplus.api.nuclear.create_reactor_coolant_pump(
            ifc4_file=ifc4_file,
            flow_rate=flow_rate,
            reactor_coolant_system=rcs,
        )
        rcp.Name = "RCP-1A"
        rcp.Description = "Reactor Coolant Pump for Loop A of Unit 1"
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=rcp,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[rcp],
            relating_structure=site,
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

    def test_create_reactor_coolant_system_with_one_loop(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="ReferenceView_V1.2",
            precision=1e-4,
        )

        project = ifc4_file.by_type(
            type="IfcProject",
            include_subtypes=False,
        )[0]

        site = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcSite",
            name="Site-01",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
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

        reactor_containment_building = bim2fem.ifcplus.api.nuclear.create_pressurized_reactor_containment_structure(
            ifc4_file=ifc4_file,
            radius=20.0,
            height=73.0,
            thickness=1.0,
        )
        reactor_containment_building.Name = "Nuclear Reactor Containment Structure"
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=reactor_containment_building,
            repositioned_location=(10.0, 5.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[reactor_containment_building],
            relating_object=site,
        )

        rpv = bim2fem.ifcplus.api.nuclear.create_reactor_pressure_vessel(
            ifc4_file=ifc4_file,
            thermal_power_capacity=3500e6,
            reactor_coolant_system=rcs,
            num_loops=1,
            reactor_unit_num=1,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=rpv,
            repositioned_location=(17.5, 17.5, 5.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[rpv],
            relating_structure=reactor_containment_building,
        )

        sg = bim2fem.ifcplus.api.nuclear.create_steam_generator(
            ifc4_file=ifc4_file,
            thermal_power_capacity=3500e6,
            reactor_coolant_system=rcs,
            secondary_coolant_system=scs,
            reactor_unit_num=1,
            loop_label="A",
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=sg,
            repositioned_location=(
                20.0 - 4.8 + 10.0 - 2.5 - 0.01 - 4.0,
                20.0 - 4.1 + 10.0 + 0.035 + 3.0,
                12.0 + 2.0,
            ),
            repositioned_x_axis=(0.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[sg],
            relating_structure=reactor_containment_building,
        )

        rcp = bim2fem.ifcplus.api.nuclear.create_reactor_coolant_pump(
            ifc4_file=ifc4_file,
            flow_rate=5.5,
            reactor_coolant_system=rcs,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=rcp,
            repositioned_location=(
                17.0 + 10.0 + 3.0,
                17.0 + 10.0 - 6.0 + 0.05 + 4.0,
                12.0,
            ),
            repositioned_x_axis=(-1.0, 0.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[rcp],
            relating_structure=reactor_containment_building,
        )

        rpv_hot_leg_outlet = ifcopenshell.util.system.get_ports(
            element=rpv,
            flow_direction="SOURCE",
        )[0]
        rpv_cold_leg_inlet = ifcopenshell.util.system.get_ports(
            element=rpv,
            flow_direction="SINK",
        )[0]

        sg_inlet_ports = ifcopenshell.util.system.get_ports(
            element=sg,
            flow_direction="SINK",
        )
        sg_pc_inlet = [port for port in sg_inlet_ports if port.SystemType == "HEATING"][
            0
        ]
        sg_feedwater_inlet = [
            port for port in sg_inlet_ports if port.SystemType != "HEATING"
        ][0]
        sg_outlet_ports = ifcopenshell.util.system.get_ports(
            element=sg,
            flow_direction="SOURCE",
        )
        sg_pc_outlet = [
            port for port in sg_outlet_ports if port.SystemType == "HEATING"
        ][0]
        sg_main_steam_outlet = [
            port for port in sg_outlet_ports if port.SystemType != "HEATING"
        ][0]

        rcp_inlet = ifcopenshell.util.system.get_ports(
            element=rcp,
            flow_direction="SINK",
        )[0]
        rcp_outlet = ifcopenshell.util.system.get_ports(
            element=rcp,
            flow_direction="SOURCE",
        )[0]

        source_ports = [
            rpv_hot_leg_outlet,
            sg_pc_outlet,
            rcp_outlet,
        ]
        sink_ports = [
            sg_pc_inlet,
            rcp_inlet,
            rpv_cold_leg_inlet,
        ]
        for source_port, sink_port in zip(source_ports, sink_ports):
            ifcopenshell.api.system.connect_port(
                file=ifc4_file,
                port1=source_port,
                port2=sink_port,
                direction="SOURCE",
            )
            rel = sink_port.ConnectedFrom[0]
            rel.Name = f"{source_port.Name} to {sink_port.Name}"
            rel.Description = (
                f"{source_port.Description} connected to {sink_port.Description}"
            )

        # input_for_auto_pipe_router = {
        #     "building_elements": [],
        #     "distribution_elements": [],
        #     "distribution_ports": [],
        #     "spatial_structure_elements": [],
        #     "port_connections": [],
        # }

        # for product in ifc4_file.by_type(type="IfcProduct", include_subtypes=True):

        #     data_of_product = {
        #         "class": product.is_a(),
        #         "guid": product.GlobalId,
        #         "predefined_type": ifcopenshell.util.element.get_predefined_type(
        #             element=product
        #         ),
        #         "name": product.Name,
        #         "description": product.Description,
        #     }

        #     if product.Representation:
        #         bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
        #             product=product,
        #         )
        #         bbox_dict = bbox.to_dict()
        #         data_of_product["min_corner"] = bbox_dict["min"]
        #         data_of_product["max_corner"] = bbox_dict["max"]
        #     else:
        #         data_of_product["min_corner"] = None
        #         data_of_product["max_corner"] = None
        #     # data_of_product["min_corner"] = None
        #     # data_of_product["max_corner"] = None

        #     if product.is_a("IfcSpatialStructureElement"):
        #         input_for_auto_pipe_router["spatial_structure_elements"].append(
        #             data_of_product
        #         )

        #     elif product.is_a("IfcBuildingElement"):
        #         input_for_auto_pipe_router["building_elements"].append(data_of_product)

        #     elif product.is_a("IfcDistributionPort"):
        #         data_of_product["port_flow_direction"] = product.FlowDirection
        #         port_location = (
        #             bim2fem.ifcplus.util.geometry.get_location_in_global_coordinates(
        #                 product=product,
        #             )
        #         )
        #         data_of_product["port_location"] = port_location
        #         port_flow_direction_vector = (
        #             bim2fem.ifcplus.util.geometry.get_z_axis_in_global_coordinates(
        #                 product=product,
        #             )
        #         )
        #         data_of_product["port_flow_direction_vector"] = (
        #             port_flow_direction_vector
        #         )
        #         port_element = ifcopenshell.util.system.get_port_element(port=product)
        #         data_of_product["port_element"] = port_element.GlobalId
        #         input_for_auto_pipe_router["distribution_ports"].append(data_of_product)

        #     elif product.is_a("IfcDistributionElement"):
        #         ports = ifcopenshell.util.system.get_ports(element=product)
        #         data_of_product["ports"] = [port.GlobalId for port in ports]
        #         input_for_auto_pipe_router["distribution_elements"].append(
        #             data_of_product
        #         )

        # for rel in ifc4_file.by_type(
        #     type="IfcRelConnectsPorts",
        #     include_subtypes=False,
        # ):
        #     data_of_rel = {
        #         "class": rel.is_a(),
        #         "guid": rel.GlobalId,
        #         "name": rel.Name,
        #         "description": rel.Description,
        #         "source_port": rel.RelatingPort.GlobalId,
        #         "sink_port": rel.RelatedPort.GlobalId,
        #     }
        #     input_for_auto_pipe_router["port_connections"].append(data_of_rel)

        rels = ifc4_file.by_type(
            type="IfcRelConnectsPorts",
            include_subtypes=False,
        )
        for n, rel in enumerate(rels):
            if n == 0:
                outer_diameter = 0.74
            elif n == 1:
                outer_diameter = 0.55
            else:
                outer_diameter = 0.55
            thickness = 0.10 * outer_diameter
            source_port = rel.RelatingPort
            sink_port = rel.RelatedPort
            piping_elements = bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=source_port,
                sink_port=sink_port,
                outer_diameter=outer_diameter,
                thickness=thickness,
                material=None,
                distribution_system=rcs,
                elbow_radius_type="SHORT",
                branch_name=f"Pipe Run from {source_port.Name} to {sink_port.Name}",
            )
            bim2fem.ifcplus.api.spatial.assign_container_v2(
                products=piping_elements,
                relating_structure=site,
                place_relative_to_parent=False,
            )
            # for piping_element in piping_elements:
            #     piping_element.ObjectPlacement.PlacementRelTo = None

        output_path = str(OUTPUT_DIR_FOR_NUCLEAR / "rcs_one_loop.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

        # output_path_for_json = str(
        #     OUTPUT_DIR_FOR_NUCLEAR / "rcs_one_loop_auto_pipe_router_input.json"
        # )
        # with open(output_path_for_json, "w") as f:
        #     json.dump(
        #         obj=input_for_auto_pipe_router,
        #         fp=f,
        #         indent=4,
        #         sort_keys=False,
        #     )
