from keebgen.better_abc import abstractmethod
from .connector import Connector
from .geometry_base import Assembly, PartCollection, CuboidAnchorCollection, Part, AnchorCollection, LabeledPoint
from .key_assy import FaceAlignedKey, KeyAssy
from . import geometry_utils as utils


import numpy as np

from typing import List, Optional, Tuple

class DebuggingPoint(Part):
    def __init__(self, coords=(0,0,0), size=5, color=(255,0,0)):
        import solid as sl
        color = np.array(color)/255
        sphere = sl.translate(coords)(sl.sphere(d=size))
        sphere = sl.color(color)(sphere)
        self._solid = sphere
        self._anchors = AnchorCollection([LabeledPoint(coords, ['center'])])

#TODO: refactor this to reduce repetition
class ThumbCluster(Assembly):
    @abstractmethod
    def __init__(self):
        super().__init__()




class KeyGrid:
    #TODO key_gap should be part of a config
    key_gap = 2.5

    def __init__(self, grid: List[List[Optional[KeyAssy]]],
                 standard_key_size: Tuple[float, float, float]):
        """
        A collection of KeyAssys in a sparse grid formation. Allows keys to be arranged with curvatures
        along both rows and columns.
        """
        self._parts = PartCollection()
        self.standard_key_size = standard_key_size

        def move_origin_to_corner(key):
            """
            Convenience function.
            Move the origin from the center of the key to the left, back corner
            """
            w,h,d = key.anchors.bounds()
            key.translate(w / 2, -h / 2)

        # Apply transforms to arrange keys into a grid
        for y in range(len(grid)):
            for x in range(len(grid[y])):
                key = grid[y][x]
                if key is None:
                    continue

                move_origin_to_corner(key)

                w,h,d = standard_key_size
                key.translate( x*(w + self.key_gap),
                              -y*(h + self.key_gap))

        self.grid = grid
        self._anchors = None
        super().__init__()


        # TODO: handle curves along all 3 dims

    def keys(self):
        """Returns a flat list of KeyAssys"""
        return [key for row in self.grid for key in row if key is not None]

    def apply_offsets(self, offset_grid: List[List[Optional[Tuple[float, float, float]]]]):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                key = self.grid[y][x]
                offset = offset_grid[y][x]
                if key is None or offset is None:
                    continue

                key.translate(*offset)

    def apply_rotations(self, rotation_grid: List[List[Optional[Tuple[float, float, float]]]],
                        degrees=True):
        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                key = self.grid[y][x]
                rotation = rotation_grid[y][x]
                if key is None or rotation is None:
                    continue

                # apply rotation around the center of the key
                center = np.array(key.anchors.centroid())
                key.translate(*(-center))
                key.rotate(*rotation, degrees=degrees)
                key.translate(*center)

    def apply_curvature(self, rx, ry, rz):

        keys = self.keys()
        # move the origin to the center of all the keys
        grid_center = np.array(utils.mean_point([x.anchors.centroid() for x in keys]))
        # grid_center[2] = 10
        [x.translate(*(-grid_center)) for x in keys]

        def angle_between(p1, p2):
            p1 = np.array(p1)
            p2 = np.array(p2)
            return np.arctan2(p2[1] - p1[1], p2[0] - p1[0])

        for y in range(len(self.grid)):
            for x in range(len(self.grid[y])):
                key = self.grid[y][x]
                if key is None:
                    continue



                kx,ky,kz = key.anchors.centroid()

                x_angle = -angle_between([kz, ky], [rz, ry])
                y_angle = -angle_between([kz, kx], [rz, rx])
                z_angle = angle_between([kx, ky], [rx, ry]) - np.pi/2

                # one_offset = np.arctan2(np.linalg.norm(np.cross(key_center,r, axis=0), axis=0), np.dot(key_center,r))

                # print('angle1', x_angle, y_angle, z_angle)
                key.rotate(x_angle, y_angle, 0, degrees=False)


                # TODO: fix this so it works with positive and negative values for `rz`

                # Rotate to face the r point

                # Get new key position
                kx, ky, kz = key.anchors.centroid()

                x_angle = angle_between([kz, ky], [rz, ry])/2
                y_angle = angle_between([kz, kx], [rz, rx])/2
                z_angle = angle_between([kx, ky], [rx, ry]) - np.pi / 2

                # print('angle2', x_angle, y_angle, z_angle)
                center = np.array(key.anchors.centroid())
                # key.translate(*(-center))
                # key.rotate(x_angle, y_angle, 0, degrees=False)
                # key.translate(*center)


                # key.translate(rx,ry,rz)



