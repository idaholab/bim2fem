# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_BUILT_ELEMENT
import ifcopenshell.api.root
import bim2fem.ifcplus.api.built_element
import bim2fem.ifcplus.api.material
from typing import cast
import ifcopenshell.api.profile
from pprint import pprint
import numpy as np
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial


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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
        )

        wall_1 = bim2fem.ifcplus.api.built_element.create_linear_wall(
            start_point_2d=(1.0, 1.0),
            end_point_2d=(7.0, 1.0),
            elevation=0.0,
            height=3.0,
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
        )
        wall_1.Name = "Wall #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_1],
            relating_structure=site,
        )

        wall_2 = bim2fem.ifcplus.api.built_element.create_linear_wall(
            start_point_2d=(9.0, 1.0),
            end_point_2d=(15.0, 3.0),
            elevation=1.0,
            height=3.0,
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
        )
        wall_2.Name = "Wall #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_2],
            relating_structure=site,
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
        )

        wall_1 = bim2fem.ifcplus.api.built_element.create_linear_wall(
            start_point_2d=(1.0, 1.0),
            end_point_2d=(7.0, 1.0),
            elevation=0.0,
            height=3.0,
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
        )
        wall_1.Name = "Wall #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_1],
            relating_structure=site,
        )

        wall_thickness = 0.10 + 0.10 + 0.20
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
            depth=wall_thickness,
            location=(2.0, -wall_thickness / 2.0, 1.5),
            z_axis=(0.0, 1.0, 0.0),
            x_axis=(-1.0, 0.0, 0.0),
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
            depth=wall_thickness,
            location=(4.5, -wall_thickness / 2.0, 2.0),
            z_axis=(0.0, 1.0, 0.0),
            x_axis=(-1.0, 0.0, 0.0),
        )

        wall_2 = bim2fem.ifcplus.api.built_element.create_linear_wall(
            start_point_2d=(9.0, 1.0),
            end_point_2d=(15.0, 3.0),
            elevation=1.0,
            height=3.0,
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
        )
        wall_2.Name = "Wall #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_2],
            relating_structure=site,
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
            depth=wall_thickness,
            location=(2.0, -wall_thickness / 2.0, 1.5),
            z_axis=(0.0, 1.0, 0.0),
            x_axis=(-1.0, 0.0, 0.0),
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
        )

        wall_1 = bim2fem.ifcplus.api.built_element.create_curved_wall(
            point_of_curvature_2d=(1.0, 1.0),
            point_on_center_of_curvature_side_2d=(1.0, 1.2),
            point_of_tangency_2d=(7.0, 7.0),
            radius_of_curvature=6.0,
            elevation=0.0,
            height=3.0,
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
        )
        wall_1.Name = "Wall #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_1],
            relating_structure=site,
        )

        wall_2 = bim2fem.ifcplus.api.built_element.create_curved_wall(
            point_of_curvature_2d=(1.0 + 10.0, 1.0),
            point_on_center_of_curvature_side_2d=(1.0 + 10.0, 1.8),
            point_of_tangency_2d=(7.0 + 10.0, 7.0),
            radius_of_curvature=6.0,
            elevation=1.0,
            height=3.0,
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
        )
        wall_2.Name = "Wall #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[wall_2],
            relating_structure=site,
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
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
            ),
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
            location=(1.0, 1.0, 0.0),
        )
        slab_1.Name = "Slab #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[slab_1],
            relating_structure=site,
        )

        slab_2 = bim2fem.ifcplus.api.built_element.create_slab(
            profile=bim2fem.ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc4_file,
                profile_class="IfcRectangleProfileDef",
                dimensions=[4.0, 2.0],
                profile_name=None,
                check_for_duplicate=True,
                calculate_mechanical_properties=False,
            ),
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
            location=(1.0 + 10.0, 1.0, 0.0 + 1.0),
        )
        slab_2.Name = "Slab #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[slab_2],
            relating_structure=site,
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
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
            ),
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
            location=(1.0, 1.0, 0.0),
        )
        slab_1.Name = "Slab #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[slab_1],
            relating_structure=site,
        )

        slab_thickness = 0.10 + 0.10 + 0.20
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
            depth=slab_thickness,
            location=(2.0, 1.0, 0.0),
            z_axis=(0.0, 0.0, 1.0),
            x_axis=(1.0, 0.0, 0.0),
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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
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

            beam_1 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=material,
            )
            beam_1.Name = f"{prefix}-Beam-A"

            beam_2 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + 1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.1 + 1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=material,
            )
            beam_2.Name = f"{prefix}-Beam-B"

            beam_3 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
                frame_member_class="IfcBeam",
                start_point=(1.0 + 1.0 * 2 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 * 2 + x_shift, 1.0, 0.5),
                orientation_point=(1.1 + 1.0 * 2 + x_shift, 6.0, 1.0),
                profile=profile,
                material=material,
            )
            beam_3.Name = f"{prefix}-Beam-C"

            bim2fem.ifcplus.api.spatial.assign_container_v2(
                products=[beam_1, beam_2, beam_3],
                relating_structure=site,
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
        bim2fem.ifcplus.api.geometry.edit_object_placement_v2(
            product=site,
            repositioned_location=(1.0, 1.0, 0.0),
        )
        bim2fem.ifcplus.api.aggregate.assign_object_v2(
            products=[site],
            relating_object=project,
        )

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
        )

        profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[0.3, 0.2, 0.03, None, None, None],
            profile_name=None,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

        beam_1 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcBeam",
            start_point=(1.0, 6.0, 0.0),
            end_point=(1.0, 1.0, 0.0),
            orientation_point=(1.0, 6.0, 1.0),
            profile=profile,
            material=steel_material,
        )
        beam_1.Name = "Beam-01"

        beam_2 = bim2fem.ifcplus.api.built_element.create_curved_frame_member(
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
            material=steel_material,
        )
        beam_2.Name = "Beam-01"

        beam_3 = bim2fem.ifcplus.api.built_element.create_curved_frame_member(
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
            material=steel_material,
        )
        beam_3.Name = "Beam-03"

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

        steel_material = (
            bim2fem.ifcplus.api.material.add_material_from_standard_library(
                ifc4_file=ifc4_file,
                region="Europe",
                material_name="S355",
                check_for_duplicate=True,
            )
        )
        steel_material = cast(
            ifcopenshell.entity_instance,
            steel_material,
        )

        profile = bim2fem.ifcplus.api.profile.add_profile_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            profile_name="HE340A",
            check_for_duplicate=True,
        )
        profile = cast(
            ifcopenshell.entity_instance,
            profile,
        )

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

        col_1 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col1_bottom,
            end_point=col1_top,
            orientation_point=col1_orientation,
            profile=profile,
            material=steel_material,
        )
        col_1.Name = "Column-01"

        col_2 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col2_bottom,
            end_point=col2_top,
            orientation_point=col2_orientation,
            profile=profile,
            material=steel_material,
        )
        col_2.Name = "Column-02"

        col_3 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col3_bottom,
            end_point=col3_top,
            orientation_point=col3_orientation,
            profile=profile,
            material=steel_material,
        )
        col_3.Name = "Column-03"

        col_4 = bim2fem.ifcplus.api.built_element.create_linear_frame_member(
            frame_member_class="IfcColumn",
            start_point=col4_bottom,
            end_point=col4_top,
            orientation_point=col4_orientation,
            profile=profile,
            material=steel_material,
        )
        col_4.Name = "Column-04"

        point_at_placement_of_slab_profile = tuple(
            (np.array(col1_top) - np.array([0.0, 0.0, 0.2])).tolist()
        )
        slab_1 = bim2fem.ifcplus.api.built_element.create_slab(
            profile=ifcopenshell.api.profile.add_arbitrary_profile(
                file=ifc4_file,
                profile=[
                    (0.0, 0.0),
                    (4.0, 0.0),
                    (4.0, 5.0),
                    (0.0, 5.0),
                    (0.0, 0.0),
                ],
            ),
            location=point_at_placement_of_slab_profile,
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
        )
        slab_1.Name = "Slab-01"

        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[col_1, col_2, col_3, col_4, slab_1],
            relating_structure=site,
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
