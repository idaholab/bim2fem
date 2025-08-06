# Copyright 2024, Battelle Energy Alliance, LLC All Rights Reserved

"""Welcome to BIM2FEM. Package for converting IFC4 files from the architectural
domain to the structural analysis domain."""


import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))


def current_time():
    return datetime.now().strftime("%H:%M:%S")
