from typing import Sequence, Union, Set

from keebgen.geometry_base import AnchorCollection, CuboidAnchorCollection, LabeledPoint
from keebgen.connector import Connector

cube_input_corners = [
        LabeledPoint((0, 0, 0), ('bottom', 'left', 'back')),
        LabeledPoint((1, 0, 0), ('bottom', 'right', 'back')),
        LabeledPoint((1, 1, 0), ('bottom', 'right', 'front')),
        LabeledPoint((0, 1, 0), ('bottom', 'left', 'front')),
        LabeledPoint((0, 0, 1), ('top', 'left', 'back')),
        LabeledPoint((1, 0, 1), ('top', 'right', 'back')),
        LabeledPoint((1, 1, 1), ('top', 'right', 'front')),
        LabeledPoint((0, 1, 1), ('top', 'left', 'front'))
            ]

cube_anchors = AnchorCollection(cube_input_corners)
print('cube_anchors\n',cube_anchors)
print('\ntop_anchors\n',cube_anchors['top'])
print('\ntop_right_anchors\n',cube_anchors['top','right'])

print('\naccess each anchor object in achors')
for anchor in cube_anchors:
    print(anchor)

# alternatively
print('\naccess each xyz point in anchors')
for anchor in cube_anchors:
    # cannot reassign the point value using these becuase they are floats
    (x,y,z) = anchor.coords
    print(x,y,z)

# direct use of Anchors object in place of a list of points
# this also implies that the Anchor object works directly in place of an (x,y,z) list
cube_connector = Connector(cube_anchors)
cube_connector.to_file('anchor_cube.scad')

#############################################
# Anchor is now an object, so its possible to modify in place.
# Connector class has been modified to use Anchors() class,
# now the Connector will move and scale with the Anchors object as needed

scale = 10
for anchor in cube_anchors:
    # can modify the anchor.point tuple without worrying about unlinking it from other objects
    # stretch anchor locations by 10
    anchor.translate(scale, scale, scale)

# cube_connector was not modified, but will be scaled with the cube_anchors that were passed in to construct it
cube_connector.to_file('scaled_anchor_cube.scad')


######## make cuboid shaped anchors without all of the corners definitions
# cube_corners can be unsorted list of corner coordinates for a cube-like shape len=8
cube_corners = [ (0, -3, 0), (15, 0, 0), (11, 13, 0), (0, 8, 0),
                 (0, -8, 12), (12, 0, 8), (15, 12, 10), (0, 11, 10) ]
cuboid_anchors = CuboidAnchorCollection(cube_corners)
Connector(cuboid_anchors).to_file('cuboid_anchors.scad')

