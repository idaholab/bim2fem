# Copyright 2025, Battelle Energy Alliance, LLC All Rights Reserved

"""Module to adjust IfcStructuralMember connectivity in IFC4 StructuralAnalysisView
Files."""


import ifcopenshell

from bim2fem.helpers.snap_frame_members import snap_frame_members
from bim2fem.helpers.snap_floor_beam_systems import snap_floor_beam_systems
from bim2fem.helpers.snap_beams_to_walls import snap_beams_to_walls
from bim2fem.helpers.snap_walls_to_slabs import snap_walls_to_slabs
from bim2fem.helpers.snap_walls_to_walls import (
    snap_walls_to_perpendicular_walls,
)
import inlbim.api.structural


def adjust_element_connectivity_of_ifc4_sav_file(
    ifc4_sav_file: ifcopenshell.file,
    execute_snap_frame_members: bool = False,
    execute_snap_floor_beam_systems: bool = False,
    execute_snap_walls_to_slabs: bool = False,
    execute_snap_walls_to_walls: bool = False,
    execute_snap_beams_to_walls: bool = False,
) -> ifcopenshell.file:

    if execute_snap_frame_members:
        ifc4_sav_file = snap_frame_members(
            ifc4_sav_file=ifc4_sav_file,
        )
        inlbim.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_sav_file
        )

    if execute_snap_floor_beam_systems:
        ifc4_sav_file = snap_floor_beam_systems(
            ifc4_sav_file=ifc4_sav_file,
        )
        inlbim.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_sav_file
        )

    if execute_snap_walls_to_slabs:
        ifc4_sav_file = snap_walls_to_slabs(
            ifc4_sav_file=ifc4_sav_file,
        )
        inlbim.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_sav_file
        )

    if execute_snap_walls_to_walls:
        ifc4_sav_file = snap_walls_to_perpendicular_walls(
            ifc4_sav_file=ifc4_sav_file,
        )
        inlbim.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_sav_file
        )

    if execute_snap_beams_to_walls:
        ifc4_sav_file = snap_beams_to_walls(
            ifc4_sav_file=ifc4_sav_file,
        )
        inlbim.api.structural.merge_all_coincident_structural_point_connections(
            ifc4sav_file=ifc4_sav_file
        )

    return ifc4_sav_file
