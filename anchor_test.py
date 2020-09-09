
from keebgen.geometry_base import Anchors

cube_input_corners = [
            ((0, 0, 0), ('bottom', 'left', 'back')),
            ((1, 0, 0), ('bottom', 'right', 'back')),
            ((1, 1, 0), ('bottom', 'right', 'front')),
            ((0, 1, 0), ('bottom', 'left', 'front')),
            ((0, 0, 1), ('top', 'left', 'back')),
            ((1, 0, 1), ('top', 'right', 'back')),
            ((1, 1, 1), ('top', 'right', 'front')),
            ((0, 1, 1), ('top', 'left', 'front'))
            ]

cube_anchors = Anchors(cube_input_corners)
print('cube_anchors',cube_anchors)
print('top_anchors',cube_anchors('top'))
print('top_right_anchors',cube_anchors('top','right'))
