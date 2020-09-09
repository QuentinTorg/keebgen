from abc import ABC, abstractmethod
import solid as sl
import numpy as np
from collections import Iterable

from . import geometry_utils as utils
from .geometry_base import Solid, Hull, Anchors

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

        # accumulate args into an achor points list that can be used to construct an Anchors object
        accumulated_anchor_points = []
        for anchors in args:
            if isinstance(anchors, Anchors) or isinstance(anchors, Anchors.Anchor):
                accumulated_anchor_points.append(anchors)
            else:
                points = _sanitize_points(anchors)
                accumulated_anchor_points += [[[x],[]] for x in points]
        self._new_style_anchors = Anchors(accumulated_anchor_points)

    def solid(self):
        # using hull around tiny spheres is a hack, but whatever. saves a ton of code
        spheres = _make_spheres(self._new_style_anchors)
        # make sure we didn't end up with zero points
        # we may want to adjust this functionality later and just return solid.part() for empty connectors
        assert len(spheres) > 0
        return sl.hull()(*spheres)

    def anchors(self):
        # a connector is not guarenteed to have cubic form, so it is not safe to use anchors
        # also, each connector should connect existing geometry that has its own anchors
        raise Exception('Connectors do not have anchors becuase they are tied to the geometry of other parts')
