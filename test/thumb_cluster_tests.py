import unittest
from keebgen.geometry_base import CuboidAnchorCollection
from keebgen.thumb_cluster import DactylThumbCluster, ManuformThumbCluster

from pathlib import Path

class ThumbClusterTests(unittest.TestCase):

    def test_basic(self):
        import configparser
        config = configparser.ConfigParser()
        config_path = Path(__file__).resolve().parent.parent / 'default_config.ini'
        config.read(config_path)
        key_config = config['key_assy']
        socket_config = config['socket']


        tc = DactylThumbCluster(key_config, socket_config)

        intermediates_dir = Path(__file__).resolve().parent.parent / 'intermediates'
        tc.to_file(intermediates_dir / 'dactyl_thumb_cluster.scad')

        tc = ManuformThumbCluster(key_config, socket_config)
        tc.to_file(intermediates_dir / 'manuform_thumb_cluster.scad')
