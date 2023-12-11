from keebgen.better_abc import abstractmethod
from .geometry_base import Assembly, PartCollection, AnchorCollection

# TODO remove this when configs updated
import configparser

from .key_column import ConcaveOrtholinearColumn
from .connector import Connector
from .thumb_cluster import ManuformThumbCluster
from .skirt import FlaredSkirt

class Keyboard(Assembly):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self._parts = PartCollection()


class DactylManuform(Keyboard):
    def __init__(self, config, col_config, key_config, socket_config):
        super().__init__()

        # TODO add config parsing. this is terrible right now
        # there should ideally be a different column config for each row, but this will do for proof of concept
        # all of these numbers should come from the config file or default config
        # TODO will want different spacing for end cols if they are tilted
        num_cols = 6

        index_radius = 56.4
        index_first_digit_len = 55.5

        middle_radius = 65.0
        middle_first_digit_len = 62

        ring_radius = 64.0
        ring_first_digit_len = 59

        pinky_radius = 48.9
        pinky_first_digit_len = 44

        section_name = 'column'
        col_configs = []
        for col in range(num_cols):
            new_conf = configparser.ConfigParser()
            new_conf.add_section(section_name)
            for key in col_config:
                new_conf.set(section_name, key, col_config.get(key))
            # add extra row a t bottom for middle and ring fingers

            if col == 2 or col == 3:
                new_conf.set(section_name, 'num_keys', str(5))
                new_conf.set(section_name, 'home_index', str(2))

            # set side lean
            if col == 0:
                new_conf.set(section_name, 'key_side_lean', str(20))
                new_conf.set(section_name, 'show_finger_wireframe', 'false')
            elif col == num_cols-1:
                new_conf.set(section_name, 'key_side_lean', str(-20))
                new_conf.set(section_name, 'show_finger_wireframe', 'false')

            # set radius by finger
            if col <= 1:
                new_conf.set(section_name, 'radius', str(index_radius))
                new_conf.set(section_name, 'first_digit_len', str(index_first_digit_len))
            elif col == 2:
                new_conf.set(section_name, 'radius', str(middle_radius))
                new_conf.set(section_name, 'first_digit_len', str(middle_first_digit_len))
            elif col == 3:
                new_conf.set(section_name, 'radius', str(ring_radius))
                new_conf.set(section_name, 'first_digit_len', str(ring_first_digit_len))
            else:
                new_conf.set(section_name, 'radius', str(pinky_radius))
                new_conf.set(section_name, 'first_digit_len', str(pinky_first_digit_len))

            col_configs.append(new_conf[section_name])

        col_x_spacing = 19.0 #mm

        sub_pointer_y_off = 0
        pointer_y_off = 0
        middle_y_off = 11
        ring_y_off = 3
        pinky_y_off = -19
        post_pinky_y_off = pinky_y_off

        sub_pointer_z_off = 3
        pointer_z_off = 0
        middle_z_off = 5
        ring_z_off = -2.5
        pinky_z_off = -6.5
        post_pinky_z_off = pinky_z_off + 3

        prev_name = None
        for col_num, col_config in enumerate(col_configs):
            name = col_num
            self._parts.add(ConcaveOrtholinearColumn(col_config, key_config, socket_config), name)

            #TODO this should be part of the config
            col_fudge = 0
            if col_num < 1:
                col_fudge = 3.5
                y_off = sub_pointer_y_off
                z_off = sub_pointer_z_off
            elif col_num == 1:
                y_off = pointer_y_off
                z_off = pointer_z_off
            elif col_num == 2:
                y_off = middle_y_off
                z_off = middle_z_off
            elif col_num == 3:
                y_off = ring_y_off
                z_off = ring_z_off
            elif col_num == 4:
                y_off = pinky_y_off
                z_off = pinky_z_off
            else:
                col_fudge = -3.5
                y_off = post_pinky_y_off
                z_off = post_pinky_z_off

            # all column positioning must happen before the connectors are made
            shift = col_num - 1
            self._parts.translate(col_x_spacing*shift+col_fudge, y_off, z_off, name=name)

            if prev_name is not None:
                # add connectors between previous col and this col
                # must check if row in this col existed in prev cal and vv.
                prev_col = self.get_part(prev_name)
                cur_col = self.get_part(name)

                #TODO make this prettier
                prev_col_prev_anchors = None
                cur_col_prev_anchors = None
                for row in range(-6, 6):
                    try:
                        prev_col_key = prev_col.get_part(row)
                        prev_col_anchors = prev_col_key.anchors_by_part('socket')
                    except:
                        prev_col_key = prev_col_anchors = None

                    try:
                        cur_col_key = cur_col.get_part(row)
                        cur_col_anchors = cur_col_key.anchors_by_part('socket')
                    except:
                        cur_col_key = cur_col_anchors = None

                    # TODO this is really annoying
                    # naming is bad too, "connect connectors"

                    # normal case, both connectors exist
                    # connect adjacent socket edges
                    if prev_col_anchors and cur_col_anchors:
                        self._parts.add(Connector(prev_col_anchors['right'] +
                                                  cur_col_anchors['left']))
                        # self._parts.add(Connector(prev_col_anchors['bottom']))


                    # cur and prev rows exist for both cols
                    # connect the connectors that are between the cur and prev rows for each col
                    if prev_col_anchors and prev_col_prev_anchors and cur_col_anchors and cur_col_prev_anchors:
                        self._parts.add(Connector(prev_col_anchors['right', 'back'] +
                                                  prev_col_prev_anchors['right', 'front'] +
                                                  cur_col_anchors['left', 'back'] +
                                                  cur_col_prev_anchors['left', 'front']))


                    # these four conditionals handle the end conditions when one col is shorter than the other

                    # prev_col one longer on bottom
                    if prev_col_anchors and prev_col_prev_anchors and cur_col_anchors and not cur_col_prev_anchors:
                        self._parts.add(Connector(prev_col_anchors['right', 'back'] +
                                                 prev_col_prev_anchors['right'] +
                                                 cur_col_anchors['left', 'back']))

                    # cur_col one longer on bottom
                    if prev_col_anchors and not prev_col_prev_anchors and cur_col_anchors and cur_col_prev_anchors:
                        self._parts.add(Connector(prev_col_anchors['right', 'bottom'] +
                                                 cur_col_anchors['left', 'bottom'] +
                                                 cur_col_prev_anchors['left']))

                    # prev_col one longer on top
                    if prev_col_anchors and prev_col_prev_anchors and not cur_col_anchors and cur_col_prev_anchors:
                        self._parts.add(Connector(prev_col_anchors['right'] +
                                                 prev_col_prev_anchors['right', 'front'] +
                                                 cur_col_prev_anchors['left', 'front']))

                    # cur_col one longer on top
                    if not prev_col_anchors and prev_col_prev_anchors and cur_col_anchors and cur_col_prev_anchors:
                        self._parts.add(Connector(prev_col_prev_anchors['right', 'front'] +
                                                 cur_col_anchors['left'] +
                                                 cur_col_prev_anchors['left', 'front']))

                    prev_col_prev_anchors = prev_col_anchors
                    cur_col_prev_anchors = cur_col_anchors

            prev_name = name

        thumbcluster = ManuformThumbCluster(key_config, socket_config)
        # offset based on home key position
        tc_home_key = thumbcluster.home_key
        col = self._parts.get(1)

        # TODO: improve column and row naming so this is readable.

        # hand tuned alignment
        thumbcluster.rotate(20, -30, 20, degrees=True)
        thumbcluster.translate(-5,-3,-7)

        anchor_pos = list(col.get_part(-1).anchors.centroid())
        anchor_pos[1] -= tc_home_key.anchors.bounds()[1]  # shift alone y axis
        tc_offset = [x for x in anchor_pos]
        thumbcluster.translate(*tc_offset)

        self._parts.add(thumbcluster)

        # add connectors between the thumb cluster and the keyboard
        thumb_key1 = thumbcluster.key_grid.grid[0][1].get_part('socket')
        thumb_key2 = thumbcluster.key_grid.grid[0][2].get_part('socket')
        thumb_key3 = thumbcluster.key_grid.grid[0][3].get_part('socket')

        bottom_left_key0 = self._parts.get(0).get_part(-1).get_part('socket')
        bottom_left_key1 = self._parts.get(1).get_part(-1).get_part('socket')
        bottom_left_key2 = self._parts.get(2).get_part(-2).get_part('socket')
        bottom_left_key3 = self._parts.get(3).get_part(-2).get_part('socket')

        self._parts.add(Connector(thumb_key1.anchors['left'] +
                                  bottom_left_key0.anchors['left','front']))

        self._parts.add(Connector(thumb_key1.anchors['left','front'] +
                                  thumb_key2.anchors['left','back'] +
                                  bottom_left_key0.anchors['left']))

        self._parts.add(Connector(thumb_key2.anchors['left'] +
                                  bottom_left_key0.anchors['back']))

        self._parts.add(Connector(thumb_key3.anchors['left'] +
                                  bottom_left_key1.anchors['back']))

        self._parts.add(Connector(thumb_key2.anchors['left','front'] +
                                  thumb_key3.anchors['left','back'] +
                                  bottom_left_key0.anchors['back','right'] +
                                  bottom_left_key1.anchors['back','left']))

        self._parts.add(Connector(thumb_key3.anchors['left','front'] +
                                  bottom_left_key2.anchors['back','left'] +
                                  bottom_left_key1.anchors['back','right']))

        self._parts.add(Connector(thumb_key3.anchors['left','front'] +
                                  bottom_left_key2.anchors['back'] +
                                  bottom_left_key3.anchors['back','left']))

        self._parts.add(Connector(thumb_key3.anchors['front'] +
                                  bottom_left_key3.anchors['back','left']))



        # load the skirt
        edge_pairs = []

        # left side
        for (num, socket_name) in enumerate(self.get_part(0).get_key_names()):
            anchors = self.get_part(0).get_part(socket_name).anchors_by_part('socket')
            if num != 0:
                edge_pairs.append((anchors['top','back'], anchors['left','back']))
            edge_pairs.append((anchors['top','front'], anchors['left','front']))

        # top
        for col_name in range(len(col_configs)):
            col = self.get_part(col_name)
            top_socket_name = col.get_key_names()[-1]
            anchors = col.get_part(top_socket_name).anchors_by_part('socket')
            edge_pairs.append((anchors['top','left'], anchors['front','left']))
            edge_pairs.append((anchors['top','right'], anchors['front','right']))

        # right, returning reversed list
        for socket_name in reversed(self.get_part(len(col_configs)-1).get_key_names()):
            anchors = self.get_part(len(col_configs)-1).get_part(socket_name).anchors_by_part('socket')
            edge_pairs.append((anchors['top','front'], anchors['right','front']))
            edge_pairs.append((anchors['top','back'], anchors['right','back']))

        # bottom, returning reversed list
        for col_name in reversed(range(len(col_configs))):
            col = self.get_part(col_name)
            bottom_socket_name = col.get_key_names()[0]
            anchors = col.get_part(bottom_socket_name).anchors_by_part('socket')
            if col_name > 2:
                edge_pairs.append((anchors['top','right'], anchors['back','right']))
                edge_pairs.append((anchors['top','left'], anchors['back','left']))

        # wrap around the thumb cluster
        thumb_anchors0 = thumbcluster.key_grid.grid[0][0].get_part('socket').anchors
        thumb_anchors1 = thumbcluster.key_grid.grid[0][1].get_part('socket').anchors
        thumb_anchors3 = thumbcluster.key_grid.grid[0][3].get_part('socket').anchors
        thumb_anchors4 = thumbcluster.key_grid.grid[1][0].get_part('socket').anchors
        thumb_anchors5 = thumbcluster.key_grid.grid[1][1].get_part('socket').anchors

        edge_pairs.append((thumb_anchors3['top','front'],thumb_anchors3['front','right']))
        edge_pairs.append((thumb_anchors3['top','back'],thumb_anchors3['back','right']))
        edge_pairs.append((thumb_anchors5['top','front'],thumb_anchors5['front','right']))
        edge_pairs.append((thumb_anchors5['top','back'],thumb_anchors5['back','right']))
        edge_pairs.append((thumb_anchors4['top','front'],thumb_anchors4['front','right']))
        edge_pairs.append((thumb_anchors4['top','back'],thumb_anchors4['back','right']))

        edge_pairs.append((thumb_anchors4['top','right'],thumb_anchors4['back','right']))
        edge_pairs.append((thumb_anchors4['top','left'],thumb_anchors4['back','left']))

        edge_pairs.append((thumb_anchors0['top','right'],thumb_anchors0['back','right']))
        edge_pairs.append((thumb_anchors0['top','left'],thumb_anchors0['back','left']))

        edge_pairs.append((thumb_anchors0['top','back'],thumb_anchors0['back','left']))
        edge_pairs.append((thumb_anchors0['top','front'],thumb_anchors0['front','left']))
        edge_pairs.append((thumb_anchors1['top','back'],thumb_anchors1['back','left']))
        #edge_pairs.append((thumb_anchors1['top','front'],thumb_anchors1['front','left']))


        # TODO add this to the config
        conf = configparser.ConfigParser()
        conf['skirt'] = {}
        conf['skirt']['wall_thickness'] = '2.0'
        conf['skirt']['flare_len'] = '4.0'
        conf['skirt']['flare_angle'] = '30.0'

        # TODO translation should happen based on the config, or based on the minimum Z height of all parts
        # to make sure all parts of the keyboard stay above the xy plane
        self._parts.translate(0,0,60)
        self._parts.rotate(0,20,0,degrees=True)
        self._parts.add(FlaredSkirt(edge_pairs, conf['skirt']), 'skirt')

        #TODO add anchors that make sense
        self._anchors = None
