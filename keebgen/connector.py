from abc import ABC, abstractmethod
import solid as sl
import numpy as np
from collections import Iterable

from . import geometry_utils as utils
from .geometry_base import Solid, Hull

# if the passed object is a 3D point, return it as a list where the only element is that point
# important for proper iteration
def _sanitize_points(maybe_point):
    if len(maybe_point) == 3:
        # check if this is a point, or iterable of 3 poitns
        iterable_count = 0
        for item in maybe_point:
            if not isinstance(item, Iterable):
                iterable_count += 1
        if iterable_count == 0:
            # all elements were not iterable, assume it is a point, nest in list
            maybe_point = [maybe_point]
        elif iterable_count != len(maybe_point):
            raise Exception('_sanitize_points() received invalid input')
    return maybe_point

# helper function to make tinys pheres around an iterable of points
def _make_spheres(geo):
    geo = _sanitize_points(geo)
    spheres = []
    for point in geo:
        spheres.append(sl.translate(point)(sl.sphere(d=0.001)))
    return spheres


#Connectors will create a part that is a convex hull around all points in *args
class Connector(Solid):
    def __init__(self, *args):
        super(Connector, self).__init__()
        # using hull around tiny spheres is a hack, but whatever. saves a ton of code
        spheres = []
        for points in args:
            spheres += _make_spheres(points)
        # make sure we didn't end up with zero points
        assert len(spheres) > 0
        self._solid = sl.hull()(*spheres)

    def anchors():
        # a connector is not guarenteed to have cubic form, so it is not safe to use anchors
        # also, each connector should connect existing geometry that has its own anchors
        raise Exception('Connectors do not have anchors becuase they are tied to the geometry of other parts')
