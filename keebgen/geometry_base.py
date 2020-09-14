from __future__ import annotations # for https://www.python.org/dev/peps/pep-0563/
from better_abc import BetterABCMeta, abstractmethod, abstractattribute
import solid as sl
import numpy as np
import itertools

from . import geometry_utils as utils

# base class for all solids
class Solid(metaclass=BetterABCMeta):
    _solid = abstractattribute()
    _anchors = abstractattribute()

    # child __init__() functions responsible for populating self._solid and self.anchors
    def solid(self):
        return self._solid

    def translate(self, x=0, y=0, z=0):
        self._solid = sl.translate([x,y,z])(self._solid)
        self._anchors.translate(x,y,z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        if degrees == False:
            x = utils.rad2deg(x)
            y = utils.rad2deg(y)
            z = utils.rad2deg(z)
        self._solid = sl.rotate([x, y, z])(self._solid)
        self._anchors.rotate(x,y,z)


    def anchors(self):
        return self._anchors

    def to_file(self, file_name):
        sl.scad_render_to_file(self.solid(), file_name)


class PartCollection:
    def __init__(self):
        self._part_list = []
        self._index_lookup = {}

    def add(self, part: Solid, name=None):
        # if name provided, track index
        if name is not None:
            if name in self._index_lookup:
                raise KeyError(f'Name "{name}" is already in this PartCollection.')
            self._index_lookup[name] = len(self._part_list)
        self._part_list.append(part)

    def get(self, name) -> Union[Solid, Assembly]:
        if name in self._index_lookup:
            return self._part_list[self._index_lookup[name]]
        raise KeyError(f'Name "{name}" could not be found.')

    def __getitem__(self, idx):
        return self._part_list[idx]

    def solid(self):
        solids = sl.part()
        for part in self._part_list:
            solids += part.solid()
        return solids

    def translate(self, x=0, y=0, z=0, name=None):
        # return specific part
        if name is not None:
            self.get(name).translate(x,y,z)
            return
        # no part specified, translate all parts
        for part in self._part_list:
            part.translate(x,y,z)

    def rotate(self, x=0, y=0, z=0, degrees=True, name=None):
        # return specific part
        if name is not None:
            self.get(name).rotate(x,y,z,degrees)
            return
        # no part specified, rotate all parts
        for part in self._part_list:
            part.rotate(x, y, z, degrees)

class Assembly(Solid):
    _parts: PartCollection = abstractattribute()
    _anchors = abstractattribute()

    def __init__(self):
        # This is purposefully left as None to bypass Solids abstractattribute.
        # It should be required, but this is an exception.
        self._solid = None

    # child __init__() functions responsible for populating self._parts and self._anchors
    def solid(self):
        return self._parts.solid()

    def translate(self, x=0, y=0, z=0):
        self._anchors.translate(x, y, z)
        self._parts.translate(x, y, z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        self._anchors.rotate(x, y, z, degrees)
        self._parts.rotate(x, y, z, degrees)

    def anchors_by_part(self, part_name):
        """Returns the anchors of the requested part"""
        if self._parts.get(part_name):
            return self._parts.get(part_name).anchors()

        raise KeyError(f'Part name "{part_name}" could not be found.')

    def get_part(self, part_name):
        return self._parts.get(part_name)


from typing import Sequence, Union, Set

class LabeledPoint:
    """A 3D point with one or more labels"""
    def __init__(self, coords: Sequence[float], labels: Union[Sequence[str], Set[str]]):
        assert len(coords) == 3
        self.coords = coords
        self.labels = set(labels)

    def translate(self, x=0, y=0, z=0):
        self.coords = utils.translate_point(self.coords, (x,y,z))

    def rotate(self, x=0, y=0, z=0, degrees=True):
        self.coords = utils.rotate_point(self.coords, (x,y,z), degrees)

    def __repr__(self):
        return f"{self.__class__.__name__}: coords: {self.coords}, labels: {self.labels}"


class AnchorCollection:
    """A container for LabeledPoints"""
    def __init__(self, points: Sequence[LabeledPoint]):
        self.labeled_points = list(points)

    @staticmethod
    def copy_from(other: AnchorCollection):
        copies = [LabeledPoint(list(x.coords), x.labels) for x in other.labeled_points]
        return AnchorCollection(copies)


    def __getitem__(self, labels):
        """Gets points by one or more labels"""
        if isinstance(labels, str):
            labels = {labels}
        else:
            labels = set(labels)

        points = [p for p in self.labeled_points if p.labels.issuperset(labels)]
        return AnchorCollection(points)

    def __iter__(self):
        return iter(self.labeled_points)

    def __len__(self):
        return len(self.labeled_points)

    def __add__(self, other):
        return AnchorCollection(self.labeled_points + other.labeled_points)

    def __radd__(self, other): # So `sum` can be used
        if other == 0:
            return AnchorCollection(self.labeled_points)
        return AnchorCollection(other.labeled_points + self.labeled_points)

    @property
    def coords(self):
        return [x.coords for x in self.labeled_points]

    def translate(self, x=0, y=0, z=0):
        for point in self.labeled_points:
            point.translate(x,y,z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        for point in self.labeled_points:
            point.rotate(x,y,z,degrees)

    def __repr__(self):
        return f"{self.__class__.__name__}: {self.labeled_points}"


class CuboidAnchorCollection(AnchorCollection):
    def __init__(self, corner_coords: Union[AnchorCollection, Sequence[Sequence[float]]]):
        """
        A LabeledPoint container specialized for six-sided shapes.

        :param corner_coords: An AnchorCollection or a list of 3D points. If an AnchorCollection
            is used, any existing labels will be lost.
        """
        assert len(corner_coords) == 8
        if isinstance(corner_coords, AnchorCollection):
            corner_coords = [x.coords for x in corner_coords]

        corner_coords = self._sort_coords(corner_coords)
        labels = self._create_labels()
        labeled_points = [LabeledPoint(c,l) for c,l in zip(corner_coords, labels)]
        super(CuboidAnchorCollection, self).__init__(labeled_points)

    @staticmethod
    def create(dims=(1,1,1), offset=(0,0,0)):
        """
        Creates a CuboidAnchorCollection based on the input dimensions.

        :param dims: Desired dimensions in (x,y,z)
        :param offset: Desired offset in (x,y,z)
        :return: CuboidAnchorCollection
        """
        corners = sorted(itertools.product([1., -1.], repeat=3))
        corners = np.array(corners) * np.array(dims) / 2.
        return CuboidAnchorCollection(corners + offset)

    @staticmethod
    def _sort_coords(coords) -> np.ndarray:
        coords = np.array(coords).reshape((8,3))
        originals = coords.copy()
        # move coords so that the origin is within the cuboid
        coords -= np.mean(coords, axis=0)

        # Sort the coords based on which side of the origin they fall on
        b = coords > 0 # b for binary mask
        idxs = np.lexsort((b[:, 2], b[:, 1], b[:, 0]))
        return originals[idxs]

    @staticmethod
    def _create_labels():
        """
        Creates an array of label sets. Assumes the same order as `_sort_coords`
        which is based on the diagram below:

           3-------7
          /|      /|
         / |     / | Z
        2--|----6  |
        |  1----|--5
        | /     | / Y
        0-------4
            X
        """

        # create a 2x2x2 cube of sets
        labels = np.array([set() for _ in range(8)]).reshape((2, 2, 2))

        def add(arr, item):
            [x.add(item) for x in arr.flatten()]

        # top, bottom, left, right are relative to the user sitting at the keyboard
        add(labels[0, :, :], 'left')
        add(labels[1, :, :], 'right')
        add(labels[:, 0, :], 'back')
        add(labels[:, 1, :], 'front') #TODO: back/front are reversed. Need to fix this and the downstream effects.
        add(labels[:, :, 0], 'bottom')
        add(labels[:, :, 1], 'top')
        return labels.flatten()

