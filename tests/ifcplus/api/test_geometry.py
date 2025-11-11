# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import ifcopenshell
import ifcopenshell.api.geometry
import ifcopenshell.validate
import ifcopenshell.util.representation
import ifcplus.api.project
import ifcplus.api.geometry
import ifcplus.api.placement
import numpy as np
import ifcplus.api.profile
from tests.conftest import OUTPUT_DIR_FOR_GEOMETRY
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import ifcopenshell.api.spatial


class TestAddCsgSolid:

    def test_add_one_block(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        block = ifcplus.api.geometry.add_block(
            ifc4_file=ifc_file_with_one_element,
            length=1.0,
            width=2.0,
            height=3.0,
        )

        csg_solid = ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=block,
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_block.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_three_blocks(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        block_1 = ifcplus.api.geometry.add_block(
            ifc4_file=ifc_file_with_one_element,
            length=0.5,
            width=1.0,
            height=4.0,
        )

        block_2 = ifcplus.api.geometry.add_block(
            ifc4_file=ifc_file_with_one_element,
            length=3.5,
            width=1.0,
            height=0.5,
            repositioned_origin=(0.5, 0.0, 3.5),
        )

        block_3 = ifcplus.api.geometry.add_block(
            ifc4_file=ifc_file_with_one_element,
            length=0.5,
            width=1.0,
            height=4.0,
            repositioned_origin=(4.0, 0.0, 0.0),
        )

        boolean_results = ifcopenshell.api.geometry.add_boolean(
            file=ifc_file_with_one_element,
            first_item=block_1,
            second_items=[block_2, block_3],
            operator="UNION",
        )

        csg_solid = ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=boolean_results[-1],
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        ifcplus.api.placement.edit_object_placement(
            product=element,
            repositioned_origin=(2.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "three_blocks.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_rectangular_pyramid(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        rectangular_pyramid = ifcplus.api.geometry.add_rectangular_pyramid(
            ifc4_file=ifc_file_with_one_element,
            length=1.0,
            width=2.0,
            height=3.0,
        )

        csg_solid = ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=rectangular_pyramid,
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_rectangular_pyramid.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_obelisk(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        block = ifcplus.api.geometry.add_block(
            ifc4_file=ifc_file_with_one_element,
            length=1.0,
            width=1.0,
            height=4.0,
        )

        rect_pyramid = ifcplus.api.geometry.add_rectangular_pyramid(
            ifc4_file=ifc_file_with_one_element,
            length=1.0,
            width=1.0,
            height=0.5,
            repositioned_origin=(0.0, 0.0, 4.0),
        )

        boolean_results = ifcopenshell.api.geometry.add_boolean(
            file=ifc_file_with_one_element,
            first_item=block,
            second_items=[rect_pyramid],
            operator="UNION",
        )

        csg_solid = ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=boolean_results[-1],
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "obelisk.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_right_circular_cylinder(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        cylinder = ifcplus.api.geometry.add_cylindrical_extruded_area_solid(
            ifc4_file=ifc_file_with_one_element,
            radius=0.5,
            extrusion_depth=4.0,
            repositioned_origin=(0.5, 0.5, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[cylinder]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[cylinder],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_right_circular_cylinder.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_sphere(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        sphere = ifcplus.api.geometry.add_sphere(
            ifc4_file=ifc_file_with_one_element,
            radius=0.5,
            repositioned_origin=(0.5, 0.5, 0.5),
        )

        csg_solid = ifcplus.api.geometry.add_csg_solid(
            boolean_result_or_primitive=sphere,
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[csg_solid]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[csg_solid],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_sphere.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestAddSweptAreaSolid:

    def test_add_l_shape_extruded_area_solid(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        depth = 2.0
        width = 1.0
        thickness = 0.2
        length = 5.0

        l_shape_extrusion = ifcplus.api.geometry.add_extruded_area_solid(
            ifc4_file=ifc_file_with_one_element,
            profile=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc_file_with_one_element,
                profile_class="IfcLShapeProfileDef",
                dimensions=[depth, width, thickness, None, None, None],
                check_for_duplicate=True,
            ),
            extrusion_depth=length,
            repositioned_origin=(0.0, 0.0, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[l_shape_extrusion]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[l_shape_extrusion],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "l_shape_extrusion.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_l_shape_extruded_area_solid_tapered(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        depth = 2.0
        width = 1.0
        thickness = 0.2
        length = 5.0

        l_shape_extrusion = ifcplus.api.geometry.add_extruded_area_solid_tapered(
            ifc4_file=ifc_file_with_one_element,
            profile_start=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc_file_with_one_element,
                profile_class="IfcLShapeProfileDef",
                dimensions=[depth, width, thickness, None, None, None],
                check_for_duplicate=True,
            ),
            profile_end=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc_file_with_one_element,
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
            ),
            extrusion_depth=length,
            repositioned_origin=(0.0, 0.0, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[l_shape_extrusion]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[l_shape_extrusion],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "l_shape_extrusion_tapered.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_l_shape_revolved_area_solid(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        depth = 2.0
        width = 1.0
        thickness = 0.2

        l_shape_extrusion = ifcplus.api.geometry.add_revolved_area_solid(
            ifc4_file=ifc_file_with_one_element,
            profile=ifcplus.api.profile.add_parameterized_profile(
                ifc4_file=ifc_file_with_one_element,
                profile_class="IfcLShapeProfileDef",
                dimensions=[depth, width, thickness, None, None, None],
                check_for_duplicate=True,
            ),
            central_angle_of_curvature=np.pi / 2.0,
            center_of_curvature_in_object_xy_plane=(5.0, 5.0),
            repositioned_origin=(0.0, 0.0, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[l_shape_extrusion]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[l_shape_extrusion],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "l_shape_extrusion_revolved.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestAddBoundingBox:

    def test_add_one_bounding_box(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        bounding_box = ifcplus.api.geometry.add_bounding_box(
            ifc4_file=ifc_file_with_one_element,
            length=4.0,
            width=2.0,
            height=3.0,
            corner_coordinates=(0.0, 0.0, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[bounding_box]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Box",
            representation_type=representation_type,
            items=[bounding_box],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        ifcplus.api.placement.edit_object_placement(
            product=element,
            repositioned_origin=(2.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_bounding_box.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestAddFacetedBrep:

    def test_add_one_faceted_brep(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

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

        faceted_brep = ifcplus.api.geometry.add_faceted_brep(
            ifc4_file=ifc_file_with_one_element,
            points=points,
            triangles=triangles,
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[faceted_brep]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcShapeRepresentation",
            representation_identifier="Body",
            representation_type=representation_type,
            items=[faceted_brep],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        ifcplus.api.placement.edit_object_placement(
            product=element,
            repositioned_origin=(2.0, 1.0, 0.0),
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_faceted_brep.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestAddTopologyRepresentation:

    def test_add_one_edge(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        edge = ifcplus.api.geometry.add_edge(
            edge_start_as_vertex_point=ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=(0.0, 0.0, 1.0),
            ),
            edge_end_as_vertex_point=ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=(4.0, 0.0, 1.0),
            ),
        )

        representation_type = ifcopenshell.util.representation.guess_type(items=[edge])
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=representation_type,
            items=[edge],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_edge.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_edge_curve(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        edge_curve = ifcplus.api.geometry.add_curved_edge(
            point_of_curvature_as_vertex_point=ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=(0.0, 0.0, 0.0),
            ),
            point_of_tangency_as_vertex_point=ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=(5.0, 0.0, 5.0),
            ),
            center_of_curvature=(5.0, 0.0, 0.0),
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[edge_curve]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=representation_type,
            items=[edge_curve],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_edge_curve.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_face_surface(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

        points_of_outer_bound = [
            (0.0, 0.0, 0.0),
            (8.0, 0.0, 0.0),
            (8.0, 4.0, 0.0),
            (0.0, 4.0, 0.0),
        ]

        vertex_points_of_outer_bound = [
            ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=point_of_outer_bound,
            )
            for point_of_outer_bound in points_of_outer_bound
        ]

        face_surface = ifcplus.api.geometry.add_face_surface(
            vertex_points_of_outer_bound=vertex_points_of_outer_bound,
            vertex_points_of_inner_bounds=[],
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[face_surface]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=representation_type,
            items=[face_surface],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_face_surface.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0

    def test_add_one_face_surface_with_voids(
        self,
        ifc_file_with_one_element: ifcopenshell.file,
    ):

        element = ifc_file_with_one_element.by_type(
            type="IfcBuildingElementProxy",
            include_subtypes=False,
        )[0]

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
            ifcplus.api.geometry.add_vertex_point(
                ifc4_file=ifc_file_with_one_element,
                point_coordinates=point_of_outer_bound,
            )
            for point_of_outer_bound in points_of_outer_bound
        ]

        vertex_points_of_inner_bounds = []
        for points_of_inner_bound in points_of_inner_bounds:
            vertex_points_of_inner_bounds.append(
                [
                    ifcplus.api.geometry.add_vertex_point(
                        ifc4_file=ifc_file_with_one_element,
                        point_coordinates=point_of_inner_bound,
                    )
                    for point_of_inner_bound in points_of_inner_bound
                ]
            )

        face_surface = ifcplus.api.geometry.add_face_surface(
            vertex_points_of_outer_bound=vertex_points_of_outer_bound,
            vertex_points_of_inner_bounds=vertex_points_of_inner_bounds,
        )

        representation_type = ifcopenshell.util.representation.guess_type(
            items=[face_surface]
        )
        assert isinstance(representation_type, str)

        shape_model = ifcplus.api.geometry.add_shape_model(
            ifc4_file=ifc_file_with_one_element,
            shape_model_class="IfcTopologyRepresentation",
            representation_identifier="Reference",
            representation_type=representation_type,
            items=[face_surface],
        )
        ifcopenshell.api.geometry.assign_representation(
            file=ifc_file_with_one_element,
            product=element,
            representation=shape_model,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "one_face_surface_with_voids.ifc")
        ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc_file_with_one_element,
            file_path=output_path,
            add_annotations=True,
        )

        logger = ifcopenshell.validate.json_logger()
        ifcopenshell.validate.validate(output_path, logger, express_rules=True)
        from pprint import pprint

        pprint(logger.statements)

        assert len(logger.statements) == 0


class TestAddWall:

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
            place_object_relative_to_parent=True,
        )

        straight_wall_1 = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcWall",
            name="Wall-01",
            predefined_type=None,
        )

        # Representation, Material, Type

        # Spatail Stuff
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[straight_wall_1],
            relating_structure=site,
        )
        ifcplus.api.placement.edit_object_placement(
            product=straight_wall_1,
            place_object_relative_to_parent=True,
        )

        output_path = str(OUTPUT_DIR_FOR_GEOMETRY / "straight_walls.ifc")
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
