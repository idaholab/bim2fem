# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""
BIM2FEM Web Interface
Flask application for non-developers users to interact with bim2fem functionality
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
import json
import ifcopenshell
import bim2fem.ifcplus.api.project
import bim2fem.bim2glb.convert_ifc_to_glb
import bim2fem.core.convert_ifc_to_fem
import bim2fem.core.recreate_fem_with_3d_body_shape_representation
from bim2fem.core.adjust_element_connectivity_of_building_fem import (
    adjust_element_connectivity_of_ifc4_sav_file,
)
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_from_directory,
    jsonify,
)


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static",
)

JOB_OPTIONS = [
    "View IFC File",
    "Convert IFC to GLB",
    "Convert IFC to Finite Element Model",
    # "Adjust Element Connectivity of Finite Element Model",
]

PATH_TO_INPUT_DIRECTORY = Path(__file__).parent / "input"
PATH_TO_OUTPUT_DIRECTORY = Path(__file__).parent / "output"
PATH_TO_METADATA_DIRECTORY = Path(__file__).parent / "metadata"

PATH_TO_INPUT_DIRECTORY.mkdir(exist_ok=True)
PATH_TO_OUTPUT_DIRECTORY.mkdir(exist_ok=True)
PATH_TO_METADATA_DIRECTORY.mkdir(exist_ok=True)


def remove_all_files(directory: Path):
    """Remove all files in a directory"""
    if not directory.exists():
        return

    for file_path in directory.glob("*"):
        if file_path.is_file():
            try:
                file_path.unlink()
                print(f"Removed: {file_path.name}")
            except Exception as e:
                print(f"Error removing {file_path.name}: {e}")


@app.route(rule="/", methods=["GET", "POST"])
def index():
    """Render Index Template"""

    # Remove previous files
    for directory in [
        PATH_TO_INPUT_DIRECTORY,
        PATH_TO_OUTPUT_DIRECTORY,
        PATH_TO_METADATA_DIRECTORY,
    ]:
        remove_all_files(directory=directory)

    # Select Job
    if request.method == "POST":
        selected_job = request.form.get(key="job")
        if selected_job == "View IFC File":
            return redirect(location=url_for(endpoint="view_ifc"))
        elif selected_job == "Convert IFC to GLB":
            return redirect(location=url_for(endpoint="convert_to_glb"))
        elif selected_job == "Convert IFC to Finite Element Model":
            # return redirect(location=url_for(endpoint="convert_to_fem"))
            return "This feature is currently broken"
        elif selected_job == "Adjust Element Connectivity of Finite Element Model":
            return "This feature is currently broken"
        else:
            return "Unknown Job"

    return render_template(
        template_name_or_list="index.html",
        jobs=JOB_OPTIONS,
    )


@app.route(rule="/convert_to_fem", methods=["GET", "POST"])
def convert_to_fem():
    if request.method == "POST":

        # Get IFC File in FileStorage
        if "ifc_file" not in request.files:
            return "No file uploaded"
        ifc_file_in_FileStorage = request.files["ifc_file"]
        if not isinstance(ifc_file_in_FileStorage.filename, str):
            return "Filename is not string"
        if ifc_file_in_FileStorage.filename == "":
            return "No selected file"

        # Get Python arguments
        element_selection_query = request.form.get("element_selection_query", "")
        element_deselection_query = request.form.get("element_deselection_query", "")
        region = request.form.get("region", "")
        snap_option = request.form.get("snap_option", "")
        if element_selection_query == "":
            element_selection_query = "IfcColumn, IfcSlab, IfcWall, IfcBeam, IfcMember"
        if element_deselection_query == "":
            element_deselection_query = None
        if region == "":
            region = "Europe"
        print(f"element_selection_query: {element_selection_query}")
        print(f"element_deselection_query: {element_deselection_query}")
        print(f"region: {region}")
        print(f"snap_option: {snap_option}")

        # Save the IFC File in FileStorage to the Input folder
        input_ifc_filename = ifc_file_in_FileStorage.filename
        input_ifc_file_path = os.path.join(PATH_TO_INPUT_DIRECTORY, input_ifc_filename)
        ifc_file_in_FileStorage.save(dst=input_ifc_file_path)

        # Process the IFC file
        ifc_source_file = ifcopenshell.open(input_ifc_file_path)
        assert isinstance(ifc_source_file, ifcopenshell.file)
        assert region == "Europe" or region == "UnitedStates"
        ifc4_sav_file = bim2fem.core.convert_ifc_to_fem.convert_ifc_to_fem(
            ifc4_source_file=ifc_source_file,
            element_selection_query=element_selection_query,
            element_deselection_query=element_deselection_query,
            region=region,
        )

        # Adjust Element Connectivity
        if snap_option == "Yes":
            ifc4_sav_file = adjust_element_connectivity_of_ifc4_sav_file(
                ifc4_sav_file=ifc4_sav_file,
                execute_snap_frame_members=True,
                execute_snap_floor_beam_systems=True,
                execute_snap_walls_to_slabs=True,
                execute_snap_walls_to_walls=True,
                execute_snap_beams_to_walls=False,
            )

        # Save the New IFC file to the Output Directory
        output_ifc_filename = input_ifc_filename.replace(
            ".ifc",
            "_converted_to_SAV.ifc",
        )
        output_ifc_file_path = os.path.join(
            PATH_TO_OUTPUT_DIRECTORY,
            output_ifc_filename,
        )
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=ifc4_sav_file,
            file_path=output_ifc_file_path,
            add_annotations=False,
        )

        # Redirect to Truncation Complete page
        return redirect(
            location=url_for(
                endpoint="convert_to_fem_done",
                input_ifc_filename=input_ifc_filename,
                output_ifc_filename=output_ifc_filename,
            )
        )

    return render_template(
        template_name_or_list="convert_to_fem.html",
    )


