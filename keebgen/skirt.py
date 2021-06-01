import numpy as np
from .geometry_utils import deg2rad, rad2deg
from .better_abc import abstractmethod
from .geometry_base import Assembly, LabeledPoint, AnchorCollection, PartCollection, CuboidAnchorCollection
from .connector import Connector
from .geometry_utils import unit_vector, vector_angle_2D
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

        #now need to work around each segment so the base is a convex hull
        # move the bottom of the skirt segment out to match the convex hull perrimeter
        # the vertical segment above will come with it
        # direction of motion is in the direction of the vector made by bottom inside and bottom outside nodes

        # find the most -x edge to start with
        furthest_left_val = 1000000000000000.0
        furtheset_left_index = -1
        for (index, segment) in enumerate(segments):
            new_val = segment['bottom', 'outside']
            assert len(new_val) == 1
            val = new_val.coords[0][0]
            if val < furthest_left_val:
                furthest_left_val = val
                furthest_left_index = index

        #now re-order the list so the furthest left index is the 0 index
        segments = segments[furthest_left_index:] + segments[:furthest_left_index]

        #now, work clockwise around the base
        prev_point = segments[0]['bottom', 'outside']
        #prev_dir = (0.,-1.) # previous vector as of now is pointing straight down

        # make a 2D point out of the x,y coord of bottom outside corner of the segment
        def make_point(seg):
            seg = seg['bottom', 'outside']
            assert len(seg) == 1
            return seg.coords[0][:2]

        def point_angles(prev_point, cur_point, next_point):
            vec1 = [prev_point[0]-cur_point[0], prev_point[1]-cur_point[1]]
            vec2 = [next_point[0]-cur_point[0], next_point[1]-cur_point[1]]
            # always return -pi to pi
            return vector_angle_2D(vec1, vec2)

        # use gift-wrapping method to find 2D convex hull of the skirt base

        # use the previous segment as an imaginary segment straight down from the current point
        hull_segment_indexes = [0]
        prev_point = make_point(segments[0])
        prev_point = [prev_point[0], prev_point[1]-10]

        while True:
            cur_point = make_point(segments[hull_segment_indexes[-1]])
            largest_angle = point_angles(prev_point, cur_point, make_point(segments[hull_segment_indexes[0]]))
            largest_index = 0
            #loop over all remaining points
            for (next_index, next_segment) in enumerate(segments[hull_segment_indexes[-1]+1:], hull_segment_indexes[-1]+1):
                angle = point_angles(prev_point, cur_point, make_point(next_segment))
                if angle > largest_angle:
                    largest_angle = angle
                    largest_index = next_index

            # once there are no larger angles than the starting angle, we have wrapped around the entire hull
            if largest_index == 0:
                break

            hull_segment_indexes.append(largest_index)
            prev_point = cur_point


        # we now have a list of the segment indexes that make up the convex hull
        # of the footprint of the skirts
        # work around the skirt segments and move concave corners so they are inline with
        # the calculated hull points

        for list_index in range(0, len(hull_segment_indexes)):
            segments_start_index = hull_segment_indexes[list_index-1]
            segments_end_index = hull_segment_indexes[list_index]
            # don't do anything if there are no segments between the start and end
            if segments_end_index - segments_start_index == 1:
                continue

            # find the first and last segment in the run
            start_segment = segments[segments_start_index]
            end_segment = segments[segments_end_index]

            start_p = make_point(start_segment)
            end_p = make_point(end_segment)

            # this redefines the start and end index for the situation where there are
            # skirt points after the final convex hull point, before wrapping to the start
            if list_index == 0:
                segments_start_index = hull_segment_indexes[list_index-1]
                segments_end_index = len(segments)-1

            # modify any internal segments between the two hull segments
            for index in range(segments_start_index, segments_end_index):
                out_p = segments[index]['bottom', 'outside'].coords[0][:2]
                in_p = segments[index]['bottom', 'inside'].coords[0][:2]

                # calculate the intersection of the inside/outside point line vs the convex hull line
                # from the wikipedia line intersection page
                # https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
                # eliminates divide by zero issues when calculating slope
                denom = (start_p[0]-end_p[0])*(out_p[1]-in_p[1]) - (start_p[1]-end_p[1])*(out_p[0]-in_p[0])
                if denom == 0:
                    # this case only happens when lines are parallel. It may be desireable later to
                    # remove the assert and just let it continue without modification
                    assert(denom != 0)
                    continue

                x_intersect = ((start_p[0]*end_p[1]-start_p[1]*end_p[0])*(out_p[0]-in_p[0]) - (start_p[0]-end_p[0])*(out_p[0]*in_p[1]-out_p[1]*in_p[0])) / denom
                y_intersect = ((start_p[0]*end_p[1]-start_p[1]*end_p[0])*(out_p[1]-in_p[1]) - (start_p[1]-end_p[1])*(out_p[0]*in_p[1]-out_p[1]*in_p[0])) / denom

                # motion distances for inside walls that aren't going all the way to the intersect
                move_x = x_intersect - out_p[0]
                move_y = y_intersect - out_p[1]

                # move the outside segment to the hull border
                segments[index]['bottom','outside'].coords[0][0] = x_intersect
                segments[index]['bottom','outside'].coords[0][1] = y_intersect
                segments[index]['middle','outside'].coords[0][0] = x_intersect
                segments[index]['middle','outside'].coords[0][1] = y_intersect

                segments[index]['bottom','inside'].coords[0][0] += move_x
                segments[index]['bottom','inside'].coords[0][1] += move_y
                segments[index]['middle','inside'].coords[0][0] += move_x
                segments[index]['middle','inside'].coords[0][1] += move_y

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
        ret_points.append(LabeledPoint(bottom_outer_corner, ('bottom', 'outside')))

        bottom_inner_corner = copy.deepcopy(mid_inner_corner)
        bottom_inner_corner[2] = 0.0
        ret_points.append(LabeledPoint(bottom_inner_corner, ('bottom', 'inside')))

        # return a plane of segments in order of top, middle, bottom
        return AnchorCollection(ret_points)
