import solid as sl
from pathlib import Path
import configparser

# within project
from keebgen.switch_socket import CherryMXSocket
from keebgen.keycap import OEM

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

    # key cap
    keycapsolid = OEM(1,1).solid()
    for r in range(2, 5):
        keycapsolid = sl.translate([0, 19, 0])(keycapsolid)
        keycapsolid += OEM(r,1).solid()
    keycap_output = intermediates_dir / 'keycaps.scad'
    sl.scad_render_to_file(keycapsolid, keycap_output)

    # key caps


if __name__ == '__main__':
    main()