@app.route(
    "/convert_to_fem_done/<input_ifc_filename>/<output_ifc_filename>",
    methods=["GET", "POST"],
)
def convert_to_fem_done(
    input_ifc_filename: str,
    output_ifc_filename: str,
):

    if request.method == "POST":

        # Get the file path for the IFC4 SAV file
        ifc4_sav_file_path = os.path.abspath(
            os.path.join(
                PATH_TO_OUTPUT_DIRECTORY,
                output_ifc_filename,
            )
        )

        # Open the IFC file as an ifcopenshell.file object
        ifc4_sav_file = ifcopenshell.open(path=ifc4_sav_file_path)
        if not isinstance(ifc4_sav_file, ifcopenshell.file):
            return "IFC file could not be opened by IfcOpenShell"

        # Recreate the IFC4 SAV file with Body Shape Representations
        recreated_ifc4_sav_file = bim2fem.core.recreate_fem_with_3d_body_shape_representation.recreate_ifc4_sav_with_3d_body_shape_representation(
            ifc4_sav_file=ifc4_sav_file,
            view_option="Wireframe_3D",
        )

        # Get the file path for the IFC4 SAV file recreated with Body Shape
        # Representations
        recreated_ifc4_sav_file_path = os.path.abspath(
            os.path.join(
                PATH_TO_OUTPUT_DIRECTORY,
                output_ifc_filename.replace(
                    ".ifc",
                    "_recreated_with_body_representations.ifc",
                ),
            )
        )

        # Write the Recreated IFC4 SAV file to disk
        bim2fem.ifcplus.api.project.write_to_ifc_spf(
            ifc4_file=recreated_ifc4_sav_file,
            file_path=recreated_ifc4_sav_file_path,
            add_annotations=False,
        )

        # Get file path for the GLB
        output_glb_filename = output_ifc_filename.replace(".ifc", ".glb")
        output_glb_file_path = os.path.abspath(
            os.path.join(
                PATH_TO_OUTPUT_DIRECTORY,
                output_glb_filename,
            )
        )

        # Convert the IFC to GLB
        output_glb_file_path = bim2fem.bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
            ifc_input_filename=recreated_ifc4_sav_file_path,
            glb_output_filename=output_glb_file_path,
            show_global_coordinate_system_axes=False,
            delete_intermediate_glb_file=True,
            store_metadata_in_glb_nodes=True,
        )

        # Create JSON Metadata file from the IFC
        metadata_file_path = create_metadata_json_file_from_ifc(
            ifc4_file=recreated_ifc4_sav_file
        )
        metadata_filename = os.path.split(metadata_file_path)[1]

        print(f"output_glb_filename: {output_glb_filename}")
        print(f"metadata_filename: {metadata_filename}")

        return redirect(
            location=url_for(
                endpoint="viewer_for_glb_from_ifc",
                filename=output_glb_filename,
                metadata_filename=metadata_filename,
            )
        )

    return render_template(
        template_name_or_list="convert_to_fem_done.html",
        input_ifc_filename=input_ifc_filename,
        output_ifc_filename=output_ifc_filename,
    )


