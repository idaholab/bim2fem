# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import ifcplus.api.project
import ifcplus.api.placement
import ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_BUILT_ELEMENT
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcplus.api.built_element
import ifcplus.api.material
from typing import cast


class TestWalls:

    def test_add_straight_walls(
        self,
    ):

        ifc4_file = ifcplus.api.project.create_ifc4_file(
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

        concrete_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )

        steel_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="S355",
            check_for_duplicate=True,
        )

        ifcplus.api.built_element.create_2pt_wall(
            start_point_2d=(1.0, 1.0),
            end_point_2d=(7.0, 1.0),
            elevation=0.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        ifcplus.api.built_element.create_2pt_wall(
            start_point_2d=(1.0 + 8.0, 1.0),
            end_point_2d=(7.0 + 8.0, 1.0 + 2.0),
            elevation=1.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / "straight_walls.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_straight_walls_with_openings(
        self,
    ):

        ifc4_file = ifcplus.api.project.create_ifc4_file(
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

        concrete_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )

        steel_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="S355",
            check_for_duplicate=True,
        )

        wall_1 = ifcplus.api.built_element.create_2pt_wall(
            start_point_2d=(1.0, 1.0),
            end_point_2d=(7.0, 1.0),
            elevation=0.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        opening_depth = 0.10 + 0.10 + 0.20

        ifcplus.api.built_element.create_opening_element(
            voided_element=wall_1,
            profile=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[2.0, 1.0],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
            depth=opening_depth,
            origin_relative_to_voided_element=(2.0, -opening_depth / 2.0, 1.5),
            z_axis_relative_to_voided_element=(0.0, 1.0, 0.0),
            x_axis_relative_to_voided_element=(-1.0, 0.0, 0.0),
        )

        ifcplus.api.built_element.create_opening_element(
            voided_element=wall_1,
            profile=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcCircleProfileDef",
                dimensions=[0.5],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
            depth=opening_depth,
            origin_relative_to_voided_element=(4.5, -opening_depth / 2.0, 2.0),
            z_axis_relative_to_voided_element=(0.0, 1.0, 0.0),
            x_axis_relative_to_voided_element=(-1.0, 0.0, 0.0),
        )

        wall_2 = ifcplus.api.built_element.create_2pt_wall(
            start_point_2d=(1.0 + 8.0, 1.0),
            end_point_2d=(7.0 + 8.0, 1.0 + 2.0),
            elevation=1.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        ifcplus.api.built_element.create_opening_element(
            voided_element=wall_2,
            profile=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[2.0, 1.0],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
            depth=opening_depth,
            origin_relative_to_voided_element=(2.0, -opening_depth / 2.0, 1.5),
            z_axis_relative_to_voided_element=(0.0, 1.0, 0.0),
            x_axis_relative_to_voided_element=(-1.0, 0.0, 0.0),
        )

        output_path = str(
            OUTPUT_DIR_FOR_BUILT_ELEMENT / "straight_walls_with_openings.ifc"
        )
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_curved_walls(
        self,
    ):

        ifc4_file = ifcplus.api.project.create_ifc4_file(
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

        concrete_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="C35/45",
            check_for_duplicate=True,
        )

        steel_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="S355",
            check_for_duplicate=True,
        )

        ifcplus.api.built_element.create_curved_wall(
            point_of_curvature_2d=(1.0, 1.0),
            point_on_center_of_curvature_side_2d=(1.0, 1.2),
            point_of_tangency_2d=(7.0, 7.0),
            radius_of_curvature=6.0,
            elevation=0.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        ifcplus.api.built_element.create_curved_wall(
            point_of_curvature_2d=(1.0 + 10.0, 1.0),
            point_on_center_of_curvature_side_2d=(1.0 + 10.0, 1.8),
            point_of_tangency_2d=(7.0 + 10.0, 7.0),
            radius_of_curvature=6.0,
            elevation=1.0,
            height=3.0,
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Wall-02",
            parent=site,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / "curved_walls.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)
        assert len(logger.statements) == 0
