# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import os
import json
import re

import ifcopenshell
import ifcopenshell.api.project
import ifcopenshell.api.owner
import ifcopenshell.api.root
import ifcopenshell.api.context
import ifcopenshell.api.unit
import ifcopenshell.api.attribute
import inlbim.api.unit
import ifcopenshell.util.selector
from inlbim import MODEL_VIEW_DEFINITION_IFC4


def create_ifc4_file(
    identification_of_user: str = "LPARTEE",
    family_name_of_user: str = "Partee",
    given_name_of_user: str = "Leeable",
    name_of_organisation: str = "Architects Without Ballpens",
    identification_of_organisation: str = "AWB",
    name_of_project: str = "My Project",
    model_view_definition: MODEL_VIEW_DEFINITION_IFC4 = "DesignTransferView",
    precision: float = 1e-5,
):
    """Create New IFC4 file with default representation contexts and  units for a
    project with metric units

    Args:
        identification_of_user (str, optional): _description_. Defaults to "LPARTEE".
        family_name_of_user (str, optional): _description_. Defaults to "Partee".
        given_name_of_user (str, optional): _description_. Defaults to "Leeable".
        name_of_organisation (str, optional): _description_. Defaults to "Architects Without Ballpens".
        identification_of_organisation (str, optional): _description_. Defaults to "AWB".
        name_of_project (str, optional): _description_. Defaults to "My Project".
        precision (float, optional): _description_. Defaults to 1e-5.

    Returns:
        _type_: _description_
    """

    # Initialize IFC4 File
    ifc4_file = ifcopenshell.api.project.create_file(version="IFC4")

    # FileDescription in Header
    ifc4_file.wrapped_data.header.file_description.description = (
        f"ViewDefinition [{model_view_definition}]",
    )

    # FileName in Header
    ifc4_file.wrapped_data.header.file_name.author = (
        f"{given_name_of_user} {family_name_of_user}",
    )
    ifc4_file.wrapped_data.header.file_name.organization = (name_of_organisation,)
    ifc4_file.wrapped_data.header.file_name.originating_system = (
        f"IfcOpenShell - IfcOpenShell - {ifcopenshell.version}"
    )
    ifc4_file.wrapped_data.header.file_name.authorization = "none"

    # Set Person and Organization for OwnerHistory
    person = ifcopenshell.api.owner.add_person(
        file=ifc4_file,
        identification=f"{identification_of_user}",
        family_name=family_name_of_user,
        given_name=given_name_of_user,
    )
    organisation = ifcopenshell.api.owner.add_organisation(
        file=ifc4_file,
        identification=identification_of_organisation,
        name=name_of_organisation,
    )
    ifcopenshell.api.owner.add_person_and_organisation(
        file=ifc4_file,
        person=person,
        organisation=organisation,
    )

    # Define authoring application
    ifcopenshell.api.owner.add_application(file=ifc4_file)

    # Create the Root entity (aka IfcProject)
    ifcopenshell.api.root.create_entity(
        file=ifc4_file,
        ifc_class="IfcProject",
        name=name_of_project,
    )

    # Define the context for 3D Modeling
    model3d_context = ifcopenshell.api.context.add_context(
        file=ifc4_file,
        context_type="Model",
    )
    ifcopenshell.api.attribute.edit_attributes(
        file=ifc4_file,
        product=model3d_context,
        attributes={"Precision": precision},
    )

    # Add subcontext for Body representations in the 3D modeling context
    ifcopenshell.api.context.add_context(
        file=ifc4_file,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model3d_context,
    )

    # Add basic SI Units
    length = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="LENGTHUNIT", si_unit_name="METRE"
    )
    area = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="AREAUNIT", si_unit_name="SQUARE_METRE"
    )
    volume = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="VOLUMEUNIT", si_unit_name="CUBIC_METRE"
    )
    mass = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="MASSUNIT", si_unit_name="GRAM", prefix="KILO"
    )
    force = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="FORCEUNIT", si_unit_name="NEWTON"
    )
    angle = inlbim.api.unit.add_si_unit(
        ifc4_file=ifc4_file, si_unit_type="PLANEANGLEUNIT", si_unit_name="RADIAN"
    )
    mass_density = inlbim.api.unit.add_derived_unit(
        ifc4_file=ifc4_file, unit_type="MASSDENSITYUNIT"
    )
    assert isinstance(mass_density, ifcopenshell.entity_instance)
    modulus_of_elasticity = inlbim.api.unit.add_derived_unit(
        ifc4_file=ifc4_file, unit_type="MODULUSOFELASTICITYUNIT"
    )
    assert isinstance(modulus_of_elasticity, ifcopenshell.entity_instance)
    ifcopenshell.api.unit.assign_unit(
        file=ifc4_file,
        units=[
            length,
            area,
            volume,
            mass,
            force,
            angle,
            mass_density,
            modulus_of_elasticity,
        ],
    )

    return ifc4_file


