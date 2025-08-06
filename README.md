# BIM2FEM
Convert 3D architectural models of buildings to 3D finite element models for structural anaysis. 

Specifically, this programs converts IFC SPF files from the architectural coordination domain (IFC4 ReferenceView/DesignTransferView) to the structural analysis domain (IFC4 StructuralAnalysisView). IFC is an open, internaional standardized schema for Building Information Modeling (BIM) and is the input and output of this program. 

# Usage

## Launch Web App

1. Install the latest version of [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/). Then, open Docker Desktop and leave it running in the background.

<!-- 2. Clone the repository:
    ```sh
    git clone https://github.com/idaholab/bim2fem
    ``` -->

2. Clone the repository:
    ```sh
    git clone https://github.inl.gov/Digital-Engineering/ifc_deeplynx_adapter
    ```

3. Navigate to the repository:
    ```sh
    cd YourDocuments/bim2fem
    ```

4. Run the following command and wait for the process to finish. The initial startup might take a while as the operation must first fetch the pre-built containers from the internet.
    ```sh
    docker compose up --build
    ```

5. Access the locally hosted web app via http://localhost:8000/

6. To terminate hit Ctrl-C or Ctrl-D

## Example Walkthrough: Convert Revit Steel Frame Construction Model to Finite Element Model

1. Launch the Web App.

2. Select "Convert IFC to Finite Element Model".

3. Upload the SteelConstruction_RV.ifc file, which can be found in the bim2fem/test/files directory.

4. In the "Selector Query" field, specify which IfcElement classes you want to run throught the FEM converter. Let's choose some typical structural building elements. Input the following in the "Selector Query" field:
    ```sh
    IfcBeam, IfcColumn, IfcSlab, IfcWall
    ```

5. We don't need to include the spread footings in our FEM, so let's deselect all the spread footings in the model using the "Deselector Query" field. Revit has assigned the IfcElementType of "M_Footing-Rectangular:1800 x 1200 x 450mm" to all spread footings, so we can use this to select all the spread footings that we don't want to run through the converter. (Note: Revit has erroneously classified the spread footings as instances of IfcSlab. The correct classification for these elements should be IfcFooting). Input the following in the "Deselector Query" field:
    ```sh
    type = "M_Footing-Rectangular:1800 x 1200 x 450mm"
    ```

6. The building elements in this Revit file are from Euro standards, so specify "Europe" as the region. (Note: The other option for region is "UnitedStates". However, the units in the output FEM are always standard SI units: meters, kilograms, celsius, seconds). Input the following in the "Region" field:
    ```sh
    Europe
    ```

7. Click "Upload and Process". 

8. After the conversion is complete, you can download the new IFC4 StructuralAnalysisView file and/or view it in the browser. 


# OpenBIM Resources

## buildingSMART

* [buildingSMART Homepage](https://www.buildingsmart.org/)

## Industry Foundation Classes (IFC)

* [Intro to IFC](https://technical.buildingsmart.org/standards/ifc/)
* [IFC Specifications Database](https://technical.buildingsmart.org/standards/ifc/ifc-schema-specifications/)
* [IFC4 Documentation](https://standards.buildingsmart.org/IFC/RELEASE/IFC4/ADD2_TC1/HTML/)
* [IFC4x3 Documentation (more reader friendly than IFC4 Docs)](https://ifc43-docs.standards.buildingsmart.org/)
* [IFC Validation Service](https://www.buildingsmart.org/users/services/validation-service/)

## IfcOpenShell

* [IfcOpenShell Homepage](https://ifcopenshell.org/)

## IFC Editors/Viewers

* [Bonsai (formely BlenderBIM)](https://ifcopenshell.org/)
