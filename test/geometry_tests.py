import unittest
from keebgen.geometry_base import CuboidAnchorCollection


class AnchorCollectionTests(unittest.TestCase):
    def test_basic(self):
        c = CuboidAnchorCollection.create()
        assert len(set(c['left']) & set(c['right'])) == 0
        assert len(set(c['left']) | set(c['right'])) == 8


# TODO: need a test to verify translations don't get applied multiple times for nested parts.