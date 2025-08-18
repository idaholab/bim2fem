# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Welcome to INLBIM. INLBIM is a supplement to IfcOpenShell developed by Idaho
National Lab. IfcOpenShell provides a way to read and write IFCs."""


import sys
import os
from typing import Literal
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

MODEL_VIEW_DEFINITION_IFC4 = Literal[
    "IFC4Precast",
    "DesignTransferView",  # Unofficial
    "StructuralAnalysisView",  # Unofficial
    "ReferenceView_V1.2",
]

REGION = Literal["Europe", "UnitedStates"]

MATERIAL_LIBRARIES = "Europe", "UnitedStates"

SECTION_LIBRARIES = ["AISC14", "BSShapes2006", "Euro", "SJIJoists"]

RGB_STEEL = (113 / 255, 121 / 255, 126 / 255)
RGB_CONCRETE = (46 / 255, 46 / 255, 51 / 255)


def current_time():
    return datetime.now().strftime("%H:%M:%S")
