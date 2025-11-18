# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import ifcplus.api.project
import ifcplus.util.geometry
import ifcplus.api.placement
import ifcplus.api.distribution_element
import ifcplus.api.material
from tests.conftest import OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
import ifcplus.util.geometry
import numpy as np
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.system
from pprint import pprint


class TestCreatePipingElements:

    def test_create_elbows(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        material = ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc4_file,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

        horizontal_curve_1 = (
            ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
                point_on_center_of_curvature_side=(2.0, 1.0, 0.0),
                point_of_curvature=(1.0, 1.0, 0.0),
                point_of_tangency=(2.0, 2.0, 0.0),
                radius_of_curvature=1.0,
            )
        )

        ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve_1,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #1",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=True,
        )

        horizontal_curve_2 = (
            ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(4.0, 1.0, 0.0),
                point_of_curvature=(3.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 2,
            )
        )

        ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve_2,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #2",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=True,
        )

        horizontal_curve_3 = (
            ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_PI(
                point_of_curvature=(5.0, 1.0, 0.0),
                point_of_intersection=(5.0, 2.0, 0.0),
                point_of_tangency=(6.0, 2.0, 0.0),
            )
        )

        ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve_3,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #3",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=True,
        )

        horizontal_curve_4 = ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
            first_point=(7.0, 1.0, 0.0),
            second_point=(7.0, 2.0, 0.0),
            third_point=(8.0, 2.0, 0.0),
            radius_of_curvature=1.0,
        )

        ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve_4,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #4",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=True,
        )

        horizontal_curve_5 = (
            ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(10.0, 1.0, 0.0),
                point_of_curvature=(9.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 3,
            )
        )

        ifcplus.api.distribution_element.create_elbow(
            ifc4_file=ifc4_file,
            horizontal_curve=horizontal_curve_5,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Elbow #5",
            parent=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "elbows.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_pipe_segments(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        material = ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc4_file,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

        ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc4_file,
            start_point=(1.0, 1.0, 0.0),
            end_point=(1.0, 1.0 + 5.0, 0.0),
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Pipe #1",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        ifcplus.api.distribution_element.create_pipe_segment(
            ifc4_file=ifc4_file,
            start_point=(1.0, 1.0 + 8.0, 0.0),
            end_point=(1.0, 1.0 + 5.0 + 8.0, 0.0 + 5.0),
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            name="Pipe #2",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "pipe_segments.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestCreateEquipment:

    def test_create_make_up_air_unit(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        mau = ifcplus.api.distribution_element.create_make_up_air_unit(
            ifc4_file=ifc4_file,
            name="MAU",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        bbox = ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=mau,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (0.0, 0.0, 0.0)
        assert bbox_dict["max"] == (4.0, 1.5, 1.5)

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "make_up_air_unit.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_air_filtration_containment_housing(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        hepa = (
            ifcplus.api.distribution_element.create_air_filtration_containment_housing(
                ifc4_file=ifc4_file,
                name="HEPA",
                spatial_element=site,
                distribution_system=distribution_system,
                place_object_relative_to_parent=False,
            )
        )

        bbox = ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=hepa,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (0.0, 0.0, 0.0)
        assert bbox_dict["max"] == (8.0, 1.0, 2.0)

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT
            / "air_filtration_containment_housing.ifc"
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

    def test_create_motorized_valve(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        ifcplus.api.distribution_element.create_motorized_valve(
            ifc4_file=ifc4_file,
            name="V4",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "motorized_valve.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_generic_air_filter(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        ifcplus.api.distribution_element.create_generic_air_filter(
            ifc4_file=ifc4_file,
            name="F2",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        output_path = str(
            OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "generic_air_filter.ifc"
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

    def test_create_hprs_exhaust_fan(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        ifcplus.api.distribution_element.create_hprs_exhaust_fan(
            ifc4_file=ifc4_file,
            name="HPRS",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "hprs_exhaust_fan.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_stack(
        self,
    ):

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
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        distribution_system = ifcopenshell.api.system.add_system(file=ifc4_file)
        distribution_system.Name = "CVS"
        distribution_system.LongName = "Central Ventilation System"
        distribution_system.PredefinedType = "VENTILATION"

        ifcplus.api.distribution_element.create_stack(
            ifc4_file=ifc4_file,
            name="HPRS",
            spatial_element=site,
            distribution_system=distribution_system,
            place_object_relative_to_parent=False,
        )

        output_path = str(OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT / "stack.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
