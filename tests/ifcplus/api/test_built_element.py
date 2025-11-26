# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_BUILT_ELEMENT
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import bim2fem.ifcplus.api.built_element
import bim2fem.ifcplus.api.material
from typing import cast
import ifcopenshell.api.profile
from pprint import pprint
import numpy as np


class TestWalls:

    def test_add_straight_walls(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.built_element.create_linear_wall(
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

        bim2fem.ifcplus.api.built_element.create_linear_wall(
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
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_straight_walls_with_openings(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        wall_1 = bim2fem.ifcplus.api.built_element.create_linear_wall(
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

        bim2fem.ifcplus.api.built_element.create_opening_element(
            voided_element=wall_1,
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
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

        bim2fem.ifcplus.api.built_element.create_opening_element(
            voided_element=wall_1,
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
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

        wall_2 = bim2fem.ifcplus.api.built_element.create_linear_wall(
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

        bim2fem.ifcplus.api.built_element.create_opening_element(
            voided_element=wall_2,
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
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
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_curved_walls(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.built_element.create_curved_wall(
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

        bim2fem.ifcplus.api.built_element.create_curved_wall(
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
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestSlabs:

    def test_add_slabs(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        bim2fem.ifcplus.api.built_element.create_slab(
            profile=ifcopenshell.api.profile.add_arbitrary_profile(
                file=ifc4_file,
                profile=[
                    (0.0, 0.0),
                    (5.0, 0.0),
                    (5.0, 3.0),
                    (0.0, 3.0),
                    (0.0, 0.0),
                ],
                name=None,
            ),
            point_at_placement_of_slab_profile=(1.0, 1.0, 0.0),
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Slab-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_slab(
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[4.0, 2.0],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
            point_at_placement_of_slab_profile=(1.0 + 10.0, 1.0, 0.0 + 1.0),
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Slab-02",
            parent=site,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / "slabs.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_slab_with_opening(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        slab_1 = bim2fem.ifcplus.api.built_element.create_slab(
            profile=ifcopenshell.api.profile.add_arbitrary_profile(
                file=ifc4_file,
                profile=[
                    (0.0, 0.0),
                    (5.0, 0.0),
                    (5.0, 3.0),
                    (0.0, 3.0),
                    (0.0, 0.0),
                ],
                name=None,
            ),
            point_at_placement_of_slab_profile=(1.0, 1.0, 0.0),
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[0.10, 0.10, 0.20],
            name="Slab-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        opening_depth = 0.10 + 0.10 + 0.20

        bim2fem.ifcplus.api.built_element.create_opening_element(
            voided_element=slab_1,
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[2.0, 1.0],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
            depth=opening_depth,
            origin_relative_to_voided_element=(2.0, 1.0, 0.0),
            z_axis_relative_to_voided_element=(0.0, 0.0, 1.0),
            x_axis_relative_to_voided_element=(1.0, 0.0, 0.0),
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / "slab_with_opening.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestFrameMembers:

    def test_add_custom_beams(
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

        concrete_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="C35/45",
                check_for_duplicate=True,
            )
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        x_shift = 0.0

        for parametrized_profile_def_class in [
            "IfcRectangleProfileDef",
            "IfcRectangleHollowProfileDef",
            "IfcCircleProfileDef",
            "IfcCircleHollowProfileDef",
            "IfcIShapeProfileDef",
            "IfcLShapeProfileDef",
            "IfcUShapeProfileDef",
            "IfcTShapeProfileDef",
        ]:

            if parametrized_profile_def_class == "IfcRectangleProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = concrete_material

            elif parametrized_profile_def_class == "IfcRectangleHollowProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3, 0.02, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcCircleProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.1],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = concrete_material

            elif parametrized_profile_def_class == "IfcCircleHollowProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.1, 0.02],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcIShapeProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3, 0.02, 0.02, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcLShapeProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.3, 0.2, 0.03, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcUShapeProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.3, 0.2, 0.02, 0.02, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcTShapeProfileDef":
                profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.3, 0.2, 0.02, 0.02, None, None, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            prefix = parametrized_profile_def_class.replace("Ifc", "").replace(
                "ProfileDef", ""
            )

            bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                name=f"{prefix}-Beam-01",
                parent=site,
                place_object_relative_to_parent=True,
            )

            bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + 1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.1 + 1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                name=f"{prefix}-Beam-02",
                parent=site,
                place_object_relative_to_parent=True,
            )

            bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + 1.0 * 2 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 * 2 + x_shift, 1.0, 0.5),
                orientation_point=(1.1 + 1.0 * 2 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                name=f"{prefix}-Beam-03",
                parent=site,
                place_object_relative_to_parent=True,
            )

            x_shift += 3.0

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / f"custom_beams.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_curved_beams(
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )

        profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[0.3, 0.2, 0.03, None, None, None],
            profile_name=None,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

        bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcBeam",
            start_point=(1.0, 6.0, 0.0),
            end_point=(1.0, 1.0, 0.0),
            orientation_point=(1.0, 6.0, 1.0),
            profile=profile,
            material=cast(ifcopenshell.entity_instance, steel_material),
            name=f"Beam-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_curved_frame_member(
            frame_member_class="IfcBeam",
            start_point=(2.0, 6.0, 0.0),
            end_point=(7.0, 1.0, 0.0),
            orientation_point=(2.0, 6.0, 0.0 + 1.0),
            point_defining_plane_of_arc_and_center_of_curvature_side=(
                2.0 + 1.0,
                6.0,
                0.0,
            ),
            radius_of_curvature=5.0,
            profile=profile,
            material=cast(ifcopenshell.entity_instance, steel_material),
            name=f"Beam-02",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_curved_frame_member(
            frame_member_class="IfcBeam",
            start_point=(2.0, 6.0, 0.0),
            end_point=(2.0, 6.0 - 5.0, 0.0 + 5.0),
            orientation_point=(2.0, 6.0, 0.0 + 1.0),
            point_defining_plane_of_arc_and_center_of_curvature_side=(
                2.0,
                6.0,
                1.0,
            ),
            radius_of_curvature=5.0,
            profile=profile,
            material=cast(ifcopenshell.entity_instance, steel_material),
            name=f"Beam-03",
            parent=site,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / f"curved_beams.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0


class TestCreateStructure:

    def test_create_simple_structure(
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
        ifcopenshell.api.aggregate.assign_object(
            file=ifc4_file,
            products=[site],
            relating_object=project,
        )
        bim2fem.ifcplus.api.placement.edit_object_placement(
            product=site,
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
        concrete_material = cast(ifcopenshell.entity_instance, concrete_material)

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(ifcopenshell.entity_instance, steel_material)

        profile = bim2fem.ifcplus.api.profile.add_profile_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            profile_name="HE340A",
            check_for_duplicate=True,
        )
        profile = cast(ifcopenshell.entity_instance, profile)

        col1_bottom = (1.0, 1.0, 0.0)
        col1_top = tuple((np.array(col1_bottom) + np.array([0.0, 0.0, 3.0])).tolist())
        col1_orientation = tuple(
            (np.array(col1_bottom) + np.array([0.0, 1.0, 0.0])).tolist()
        )

        col2_bottom = (1.0 + 4.0, 1.0, 0.0)
        col2_top = tuple((np.array(col2_bottom) + np.array([0.0, 0.0, 3.0])).tolist())
        col2_orientation = tuple(
            (np.array(col2_bottom) + np.array([0.0, 1.0, 0.0])).tolist()
        )

        col3_bottom = (1.0 + 4.0, 1.0 + 5.0, 0.0)
        col3_top = tuple((np.array(col3_bottom) + np.array([0.0, 0.0, 3.0])).tolist())
        col3_orientation = tuple(
            (np.array(col3_bottom) + np.array([0.0, 1.0, 0.0])).tolist()
        )

        col4_bottom = (1.0, 1.0 + 5.0, 0.0)
        col4_top = tuple((np.array(col4_bottom) + np.array([0.0, 0.0, 3.0])).tolist())
        col4_orientation = tuple(
            (np.array(col4_bottom) + np.array([0.0, 1.0, 0.0])).tolist()
        )

        bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col1_bottom,
            end_point=col1_top,
            orientation_point=col1_orientation,
            profile=profile,
            material=steel_material,
            name="Column-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col2_bottom,
            end_point=col2_top,
            orientation_point=col2_orientation,
            profile=profile,
            material=steel_material,
            name="Column-02",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col3_bottom,
            end_point=col3_top,
            orientation_point=col3_orientation,
            profile=profile,
            material=steel_material,
            name="Column-03",
            parent=site,
            place_object_relative_to_parent=True,
        )

        bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col4_bottom,
            end_point=col4_top,
            orientation_point=col4_orientation,
            profile=profile,
            material=steel_material,
            name="Column-04",
            parent=site,
            place_object_relative_to_parent=True,
        )

        point_at_placement_of_slab_profile = tuple(
            (np.array(col1_top) - np.array([0.0, 0.0, 0.2])).tolist()
        )

        bim2fem.ifcplus.api.built_element.create_slab(
            profile=ifcopenshell.api.profile.add_arbitrary_profile(
                file=ifc4_file,
                profile=[
                    (0.0, 0.0),
                    (4.0, 0.0),
                    (4.0, 5.0),
                    (0.0, 5.0),
                    (0.0, 0.0),
                ],
                name=None,
            ),
            point_at_placement_of_slab_profile=point_at_placement_of_slab_profile,
            materials=[
                concrete_material,
                steel_material,
                concrete_material,
            ],
            thicknesses=[
                0.10,
                0.10,
                0.20,
            ],
            name="Slab-01",
            parent=site,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_BUILT_ELEMENT / "simple_structure_RV.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
