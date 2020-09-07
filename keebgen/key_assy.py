from abc import abstractmethod
import solid as sl
import numpy as np

from .geometry_base import Assembly, Hull
from . import geometry_utils as utils
from . import switch_socket
from . import keycap

# different Key subclasses will exist depending on the desired alignment
# alignment is driven by where the anchor points are placed
class KeyAssy(Assembly):
    # a Key represents the socket and keycap together,
    # this allows sockets to be arranged differently on a board depending on keycap geometry

    # TODO the config shoud have the socket_config nested within it eventaully
    @abstractmethod
    def __init__(self, config, socket_config, r, u=1):
        super(KeyAssy, self).__init__()

        # this will hold all parts of the key
        self._parts = {}
        if config.get('switch_type') == 'cherry_mx':
            self._parts['socket'] = switch_socket.CherryMXSocket(socket_config, u)
        else:
            raise Exception('socket for switch type ' + config.get('switch_type') + ' not implemented')

        if config.get('keycap_type') == 'oem':
            self._parts['keycap'] = keycap.OEM(r, u)
        else:
            raise Exception('keycap type ' + config.get('keycap_type') + ' not implemented')

        self._anchors = Hull(self._parts['keycap'].anchors().top() | self._parts['socket'].anchors().top())


# FaceAlignedKeys will have the faces forming a smooth curve on the keybaord regardless of switch and keycap type
class FaceAlignedKey(KeyAssy):
    def __init__(self, config, socket_config, r, u=1):
        # this will load the self._parts dict according to config
        super(FaceAlignedKey, self).__init__(config, socket_config, r, u)
        # set the assembly corner anchors to top of the socket

        # reorient the key and switch together so the top face of the keycap is centered
        # on the z axis and coplanar with the xy plane
        # assumes a symmetrical keycap from left to right

        # top front and top back anchors
        tf_anchors = self._anchors.top() & self._anchors.front()
        tb_anchors = self._anchors.top() & self._anchors.back()

        assert len(tf_anchors) == 2
        assert len(tb_anchors) == 2

        # center front and center back anchors
        cf_anchor = utils.mean_point(tf_anchors)
        cb_anchor = utils.mean_point(tb_anchors)

        # how far to tilt keys in x axis to make them flat
        tiltback_angle = np.arctan((cb_anchor[2] - cf_anchor[2] ) / abs(cf_anchor[1] - cb_anchor[1]))
        self.rotate(tiltback_angle, 0, 0, degrees=False)

        # in the case of non symmetric keys, how much to rotate in x to make them flat
        # has no affect on most key types

        # top right and top left anchors
        tr_anchors = self._anchors.top() & self._anchors.right()
        tl_anchors = self._anchors.top() & self._anchors.left()
        cr_anchor = utils.mean_point(tr_anchors)
        cl_anchor = utils.mean_point(tl_anchors)

        roll_angle = np.arctan((cr_anchor[2] - cl_anchor[2] ) / abs(cl_anchor[0] - cr_anchor[0]))
        self.rotate(0, roll_angle, 0, degrees=False)

        # top face of keycap is parallel to xy plane

        # translate so face centered on Z axis, and planar with xy plane
        center_anchor = utils.mean_point(self._anchors.top())
        self.translate(-center_anchor[0], -center_anchor[1], -center_anchor[2])

# simplest case, the switches are aligned based on the socket.
# should be used for plate mount boards
class SocketAlignedKey(KeyAssy):
    def __init__(self, config, socket_config, r, u=1):
        # this will load the self._parts dict according to config
        super(SocketAlignedKey, self).__init__(config, socket_config, r, u)

        # set the assembly corner anchors to top of the socket
        # no additional alignment required