def annotate_ifc_spf(
    file_path: str | os.PathLike,
):
    """Annotate IFC-SPF File"""

    ifc4_file = ifcopenshell.open(path=file_path)
    assert isinstance(ifc4_file, ifcopenshell.file)

    json_filenames = [
        "IfcElement_IFC4.json",
        "IfcElementType_IFC4.json",
        "IfcGroup_IFC4.json",
        # "IfcMaterialDefinition_IFC4.json",
        "IfcParameterizedProfileDef_IFC4.json",
        "IfcPositioningElement_IFC4.json",
        "IfcSpatialElement_IFC4.json",
        "IfcStructural_IFC4.json",
    ]

    ifc_entities = {}
    for json_filename in json_filenames:
        json_file_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "schema", json_filename)
        )
        json_dict = json.load(open(json_file_path))
        ifc_entities[json_filename] = {}
        for name_of_ifc_entity in list(json_dict.keys()):
            ifc_entities[json_filename][name_of_ifc_entity.upper()] = name_of_ifc_entity

    original_lines = open(file=file_path, mode="r").readlines()
    with open(file=file_path, mode="w") as f:
        for line in original_lines:
            if "HEADER;" in line:
                f.write(
                    "".join(
                        [
                            "\n/* NOTE standard header information ",
                            "according to ISO 10303-21 ",
                            "----------------- */\n",
                        ]
                    )
                )
                f.write(line)
            elif "FILE_DESCRIPTION((" in line:
                f.write(f"\n{line}")
            elif "FILE_NAME(" in line:
                name = ifc4_file.wrapped_data.header.file_name.name
                time_stamp = ifc4_file.wrapped_data.header.file_name.time_stamp
                author = ifc4_file.wrapped_data.header.file_name.author
                organization = ifc4_file.wrapped_data.header.file_name.organization
                preprocessor_ver = (
                    ifc4_file.wrapped_data.header.file_name.preprocessor_version
                )
                originating_system = (
                    ifc4_file.wrapped_data.header.file_name.originating_system
                )
                authorization = ifc4_file.wrapped_data.header.file_name.authorization
                f.write(
                    "".join(
                        [
                            "\nFILE_NAME(\n",
                            f"\t/* name */ '{name}',\n",
                            f"\t/* time_stamp */ '{time_stamp}',\n",
                            f"\t/* author */ ('{author[0]}'),\n",
                            f"\t/* organization */ ('{organization[0]}'),\n",
                            f"\t/* preprocessor_version */ '{preprocessor_ver}',\n",
                            f"\t/* originating_system */ '{originating_system}',\n",
                            f"\t/* authorization */ '{authorization}');\n",
                        ]
                    )
                )
            elif "FILE_SCHEMA((" in line:
                f.write(f"\n{line}")
            elif "DATA;" in line:
                f.write(f"\n{line}")
            elif "ENDSEC;" in line:
                f.write(f"\n{line}")
            elif "END-ISO-10303-21;" in line:
                f.write(f"\n{line}")
            elif "IFCPERSON(" in line:
                f.write("\n/* Person and Organization */\n")
                f.write(line)
            # elif "IFCOWNERHISTORY(" in line:
            #     f.write("\n/* Owner history */\n")
            #     f.write(line)
            # elif "IFCUNITASSIGNMENT(" in line:
            #     f.write("\n/* Global unit definitions */\n")
            #     f.write(line)
            elif "IFCPROJECT(" in line:
                f.write("\n/* Project, representation contexts, and Units */\n")
                f.write(line)
            elif "IFCRELDECLARES(" in line:
                f.write("\n/* Declarations on Project */\n")
                f.write(line)
            elif "IFCRELAGGREGATES(" in line:
                f.write("\n/* Aggregation Relationship */\n")
                f.write(line)
            elif "IFCRELCONTAINEDINSPATIALSTRUCTURE(" in line:
                f.write("\n/* Spatial Structure Containment */\n")
                f.write(line)
            elif "IFCRELASSIGNSTOGROUP(" in line:
                f.write("\n/* Assignments to Group */\n")
                f.write(line)
            # elif "IFCRELASSOCIATESMATERIAL(" in line:
            #     f.write("\n/* Material Relationship */\n")
            #     f.write(line)
            # elif "IFCRELDEFINESBYTYPE(" in line:
            #     f.write("\n/* Type Relationship */\n")
            #     f.write(line)
            elif "IFCSURFACESTYLE(" in line:
                f.write("\n/* IfcSurfaceStyle */\n")
                f.write(line)
            elif "IFCMATERIAL(" in line:
                f.write("\n/* IfcMaterial */\n")
                f.write(line)
            elif "IFCMATERIALLAYERSET(" in line:
                f.write("\n/* IfcMaterialLayerSet */\n")
                f.write(line)
            elif "IFCMATERIALPROFILESET(" in line:
                f.write("\n/* IfcMaterialProfileSet */\n")
                f.write(line)
            elif "IFCDISTRIBUTIONPORT(" in line:
                f.write("\n/* Port */\n")
                f.write(line)
            # elif "IFCRELNESTS(" in line:
            #     f.write("\n/* Nest Relationship */\n")
            #     f.write(line)
            elif "IFCRELASSIGNSTOPRODUCT(" in line:
                f.write("\n/* Product Assignment */\n")
                f.write(line)

            else:
                line_contains_ifc_class = line[0] == "#"
                if line_contains_ifc_class:
                    line_with_no_spaces = line.replace(" ", "")
                    ifc_class_from_line = re.split(r"[#(=]", line_with_no_spaces)[2]
                    for json_filename in json_filenames:
                        ifc_class_from_json = ifc_entities[json_filename].get(
                            ifc_class_from_line, None
                        )
                        if isinstance(ifc_class_from_json, str):
                            f.write(f"\n/* {ifc_class_from_json} */\n")
                            break
                    f.write(line)
                else:
                    f.write(line)


