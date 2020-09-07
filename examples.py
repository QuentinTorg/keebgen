import solid as sl
from pathlib import Path
import configparser

# within project
from keebgen.switch_socket import CherryMXSocket
from keebgen.keycap import OEM
from keebgen.key_assy import SocketAlignedKey, FaceAlignedKey
from keebgen.key_column import CurvedOrtholinearColumn

def main():
    config = configparser.ConfigParser()
    config.read('default_config.ini')

#    intermediates_dir = Path(__file__).resolve().parent.parent / 'intermediates'
    intermediates_dir = Path(__file__).resolve().parent / 'intermediates'
    intermediates_dir.mkdir(exist_ok=True)

    # key switch socket
    socket = CherryMXSocket(config['socket'])
    socket_output = intermediates_dir / 'socket.scad'
    sl.scad_render_to_file(socket.solid(), socket_output)

    # keycap
    keycaps = []
    for r in range(1, 5):
        keycap = OEM(r,1)
        keycap.translate(0, 19*(4-r), 0)
        keycaps.append(keycap)

    keycapsolid = sl.part()
    for key in keycaps:
        keycapsolid += key.solid()
    keycap_output = intermediates_dir / 'keycaps.scad'
    sl.scad_render_to_file(keycapsolid, keycap_output)


    # key_assy
    socket_aligned_keys = []
    face_aligned_keys = []
    for r in range(1, 5):
        socket_key = SocketAlignedKey(config['key_assy'], config['socket'],r)
        socket_key.translate(0, 19*(4-r), 0)
        socket_aligned_keys.append(socket_key)
        face_key = FaceAlignedKey(config['key_assy'], config['socket'],r)
        face_key.translate(0, 19*(4-r), 0)
        face_aligned_keys.append(face_key)

    key_solid = sl.part()
    for key in socket_aligned_keys:
        key_solid += key.solid()
    socket_aligned_keys_output = intermediates_dir / 'socket_aligned_keys.scad'
    sl.scad_render_to_file(key_solid, socket_aligned_keys_output)

    key_solid = sl.part()
    for key in face_aligned_keys:
        key_solid += key.solid()
    face_aligned_keys_output = intermediates_dir / 'face_aligned_keys.scad'
    sl.scad_render_to_file(key_solid, face_aligned_keys_output)

    curved_column = CurvedOrtholinearColumn(config['column'], config['key_assy'], config['socket'])
    col_output = intermediates_dir / 'curved_column.scad'
    sl.scad_render_to_file(curved_column.solid(), col_output)


if __name__ == '__main__':
    main()
