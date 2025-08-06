# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

"""Welcome to BIM2GLB. Modification of IFC to GLB conversion provided by IfcConvert."""


import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))


def current_time():
    return datetime.now().strftime("%H:%M:%S")
