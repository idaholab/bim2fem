# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.system
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.distribution_element
import ifcopenshell.util.system
import bim2fem.ifcplus.api.material
from tests.conftest import OUTPUT_DIR_FOR_SYSTEM
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.system
from pprint import pprint


class TestCreatePipingSystem:

    def test_create_pipe_run_from_polyline(
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

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

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

        bim2fem.ifcplus.api.system.create_pipe_run_from_polyline(
            ifc4_file=ifc4_file,
            polyline=pipe_run_polyline,
            nominal_diameter=0.5,
            thickness=0.05,
            material=galvanized_steel,
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Pipe Run #1",
            spatial_element=site,
            place_objects_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_SYSTEM / "pipe_run.ifc")
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

    def test_connect_make_up_air_unit_to_hepa_containment(
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

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        mau = bim2fem.ifcplus.api.distribution_element.create_make_up_air_unit(
            ifc4_file=ifc4_file,
            name="MAU",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=mau,
            repositioned_origin=(4.0, 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )

        hepa = bim2fem.ifcplus.api.distribution_element.create_hepa_containment_housing(
            ifc4_file=ifc4_file,
            name="HEPA",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=hepa,
            repositioned_origin=(4.0 + 10.0, 2.0 + 5.0, 0.0 + 6.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
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

        bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_pipe_run(
            ifc4_file=ifc4_file,
            source_port=mau_source_port,
            sink_port=hepa_sink_port,
            nominal_diameter=0.20,
            thickness=0.20 * 0.10,
            material=galvanized_steel,
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Pipe Run #1",
            spatial_element=site,
        )

        output_path = str(OUTPUT_DIR_FOR_SYSTEM / "mau_connected_to_hepa.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
