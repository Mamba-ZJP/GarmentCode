

import numpy as np
from copy import copy
from numpy.linalg import norm
from numpy.polynomial import polynomial as npoly
import matplotlib.pyplot as plt
from scipy.optimize import minimize
from pprint import pprint

def _rel_to_abs_coords(start, end, vrel):
        """Convert coordinates specified relative to vector v2 - v1 to world coords"""
        start, end, vrel = np.asarray(start), np.asarray(end), np.asarray(vrel)
        vec = end - start
        vec = vec / norm(vec)
        vec_perp = np.array([-vec[1], vec[0]])
        
        new_start = start + vrel[0] * vec
        new_point = new_start + vrel[1] * vec_perp

        return new_point 

def dart(v0, v1, width, depth, location=0.5, right=True):

    # Targets
    L = norm(v1 - v0)
    d0, d1 = L * location, L * (1 - location)
    depth_perp = np.sqrt((depth**2 - (width / 2)**2))
    dart_side = depth

    # Extended triangle 
    delta_l = dart_side * width / (2 * depth_perp)  # extention of edge length beyong the dart points
    side0, side1 = d0 + delta_l, d1 + delta_l
    
    # long side
    alpha = abs(np.arctan(width / 2 / depth_perp))  # half of dart tip angle
    top_angle = np.pi - 2*alpha  # top of the triangle (v0, imaginative dart top, v1)
    long_side = np.sqrt(side0**2 + side1**2 - 2*side0*side1*np.cos(top_angle))
    
    # angles
    sin0, sin1 = side1 * np.sin(top_angle) / long_side, side0 * np.sin(top_angle) / long_side
    angle0, angle1 = np.arcsin(sin0), np.arcsin(sin1)

    # Find the location of dart points
    p1x = d0 * np.cos(angle0)
    p1y = d0 * sin0
    p1 = np.array([p1x, p1y])

    p1 = _rel_to_abs_coords(v0, v1, p1)
    new_v1 = _rel_to_abs_coords(v0, v1, np.array([long_side, 0]))

    # Other dart vertices
    p2x = long_side - (d1 * np.cos(angle1))
    p2y = d1 * sin1
    p2 = np.array([p2x, p2y])
    p2 = _rel_to_abs_coords(v0, v1, p2)

    p_vec = p2 - p1
    p_perp = np.array([-p_vec[1], p_vec[0]])
    p_perp = p_perp / norm(p_perp) * depth_perp

    p_tip = p1 + p_vec / 2 - p_perp

    print('Tip location: ', p_tip, p_vec, p_perp, norm(p_tip - p1))

    print('Depth: ', norm(p_tip - p1), norm(p_tip - p2))
    print('Width: ', norm(p2 - p1))
    print('Total Length requested: ', d0, d1, norm(v1 - v0))
    print('Total Length: ', norm(p1 - v0), norm(p2 - new_v1), norm(p1 - v0) + norm(p2 - new_v1))

    dart_points = [p1, p_tip, p2]

    if not right:
        # flip dart to be the left of the vector
        dart_points = _reflect(dart_points, v0, new_v1)
    

    # return np.array([v0, dart_st_point, _rel_to_abs_coords(v0, v1, p_tip),  _rel_to_abs_coords(v0, v1, p2), new_v1_1])
    return np.array([v0] + dart_points + [new_v1])
    # return np.array([v0, dart_st_point, dart_st_point + np.array([width / 2, -depth_perp]), dart_st_point + np.array([width, 0]), new_v1, new_v1_1])


