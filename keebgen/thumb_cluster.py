from keebgen.better_abc import abstractmethod
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
                center = np.array(key.anchors.center())
                key.translate(*(-center))
                key.rotate(*rotation, degrees=degrees)
                key.translate(*center)

    def apply_curvature(self, rx, ry, rz):

        keys = self.keys()
        # move the origin to the center of all the keys
        grid_center = np.array(utils.mean_point([x.anchors.center() for x in keys]))
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



                kx,ky,kz = key.anchors.center()

                x_angle = -angle_between([kz, ky], [rz, ry])
                y_angle = -angle_between([kz, kx], [rz, rx])
                z_angle = angle_between([kx, ky], [rx, ry]) - np.pi/2

                # one_offset = np.arctan2(np.linalg.norm(np.cross(key_center,r, axis=0), axis=0), np.dot(key_center,r))

                # print('angle1', x_angle, y_angle, z_angle)
                key.rotate(x_angle, y_angle, 0, degrees=False)


                # TODO: fix this so it works with positive and negative values for `rz`

                # Rotate to face the r point

                # Get new key position
                kx, ky, kz = key.anchors.center()

                x_angle = angle_between([kz, ky], [rz, ry])/2
                y_angle = angle_between([kz, kx], [rz, rx])/2
                z_angle = angle_between([kx, ky], [rx, ry]) - np.pi / 2

                # print('angle2', x_angle, y_angle, z_angle)
                center = np.array(key.anchors.center())
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

        [1][2][3][4]
        [5][6]

        Keys 3 and 4 are 1.5U.
        By default, key 4 is the home_key.
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
            [None, (0, 6, 0), (2, 7, -1), (-2, -6, -3)],
            [None, (0, 2, 0)]
        ]
        self.key_grid.apply_offsets(xyz_offsets)

        # Units are in degrees
        xyz_rotations = [
            [(0, 0, 0), (0, 0, -5), (0, 5, -25), (0, 9, -25)],
            [None, None]
        ]
        self.key_grid.apply_rotations(xyz_rotations)



        # Get the corner keys
        back_left  = keys[0][0] # key 1
        front_left = keys[1][0] # key 5
        back_right = keys[0][3] # key 4
        front_right = back_right # reuse key 4 since it's the only one on that column.

        self._anchors = CuboidAnchorCollection(
            back_left.anchors['back', 'left'] +
            front_left.anchors['front', 'left'] +
            back_right.anchors['back', 'right'] +
            front_right.anchors['front', 'right'])

        self.skirt = None # TODO
