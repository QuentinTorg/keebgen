from numpy import pi
from scipy.spatial.transform import Rotation

def deg2rad(degrees: float) -> float:
    return degrees * pi / 180


def rad2deg(rad: float) -> float:
    return rad * 180 / pi

# eulers are xyz euler angle in degrees
# can rotate single point or N points
# 3 vecotr, or 3xN vector of points
def rotate_points(points, eulers, degrees=True):
    r = Rotation.from_euler('xyz', eulers, degrees=degrees)
    return r.apply(points)

# for convenience to match translation syntax
def rotate_point(point, eulers, degrees=True):
    return rotate_points(point, eulers, degrees)


def translate_point(p, t):
    assert len(t) == 3
    assert len(p) == 3
    return [p[0] + t[0],
            p[1] + t[1],
            p[2] + t[2]]

def translate_points(points, t):
    new_points = []
    for point in points:
        new_points.append(translate_point(point, t))
    return new_points
