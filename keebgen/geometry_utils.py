from numpy import pi
from scipy.spatial.transform import Rotation
from numpy.linalg import norm
import numpy as np

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

# return the mean of the individual x, y, and z values of points
def mean_point(points):
    # TODO this is inelegant but I was sure it would work. could use cleanup and a test
    mean_point = [0, 0, 0]
    for point in points:
        assert len(point) == 3
        mean_point[0] += point[0]
        mean_point[1] += point[1]
        mean_point[2] += point[2]

    mean_point[0] = mean_point[0] / len(points)
    mean_point[1] = mean_point[1] / len(points)
    mean_point[2] = mean_point[2] / len(points)
    return mean_point

# return vector of length one pointing from 1->2
def unit_vector(point1, point2):
    point1 = np.array(point1)
    point2 = np.array(point2)
    dir_vec = point2 - point1
    return dir_vec / norm(dir_vec)
