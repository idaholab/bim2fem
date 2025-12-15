# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.validate
import ifcopenshell.util.representation
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.geometry
import numpy as np
import bim2fem.ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_GEOMETRY
import ifcopenshell.api.root
from typing import cast
from pprint import pprint
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial


class TestCreateCsgSolids:

    def test_create_block(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        block = bim2fem.ifcplus.api.geometry.add_block(
            ifc4_file=ifc4_file,
            length=1.0,
            width=2.0,
            height=3.0,
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=block,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[csg_solid]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "block.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_blocks(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        block_1 = bim2fem.ifcplus.api.geometry.add_block(
            ifc4_file=ifc4_file,
            length=0.5,
            width=1.0,
            height=4.0,
        )
        block_2 = bim2fem.ifcplus.api.geometry.add_block(
            ifc4_file=ifc4_file,
            length=3.5,
            width=1.0,
            height=0.5,
            repositioned_origin=(0.5, 0.0, 3.5),
        )
        block_3 = bim2fem.ifcplus.api.geometry.add_block(
            ifc4_file=ifc4_file,
            length=0.5,
            width=1.0,
            height=4.0,
            repositioned_origin=(4.0, 0.0, 0.0),
        )
        boolean_results = ifcopenshell.api.geometry.add_boolean(
            file=ifc4_file,
            first_item=block_1,
            second_items=[block_2, block_3],
            operator="UNION",
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=boolean_results[-1],
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[csg_solid]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "blocks.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_rectangular_pyramid(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        rectangular_pyramid = bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
            ifc4_file=ifc4_file,
            length=1.0,
            width=2.0,
            height=3.0,
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=rectangular_pyramid,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[csg_solid]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "rectangular_pyramid.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_block_and_pyramid(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        block = bim2fem.ifcplus.api.geometry.add_block(
            ifc4_file=ifc4_file,
            length=1.0,
            width=1.0,
            height=4.0,
        )
        rect_pyramid = bim2fem.ifcplus.api.geometry.add_rectangular_pyramid(
            ifc4_file=ifc4_file,
            length=1.0,
            width=1.0,
            height=0.5,
            repositioned_origin=(0.0, 0.0, 4.0),
        )
        boolean_results = ifcopenshell.api.geometry.add_boolean(
            file=ifc4_file,
            first_item=block,
            second_items=[rect_pyramid],
            operator="UNION",
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=boolean_results[-1],
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[csg_solid]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "block_and_pyramid.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_right_circular_cylinder(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        cylindrical_extruded_area_solid = (
            bim2fem.ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
                ifc4_file=ifc4_file,
                radius=0.5,
                extrusion_depth=4.0,
                repositioned_origin=(0.5, 0.5, 0.0),
            )
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[cylindrical_extruded_area_solid]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[cylindrical_extruded_area_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "right_circular_cylinder.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_sphere(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )

        sphere = bim2fem.ifcplus.api.geometry.add_sphere(
            ifc4_file=ifc4_file,
            radius=0.5,
            repositioned_origin=(0.5, 0.5, 0.5),
        )
        csg_solid = bim2fem.ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=sphere,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[csg_solid]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "sphere.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestSweptAreaSolids:

    def test_create_extruded_area_solid(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        depth = 2.0
        width = 1.0
        thickness = 0.2
        length = 8.0
        profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[depth, width, thickness, None, None, None],
            check_for_duplicate=True,
        )
        extruded_area_solid = bim2fem.ifcplus.api.geometry.add_extruded_area_solid(
            ifc4_file=ifc4_file,
            swept_area=profile,
            depth=length,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[extruded_area_solid]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[extruded_area_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(0.0, 8.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, -1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "extruded_area_solid.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_extruded_area_solid_tapered(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        depth = 2.0
        width = 1.0
        thickness = 0.2
        length = 8.0
        starting_profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[depth, width, thickness, None, None, None],
            check_for_duplicate=True,
        )
        ending_profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[
                depth * 0.25,
                width * 0.25,
                thickness * 0.25,
                None,
                None,
                None,
            ],
            check_for_duplicate=True,
        )
        extruded_area_solid_tapered = (
            bim2fem.ifcplus.api.geometry.add_extruded_area_solid_tapered(
                ifc4_file=ifc4_file,
                swept_area=starting_profile,
                end_swept_area=ending_profile,
                depth=length,
            )
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[extruded_area_solid_tapered]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[extruded_area_solid_tapered],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(0.0, 8.0, 0.0),
            repositioned_x_axis=(1.0, 0.0, 0.0),
            repositioned_z_axis=(0.0, -1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "extruded_area_solid_tapered.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_revolved_area_solid(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        depth = 2.0
        width = 1.0
        thickness = 0.2
        revolved_area_solid = bim2fem.ifcplus.api.geometry.add_revolved_area_solid(
            ifc4_file=ifc4_file,
            swept_area=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcLShapeProfileDef",
                dimensions=[depth, width, thickness, None, None, None],
                check_for_duplicate=True,
            ),
            central_angle_of_curvature=np.pi / 2.0,
            center_of_curvature_in_object_xy_plane=(5.0, 5.0),
            repositioned_origin=(0.0, 0.0, 0.0),
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[revolved_area_solid]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[revolved_area_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "revolved_area_solid.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestBoundingBox:

    def test_create_bounding_box(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        bounding_box = bim2fem.ifcplus.api.geometry.add_bounding_box(
            ifc4_file=ifc4_file,
            length=4.0,
            width=2.0,
            height=3.0,
            corner_coordinates=(0.0, 0.0, 0.0),
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Box",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[bounding_box]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[bounding_box],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "bounding_box.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestFacetedBrep:

    def test_create_faceted_brep(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        points = [
            (-0.5 + 0.5, -0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, -0.5 + 0.5, 0.5 + 0.5),
            (-0.5 + 0.5, 0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, 0.5 + 0.5, 0.5 + 0.5),
            (0.5 + 0.5, -0.5 + 0.5, -0.5 + 0.5),
            (-0.5 + 0.5, -0.5 + 0.5, -0.5 + 0.5),
            (0.5 + 0.5, 0.5 + 0.5, -0.5 + 0.5),
            (-0.5 + 0.5, 0.5 + 0.5, -0.5 + 0.5),
        ]
        triangles = [
            [0, 1, 2],
            [3, 2, 1],
            [1, 0, 4],
            [5, 4, 0],
            [3, 1, 6],
            [4, 6, 1],
            [2, 3, 7],
            [6, 7, 3],
            [0, 2, 5],
            [7, 5, 2],
            [5, 7, 4],
            [6, 4, 7],
        ]
        faceted_brep = bim2fem.ifcplus.api.geometry.add_faceted_brep(
            ifc4_file=ifc4_file,
            points=points,
            triangles=triangles,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[faceted_brep]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[faceted_brep],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "faceted_brep.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestTopologicalRepresentationItems:

    def test_create_edge(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        edge = bim2fem.ifcplus.api.geometry.add_edge(
            edge_start_as_vertex_point=bim2fem.ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=(0.0, 0.0, 1.0),
            ),
            edge_end_as_vertex_point=bim2fem.ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=(4.0, 0.0, 1.0),
            ),
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[edge]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[edge],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "edge.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_edge_curve(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        vertex_point_1 = bim2fem.ifcplus.api.geometry.add_vertex_point(
            ifc4_file=ifc4_file,
            point_coordinates=(2.0, 6.0, 0.0),
        )
        vertex_point_2 = bim2fem.ifcplus.api.geometry.add_vertex_point(
            ifc4_file=ifc4_file,
            point_coordinates=(7.0, 1.0, 0.0),
        )
        vertex_point_3 = bim2fem.ifcplus.api.geometry.add_vertex_point(
            ifc4_file=ifc4_file,
            point_coordinates=(2.0, 6.0 - 5.0, 0.0 + 5.0),
        )
        edge_curve_1 = bim2fem.ifcplus.api.geometry.add_edge_curve(
            point_of_curvature_as_vertex_point=vertex_point_1,
            point_of_tangency_as_vertex_point=vertex_point_2,
            point_defining_plane_of_arc_and_center_of_curvature_side=(7.0, 6.0, 0.0),
            radius_of_curvature=5.0,
        )
        edge_curve_2 = bim2fem.ifcplus.api.geometry.add_edge_curve(
            point_of_curvature_as_vertex_point=vertex_point_1,
            point_of_tangency_as_vertex_point=vertex_point_3,
            point_defining_plane_of_arc_and_center_of_curvature_side=(2.0, 6.0, 1.0),
            radius_of_curvature=5.0,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(
                    items=[edge_curve_1, edge_curve_2]
                ),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[edge_curve_1, edge_curve_2],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "edge_curve.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_face_surface(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        points_of_outer_bound = [
            (0.0, 0.0, 0.0),
            (8.0, 0.0, 0.0),
            (8.0, 4.0, 0.0),
            (0.0, 4.0, 0.0),
        ]
        vertex_points_of_outer_bound = [
            bim2fem.ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=point_of_outer_bound,
            )
            for point_of_outer_bound in points_of_outer_bound
        ]
        face_surface = bim2fem.ifcplus.api.geometry.add_face_surface(
            vertex_points_of_outer_bound=vertex_points_of_outer_bound,
            vertex_points_of_inner_bounds=[],
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[face_surface]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[face_surface],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "face_surface.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_create_face_surface_with_voids(
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

        element = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBuildingElementProxy",
            name="Element-01",
            predefined_type=None,
        )
        points_of_outer_bound = [
            (0.0, 0.0, 0.0),
            (8.0, 0.0, 0.0),
            (8.0, 4.0, 0.0),
            (0.0, 4.0, 0.0),
        ]
        points_of_inner_bounds = [
            [
                (1.0, 1.0, 0.0),
                (2.0, 1.0, 0.0),
                (2.0, 2.0, 0.0),
            ],
            [
                (1.0 + 3.0, 1.0, 0.0),
                (2.0 + 3.0, 1.0, 0.0),
                (2.0 + 3.0, 2.0, 0.0),
            ],
        ]
        vertex_points_of_outer_bound = [
            bim2fem.ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc4_file,
                point_coordinates=point_of_outer_bound,
            )
            for point_of_outer_bound in points_of_outer_bound
        ]
        vertex_points_of_inner_bounds = []
        for points_of_inner_bound in points_of_inner_bounds:
            vertex_points_of_inner_bounds.append(
                [
                    bim2fem.ifcplus.api.geometry.add_vertex_point(
                        ifc4_file=ifc4_file,
                        point_coordinates=point_of_inner_bound,
                    )
                    for point_of_inner_bound in points_of_inner_bound
                ]
            )
        face_surface = bim2fem.ifcplus.api.geometry.add_face_surface(
            vertex_points_of_outer_bound=vertex_points_of_outer_bound,
            vertex_points_of_inner_bounds=vertex_points_of_inner_bounds,
        )
        shape_representation = bim2fem.ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc4_file,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=cast(
                str,
                ifcopenshell.util.representation.guess_type(items=[face_surface]),
            ),
            context_type="Model",
            target_view="MODEL_VIEW",
            items=[face_surface],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc4_file,
            product=element,
            representation=shape_representation,
        )
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=element,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[element],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "face_surface_with_voids.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
