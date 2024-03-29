import unittest
from keebgen.geometry_base import CuboidAnchorCollection, Assembly, PartCollection, AnchorCollection
from keebgen.connector import Connector
import copy

# convenience function
def anchors_equal(anchors1, anchors2):
    if len(anchors1) != len(anchors2):
        return False

    # check that all anchors in anchor1 exist and are equal to anchors2
    for anchor1 in anchors1:
        anchor2_collection = anchors2[anchor1.labels]

        if len(anchor2_collection) != 1:
            # more than one anchor exists in anchors2 with these labels
            return False
        anchor2 = anchor2_collection.labeled_points[0]

        # check that each coordinate matches
        for anchor1_coord, anchor2_coord in zip(anchor1.coords, anchor2.coords):
            if anchor1_coord != anchor2_coord:
                return False
    return True


class AnchorCollectionTests(unittest.TestCase):
    def test_basic(self):
        c = CuboidAnchorCollection.create()
        assert len(set(c['left']) & set(c['right'])) == 0
        assert len(set(c['left']) | set(c['right'])) == 8

        #TODO: check that
        # 4 smallest X vals are left
        # 4 largest X vals are right
        # 4 smallest Y values are back
        # 4 largest Y values are front
        # 4 smallest Z values are bottom
        # 4 largest Z values are top

        # do the same for CuboidAnchorCollection generated from non-unit coords
        # cube_corners = [ (0, -3, 0),  (15, 0, 0), (11, 13, 0),  (0, 8, 0),
        #                  (0, -8, 12), (12, 0, 8), (15, 12, 10), (0, 11, 10) ]


class AnchorLinkTest(unittest.TestCase):
    def test_basic(self):
        cube_anchors = CuboidAnchorCollection.create()
        cube_part = Connector(cube_anchors)

        # test upfront that the coordinates match before doing anything
        for anchor, part_anchor in zip(cube_anchors, cube_part.anchors()):
            for anchor_coord, part_coord in zip(anchor.coords, part_anchor.coords):
                self.assertEqual(anchor_coord, part_coord, 'initial part anchors do not match input anchors')

        # translations
        x = 10
        y = 20
        z = 30

        # translate anchors only
        cube_anchors.translate(x, y, z)
        self.assertTrue(anchors_equal(cube_anchors, cube_part.anchors()),
                'part anchors do not match input anchors after translating anchors')

        # translate part only
        cube_part.translate(x, y, z)
        self.assertTrue(anchors_equal(cube_anchors, cube_part.anchors()),
                'part anchors do not match input anchors after translating part')

        #TODO: need to make sure that an exported .scad file matches the expected shape


class ConnectorLinkTest(unittest.TestCase):
    def test_basic(self):
        # make two cubes, and a connector from one to the other
        # translate one cube and make sure connector anchors follow
        cube1_anchors = CuboidAnchorCollection.create()
        cube1_part = Connector(cube1_anchors)
        cube2_anchors = CuboidAnchorCollection.create()
        cube2_part = Connector(cube2_anchors)

        # make sure everything starts out equal
        self.assertTrue(anchors_equal(cube1_anchors, cube1_part.anchors()),
                'initial part anchors do not match input anchors for cube1')
        self.assertTrue(anchors_equal(cube2_anchors, cube2_part.anchors()),
                'initial part anchors do not match input anchors for cube2')
        self.assertTrue(anchors_equal(cube1_anchors, cube2_anchors),
                'initial cube1 anchors do not match cube2 anchors')

        connector_anchors = cube1_anchors['right'] + cube2_anchors['left']
        cube_connector = Connector(connector_anchors)

        self.assertTrue(anchors_equal(connector_anchors, cube_connector.anchors()),
                'initial cube_connector anchors do not match input connectors')

        # translate in x only
        cube2_part.translate(10, 0, 0)
        self.assertTrue(anchors_equal(cube1_anchors['right']+cube2_anchors['left'], cube_connector.anchors()),
                'connector anchors do not match cube anchors after translation')

        #TODO: need to make sure that an exported .scad file matches the expected shape


class MultipleTranslationTest(unittest.TestCase):
    # simple assebly to be used by the test
    class TestAssembly(Assembly):
        def __init__(self, part1, part2, connector):
            super().__init__()
            self._parts = PartCollection()
            self._anchors = AnchorCollection(())
            self._parts.add(part1, 'part1')
            self._parts.add(part2, 'part2')
            self._parts.add(connector, 'connector')

    def test_basic(self):
        cube1_anchors = CuboidAnchorCollection.create()
        cube1_part = Connector(cube1_anchors)
        cube2_anchors = CuboidAnchorCollection.create()
        cube2_part = Connector(cube2_anchors)
        connector_anchors = cube1_anchors['right'] + cube2_anchors['left']
        cube_connector = Connector(connector_anchors)

        # make sure everything starts out equal
        self.assertTrue(anchors_equal(cube1_anchors, cube1_part.anchors()),
                'initial part anchors do not match input anchors for cube1')
        self.assertTrue(anchors_equal(cube2_anchors, cube2_part.anchors()),
                'initial part anchors do not match input anchors for cube2')
        self.assertTrue(anchors_equal(connector_anchors, cube_connector.anchors()),
                'initial cube_connector anchors do not match input connectors')

        # translations
        x = 10
        y = 20
        z = 30
        assembly = MultipleTranslationTest.TestAssembly(cube1_part, cube2_part, cube_connector)

        # make a deep copy of the anchors to be translated directly
        part1_anchors_reference = copy.deepcopy(assembly.anchors_by_part('part1'))
        part2_anchors_reference = copy.deepcopy(assembly.anchors_by_part('part2'))
        connector_anchors_reference = copy.deepcopy(assembly.anchors_by_part('connector'))

        assembly.translate(x,y,z)

        # translate reference anchors by themselves
        part1_anchors_reference.translate(x,y,z)
        part2_anchors_reference.translate(x,y,z)
        connector_anchors_reference.translate(x,y,z)

        part1_anchors = assembly.anchors_by_part('part1')
        part2_anchors = assembly.anchors_by_part('part2')
        connector_anchors = assembly.anchors_by_part('connector')

        # make sure assembly anchors translated same amount as reference
        # assembly anchors may be double translated, specifically the Connector anchors
        self.assertTrue(anchors_equal(part1_anchors, part1_anchors_reference),
                'assembly translate does not match anchors only translate for part1')
        self.assertTrue(anchors_equal(part2_anchors, part2_anchors_reference),
                'assembly translate does not match anchors only translate for part2')
        self.assertTrue(anchors_equal(connector_anchors, connector_anchors_reference),
                'assembly translate does not match anchors only translate for connector')

        #TODO: need to make sure that an exported .scad file matches the expected shape
        # in current config, all three cubes are overlapping unit cubes

if __name__ == '__main__':
    unittest.main()