class DactylThumbCluster(ThumbCluster):
    def __init__(self, key_config, socket_config, home_key_idx=(1,1)):
        """
        Right handed thumb cluster.
        It has 4 1U and 2 2U keys arranged like this:

        [1][2]
        [3]|4||5|
        [6]|_||_|

        By default, key 5 is the home_key.
        """

        super().__init__()
        self._parts = PartCollection()
        self._home_key_idx = home_key_idx

        def K(u=1.):
            """Convenience function for creating new keys"""
            key = FaceAlignedKey(key_config, socket_config, r=1, u=u)
            key.rotate(z=-90) # make the u>1 keys are vertical
            self._parts.add(key)
            return key

        # Populate the right hand keys
        key_grid = [
            [K(), K(),  None],
            [K(), K(2), K(2)], # vertical 2U keys
            [K(), None, None]
        ]


        # KeyGrid class will apply the actual geometry
        self.key_grid = KeyGrid(key_grid, standard_key_size=key_grid[0][0].anchors.bounds())

        # Get the corner keys
        back_left  = key_grid[0][0] # key 1
        front_left = key_grid[2][0] # key 6
        back_right = key_grid[1][2] # key 5
        front_right = back_right # reuse key 5 since it's the only one on that column.

        self._anchors = CuboidAnchorCollection(
            back_left.anchors['back', 'left'] +
            front_left.anchors['front', 'left'] +
            back_right.anchors['back', 'right'] +
            front_right.anchors['front', 'right'])

        self.skirt = None # TODO

    def home_key(self):
        x,y = self._home_key_idx
        return self.key_grid.grid[y][x]


class ManuformThumbCluster(ThumbCluster):
    def __init__(self, key_config, socket_config, home_key_idx=(0,3)):
        """
        Right handed thumb cluster.
        In the final shape, the top row should be fanned out and slightly staggered.

        [0][1][2][3]
        [4][5]

        Keys 2 and 3 are 1.5U.
        By default, key 3 is the home_key.
        """

        super().__init__()
        self._parts = PartCollection()
        self._home_key_idx = home_key_idx

        def K(u=1.):
            """Convenience function for creating new keys"""
            key = FaceAlignedKey(key_config, socket_config, r=1, u=u)
            key.rotate(z=-90) # make the u>1 keys are vertical
            self._parts.add(key)
            return key

        # Populate the right hand keys
        keys = [
            [K(), K(), K(1.5), K(1.5)],
            [K(), K()],
        ]

        # KeyGrid class will apply the actual geometry
        self.key_grid = KeyGrid(keys, standard_key_size=keys[0][0].anchors.bounds())

        # TODO: fix this
        # self.key_grid.apply_curvature(0, 0, -500)

        # Units are in millimeters
        xyz_offsets = [
            [(1, 0, -2), (0, 4, -1), (3, 3, -1), (-4, -12, -3)],
            [(1, 0, -2), (0, 2, -1)]
        ]
        self.key_grid.apply_offsets(xyz_offsets)

        # Units are in degrees
        xyz_rotations = [
            [(0, 0, 0), (0, 0, -5), (0, 5, -35), (0, 9, -35)],
            [None, None]
        ]
        self.key_grid.apply_rotations(xyz_rotations)



        # Get the corner keys
        back_left  = keys[0][0] # key 0
        front_left = keys[1][0] # key 4
        back_right = keys[0][3] # key 3
        front_right = back_right # reuse key 3 since it's the only one on that column.

        self._anchors = CuboidAnchorCollection(
            back_left.anchors['back', 'left'] +
            front_left.anchors['front', 'left'] +
            back_right.anchors['back', 'right'] +
            front_right.anchors['front', 'right'])


        # Connectors

        # keys as a flat list
        keys_map = sum([x for x in keys], [])
        socket_map = [x.get_part('socket') for x in keys_map]


        # First apply the main connectors between the grid-ish keys
        front_back_connector_pair_map = np.array([
            [0,1], [1,2], [2,3],
            [4,5]
        ])

        for idx1, idx2 in front_back_connector_pair_map:
            self._parts.add(Connector(socket_map[idx1].anchors['front'] +
                                      socket_map[idx2].anchors['back']))

        right_left_connector_pair_map = np.array([
            [0, 4], [1, 5]
        ])

        for idx1, idx2 in right_left_connector_pair_map:
            self._parts.add(Connector(socket_map[idx1].anchors['right'] +
                                      socket_map[idx2].anchors['left']))

        # fill in the center between the 4 small keys
        self._parts.add(Connector(
            socket_map[0].anchors['front', 'right'] +
            socket_map[1].anchors['back', 'right'] +
            socket_map[4].anchors['front', 'left'] +
            socket_map[5].anchors['back', 'left']
        ))

        # Fill in the gap around the long keys
        self._parts.add(Connector(
            socket_map[2].anchors['right'] +
            socket_map[5].anchors['front']
        ))

        self._parts.add(Connector(
            socket_map[2].anchors['front', 'right'] +
            socket_map[5].anchors['front', 'right'] +
            socket_map[3].anchors['back', 'right']
        ))

        # self._parts.add(Connector(
        #     socket_map[5].anchors['front', 'right'] +
        #     socket_map[3].anchors['right']
        # ))

        self.skirt = None # TODO: Should this be done at the keyboard level?

        # move the TC so the home key is in the center
        offset = [-x for x in self.home_key.anchors.centroid()]
        self.translate(*offset)

    @property
    def home_key(self):
        x,y = self._home_key_idx
        return self.key_grid.grid[x][y]
