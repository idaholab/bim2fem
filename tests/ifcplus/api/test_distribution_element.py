# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.system
import bim2fem.ifcplus.util.geometry
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.distribution_element
import ifcopenshell.util.system
import bim2fem.ifcplus.api.material
import ifcopenshell.api.root
import ifcopenshell.api.spatial
import ifcopenshell.api.geometry
import bim2fem.ifcplus.api.geometry
import ifcopenshell.util.representation
import pytest
from tests.conftest import OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
import bim2fem.ifcplus.util.geometry
import numpy as np
from typing import cast


class TestAddEquipment:

    def test_add_one_make_up_air_unit(
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

        bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=mau,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (0.0, 0.0, 0.0)
        assert bbox_dict["max"] == (4.0, 1.5, 1.5)

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "one_make_up_air_unit.ifc"
        )
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

    def test_add_air_filtration_containment_housing(
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
            repositioned_origin=(12.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )

        bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=hepa,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (12.0, 0.0, 0.0)
        assert bbox_dict["max"] == (20.0, 1.0, 2.0)

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
            / "one_air_filtration_containment_housing.ifc"
        )
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

    def test_add_elbows(
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

        horizontal_curve_1 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
                point_on_center_of_curvature_side=(2.0, 1.0, 0.0),
                point_of_curvature=(1.0, 1.0, 0.0),
                point_of_tangency=(2.0, 2.0, 0.0),
                radius_of_curvature=1.0,
            )
        )

        material = bim2fem.ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

        bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            horizontal_curve=horizontal_curve_1,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #1",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        horizontal_curve_2 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(4.0, 1.0, 0.0),
                point_of_curvature=(3.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 2,
            )
        )

        bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            horizontal_curve=horizontal_curve_2,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #2",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        horizontal_curve_3 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_PI(
                point_of_curvature=(5.0, 1.0, 0.0),
                point_of_intersection=(5.0, 2.0, 0.0),
                point_of_tangency=(6.0, 2.0, 0.0),
            )
        )

        bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            horizontal_curve=horizontal_curve_3,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #3",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        horizontal_curve_4 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                first_point=(7.0, 1.0, 0.0),
                second_point=(7.0, 2.0, 0.0),
                third_point=(8.0, 2.0, 0.0),
                radius_of_curvature=1.0,
            )
        )

        bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            horizontal_curve=horizontal_curve_4,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #4",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        horizontal_curve_5 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(10.0, 1.0, 0.0),
                point_of_curvature=(9.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 3,
            )
        )

        bim2fem.ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            horizontal_curve=horizontal_curve_5,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #5",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "elbows.ifc")
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

    def test_add_pipe_segments(
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

        material = bim2fem.ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

        bim2fem.ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            start_point=(1.0, 1.0, 0.0),
            end_point=(1.0, 1.0 + 5.0, 0.0),
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Pipe #1",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        bim2fem.ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            start_point=(1.0, 1.0 + 8.0, 0.0),
            end_point=(1.0, 1.0 + 5.0 + 8.0, 0.0 + 5.0),
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Pipe #2",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
            add_shape_representation_to_ports=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "pipe_segments.ifc")
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

    def test_connect_make_up_air_unit_and_hepa_filter_with_dumb_piping(
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc_file_with_ventilation_distribution_system,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_piping_with_no_intelligence(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            source_port=mau_source_port,
            sink_port=hepa_sink_port,
            nominal_diameter=0.20,
            thickness=0.20 * 0.10,
            material=cast(ifcopenshell.entity_instance, steel_material),
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Branch #1",
            spatial_element=site,
            add_shape_representation_to_ports=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
            / "connected_mau_and_hepa_using_dumb_piping.ifc"
        )
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

    @pytest.mark.skip(reason="This feature is currently unavailable.")
    def test_connect_make_up_air_unit_and_hepa_filter_using_ant_colony(
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
            repositioned_origin=(4.0, 2.0 + 0.25, 0.0 + 0.25),
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
            repositioned_origin=(4.0 + 10.0, 2.0 + 5.0 + 0.5, 0.0 + 6.0),
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc_file_with_ventilation_distribution_system,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_piping_using_ant_colony(
            source_port=mau_source_port,
            sink_port=hepa_sink_port,
            obstacle=None,
            nominal_diameter=0.20,
            thickness=0.20 * 0.10,
            material=cast(ifcopenshell.entity_instance, steel_material),
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Branch #1",
            spatial_element=site,
            add_shape_representation_to_ports=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
            / "connected_mau_and_hepa_using_ant_colony.ifc"
        )
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

    @pytest.mark.skip(reason="This feature is currently unavailable.")
    def test_connect_make_up_air_unit_and_hepa_filter_using_ant_colony_with_obstacle(
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
            repositioned_origin=(4.0, 2.0 + 0.25, 0.0 + 0.25),
            repositioned_z_axis=(0.0, 0.0, 1.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            place_object_relative_to_parent=True,
        )

        obstacle = ifcopenshell.api.root.create_entity(
            file=ifc_file_with_ventilation_distribution_system,
            ifc_class="IfcBuildingElementProxy",
            name="Obstacle",
            predefined_type=None,
        )
        ifcopenshell.api.spatial.assign_container(
            file=ifc_file_with_ventilation_distribution_system,
            products=[obstacle],
            relating_structure=site,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=obstacle,
            place_object_relative_to_parent=True,
        )
        cylinder = bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            radius=1.0,
            extrusion_depth=7.0,
        )
        sphere = bim2fem.ifcplus.api.geometry.add_sphere(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            radius=1.0,
            repositioned_origin=(0.0, 0.0, 7.0),
        )
        boolean_results = ifcopenshell.api.geometry.add_boolean(
            file=ifc_file_with_ventilation_distribution_system,
            first_item=cylinder,
            second_items=[sphere],
            operator="UNION",
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=boolean_results[-1],
        )
        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        shape_model = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_ventilation_distribution_system,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(str, representation_type),
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_ventilation_distribution_system,
            product=obstacle,
            representation=shape_model,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=obstacle,
            repositioned_origin=(12.0, 3.0, 0.0),
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
            repositioned_origin=(4.0 + 10.0, 2.0 + 5.0 + 0.5, 0.0 + 6.0),
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc_file_with_ventilation_distribution_system,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.system.connect_two_distribution_ports_via_piping_using_ant_colony(
            source_port=mau_source_port,
            sink_port=hepa_sink_port,
            obstacle=obstacle,
            nominal_diameter=0.20,
            thickness=0.20 * 0.10,
            material=cast(ifcopenshell.entity_instance, steel_material),
            distribution_system=distribution_system,
            elbow_radius_type="SHORT",
            branch_name="Branch #1",
            spatial_element=site,
            add_shape_representation_to_ports=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
            / "connected_mau_and_hepa_using_ant_colony_with_obstacle.ifc"
        )
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
