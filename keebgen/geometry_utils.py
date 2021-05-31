from numpy import pi
from scipy.spatial.transform import Rotation
from numpy.linalg import norm
import numpy as np

def deg2rad(degrees: float) -> float:
    return np.deg2rad(degrees)

def rad2deg(rad: float) -> float:
    return np.rad2deg(rad)

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

# return the angle from one vector to the other. ccw is + rotation
# returns (-pi, pi]
def vector_angle_2D(vec1, vec2, degrees=True):
    assert len(vec1) == 2
    assert len(vec2) == 2

    # get angle between each and the horizontal, returns (0, 2pi]
    def horizon_angle(vec):
        # horizon is (1,0)
        mag = np.arctan2(vec[1], vec[0])
        if mag < 0:
            mag += (2*pi)
        return mag

    angle = horizon_angle(vec2) - horizon_angle(vec1)
    while angle > pi:
        angle -= (2*pi)
    while angle <= -pi:
        angle += (2*pi)

    if degrees:
        return rad2deg(angle)
    return angle
