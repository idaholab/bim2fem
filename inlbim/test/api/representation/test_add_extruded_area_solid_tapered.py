# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

import os
import sys


# Insert parent directory of package to path
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")),
)


from inlbim import current_time
import time
import chime
import inlbim.api.file
import ifcopenshell
import ifcopenshell.api.root
import ifcopenshell.api.aggregate
import inlbim.api.geometry
import inlbim.api.style
import ifcopenshell.api.spatial
import inlbim.api.profile
import ifcopenshell.api.geometry
import inlbim.api.representation
import inlbim.api.spatial_element


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    # Add IFC File
    ifc4_file = inlbim.api.file.create_ifc4_file(
        model_view_definition="ReferenceView_V1.2",
        precision=1e-4,
    )

    # Get Project
    project = ifc4_file.by_type(type="IfcProject", include_subtypes=False)[0]

    # Add Site
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
    inlbim.api.geometry.edit_object_placement(
        product=site,
        place_object_relative_to_parent=True,
    )

    # Add Building
    building = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuilding",
        name="Building-01",
    )
    ifcopenshell.api.aggregate.assign_object(
        file=ifc4_file,
        products=[building],
        relating_object=site,
    )
    inlbim.api.geometry.edit_object_placement(
        product=building,
        place_object_relative_to_parent=True,
    )

    # Add Space
    space = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=10.0,
        width=4.0,
        height=4.0,
        repositioned_origin=(1.0, 1.0, 0.0),
        name="Space-01",
        spatial_element=building,
        should_transform_relative_to_parent=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=space,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
    )

    # Create Element
    element = ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcBuildingElementProxy",
        name="Element-01",
        predefined_type=None,
    )
    ifcopenshell.api.spatial.assign_container(
        file=ifc4_file,
        products=[element],
        relating_structure=space,
    )
    inlbim.api.geometry.edit_object_placement(
        product=element,
        place_object_relative_to_parent=True,
    )

    # Add and Assign Representation
    representation_item = inlbim.api.representation.add_extruded_area_solid_tapered(
        ifc4_file=ifc4_file,
        profile_start=inlbim.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[0.25, 0.05],
        ),
        extrusion_depth=3.0,
        profile_end=inlbim.api.profile.add_parameterized_profile(
            ifc4_file=ifc4_file,
            profile_class="IfcCircleHollowProfileDef",
            dimensions=[0.10, 0.05],
        ),
    )
    shape_model = inlbim.api.representation.add_shape_model(
        ifc4_file=ifc4_file,
        shape_model_class="IfcShapeRepresentation",
        representation_identifier="Body",
        representation_type="AdvancedSweptSolid",
        context_type="Model",
        target_view="MODEL_VIEW",
        items=[representation_item],
    )
    ifcopenshell.api.geometry.assign_representation(
        file=ifc4_file,
        product=element,
        representation=shape_model,
    )

    # Edit Element Placement
    inlbim.api.geometry.edit_object_placement(
        product=element,
        repositioned_origin=(1.0, 1.0, 0.0),
        place_object_relative_to_parent=True,
    )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_add_extruded_area_solid_tapered.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
