# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

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
import inlbim.api.spatial_element
import inlbim.api.material
import inlbim.api.profile
import inlbim.api.structural
import ifcopenshell.api.spatial


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

    # Create Space
    space = inlbim.api.spatial_element.create_rectangular_solid_space(
        ifc4_file=ifc4_file,
        length=5.25,
        width=2.0,
        height=1.0,
        repositioned_origin=(0.0, 0.0, 0.0),
        name="Space-01",
        spatial_element=building,
        should_transform_relative_to_parent=True,
    )
    inlbim.api.style.assign_color_to_element(
        element=space,
        rgb_triplet=inlbim.api.style.generate_random_rgb(),
        transparency=0.1,
    )

    # Add StructuralAnalysisModel
    structural_analysis_model = inlbim.api.structural.add_structural_analysis_model(
        ifc4_file=ifc4_file,
        name="SA Model 01",
    )

    # Geometry of Elements
    elements_information = [
        {
            "name": "Horizontal L-Shape",
            "p1": (0.0, 0.0, 0.0),
            "p2": (0.0, 2.0, 0.0),
            "p3": (0.0, 0.0, 1.0),
            "profile_name": "L150X100X14",
            "material_name": "S355",
        },
        {
            "name": "Raised L-Shape",
            "p1": (0.0, 0.0, 0.5),
            "p2": (0.25, 2.0, 1.0),
            "p3": (0.25, 0.0, 1.0),
            "profile_name": "L150X100X14",
            "material_name": "S355",
        },
        {
            "name": "Horizontal Hollow Rectangle",
            "p1": (1.0, 0.0, 0.0),
            "p2": (1.0, 2.0, 0.0),
            "p3": (1.0, 0.0, 1.0),
            "profile_name": "TUBO400X200X35",
            "material_name": "S355",
        },
        {
            "name": "Raised Hollow Rectangle",
            "p1": (1.0, 0.0, 0.5),
            "p2": (1.25, 2.0, 1.0),
            "p3": (1.25, 0.0, 1.0),
            "profile_name": "TUBO400X200X35",
            "material_name": "S355",
        },
        {
            "name": "Horizontal C-Shape",
            "p1": (2.0, 0.0, 0.0),
            "p2": (2.0, 2.0, 0.0),
            "p3": (2.0, 0.0, 1.0),
            "profile_name": "UPN400",
            "material_name": "S355",
        },
        {
            "name": "Raised C-Shape",
            "p1": (2.0, 0.0, 0.5),
            "p2": (2.25, 2.0, 1.0),
            "p3": (2.25, 0.0, 1.0),
            "profile_name": "UPN400",
            "material_name": "S355",
        },
        {
            "name": "Horizontal I-Shape",
            "p1": (3.0, 0.0, 0.0),
            "p2": (3.0, 2.0, 0.0),
            "p3": (3.0, 0.0, 1.0),
            "profile_name": "IPE750X210",
            "material_name": "S355",
        },
        {
            "name": "Raised I-Shape",
            "p1": (3.0, 0.0, 0.5),
            "p2": (3.25, 2.0, 1.0),
            "p3": (3.25, 0.0, 1.0),
            "profile_name": "IPE750X210",
            "material_name": "S355",
        },
        {
            "name": "Horizontal Hollow Circle",
            "p1": (4.0, 0.0, 0.0),
            "p2": (4.0, 2.0, 0.0),
            "p3": (4.0, 0.0, 1.0),
            "profile_name": "TUBO-D419X7.1",
            "material_name": "S355",
        },
        {
            "name": "Raised Hollow Circle",
            "p1": (4.0, 0.0, 0.5),
            "p2": (4.25, 2.0, 1.0),
            "p3": (4.25, 0.0, 1.0),
            "profile_name": "TUBO-D419X7.1",
            "material_name": "S355",
        },
        {
            "name": "Horizontal T-Shape",
            "p1": (5.0, 0.0, 0.0),
            "p2": (5.0, 2.0, 0.0),
            "p3": (5.0, 0.0, 1.0),
            "profile_name": "T-HE600M/.65/",
            "material_name": "S355",
        },
        {
            "name": "Raised T-Shape",
            "p1": (5.0, 0.0, 0.5),
            "p2": (5.25, 2.0, 1.0),
            "p3": (5.25, 0.0, 1.0),
            "profile_name": "T-HE600M/.65/",
            "material_name": "S355",
        },
    ]

    # Create Elements
    for element_information in elements_information:

        # Get Material
        material = inlbim.api.material.add_material_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            material_name=element_information["material_name"],
            check_for_duplicate=True,
        )
        assert isinstance(material, ifcopenshell.entity_instance)

        # Get Profile
        profile_def = inlbim.api.profile.add_profile_from_standard_library(
            ifc4_file=ifc4_file,
            region="Europe",
            profile_name=element_information["profile_name"],
        )
        assert isinstance(profile_def, ifcopenshell.entity_instance)

        # Create corresponding product
        beam = ifcopenshell.api.root.create_entity(
            file=ifc4_file,
            ifc_class="IfcBeam",
            name=element_information["name"],
        )
        ifcopenshell.api.spatial.assign_container(
            file=ifc4_file,
            products=[beam],
            relating_structure=space,
        )

        # Create StructuralItem
        inlbim.api.structural.create_3pt_structural_curve_member(
            p1=element_information["p1"],
            p2=element_information["p2"],
            p3=element_information["p3"],
            profile_def=profile_def,
            material=material,
            structural_analysis_model=structural_analysis_model,
            corresponding_product=beam,
        )

    # Write IFC file
    inlbim.api.file.write_to_ifc_spf(
        ifc4_file=ifc4_file,
        file_path=os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "test_create_3pt_structural_curve_member.ifc",
            )
        ),
        add_annotations=True,
    )

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
