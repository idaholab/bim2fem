# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from pathlib import Path

TEST_DIR = Path(__file__).parent
FIXTURES_DIR = TEST_DIR / "fixtures"
INPUT_DIR = FIXTURES_DIR / "input"
EXPECTED_DIR = FIXTURES_DIR / "expected"

OUTPUT_DIR = TEST_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_IFCPLUS = OUTPUT_DIR / "ifcplus"
OUTPUT_DIR_FOR_IFCPLUS.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_GEOMETRY = OUTPUT_DIR_FOR_IFCPLUS / "geometry"
OUTPUT_DIR_FOR_GEOMETRY.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT = OUTPUT_DIR_FOR_IFCPLUS / "distribution_element"
OUTPUT_DIR_FOR_DISTRIBUTION_ELEMENT.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_SYSTEM = OUTPUT_DIR_FOR_IFCPLUS / "system"
OUTPUT_DIR_FOR_SYSTEM.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_NUCLEAR = OUTPUT_DIR_FOR_IFCPLUS / "nuclear"
OUTPUT_DIR_FOR_NUCLEAR.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_BUILT_ELEMENT = OUTPUT_DIR_FOR_IFCPLUS / "built_element"
OUTPUT_DIR_FOR_BUILT_ELEMENT.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_STRUCTURAL = OUTPUT_DIR_FOR_IFCPLUS / "structural"
OUTPUT_DIR_FOR_STRUCTURAL.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_CORE = OUTPUT_DIR / "core"
OUTPUT_DIR_FOR_CORE.mkdir(exist_ok=True)

OUTPUT_DIR_FOR_CONVERT = OUTPUT_DIR_FOR_CORE / "convert"
OUTPUT_DIR_FOR_CONVERT.mkdir(exist_ok=True)
