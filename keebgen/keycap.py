from abc import abstractmethod
import numpy as np
import solid as sl

from .geometry_base import Solid, Hull
from . import transform_utils as utils

# when adding new keycaps, they should be oriented so the mounting feature is aligned with the Z axis
# the bottom face should be offset from the XY plane by the same distance that they would be offset from
# a mounting plate if they were plate mounted switches

class OEM(Solid):
    def __init__(self, r, u=1):
        super(OEM, self).__init__()
        key_pitch = 19.0 # width between keys on standard board

        vertical_offset = 5.5 # vertical height from plate mount when mounted on switch
        bottom_width = 18.0 + key_pitch * (u-1);
        bottom_length = 18.0;

        top_width = 12.5 + key_pitch * (u-1)
        top_length = 14.5
        top_curve_depth = 0.85

        # all keys have same angle from vertical for front face
        # measured using depth and height of number key
        # units radians
        front_tiltback_angle = np.arctan(0.5/11.5)

        # keys measured from ducky one2 key caps
        # R1 is number row, counting down.
        # measured to the ridge on the edges, not the valley of the curved cutout
        if r == 1:
            # number row and F row
            top_front_height = 11.5
            top_back_height = 11.05
        elif r == 2:
            # Q row
            top_front_height = 9.1
            top_back_height = 9.35

        elif r == 3:
            # A row
            top_front_height = 8.0
            top_back_height = 9.35
        elif r == 4:
            # Z row and Ctrl row
            top_front_height = 8.05
            top_back_height = 10.25
        else:
            # other rows can be implemented later, such as R5
            raise Exception('OEM Keycap R value out of range:' + str(r))

        top_offset_front = top_front_height * np.tan(front_tiltback_angle)
        top_face_angle = utils.rad2deg(np.arcsin((top_front_height - top_back_height) / top_length));

        bottom_corners = [[-bottom_width/2, 0, 0], # front left
                          [ bottom_width/2, 0, 0],  # front right
                          [ bottom_width/2, -bottom_length, 0], # back right
                          [-bottom_width/2, -bottom_length, 0]] # back left
        top_corners = [[-top_width/2, 0, 0], # front left
                       [ top_width/2, 0, 0], # front right
                       [ top_width/2, -top_length, 0], #back right
                       [-top_width/2, -top_length, 0]] # back left
        top_corners = utils.rotate_points(top_corners, [top_face_angle, 0, 0])
        top_corners = utils.translate_points(top_corners, [0, -top_offset_front, top_front_height])

        corners = top_corners + bottom_corners
        # faces must be numbered clockwise when looking at exterior
        key_faces = [[2, 3, 0, 1], # top
                     [1, 0, 4, 5], # front
                     [5, 4, 7, 6], # bottom
                     [2, 1, 5, 6], # right
                     [3, 2, 6, 7], # back
                     [0, 3, 7, 4]] # left

        key_cap = sl.polyhedron(corners, key_faces)

        top_curve_radius = (top_curve_depth**2 + (top_width/2)**2)/(2 * top_curve_depth)
        curve_cut = sl.cylinder(top_curve_radius, bottom_length*2, center=True, segments=100)
        curve_cut = sl.rotate([90+top_face_angle, 0, 0])(curve_cut)
        curve_cut = sl.translate([0,-top_offset_front,top_curve_radius+top_front_height-top_curve_depth])(curve_cut)

        key_cap = key_cap - curve_cut
        key_cap = sl.translate([0, bottom_length/2, 0])(key_cap)
        key_cap -= curve_cut
        key_cap = sl.translate([0, 0, vertical_offset])(key_cap)
        key_cap = sl.color([50 / 255, 175 / 255, 255 / 255, 1])(key_cap)

        # setting the % modifier makes it render visually in openscad, but not when exporting to stl
        self._solid = key_cap.set_modifier('%')
        self._anchors = Hull(corners)