def write_to_ifc_spf(
    ifc4_file: ifcopenshell.file,
    file_path: str,
    add_annotations: bool = False,
) -> str:
    """Write ifcopenshell.file to IFC4-SPF File with option to add annotations"""

    filename = os.path.basename(file_path)

    ifc4_file.wrapped_data.header.file_name.name = filename

    ifc4_file.write(file_path)

    if add_annotations:
        annotate_ifc_spf(file_path=file_path)

    return file_path


def filter_out_elements(
    ifc4_file: ifcopenshell.file,
    deselection_query: str,
    selection_query: str = ",".join(
        [
            "IfcColumn",
            "IfcSlab",
            "IfcWall",
            "IfcBeam",
            "IfcMember",
            "IfcElementAssembly",
            "IfcOpeningElement",
        ]
    ),
) -> ifcopenshell.file:

    all_elements = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query="IfcElement",
        elements=None,
    )

    selected_elements = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query=selection_query,
        elements=all_elements,
    )

    deselected_elements = ifcopenshell.util.selector.filter_elements(
        ifc_file=ifc4_file,
        query=deselection_query,
        elements=all_elements,
    )

    elements_slated_for_removal = all_elements.difference(selected_elements).union(
        deselected_elements
    )

    for element_slated_for_removal in elements_slated_for_removal:
        ifcopenshell.api.root.remove_product(
            file=ifc4_file,
            product=element_slated_for_removal,
        )

    return ifc4_file
