# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.system
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.hvac
import ifcopenshell.util.system
import bim2fem.ifcplus.api.material
from tests.conftest import OUTPUT_DIR_FOR_SYSTEM
import ifcopenshell.api.root
import ifcopenshell.api.system
from pprint import pprint
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial
import numpy as np


class TestCreatePipingSystem:

    def test_create_pipe_run_from_polyline(
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

        cvs = ifcopenshell.api.system.add_system(file=ifc4_file)
        cvs.Name = "CVS"
        cvs.LongName = "Central Ventilation System"
        cvs.PredefinedType = "VENTILATION"

        galvanized_steel = (
            bim2fem.ifcplus.api.material.add_material_with_structural_properties(
                ifc4_file=ifc4_file,
                name="Galvanized Steel",
                category="steel",
                mass_density=7850.0,
                young_modulus=200.0e9,
                poisson_ratio=0.3,
                thermal_expansion_coefficient=1.2e-6,
                check_for_duplicate=True,
            )
        )

        pipe_run_polyline = [
            (0.0, 0.0, 0.0),
            (10.0, 0.0, 0.0),
            (10.0, 10.0, 0.0),
            (15.0, 15.0, 5.0),
            (20.0, 15.0, 5.0),
            (20.0, 15.0, 10.0),
        ]

        piping_elements = bim2fem.ifcplus.api.system.create_pipe_run_from_polyline(
            polyline=pipe_run_polyline,
            outer_diameter=0.5,
            thickness=0.05,
            material=galvanized_steel,
            distribution_system=cvs,
            elbow_radius_type="SHORT",
            branch_name="Pipe Run #1",
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_SYSTEM / "pipe_run_from_polyline.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestConnectEquipment:

    def test_connect_mau_to_hepa_via_dumb_pipng(
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

        cvs = ifcopenshell.api.system.add_system(file=ifc4_file)
        cvs.Name = "CVS"
        cvs.LongName = "Central Ventilation System"
        cvs.PredefinedType = "VENTILATION"

        mau = bim2fem.ifcplus.api.hvac.create_make_up_air_unit(
            distribution_system=cvs,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=mau,
            repositioned_location=(4.0, 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[mau],
            relating_structure=site,
        )

        hepa = bim2fem.ifcplus.api.hvac.create_hepa_containment_housing(
            distribution_system=cvs,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=hepa,
            repositioned_location=(4.0 + 10.0, 2.0 + 5.0, 0.0 + 6.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[hepa],
            relating_structure=site,
        )

        mau_source_port = ifcopenshell.util.system.get_ports(
            element=mau,
            flow_direction="SOURCE",
        )[0]

        hepa_sink_port = ifcopenshell.util.system.get_ports(
            element=hepa,
            flow_direction="SINK",
        )[0]

        galvanized_steel = (
            bim2fem.ifcplus.api.material.add_material_with_structural_properties(
                ifc4_file=ifc4_file,
                name="Galvanized Steel",
                category="steel",
                mass_density=7850.0,
                young_modulus=200.0e9,
                poisson_ratio=0.3,
                thermal_expansion_coefficient=1.2e-6,
                check_for_duplicate=True,
            )
        )

        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=mau_source_port,
                sink_port=hepa_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=galvanized_steel,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #1",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_SYSTEM / "mau_connected_to_hepa_via_dumb_piping.ifc"
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

    def test_connect_all_hvac_equipment_via_dumb_piping(
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

        cvs = ifcopenshell.api.system.add_system(file=ifc4_file)
        cvs.Name = "CVS"
        cvs.LongName = "Central Ventilation System"
        cvs.PredefinedType = "VENTILATION"

        shift_vector = np.array([5.0, 5.0, 5.0])

        mau = bim2fem.ifcplus.api.hvac.create_make_up_air_unit(
            distribution_system=cvs, location=(0.0, 0.0, 0.0)
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[mau],
            relating_structure=site,
        )

        hepa = bim2fem.ifcplus.api.hvac.create_hepa_containment_housing(
            distribution_system=cvs,
            location=tuple((shift_vector * 1.0).tolist()),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[hepa],
            relating_structure=site,
        )

        mau_source_port = ifcopenshell.util.system.get_ports(
            element=mau,
            flow_direction="SOURCE",
        )[0]
        hepa_sink_port = ifcopenshell.util.system.get_ports(
            element=hepa,
            flow_direction="SINK",
        )[0]
        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=mau_source_port,
                sink_port=hepa_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=None,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #1",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        v4 = bim2fem.ifcplus.api.hvac.create_motorized_valve(
            distribution_system=cvs,
            location=tuple((shift_vector * 2.0).tolist()),
            x_axis=(0.0, -1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[v4],
            relating_structure=site,
        )

        hepa_source_port = ifcopenshell.util.system.get_ports(
            element=hepa,
            flow_direction="SOURCE",
        )[0]
        v4_sink_port = ifcopenshell.util.system.get_ports(
            element=v4,
            flow_direction="SINK",
        )[0]
        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=hepa_source_port,
                sink_port=v4_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=None,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #2",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        filter = bim2fem.ifcplus.api.hvac.create_generic_air_filter(
            distribution_system=cvs,
            location=tuple((shift_vector * 3.0).tolist()),
            x_axis=(0.0, -1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[filter],
            relating_structure=site,
        )

        v4_source_port = ifcopenshell.util.system.get_ports(
            element=v4,
            flow_direction="SOURCE",
        )[0]
        filter_sink_port = ifcopenshell.util.system.get_ports(
            element=filter,
            flow_direction="SINK",
        )[0]
        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=v4_source_port,
                sink_port=filter_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=None,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #3",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        hprs = bim2fem.ifcplus.api.hvac.create_hprs_exhaust_fan(
            distribution_system=cvs,
            location=tuple((shift_vector * 4.0).tolist()),
            x_axis=(0.0, -1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[hprs],
            relating_structure=site,
        )

        filter_source_port = ifcopenshell.util.system.get_ports(
            element=filter,
            flow_direction="SOURCE",
        )[0]
        hprs_sink_port = ifcopenshell.util.system.get_ports(
            element=hprs,
            flow_direction="SINK",
        )[0]
        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=filter_source_port,
                sink_port=hprs_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=None,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #4",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        stack = bim2fem.ifcplus.api.hvac.create_exhaust_stack(
            distribution_system=cvs,
            location=tuple((shift_vector * 5.0).tolist()),
            x_axis=(-1.0, 0.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[stack],
            relating_structure=site,
        )

        hprs_source_port = ifcopenshell.util.system.get_ports(
            element=hprs,
            flow_direction="SOURCE",
        )[0]
        stack_sink_port = ifcopenshell.util.system.get_ports(
            element=stack,
            flow_direction="SINK",
        )[0]
        piping_elements = (
            bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_dumb_piping(
                source_port=hprs_source_port,
                sink_port=stack_sink_port,
                outer_diameter=0.20,
                thickness=0.20 * 0.10,
                material=None,
                distribution_system=cvs,
                elbow_radius_type="SHORT",
                branch_name="Pipe Run #5",
            )
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=piping_elements,
            relating_structure=site,
            place_relative_to_parent=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_SYSTEM / "all_hvac_equipment_connected_via_dumb_piping.ifc"
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
