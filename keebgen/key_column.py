from abc import abstractmethod
import numpy as np
import solid as sl

from .geometry_base import Assembly, Hull
from . import geometry_utils as utils
from . import key_assy
from . import connector

class KeyColumn(Assembly):
    @abstractmethod
    def __init__(self):
        super(KeyColumn, self).__init__()


class CurvedOrtholinearColumn(KeyColumn):
    def __init__(self, config, key_config, socket_config):
        super(CurvedOrtholinearColumn, self).__init__()

        # config has the following
            # num_keys
            # curve_radius
            # key_gap # gap between each key @ the top face

        radius = config.getfloat('radius')
        gap = config.getfloat('key_gap')
        num_keys = config.getint('num_keys')
        home_index = config.getint('home_index')
        key_lean = config.getfloat('key_side_lean')
        home_angle = config.getfloat('home_tiltback_angle')

        self._parts = {}
        prev_anchors = None
        for i in range(num_keys):
            r = 4-i + (home_index-1)
            rotation_index = i - home_index
            if r <= 0:
                r = 1
            if r > 4:
                r = 4

            # add a key_assy to the parts
            key_name = i
            self._parts[key_name] = (key_assy.FaceAlignedKey(key_config, socket_config, r))
            self._parts[key_name].rotate(0, key_lean, 0)
            self._parts[key_name].translate(0, 0, -radius)

            # get y values from top face of the key
            anchors = self._parts[key_name].anchors()
            center_top_front_anchor = utils.mean_point(anchors.top() & anchors.front())
            center_top_back_anchor = utils.mean_point(anchors.top() & anchors.back())
            y_front = center_top_front_anchor[1]
            y_back = center_top_back_anchor[1]

            # find angle to rotate to space keys properly
            one_offset = np.arctan(abs(y_front)/radius) + np.arctan(abs(y_back)/radius) + 2 * np.arctan(gap/(2*radius))

            #some function of gap
            #TODO figure out the angle
            rotation_angle = one_offset * -rotation_index # some function of gap
            self._parts[key_name].rotate(-rotation_angle, 0, 0, degrees=False)
            self._parts[key_name].translate(0, 0, radius)

            if prev_anchors is not None:
                connector_name = 'connector'+str(i-1)+'to'+str(i)
                self._parts[connector_name] = connector.Connector(self._parts[key_name].anchors('socket').back(), prev_anchors)

            # remember where to connect the next key
            prev_anchors = self._parts[key_name].anchors('socket').front()

        self._anchors = Hull(self._parts[0].anchors('socket').back() | self._parts[num_keys-1].anchors('socket').front())
        self.rotate(home_angle, 0, 0, degrees=True)
