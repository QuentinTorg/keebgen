from abc import abstractmethod
import solid as sl

from .geometry_base import Assembly, Hull
from . import key_assy

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
        key_lean = config.getfloat('key_lean')

        self._parts = {}
        for i in range(num_keys):
            r = 4-i + (home_index-1)
            rotation_index = i - home_index
            if r <= 0:
                r = 1
            if r > 4:
                r = 4

            key_name = 'key'+str(i)
            self._parts[key_name] = (key_assy.FaceAlignedKey(key_config, socket_config, r))
            self._parts[key_name].rotate(0, key_lean, 0)
            self._parts[key_name].translate(0, 0, -radius)

            #some function of gap
            rotation_angle = 20 * -rotation_index # some function of gap
            self._parts[key_name].rotate(-rotation_angle, 0, 0)
            self._parts[key_name].translate(0, 0, radius)

