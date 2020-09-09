from abc import ABC, abstractmethod
import solid as sl
import numpy as np
from functools import partialmethod

from . import geometry_utils as utils

# base class for all solids
class Solid(ABC):
    @abstractmethod
    def __init__(self):
        # check if defined
        try:
            self._anchors
        except AttributeError:
            # not defined
            # define arbitrary anchors for compatibility
            self._anchors = Hull(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                                  (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)))
        # check if defined
        try:
            self._solid
        except AttributeError:
            # not defined
            # define arbitrary solid for compatibility
            self._solid = sl.part()


    # child __init__() functions responsible for populating self._solid and self._anchors
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


class Assembly(ABC):
    class PartCollection:
        def __init__(self):
            self._part_list = []
            self._index_lookup = {}

        def add(self, part, name=None):
            # if name provided, track index
            if name is not None:
                if name in self._index_lookup:
                    raise Exception(str(name)+'already in this PartCollection')
                self._index_lookup[name] = len(self._part_list)
            self._part_list.append(part)

        def get(self, name):
            if name in self._index_lookup:
                return self._part_list[self._index_lookup[name]]
            return None

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

    @abstractmethod
    def __init__(self):
        # check if defined
        try:
            self._parts
        except AttributeError:
            # not defined
            # define arbitrary solid for compatibility
            self._parts = self.PartCollection()

        # check if defined
        try:
            self._anchors
        except AttributeError:
            # not defined
            # define arbitrary anchors for compatibility
            self._anchors = Hull(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                                  (0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)))

    # child __init__() functions responsible for populating self._parts and self._anchors
    def solid(self):
        return self._parts.solid()

    def translate(self, x=0, y=0, z=0):
        self._anchors.translate(x,y,z)
        self._parts.translate(x,y,z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        self._anchors.rotate(x, y, z, degrees)
        self._parts.rotate(x,y,z, degrees)

    def anchors(self, part_name=None):
        # return assembly anchors if no part specified
        if part_name == None:
            return self._anchors
        # return the anchors of the requested part
        if self._parts.get(part_name):
            return self._parts.get(part_name).anchors()
        return None

    def get_part(self, part_name):
        return self._parts.get(part_name)

    def to_file(self, file_name):
        sl.scad_render_to_file(self.solid(), file_name)


# top, bottom, left, right are relative to the user sitting at the keyboard
class Hull(object):
    def __init__(self, corners):
        # assumes a volume. No more than 4 corners should be in plane or behavior is undefined
        """
        sorted corner ordering
           3-------7
          /|      /|
         / |     / | Z
        2--|----6  |
        |  1----|--5
        | /     | / Y
        0-------4
            X
        """
        assert len(corners) == 8
        self.corners = np.array(self._sort_corners(corners)).reshape((2,2,2,3))
        self._output_shape = (4,3)

    def _sort_corners(self, corners):
        assert len(corners) == 8
        top_corners = sorted(corners, key = lambda x: x[2])[:4]
        bottom_corners = sorted(corners, key = lambda x: x[2], reverse=True)[:4]
        front_top_corners = sorted(top_corners, key = lambda x: x[1])[:2]
        back_top_corners = sorted(top_corners, key = lambda x: x[1], reverse=True)[:2]
        front_bottom_corners = sorted(bottom_corners, key = lambda x: x[1])[:2]
        back_bottom_corners = sorted(bottom_corners, key = lambda x: x[1], reverse=True)[:2]

        # sorted corners match indices in __init__ ascii art
        sorted_corners = []
        # left
        sorted_corners.append(sorted(back_bottom_corners, key=lambda x: x[0])[0])
        sorted_corners.append(sorted(front_bottom_corners, key=lambda x: x[0])[0])
        sorted_corners.append(sorted(back_top_corners, key=lambda x: x[0])[0])
        sorted_corners.append(sorted(front_top_corners, key=lambda x: x[0])[0])
        # right
        sorted_corners.append(sorted(back_bottom_corners, key=lambda x: x[0])[1])
        sorted_corners.append(sorted(front_bottom_corners, key=lambda x: x[0])[1])
        sorted_corners.append(sorted(back_top_corners, key=lambda x: x[0])[1])
        sorted_corners.append(sorted(front_top_corners, key=lambda x: x[0])[1])
        return sorted_corners

    def _get_side(self, slice):
        coords =  self.corners[slice].reshape(self._output_shape)
        return set(tuple(x) for x in coords)

    def translate(self, x=0, y=0, z=0):
        for i in range(len(self.corners)):
            for j in range(len(self.corners[i])):
                for k in range(len(self.corners[i][j])):
                    self.corners[i,j,k] = utils.translate_point(self.corners[i,j,k], (x,y,z))

    def rotate(self, x=0, y=0, z=0, degrees=True):
        for i in range(len(self.corners)):
            for j in range(len(self.corners[i])):
                for k in range(len(self.corners[i][j])):
                    self.corners[i,j,k] = np.array(utils.rotate_point(self.corners[i,j,k], (x,y,z), degrees))

    right  = partialmethod(_get_side, np.s_[1,:,:])
    left   = partialmethod(_get_side, np.s_[0,:,:])
    bottom    = partialmethod(_get_side, np.s_[:,1,:])
    top = partialmethod(_get_side, np.s_[:,0,:])
    back  = partialmethod(_get_side, np.s_[:,:,1])
    front = partialmethod(_get_side, np.s_[:,:,0])

# proposed replacement for Hull class
class Anchors():
    # subclass to represent each point
    class Anchor():
        def __init__(self, point, faces):
            assert(len(point) == 3)
            self.point = point
            self.faces = set()
            for face in faces:
                self.faces.add(face)

        # makes points behave as though it is a list of points
        def __iter__(self):
            return iter(self.point)

        def __len__(self):
            return len(self.point)

        def __str__(self):
            return 'point:' + str(self.point) + ' faces:' + str(self.faces)

        # maybe not useful?
        #def __contains__(self, face):
        #    # check 'face in self'
        def translate(self, x=0, y=0, z=0):
            self.point = utils.translate_point(self.point, (x,y,z))
        def rotate(self, x=0, y=0, z=0, degrees=True):
            self.point = utils.rotate_point(self.point, (x,y,z), degrees)


    def __init__(self, points):
        self._anchors = [];
        # points come in as a collection of elements
        # each element has the form ((x,y,z), ('facenameA', 'facenameB'))
        for point in points:
            assert(len(point) == 2)
            self._anchors.append(self.Anchor(point[0], point[1]))

    # this could be replaced with a function called anchors() or similar
    # when anchor is called, return new Anchor that contains only points with specified faces
    # *args is a list of any number of face specifiers, usually strings
    def __call__(self, *args):
        faces = set(args)
        ret_anchors = []
        for anchor in self._anchors:
            if len(faces & anchor.faces) == len(faces):
                ret_anchors.append((anchor.point, anchor.faces))
        return Anchors(ret_anchors)

    def __iter__(self):
        return iter(self._anchors)

    def __len__(self):
        return len(self._anchors)

    def __str__(self):
        ret_str = ''
        for anchor in self._anchors:
            ret_str += str(anchor) + '\n'
        return ret_str

    def translate(self, x=0, y=0, z=0):
        for anchor in self._anchors:
            anchor.translate(x,y,z)
    def rotate(self, x=0, y=0, z=0, degrees=True):
        for anchor in self._anchors:
            anchor.rotate(x,y,z,degrees)

# sublcasses can be specific shapes that automatically load bare points and assign the names automatcially
class CubicAnchors(Anchors):
    # point_list in the form of ((x,y,z),(x,y,z),(x,y,z))
    def __init__(point_list):
        # sort points and assign faces to each point
        # convert into standard points then call super
        faced_points = []
        super(CubicAnchors, self).__init__(faced_points)

