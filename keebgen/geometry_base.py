from abc import ABC, abstractmethod
import solid as sl
import numpy as np
from functools import partialmethod

from . import transform_utils as utils

# base class for all solids
class Solid(ABC):
    @abstractmethod
    def __init__(self):
        pass

    # child __init__() functions responsible for populating self._solid and self._anchors
    def solid(self):
        return self._solid

    def translate(self, x=0, y=0, z=0):
        self._solid = sl.translate([x,y,z])(self._solid)
        self._anchors.translate(x,y,z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        self._solid = sl.rotate([x, y, z])(self._solid)
        self._anchors.rotate(x,y,z,degrees)

    def anchors(self):
        return self._anchors

class Assembly(ABC):
    @abstractmethod
    def __init__(self):
        pass

    # child __init__() functions responsible for populating self._solid and self._anchors
    def solid(self):
        out_solid = None
        for part in self._parts.values():
            out_solid += part.solid()
        return out_solid

    def translate(self, x=0, y=0, z=0):
        self._anchors.translate(x,y,z)
        for part in self._parts.values():
            part.translate(x, y, z)

    def rotate(self, x=0, y=0, z=0, degrees=True):
        self._anchors.rotate(x,y,z,degrees)
        for part in self._parts.values():
            part.rotate(x, y, z)

    def anchors(self, part_name=None):
        # return assembly anchors if no part specified
        if part_name == None:
            return self._anchors
        # return the anchors of the requested part
        return self._parts[part_name].anchors()


# top, bottom, left, right are relative to the user sitting at the keyboard
class Hull(object):
    def __init__(self, corners):
        """
        sorted corner ordering
           3-------7
          /|      /|
         / |     / | Y
        2--|----6  |
        |  1----|--5
        | /     | / Z
        0-------4
            X
        """
        self.corners = np.array(sorted(corners)).reshape((2,2,2,3))
        self._output_shape = (4,3)

    def _get_side(self, slice):
        coords =  self.corners[slice].reshape(self._output_shape)
        return set(tuple(x) for x in coords)

    def translate(self, x=0, y=0, z=0):
        for i in range(len(self.corners)):
            for j in range(len(self.corners[i])):
                for k in range(len(self.corners[i][j])):
                    self.corners[i][j][k] = utils.translate_point(self.corners[i][j][k], (x,y,z))

    def rotate(self, x=0, y=0, z=0, degrees=True):
        for i in range(len(self.corners)):
            for j in range(len(self.corners[i])):
                for k in range(len(self.corners[i][j])):
                    self.corners[i][j][k] = utils.rotate_point(self.corners[i][j][k], (x,y,z), degrees)


    right  = partialmethod(_get_side, np.s_[1,:,:])
    left   = partialmethod(_get_side, np.s_[0,:,:])
    top    = partialmethod(_get_side, np.s_[:,1,:])
    bottom = partialmethod(_get_side, np.s_[:,0,:])
    front  = partialmethod(_get_side, np.s_[:,:,1])
    back   = partialmethod(_get_side, np.s_[:,:,0])
