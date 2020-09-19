import solid as sl
from collections import Iterable

from .geometry_base import Part, AnchorCollection

# if the passed object is a 3D point, return it as a list where the only element is that point
# important for proper iteration
def _sanitize_points(maybe_point):
    if len(maybe_point) == 3:
        # check if this is a point, or iterable of 3 points
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

# helper function to make tiny spheres around an iterable of points
def _make_spheres(geo):
    geo = _sanitize_points(geo)
    spheres = []
    for point in geo:
        spheres.append(sl.translate(point.coords)(sl.sphere(d=0.001)))
    return spheres


#Connectors will create a part that is a convex hull around all points in *args
class Connector(Part):
    def __init__(self, anchors: AnchorCollection):
        super().__init__()
        assert len(anchors) > 0
        self._anchors = AnchorCollection.copy_from(anchors)

        # using hull around tiny spheres is a hack, but whatever. saves a ton of code
        spheres = _make_spheres(self._anchors)
        # make sure we didn't end up with zero points
        # we may want to adjust this functionality later and just return solid.part() for empty connectors
        assert len(spheres) > 0
        self._solid = sl.hull()(*spheres)
