from abc import abstractmethod

from .geometry_base import Assembly
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
            self._parts['socket'] = socket.CherryMXSocket(socket_config, u)
        else:
            raise Exception('socket for switch type ' + config.get('switch_type') + ' not implemented')

        if config.get('keycap_type') == 'oem':
            self._parts['keycap'] = keycap.OEM(r, u)
        else:
            raise Exception('keycap type ' + config.get('keycap_type') + ' not implemented')


# FaceAlignedKeys will have the faces forming a smooth curve on the keybaord regardless of switch and keycap type
class FaceAlignedKey(KeyAssy):
    def __init__(self, config, socket_config, r, u=1):
        # this will load the self._parts dict according to config
        super(FaceAlignedKey, self).__init__(config, socket_config, r, u)
        # set the assembly corner anchors to top of the socket

        self._anchors = self.anchors('keycap')['top']

        # reorient the key and switch together so the top face of the keycap is centered
        # on the z axis and coplanar with the xy plane

        # assumes a symmetrical keycap from left to right




# simplest case, the switches are aligned based on the socket.
# should be used for plate mount boards
class SocketAlignedKey(KeyAssy):
    def __init__(self, config, socket_config, r, u=1):
        # this will load the self._parts dict according to config
        super(FaceAlignedKey, self).__init__(config, socket_config, r, u)

        # set the assembly corner anchors to top of the socket
        self._anchors = self.anchors('socket')['top']
        # no additional alignment required
