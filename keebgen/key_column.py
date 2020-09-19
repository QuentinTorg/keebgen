from keebgen.better_abc import abstractmethod
import numpy as np

from .geometry_base import Assembly, PartCollection, CuboidAnchorCollection
from . import geometry_utils as utils
from .key_assy import FaceAlignedKey
from .connector import Connector

class KeyColumn(Assembly):
    @abstractmethod
    def __init__(self):
        super().__init__()

class ConcaveOrtholinearColumn(KeyColumn):
    def __init__(self, config, key_config, socket_config):
        super().__init__()
        self._parts = PartCollection()

        radius = config.getfloat('radius')
        gap = config.getfloat('key_gap')
        num_keys = config.getint('num_keys')
        home_index = config.getint('home_index')
        key_lean = config.getfloat('key_side_lean')
        home_angle = config.getfloat('home_tiltback_angle')

        prev_anchors = None
        for i in range(num_keys):
            r = 4-i + (home_index-1)
            rotation_index = i - home_index
            if r <= 0:
                r = 1
            if r > 4:
                r = 4

            # for alignment across rows, name keys by index from the home row. negative is below home
            key_name = rotation_index


            # add a key_assy to the parts
            self._parts.add(FaceAlignedKey(key_config, socket_config, r), key_name)
            self._parts.rotate(0, key_lean, 0, name=key_name)
            self._parts.translate(0, 0, -radius, name=key_name)

            # get y values from top face of the key
            anchors = self.anchors_by_part(key_name)
            center_top_front_anchor = utils.mean_point(anchors['top', 'front'].coords)
            center_top_back_anchor = utils.mean_point(anchors['top', 'back'].coords)
            y_front = center_top_front_anchor[1]
            y_back = center_top_back_anchor[1]

            # find rotation angle to create one gap width between adjacent keys
            one_offset = np.arctan(abs(y_front)/radius) + np.arctan(abs(y_back)/radius) + 2 * np.arctan(gap/(2*radius))

            rotation_angle = one_offset * -rotation_index
            self._parts.rotate(-rotation_angle, 0, 0, degrees=False, name=key_name)
            self._parts.translate(0, 0, radius, name=key_name)

            if prev_anchors is not None:
                connector = Connector(prev_anchors + self.get_part(key_name).anchors_by_part('socket')['back'])
                self._parts.add(connector)

            # remember where to connect the next key
            prev_anchors = self.get_part(key_name).anchors_by_part('socket')['front']

        first_anchors = self._parts[0].anchors_by_part('socket')
        self._anchors = CuboidAnchorCollection.copy_from(first_anchors['back'] + prev_anchors)

        self.rotate(home_angle, 0, 0, degrees=True)
