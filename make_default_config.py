import configparser

conf = configparser.ConfigParser()

# socket class parameters
conf['socket'] = {}
socket_conf = conf['socket']
socket_conf['overall_width'] = '18.0'
socket_conf['overall_length'] = '18.0'
socket_conf['switch_opening_width'] = '14.4'
socket_conf['switch_opening_length'] = '14.4'
socket_conf['plate_thickness'] = '4.0'
socket_conf['hot_swap'] = 'false'
socket_conf['side_nubs'] = 'true'

conf['key_assy'] = {}
key_conf = conf['key_assy']
key_conf['switch_type'] = 'cherry_mx'
key_conf['keycap_type'] = 'oem'

conf['column'] = {}
col_conf = conf['column']
col_conf['num_keys'] = '4' # number of keys in column
col_conf['home_index'] = '1' # 0 indexed, starting with bottom-most key
col_conf['radius'] = '55'
col_conf['key_gap'] = '2.25'
col_conf['key_lean'] = '0.0'

with open('default_config.ini', 'w') as configfile:
    conf.write(configfile)
