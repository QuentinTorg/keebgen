import numpy as np
from .geometry_utils import deg2rad, rad2deg
from .better_abc import abstractmethod
from .geometry_base import Assembly, LabeledPoint, AnchorCollection, PartCollection, CuboidAnchorCollection
from .connector import Connector
from .geometry_utils import unit_vector
import numpy as np
import copy

class FlaredSkirt(Assembly):
    # edge pairs in the format of (top_edge, outer_edge),
    # where each edge is made of two anchor points
    # edges will be connected consecutively and last will connect to first
    def __init__(self, edge_pairs, config):
        super().__init__()

        self._thickness = config.getfloat('wall_thickness')
        self._flare_len = config.getfloat('flare_len')
        self._flare_angle = config.getfloat('flare_angle')

        segments = []
        for edge_pair in edge_pairs:
            # make sure pair is a pair
            assert(len(edge_pair) == 2)
            segments.append(self._make_skirt_segment(edge_pair[0], edge_pair[1]))

        self._parts = PartCollection()
        prev_segment = segments[-1]

        for segment in segments:
            self._parts.add(Connector(segment['top'] + segment['middle'] + prev_segment['top'] + prev_segment['middle']))
            self._parts.add(Connector(segment['middle'] + segment['bottom'] + prev_segment['middle'] + prev_segment['bottom']))
            self._anchors = CuboidAnchorCollection.create()
            prev_segment = segment

    def _same_anchor(self, anchor1, anchor2):
        for coord1, coord2 in zip(anchor1.coords, anchor2.coords):
            if coord1 != coord2:
                return False
        return True

    # two edges actually made up of three points
    def _make_skirt_segment(self, top_edge, outer_edge):
    # known limitation: top edge and outer edge are assumed to be perpendicular
    # it will work without this, but the thickness dimensions may not be correct
        '''
         top_edge
        --------|
                | outer_edge
        --------|


        --------|---\
                |    \
        --------|     \ sloping wall
                 \     \
                  \    |
                  |    |
                  |    | vertical wall to xy plane
                  |_ __|
        '''
        # make sure there are only 2 points in each edge
        assert len(top_edge) == 2
        assert len(outer_edge) == 2

        # identify each corner
        shared_point = None
        bottom_point = None
        back_point = None
        for top_point in top_edge:
            for outer_point in outer_edge:
                if self._same_anchor(top_point, outer_point):
                    point_check = top_point
                    shared_point = np.array(top_point.coords)
                    break
        for top_point in top_edge:
            if not self._same_anchor(top_point, point_check):
                back_point = np.array(top_point.coords)
                break
        for outer_point in outer_edge:
            if not self._same_anchor(outer_point, point_check):
                bottom_point = np.array(outer_point.coords)
                break

        # make sure all assigned. Will fail if two identical edges provided as input
        assert len(shared_point) == 3
        assert len(bottom_point) == 3
        assert len(back_point) == 3

        # unit vector pointing out, in line with the top edge
        top_dir = unit_vector(back_point, shared_point)
        # unit vector pointing down, in line with the outer edge
        front_dir = unit_vector(shared_point, bottom_point)

        alpha = deg2rad(90 - self._flare_angle) / 2
        u = self._thickness * np.tan(alpha)

        wall_start_point = front_dir*self._thickness+shared_point
        top_extension_point = top_dir*u+shared_point
        ret_points = [LabeledPoint(shared_point, ('outside', 'top')),
                      LabeledPoint(wall_start_point, ('inside', 'top')),
                      LabeledPoint(top_extension_point, ('outside', 'top'))]

        flare_dir = unit_vector((0,0,0), top_dir*np.sin(deg2rad(self._flare_angle)) +
                                         front_dir*np.cos(deg2rad(self._flare_angle)))

        beta = np.arccos(np.dot(flare_dir,(0,0,-1))) / 2
        v = self._thickness * np.tan(beta)

        mid_outer_corner = top_extension_point + (u + v + self._flare_len)*flare_dir
        mid_inner_corner = wall_start_point + self._flare_len*flare_dir

        ret_points.append(LabeledPoint(mid_outer_corner, ('outside', 'middle')))
        ret_points.append(LabeledPoint(mid_inner_corner, ('inside', 'middle')))

        bottom_outer_corner = copy.deepcopy(mid_outer_corner)
        bottom_outer_corner[2] = 0.0
        ret_points.append(LabeledPoint(bottom_outer_corner, ('bottom', 'outer')))

        bottom_inner_corner = copy.deepcopy(mid_inner_corner)
        bottom_inner_corner[2] = 0.0
        ret_points.append(LabeledPoint(bottom_inner_corner, ('bottom', 'inner')))

        # return a plane of segments in order of top, middle, bottom
        return AnchorCollection(ret_points)