@app.route(rule="/convert_to_glb", methods=["GET", "POST"])
def convert_to_glb():
    if request.method == "POST":

        # Get IFC File in FileStorage
        if "ifc_file" not in request.files:
            return "No file uploaded"
        ifc_file_in_FileStorage = request.files["ifc_file"]
        if not isinstance(ifc_file_in_FileStorage.filename, str):
            return "Filename is not string"
        if ifc_file_in_FileStorage.filename == "":
            return "No selected file"

        # Get the input file path for the IFC
        input_ifc_filename = ifc_file_in_FileStorage.filename
        input_ifc_file_path = os.path.abspath(
            os.path.join(PATH_TO_INPUT_DIRECTORY, input_ifc_filename)
        )

        # Save the IFC to the input folder
        ifc_file_in_FileStorage.save(dst=input_ifc_file_path)

        # Open the IFC file as an ifcopenshell.file object
        ifcopenshell_file = ifcopenshell.open(path=input_ifc_file_path)
        if not isinstance(ifcopenshell_file, ifcopenshell.file):
            return "IFC file could not be opened by IfcOpenShell"

        # Get output file path for the GLB
        output_glb_filename = input_ifc_filename.replace(".ifc", ".glb")
        output_glb_file_path = os.path.abspath(
            os.path.join(PATH_TO_OUTPUT_DIRECTORY, output_glb_filename)
        )

        # Convert the IFC to GLB
        output_glb_file_path = bim2fem.bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
            ifc_input_filename=input_ifc_file_path,
            glb_output_filename=output_glb_file_path,
            show_global_coordinate_system_axes=False,
            delete_intermediate_glb_file=True,
            store_metadata_in_glb_nodes=True,
        )

        # Redirect to Process Completion page
        return redirect(
            location=url_for(
                endpoint="convert_to_glb_done",
                input_ifc_filename=input_ifc_filename,
                output_glb_filename=output_glb_filename,
            )
        )

    return render_template(
        template_name_or_list="convert_to_glb.html",
    )


@app.route(
    "/convert_to_glb_done/<input_ifc_filename>/<output_glb_filename>",
    methods=["GET", "POST"],
)
def convert_to_glb_done(
    input_ifc_filename: str,
    output_glb_filename: str,
):
    if request.method == "POST":

        # Get the input file path for the IFC
        input_ifc_file_path = os.path.abspath(
            os.path.join(PATH_TO_INPUT_DIRECTORY, input_ifc_filename)
        )

        # Open the IFC file as an ifcopenshell.file object
        ifcopenshell_file = ifcopenshell.open(path=input_ifc_file_path)
        if not isinstance(ifcopenshell_file, ifcopenshell.file):
            return "IFC file could not be opened by IfcOpenShell"

        # Create JSON Metadata file from the IFC
        metadata_file_path = create_metadata_json_file_from_ifc(
            ifc4_file=ifcopenshell_file
        )
        metadata_filename = os.path.split(metadata_file_path)[1]

        print(f"output_glb_filename: {output_glb_filename}")
        print(f"metadata_filename: {metadata_filename}")

        return redirect(
            location=url_for(
                endpoint="viewer_for_glb_from_ifc",
                filename=output_glb_filename,
                metadata_filename=metadata_filename,
            )
        )

    return render_template(
        template_name_or_list="convert_to_glb_done.html",
        input_ifc_filename=input_ifc_filename,
        output_glb_filename=output_glb_filename,
    )


@app.route("/<directory>/<filename>")
def download_file(
    directory: str,
    filename: str,
):
    return send_from_directory(
        directory=directory,
        path=filename,
        as_attachment=True,
    )


