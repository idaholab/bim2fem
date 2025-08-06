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
import inlbim.util.geometry


def main() -> int:

    start_time = time.time()  # Record the start time

    print(f"{current_time()}: Running {os.path.basename(__file__)} ...")

    horizontal_curve_A1 = inlbim.util.geometry.HorizontalCurve.from_3pt_polyline(
        p1=(10.0, 0.0, 0.0),
        p2=(10.0, 17.0, 0.0),
        p3=(20.0, 17.0, 0.0),
        radius_of_curvature=2.0,
    )
    print(horizontal_curve_A1.__repr__(), end="\n\n")

    horizontal_curve_A2 = inlbim.util.geometry.HorizontalCurve.from_PC_and_PT_and_PI(
        point_of_curvature=(10.0, 15.0, 0.0),
        point_of_intersection=(10.0, 17.0, 0.0),
        point_of_tangency=(12.0, 17.0, 0.0),
    )
    print(horizontal_curve_A2.__repr__(), end="\n\n")

    horizontal_curve_A3 = inlbim.util.geometry.HorizontalCurve.from_PC_and_PT_and_CC(
        point_of_curvature=(10.0, 15.0, 0.0),
        point_on_center_of_curvature_side=(10.0 + 2, 15.0 - 2, 0.0),
        point_of_tangency=(12.0, 17.0, 0.0),
        radius_of_curvature=2.0,
    )
    print(horizontal_curve_A3.__repr__(), end="\n\n")

    horizontal_curve_B1 = inlbim.util.geometry.HorizontalCurve.from_3pt_polyline(
        p1=(12.0, 17.0, 0.0),
        p2=(21.0, 17.0, 0.0),
        p3=(28.0, 24.0, 0.0),
        radius_of_curvature=2.0,
    )
    print(horizontal_curve_B1.__repr__(), end="\n\n")

    horizontal_curve_B2 = inlbim.util.geometry.HorizontalCurve.from_PC_and_PT_and_PI(
        point_of_curvature=(20.17157287525381, 17.0, 0.0),
        point_of_intersection=(21.0, 17.0, 0.0),
        point_of_tangency=(21.585786437626904, 17.585786437626904, 0.0),
    )
    print(horizontal_curve_B2.__repr__(), end="\n\n")

    print(f"{current_time()}: Total elapsed was {time.time() - start_time:.4f} s\n")

    return 0


if __name__ == "__main__":

    main()

    chime.success(sync=True)
