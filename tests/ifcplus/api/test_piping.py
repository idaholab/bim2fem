# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.validate
import bim2fem.ifcplus.api.project
import bim2fem.ifcplus.util.geometry
import bim2fem.ifcplus.api.geometry
import bim2fem.ifcplus.api.piping
import bim2fem.ifcplus.api.material
from tests.conftest import OUTPUT_DIR_FOR_PIPING
import bim2fem.ifcplus.util.geometry
import ifcopenshell.api.root
import ifcopenshell.api.system
from pprint import pprint
import bim2fem.ifcplus.api.aggregate
import bim2fem.ifcplus.api.spatial
import numpy as np


class TestCreatePipingElements:

    def test_create_elbows(
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

        material = bim2fem.ifcplus.api.material.add_material_with_structural_properties(
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
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
                point_on_center_of_curvature_side=(2.0, 1.0, 0.0),
                point_of_curvature=(1.0, 1.0, 0.0),
                point_of_tangency=(2.0, 2.0, 0.0),
                radius_of_curvature=1.0,
            )
        )
        elbow_1 = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve_1.point_of_curvature,
            end_point=horizontal_curve_1.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve_1.center_of_curvature,
            radius_of_curvature=horizontal_curve_1.radius_of_curvature,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        elbow_1.Name = "Elbow #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[elbow_1],
            relating_structure=site,
        )

        horizontal_curve_2 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(4.0, 1.0, 0.0),
                point_of_curvature=(3.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 2,
            )
        )
        elbow_2 = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve_2.point_of_curvature,
            end_point=horizontal_curve_2.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve_2.center_of_curvature,
            radius_of_curvature=horizontal_curve_2.radius_of_curvature,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        elbow_2.Name = "Elbow #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[elbow_2],
            relating_structure=site,
        )

        horizontal_curve_3 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_PT_and_PI(
                point_of_curvature=(5.0, 1.0, 0.0),
                point_of_intersection=(5.0, 2.0, 0.0),
                point_of_tangency=(6.0, 2.0, 0.0),
            )
        )
        elbow_3 = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve_3.point_of_curvature,
            end_point=horizontal_curve_3.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve_3.center_of_curvature,
            radius_of_curvature=horizontal_curve_3.radius_of_curvature,
            nominal_diameter=1.0,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        elbow_3.Name = "Elbow #3"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[elbow_3],
            relating_structure=site,
        )

        horizontal_curve_4 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_3pt_polyline(
                first_point=(7.0, 1.0, 0.0),
                second_point=(7.0, 2.0, 0.0),
                third_point=(8.0, 2.0, 0.0),
                radius_of_curvature=1.0,
            )
        )
        elbow_4 = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve_4.point_of_curvature,
            end_point=horizontal_curve_4.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve_4.center_of_curvature,
            radius_of_curvature=horizontal_curve_4.radius_of_curvature,
            nominal_diameter=1.2,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        elbow_4.Name = "Elbow #4"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[elbow_4],
            relating_structure=site,
        )

        horizontal_curve_5 = (
            bim2fem.ifcplus.util.geometry.HorizontalCurve.from_PC_and_CC_and_angle(
                point_of_center_of_curvature=(10.0, 1.0, 0.0),
                point_of_curvature=(9.0, 1.0, 0.0),
                central_angle_of_curvature=np.pi / 3,
            )
        )
        elbow_5 = bim2fem.ifcplus.api.piping.create_elbow(
            start_point=horizontal_curve_5.point_of_curvature,
            end_point=horizontal_curve_5.point_of_tangency,
            point_defining_plane_of_arc_and_center_of_curvature_side=horizontal_curve_5.center_of_curvature,
            radius_of_curvature=horizontal_curve_5.radius_of_curvature,
            nominal_diameter=1.2,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        elbow_5.Name = "Elbow #5"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[elbow_5],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_PIPING / "elbows.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
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

        material = bim2fem.ifcplus.api.material.add_material_with_structural_properties(
            ifc4_file=ifc4_file,
            name="Galvanized Steel",
            category="steel",
            mass_density=7850.0,
            young_modulus=200.0e9,
            poisson_ratio=0.3,
            thermal_expansion_coefficient=1.2e-6,
            check_for_duplicate=True,
        )

        pipe_1 = bim2fem.ifcplus.api.piping.create_pipe_segment(
            start_point=(1.0, 1.0, 0.0),
            end_point=(1.0, 1.0 + 5.0, 0.0),
            outer_diameter=1.0,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        pipe_1.Name = "Pipe #1"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[pipe_1],
            relating_structure=site,
        )

        pipe_2 = bim2fem.ifcplus.api.piping.create_pipe_segment(
            start_point=(1.0, 1.0 + 8.0, 0.0),
            end_point=(1.0, 1.0 + 5.0 + 8.0, 0.0 + 5.0),
            outer_diameter=1.0,
            thickness=0.10,
            material=material,
            distribution_system=cvs,
        )
        pipe_2.Name = "Pipe #2"
        bim2fem.ifcplus.api.spatial.assign_container_v2(
            products=[pipe_2],
            relating_structure=site,
        )

        output_path = str(OUTPUT_DIR_FOR_PIPING / "pipe_segments.ifc")
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_file,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        pprint(logger.statements)
        assert len(logger.statements) == 0
