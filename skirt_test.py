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

cube0 = Connector(AnchorCollection(cube_input_corners))
cube0.translate(0,0,25)
cube0.rotate(30,0,0)

cube1 = Connector(AnchorCollection(cube_input_corners))
cube1.translate(5,5,25)
cube1.rotate(15,0,0)

cube_connection = Connector(AnchorCollection(cube1.anchors()['back'] + cube0.anchors()['front']))

conf = configparser.ConfigParser()
conf['skirt'] = {}
conf['skirt']['wall_thickness'] = '2.0'
conf['skirt']['flare_len'] = '4.0'
conf['skirt']['flare_angle'] = '50.0'

skirt_edges = (
        (cube1.anchors()['top','left'], cube1.anchors()['front','left']),
        (cube1.anchors()['top','right'], cube1.anchors()['front','right']),
        (cube1.anchors()['top','front'], cube1.anchors()['front','right']),
        (cube1.anchors()['top','back'], cube1.anchors()['back','right']),
        (cube0.anchors()['top','front'], cube0.anchors()['front','right']),
        (cube0.anchors()['top','back'], cube0.anchors()['back','right']),

        (cube0.anchors()['top','right'], cube0.anchors()['back','right']),
        (cube0.anchors()['top','left'],  cube0.anchors()['back','left']),
        (cube0.anchors()['top','back'],  cube0.anchors()['back','left']),
        (cube0.anchors()['top','front'], cube0.anchors()['front','left']),
        (cube1.anchors()['top','back'],  cube1.anchors()['back','left']),
        (cube1.anchors()['top','front'], cube1.anchors()['front','left']))

skirt = FlaredSkirt(skirt_edges, conf['skirt'])

solids = cube0.solid() + cube1.solid() + cube_connection.solid()
solids += skirt.solid()

sl.scad_render_to_file(solids, 'skirt_test.scad')

