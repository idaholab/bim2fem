# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.api.placement
import bim2fem.ifcplus.api.profile
import bim2fem.ifcplus.util.geometry
from tests.conftest import OUTPUT_DIR_FOR_STRUCTURAL, INPUT_DIR
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import bim2fem.ifcplus.api.material
from typing import cast
from pprint import pprint
import bim2fem.ifcplus.api.structural
import numpy as np
import bim2fem.ifcplus.util.structural


class TestStructuralSurfaceMembers:

    def test_add_structural_surface_member(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="StructuralAnalysisView",
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

        structural_analysis_model = (
            bim2fem.ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

        bim2fem.ifcplus.api.structural.create_structural_surface_member(
            outer_profile=[
                (3.0, 1.0, 0.2),
                (11.0, 1.0, 0.2),
                (3.0, 9.0, 0.2),
            ],
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
            structural_analysis_model=structural_analysis_model,
            name="Slab-01",
        )

        output_path = str(OUTPUT_DIR_FOR_STRUCTURAL / "structural_surface_member.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0

    def test_add_structural_surface_member_with_opening(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="StructuralAnalysisView",
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

        structural_analysis_model = (
            bim2fem.ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

        bim2fem.ifcplus.api.structural.create_structural_surface_member(
            outer_profile=[
                (3.0, 1.0, 0.2),
                (11.0, 1.0, 0.2),
                (3.0, 9.0, 0.2),
            ],
            inner_profiles=[
                [
                    (4.0, 2.0, 0.2),
                    (6.0, 3.0, 0.2),
                    (4.0, 5.0, 0.2),
                ]
            ],
            materials=[
                cast(ifcopenshell.entity_instance, concrete_material),
                cast(ifcopenshell.entity_instance, steel_material),
                cast(ifcopenshell.entity_instance, concrete_material),
            ],
            thicknesses=[
                0.10,
                0.10,
                0.20,
            ],
            structural_analysis_model=structural_analysis_model,
            name="Slab-01",
        )

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / "structural_surface_member_with_opening.ifc"
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


class TestStructuralCurveMembers:

    def test_add_linear_structural_curve_members(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="StructuralAnalysisView",
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

        structural_analysis_model = (
            bim2fem.ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

            bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
                start_point=(1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                structural_analysis_model=structural_analysis_model,
                name=f"{prefix}-Beam-01",
                product_to_be_assigned_to=None,
            )

            bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
                start_point=(1.0 + 1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.1 + 1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                structural_analysis_model=structural_analysis_model,
                name=f"{prefix}-Beam-02",
                product_to_be_assigned_to=None,
            )

            bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
                start_point=(1.0 + 1.0 * 2 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 * 2 + x_shift, 1.0, 0.5),
                orientation_point=(1.1 + 1.0 * 2 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                structural_analysis_model=structural_analysis_model,
                name=f"{prefix}-Beam-03",
                product_to_be_assigned_to=None,
            )

            x_shift += 3.0

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / "linear_structural_curve_members.ifc"
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

    def test_add_curved_structural_curve_members(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="StructuralAnalysisView",
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

        structural_analysis_model = (
            bim2fem.ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
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

        profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[0.3, 0.2, 0.03, None, None, None],
            profile_name=None,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=(1.0, 6.0, 0.0),
            end_point=(1.0, 1.0, 0.0),
            orientation_point=(1.0, 6.0, 1.0),
            profile=profile,
            material=cast(ifcopenshell.entity_instance, steel_material),
            name=f"Beam-01",
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_curved_structural_curve_member(
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
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_curved_structural_curve_member(
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
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=None,
        )

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / f"curved_structural_curve_members.ifc"
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


class TestMergeStructuralPointConnections:

    def test_create_simple_structure_with_merged_nodes(
        self,
    ):

        ifc4_file = bim2fem.ifcplus.api.project.create_ifc4_file(
            model_view_definition="StructuralAnalysisView",
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

        structural_analysis_model = (
            bim2fem.ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

        profile = bim2fem.ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcIShapeProfileDef",
            dimensions=[0.2, 0.3, 0.02, 0.02, None, None, None],
            profile_name=None,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
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

        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=col1_bottom,
            end_point=col1_top,
            orientation_point=col1_orientation,
            profile=profile,
            material=steel_material,
            structural_analysis_model=structural_analysis_model,
            name="Column-01",
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=col2_bottom,
            end_point=col2_top,
            orientation_point=col2_orientation,
            profile=profile,
            material=steel_material,
            structural_analysis_model=structural_analysis_model,
            name="Column-02",
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=col3_bottom,
            end_point=col3_top,
            orientation_point=col3_orientation,
            profile=profile,
            material=steel_material,
            structural_analysis_model=structural_analysis_model,
            name="Column-03",
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=col4_bottom,
            end_point=col4_top,
            orientation_point=col4_orientation,
            profile=profile,
            material=steel_material,
            structural_analysis_model=structural_analysis_model,
            name="Column-04",
            product_to_be_assigned_to=None,
        )

        bim2fem.ifcplus.api.structural.create_structural_surface_member(
            outer_profile=[
                col1_top,
                col2_top,
                col4_top,
            ],
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
            structural_analysis_model=structural_analysis_model,
            name="Slab-01",
        )

        bim2fem.ifcplus.api.structural.create_structural_surface_member(
            outer_profile=[
                col2_top,
                col3_top,
                col4_top,
            ],
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
            structural_analysis_model=structural_analysis_model,
            name="Slab-02",
        )

        bim2fem.ifcplus.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_file,
        )

        all_nodes = ifc4_file.by_type(
            type="IfcStructuralPointConnection",
            include_subtypes=False,
        )

        total_node_count = len(all_nodes)

        assert total_node_count == 8

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / "simple_structure_SAV_with_merged_nodes.ifc"
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


class TestTranslateStructuralPointConnections:

    def test_translate_structural_point_connection_of_simple_structure(
        self,
    ):

        ifc4_file = ifcopenshell.open(
            path=str(INPUT_DIR / "simple_structure_SAV.ifc"),
        )
        ifc4_file = cast(ifcopenshell.file, ifc4_file)

        selected_nodes = (
            bim2fem.ifcplus.util.structural.select_structural_point_connections(
                ifc4_sav_file=ifc4_file,
                bbox=bim2fem.ifcplus.util.geometry.BoundingBox.from_points(
                    points=np.array([[1.0, 1.0, 3.0]])
                ),
            )
        )

        selected_node_at_top_of_column_1 = selected_nodes[0]

        bim2fem.ifcplus.api.structural.translate_structural_point_connection(
            structural_point_connection=selected_node_at_top_of_column_1,
            translation=(-1.0, -1.0, 1.0),
        )

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / "simple_structure_SAV_with_translated_node.ifc"
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


class TestDivideStructuralCurveMembers:

    def test_divide_structural_curve_members_of_simple_structure(
        self,
    ):

        ifc4_file = ifcopenshell.open(
            path=str(INPUT_DIR / "simple_structure_SAV.ifc"),
        )
        ifc4_file = cast(ifcopenshell.file, ifc4_file)

        all_structural_curve_members = ifc4_file.by_type(
            type="IfcStructuralCurveMember",
            include_subtypes=False,
        )

        column_1 = all_structural_curve_members[0]

        column_2 = all_structural_curve_members[1]

        column_3 = all_structural_curve_members[2]

        column_4 = all_structural_curve_members[3]

        bim2fem.ifcplus.api.structural.divide_structural_curve_member(
            structural_curve_member=column_1,
            division_locations_as_proportions_of_length=[],
        )

        bim2fem.ifcplus.api.structural.divide_structural_curve_member(
            structural_curve_member=column_2,
            division_locations_as_proportions_of_length=[0.4],
        )

        bim2fem.ifcplus.api.structural.divide_structural_curve_member(
            structural_curve_member=column_3,
            division_locations_as_proportions_of_length=[0.2, 0.8],
        )

        bim2fem.ifcplus.api.structural.divide_structural_curve_member(
            structural_curve_member=column_4,
            division_locations_as_proportions_of_length=[0.2, 0.4, 0.8],
        )

        bim2fem.ifcplus.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_file,
        )

        output_path = str(
            OUTPUT_DIR_FOR_STRUCTURAL / "simple_structure_SAV_with_divided_members.ifc"
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
