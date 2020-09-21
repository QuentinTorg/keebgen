from keebgen.connector import Connector
from keebgen.geometry_base import AnchorCollection, LabeledPoint
from keebgen.skirt import FlaredSkirt
import configparser
import solid as sl


cube_input_corners = [
            LabeledPoint((0, 0, 0), ('bottom', 'left', 'back')),
            LabeledPoint((10, 0, 0), ('bottom', 'right', 'back')),
            LabeledPoint((10, 10, 0), ('bottom', 'right', 'front')),
            LabeledPoint((0, 10, 0), ('bottom', 'left', 'front')),
            LabeledPoint((0, 0, 3), ('top', 'left', 'back')),
            LabeledPoint((10, 0, 3), ('top', 'right', 'back')),
            LabeledPoint((10, 10, 3), ('top', 'right', 'front')),
            LabeledPoint((0, 10, 3), ('top', 'left', 'front'))
            ]

cube = Connector(AnchorCollection(cube_input_corners))
cube.translate(0,0,25)
cube.rotate(30,0,0)

conf = configparser.ConfigParser()
conf['skirt'] = {}
conf['skirt']['wall_thickness'] = '2.0'
conf['skirt']['flare_size'] = '5.0'

skirt_edges = (
        (cube.anchors()['top','left'], cube.anchors()['front','left']),
        (cube.anchors()['top','right'], cube.anchors()['front','right']),
        (cube.anchors()['top','front'], cube.anchors()['front','right']),
        (cube.anchors()['top','back'], cube.anchors()['back','right']),
        (cube.anchors()['top','right'], cube.anchors()['back','right']),
        (cube.anchors()['top','left'], cube.anchors()['back','left']),
        (cube.anchors()['top','back'], cube.anchors()['back','left']),
        (cube.anchors()['top','front'], cube.anchors()['front','left']))

skirt = FlaredSkirt(skirt_edges, conf['skirt'])

solids = cube.solid()
solids += skirt.solid()

sl.scad_render_to_file(solids, 'skirt_test.scad')