def dart_len(v0, v1, target_length, depth, location=0.5, right=True, theta=90):

    # Targets
    d0, d1 = target_length * location, target_length * (1 - location)

    # DRAFT
    # Initial guess
    v = (v1 - v0) / norm(v1 - v0)
    p0 = v0 + v * norm(v1-v0) * location
    p1 = copy(p0)
    vperp = np.asarray([v[1], -v[0]]) 
    p_tip = p0 + depth * vperp
    guess = np.concatenate([p0, p_tip, p1])

    print(p1, p0)
    print(d0, norm(p0 - v0), d1, norm(p1 - v1))

    # Optimize
    out = minimize(
        equations, guess, args=(v0, v1, d0, d1, depth, theta))

    p0, p_tip, p1 = out.x[:2], out.x[2:4], out.x[4:]

    print(out)

    if abs(out.fun) > 1e-4:
        raise RuntimeError('Failed to evaluate the dart')

    # Result
    print('Tip location: ', p_tip, norm(p_tip - p1))
    print('Depth: ', norm(p_tip - p0), norm(p_tip - p1))
    print('Width: ', norm(p0 - p1))
    print('Total Length requested: ', d0, d1, norm(v1 - v0))
    print('Total Length: ', norm(p0 - v0), norm(p1 - v1), norm(v1 - v0))

    dart_points = [p0, p_tip, p1]

    right_position = np.sign(np.cross(v1 - v0, p_tip - v0)) == -1 
    if not right and right_position or right and not right_position:
        # flip dart to be the left of the vector
        dart_points = _reflect(dart_points, v0, v1)

    return np.array([v0] + dart_points + [v1])


def _reflect(points, v0, v1):
    """Reflect 2D points w.r.t. 1D line defined by two points"""
    vec = v1 - v0
    vec = vec / norm(vec)  # normalize

    # https://demonstrations.wolfram.com/ReflectionMatrixIn2D/#more
    Ref = np.array([
        [ 1 - 2 * vec[1]**2,  2*vec[0]*vec[1]],
        [ 2*vec[0]*vec[1],    - 1 + 2 * vec[1]**2 ]
        ])
    
    # translate -> reflect -> translate back
    return [np.matmul(Ref, p - v0) + v0 for p in points]

def softsign(x):
    return x / (abs(x) + 1)

# DRAFT
def equations(coords, v0, v1, d0, d1, depth, theta=90):

    theta = np.deg2rad(theta)

    p0, p, p1 = coords[:2], coords[2:4], coords[4:]
    error = {}

    # Distance constraints
    error['d0'] = (norm(p0 - v0) - d0)**2
    error['d1'] = (norm(p1 - v1) - d1)**2

    # Depth constraint
    error['depth0'] = (norm(p0 - p) - depth)**2
    error['depth1'] = (norm(p1 - p) - depth)**2

    # Angle constraint
    # error['perp0'] = (np.dot(p - p0, v0 - p0))**2
    # error['perp1'] = (np.dot(p - p1, v1 - p1))**2
    # TODO arbitrary angle 
    # DRAFT -- doesn't give good solution
    error['angle0'] = (np.dot(p - p0, v0 - p0) - np.cos(theta) * d0 * depth)**2
    # cos(pi - theta) = - cos(theta)
    error['angle1'] = (np.dot(p - p1, v1 - p1) + np.cos(theta) * d1 * depth)**2

    # same side w.r.t to v0-v1
    # error['side0'] = (softsign(np.cross(v1 - v0, p0 - v0)) - 1)**2 / 4
    # error['side1'] = (softsign(np.cross(v1 - v0, p1 - v0)) - 1)**2 / 4
    error['side'] = (softsign(np.cross(v1 - v0, p1 - v0)) - softsign(np.cross(v1 - v0, p0 - v0)))**2 / 4
    # error['angle'] = (softsign(np.dot(p0 - p, p1 - p)) - 1)**2 / 4

    # Minimize angle at dart tip
    # error['angle'] = (np.cross(p0 - p, p1 - p))**2

    pprint(error)
    print('Total: ', sum(error.values()))

    return sum(error.values())



# edge_side = dart(np.array([50, -20]), np.array([50, 15]), 5, 20, location=0.2, right=False)
# edge_side = dart_len(np.array([-21.5, 0]), np.array([-21.5, 70]), 70*0.95, 20, location=0.3, right=False)
# edge_side = dart_len(np.array([-20, 0]), np.array([15, 0]), 30, 20, location=0.2, right=False)
edge_side = dart_len(
    np.array([0, 0]), np.array([45, 0]), target_length=40, depth=12, 
    location=12/40, right=True, theta=90)

plt.plot(edge_side[:, 0], edge_side[:, 1], marker='o')
plt.title('Dart')
plt.xlabel('x')
plt.ylabel('y')
plt.grid(True)  
plt.axis('equal')
plt.show()