def create_metadata_json_file_from_ifc(
    ifc4_file: ifcopenshell.file,
) -> str:

    metadata_file_path = os.path.abspath(
        os.path.join(PATH_TO_METADATA_DIRECTORY, "metadata.json")
    )
    # metadata_file_path = os.path.join("metadata", "metadata.json")

    ifc_products = ifc4_file.by_type(type="IfcProduct", include_subtypes=True)

    objects = []
    for ifc_product in ifc_products:
        # if ifc_product.is_a() == "IfcOpeningElement":
        #     continue
        objects.append(
            {
                "class": ifc_product.is_a(),
                "globalid": ifc_product.GlobalId,
                "name": ifc_product.Name,
                "description": ifc_product.Description,
                "objecttype": ifc_product.ObjectType,
                "requirement": "None",
            },
        )

    data = {"objects": objects}

    with open(file=metadata_file_path, mode="w") as json_file:
        json.dump(data, json_file, indent=4)

    return metadata_file_path


@app.route("/view_ifc", methods=["GET", "POST"])
def view_ifc():
    if request.method == "POST":

        # Get IFC File in FileStorage
        if "ifc_file" not in request.files:
            return "No file uploaded"
        ifc_file_in_FileStorage = request.files["ifc_file"]
        if not isinstance(ifc_file_in_FileStorage.filename, str):
            return "Filename is not string"
        if ifc_file_in_FileStorage.filename == "":
            return "No selected file"

        # Get the input file path for the IFC
        input_ifc_filename = ifc_file_in_FileStorage.filename
        input_ifc_file_path = os.path.abspath(
            os.path.join(PATH_TO_INPUT_DIRECTORY, input_ifc_filename)
        )

        # Save the IFC to the input folder
        ifc_file_in_FileStorage.save(dst=input_ifc_file_path)

        # Open the IFC file as an ifcopenshell.file object
        ifcopenshell_file = ifcopenshell.open(path=input_ifc_file_path)
        if not isinstance(ifcopenshell_file, ifcopenshell.file):
            return "IFC file could not be opened by IfcOpenShell"

        # Get output file path for the GLB
        output_glb_filename = input_ifc_filename.replace(".ifc", ".glb")
        output_glb_file_path = os.path.abspath(
            os.path.join(PATH_TO_OUTPUT_DIRECTORY, output_glb_filename)
        )

        # Convert the IFC to GLB
        output_glb_file_path = bim2fem.bim2glb.convert_ifc_to_glb.convert_ifc_to_glb(
            ifc_input_filename=input_ifc_file_path,
            glb_output_filename=output_glb_file_path,
            show_global_coordinate_system_axes=False,
            delete_intermediate_glb_file=True,
            store_metadata_in_glb_nodes=True,
        )

        # Create JSON Metadata file from the IFC
        metadata_file_path = create_metadata_json_file_from_ifc(
            ifc4_file=ifcopenshell_file
        )
        metadata_filename = os.path.split(metadata_file_path)[1]

        print(f"output_glb_filename: {output_glb_filename}")
        print(f"metadata_filename: {metadata_filename}")

        return redirect(
            location=url_for(
                endpoint="viewer_for_glb_from_ifc",
                filename=output_glb_filename,
                metadata_filename=metadata_filename,
            )
        )

    return render_template("view_ifc.html")


@app.route("/viewer_for_glb_from_ifc/<filename>/<metadata_filename>")
def viewer_for_glb_from_ifc(filename, metadata_filename):
    return render_template(
        "viewer_for_glb_from_ifc.html",
        glb_filename=filename,
        metadata_filename=metadata_filename,
    )


@app.route("/output/<path:filename>")
def outputted_file(filename):
    return send_from_directory("output", filename)


@app.route("/metadata/<metadata_filename>")
def get_metadata(metadata_filename):
    """Serve the requested metadata JSON file."""
    metadata_path = os.path.join(PATH_TO_METADATA_DIRECTORY, metadata_filename)
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        return jsonify(metadata)
    else:
        return jsonify({"error": "Metadata file not found"}), 404


def main():
    """Run the Flask development server"""
    port = int(os.environ.get("PORT", 5000))

    # For casual users via launcher, default to production mode
    # Developers can set FLASK_DEBUG=true manually
    debug = os.environ.get("FLASK_DEBUG", "False").lower() == "true"

    print("=" * 50)
    print(f"BIM2FEM Web Interface")
    print(f"Navigate to: http://localhost:{port}")
    print(f"Debug mode: {debug}")
    print("Press Ctrl+C to stop")
    print("=" * 50)

    app.run(
        host="127.0.0.1",  # More secure than 0.0.0.0 for local use
        port=port,
        debug=debug,
        use_reloader=debug,
    )


if __name__ == "__main__":
    main()
