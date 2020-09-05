from abc import ABC, abstractmethod
import solid as sl
from pathlib import Path

from keebgen.geometry_base import Solid, Hull

# when adding new sockets, the top of the socket should be coplanar with the X,Y plane
# when the switch is installed, the keycap mounting feature should align with the Z axis

class CherryMXSocket(Solid):
    def __init__(self, config, u=1):
        super(CherryMXSocket, self).__init__()
        # determines how much flat space to reserve around the switch
        # prevents interference between keycap and other geometry
        width = config.getfloat('overall_width') + (u-1) * 19.0
        length = config.getfloat('overall_length')
        # changes how tight of a fit the switch is in the opening
        switch_length = config.getfloat('switch_opening_length')  ## Was 14.1, then 14.25
        switch_width = config.getfloat('switch_opening_width')
        # plate thickness for where the switch plugs in
        thickness = config.getfloat('plate_thickness')
        # if using hot swap PCB's. This is not currently implemented
        add_hot_swap = config.getboolean('hot_swap')
        add_side_nubs = config.getboolean('side_nubs')

        # parameters not pulled from config file
        # most people should not need to modify these
        side_nub_width = 2.75
        side_nub_radius = 1.0

        ### Make Geometry ###
        # make two of the four walls, b/c rotationally symmetric
        socket = sl.cube([width, length, thickness], center=True)
        socket -= sl.cube([switch_width, switch_length, thickness*2], center=True)
        socket = sl.translate([0, 0, -thickness/2])(socket)

        # tapered side nub that stabilizes the switch, goes in right wall
        if add_side_nubs:
            side_nub = sl.cylinder(side_nub_radius, side_nub_width, segments=20, center=True)
            side_nub = sl.rotate(90, [1, 0, 0])(side_nub)
            side_nub = sl.translate([switch_width/2, 0, side_nub_radius-thickness])(side_nub)
            nub_cube_len = (width-switch_width)/2
            nub_cube = sl.cube([nub_cube_len, side_nub_width, thickness], center=True)
            nub_cube = sl.translate([(width-nub_cube_len)/2, 0, -thickness/2])(nub_cube)
            side_nub = sl.hull()(side_nub, nub_cube)

            socket += side_nub + sl.rotate([0, 0, 180])(side_nub)

        # add hot swap socket
        # TODO, configure for different hot swap socket types
        if add_hot_swap:
            #TODO: fix the hot swap socket. currently not parameterized
            # missing the stl file in this repo
            raise Exception('hot swap sockets are not yet implemented')

            hot_swap_socket = sl.import_(Path.cwd().parent / "geometry" / "hot_swap_plate.stl")
            hot_swap_socket = sl.translate([0, 0, thickness - 5.25])(hot_swap_socket)
            socket = sl.union()(socket, hot_swap_socket)

        self._solid = socket

        # anchors start in top left, then work their way around
        #
        top_z = 0.0
        bottom_z = -thickness
        half_width = width/2.0
        half_length = length/2.0
        # self._anchors must be loaded in this order
        self._anchors = Hull([[-half_width,  half_length, top_z],
                              [ half_width,  half_length, top_z],
                              [ half_width, -half_length, top_z],
                              [-half_width, -half_length, top_z],
                              [-half_width,  half_length, bottom_z],
                              [ half_width,  half_length, bottom_z],
                              [ half_width, -half_length, bottom_z],
                              [-half_width, -half_length, bottom_z]])
