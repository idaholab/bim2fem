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


class TestCreatePipingSystem:

    def test_create_pipe_run_from_polyline(
        self,
        ifc_file_with_ventilation_distribution_system: ifcopenshell.file,
    ):

        distribution_system = ifc_file_with_ventilation_distribution_system.by_type(
            type="IfcDistributionSystem",
            include_subtypes=False,
        )[0]

        site = ifc_file_with_ventilation_distribution_system.by_type(
            type="IfcSite",
            include_subtypes=False,
        )[0]

        galvanized_steel = (
            bim2fem.ifcplus.api.material.add_material_with_structural_properties(
                ifc4_file=ifc_file_with_ventilation_distribution_system,
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
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            polyline=pipe_run_polyline,
            nominal_diameter=0.5,
            thickness=0.05,
            material=galvanized_steel,
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Pipe Run #1",
            spatial_element=site,
            place_objects_relative_to_parent=True,
            add_shape_representation_to_ports=False,
        )

        output_path = str(OUTPUT_DIR_FOR_SYSTEM / "pipe_run.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestConnectEquipment:

    def test_connect_make_up_air_unit_and_hepa_filter_with_pipe_run(
        self,
        ifc_file_with_ventilation_distribution_system: ifcopenshell.file,
    ):

        distribution_system = ifc_file_with_ventilation_distribution_system.by_type(
            type="IfcDistributionSystem",
            include_subtypes=False,
        )[0]

        site = ifc_file_with_ventilation_distribution_system.by_type(
            type="IfcSite",
            include_subtypes=False,
        )[0]

        mau = bim2fem.ifcplus.api.distribution_element.create_make_up_air_unit(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            name="MAU",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=mau,
            repositioned_origin=(4.0, 2.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )

        hepa = bim2fem.ifcplus.api.distribution_element.create_air_filtration_containment_housing(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            name="HEPA",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
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
                ifc4_file=ifc_file_with_ventilation_distribution_system,
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
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            source_port=mau_source_port,
            sink_port=hepa_sink_port,
            nominal_diameter=0.20,
            thickness=0.20 * 0.10,
            material=galvanized_steel,
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Pipe Run #1",
            spatial_element=site,
            add_shape_representation_to_ports=False,
        )

        output_path = str(OUTPUT_DIR_FOR_SYSTEM / "mau_connected_to_hepa.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0
