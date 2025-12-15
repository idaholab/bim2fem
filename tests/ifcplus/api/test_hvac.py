# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.util.geometry
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.hvac
from tests.conftest import OUTPUT_DIR_FOR_HVAC
import bim2fem.ifcplus.util.geometry
import ifcopenshell.api.root
import ifcopenshell.api.system
from pprint import pprint
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial


class TestCreateHVACEquipment:

    def test_create_make_up_air_unit(
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
        mau.Name = "MAU"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[mau],
            relating_structure=site,
        )

        bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=mau,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (1.0, 1.0, 0.0)
        assert bbox_dict["max"] == (5.0, 2.5, 1.5)

        output_path = str(OUTPUT_DIR_FOR_HVAC / "make_up_air_unit.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_hepa_containment_housing(
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

        hepa = bim2fem.ifcplus.api.hvac.create_hepa_containment_housing(
            distribution_system=cvs,
        )
        hepa.Name = "HEPA"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[hepa],
            relating_structure=site,
        )

        bbox = bim2fem.ifcplus.util.geometry.BoundingBox.from_ifc_product(
            product=hepa,
        )
        bbox_dict = bbox.to_dict()
        assert bbox_dict["min"] == (1.0, 1.0, 0.0)
        assert bbox_dict["max"] == (9.0, 2.0, 2.0)

        output_path = str(OUTPUT_DIR_FOR_HVAC / "hepa_containment_housing.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
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

        valve_4 = bim2fem.ifcplus.api.hvac.create_motorized_valve(
            distribution_system=cvs,
        )
        valve_4.Name = "V4"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[valve_4],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_HVAC / "motorized_valve.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
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

        filter_2 = bim2fem.ifcplus.api.hvac.create_generic_air_filter(
            distribution_system=cvs,
        )
        filter_2.Name = "F2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[filter_2],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_HVAC / "generic_air_filter.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
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

        hprs = bim2fem.ifcplus.api.hvac.create_hprs_exhaust_fan(
            distribution_system=cvs,
        )
        hprs.Name = "HPRS"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[hprs],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_HVAC / "hprs_exhaust_fan.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_exhaust_stack(
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

        stack = bim2fem.ifcplus.api.hvac.create_exhaust_stack(
            distribution_system=cvs,
        )
        stack.Name = "STACK"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[stack],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_HVAC / "exhaust_stack.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
