# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import ifcplus.api.project
import ifcplus.api.placement
import ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_STRUCTURAL
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcplus.api.material
from typing import cast
from pprint import pprint
import ifcplus.api.structural


class TestStructuralSurfaceMembers:

    def test_add_structural_surface_member(
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

        structural_analysis_model = (
            ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

        ifcplus.api.structural.create_structural_surface_member(
            outer_profile=[
                (3.0, 1.0, 0.2),
                (11.0, 1.0, 0.2),
                (3.0, 9.0, 0.2),
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

        output_path = str(OUTPUT_DIR_FOR_STRUCTURAL / "structural_surface_member.ifc")
        ifcplus.api.project.write_to_ifc_spf(
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

        structural_analysis_model = (
            ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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

        ifcplus.api.structural.create_structural_surface_member(
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
        ifcplus.api.project.write_to_ifc_spf(
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

        ifc4_file = ifcplus.api.project.create_ifc4_file(
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
        ifcplus.api.placement.edit_object_placement(
            product=site,
            place_object_relative_to_parent=True,
        )

        structural_analysis_model = (
            ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
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
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = concrete_material

            elif parametrized_profile_def_class == "IfcRectangleHollowProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3, 0.02, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcCircleProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.1],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = concrete_material

            elif parametrized_profile_def_class == "IfcCircleHollowProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.1, 0.02],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcIShapeProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.2, 0.3, 0.02, 0.02, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcLShapeProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.3, 0.2, 0.03, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcUShapeProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
                    ifc4_file=ifc4_file,
                    profile_class=parametrized_profile_def_class,
                    dimensions=[0.3, 0.2, 0.02, 0.02, None, None, None],
                    profile_name=None,
                    check_for_duplicate=True,
                    calculate_mechanical_properties=True,
                )
                material = steel_material

            elif parametrized_profile_def_class == "IfcTShapeProfileDef":
                profile = ifcplus.api.profile.add_parameterized_profile(
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

            ifcplus.api.structural.create_linear_structural_curve_member(
                start_point=(1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                structural_analysis_model=structural_analysis_model,
                name=f"{prefix}-Beam-01",
                product_to_be_assigned_to=None,
            )

            ifcplus.api.structural.create_linear_structural_curve_member(
                start_point=(1.0 + 1.0 + x_shift, 6.0, 0.0),
                end_point=(1.0 + 1.0 + x_shift, 1.0, 0.0),
                orientation_point=(1.1 + 1.0 + x_shift, 6.0, 1.0),
                profile=profile,
                material=cast(ifcopenshell.entity_instance, material),
                structural_analysis_model=structural_analysis_model,
                name=f"{prefix}-Beam-02",
                product_to_be_assigned_to=None,
            )

            ifcplus.api.structural.create_linear_structural_curve_member(
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
        ifcplus.api.project.write_to_ifc_spf(
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

        ifc4_file = ifcplus.api.project.create_ifc4_file(
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
        ifcplus.api.placement.edit_object_placement(
            product=site,
            repositioned_origin=(1.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        structural_analysis_model = (
            ifcplus.api.structural.add_structural_analysis_model(
                ifc4_file=ifc4_file,
                name="SA Model - 1",
            )
        )

        steel_material = ifcplus.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name="S355",
            check_for_duplicate=True,
        )

        profile = ifcplus.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcLShapeProfileDef",
            dimensions=[0.3, 0.2, 0.03, None, None, None],
            profile_name=None,
            check_for_duplicate=True,
            calculate_mechanical_properties=True,
        )

        ifcplus.api.structural.create_linear_structural_curve_member(
            start_point=(1.0, 6.0, 0.0),
            end_point=(1.0, 1.0, 0.0),
            orientation_point=(1.0, 6.0, 1.0),
            profile=profile,
            material=cast(ifcopenshell.entity_instance, steel_material),
            name=f"Beam-01",
            structural_analysis_model=structural_analysis_model,
            product_to_be_assigned_to=None,
        )

        ifcplus.api.structural.create_curved_structural_curve_member(
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

        ifcplus.api.structural.create_curved_structural_curve_member(
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
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
