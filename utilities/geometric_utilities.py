"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from math import acos
from numpy import arctan2

TOL = 1e-8


def euclidean_distance(points):
    return ((points[1][0] - points[0][0])**2 + (points[1][1] - points[0][1])**2)**0.5


def magnitude(vector):
    return (vector[0]**2 + vector[1]**2)**0.5


def angle_between_directions(directions):
    # https://in.mathworks.com/matlabcentral/answers/180131-how-can-i-find-the-angle-between-two-vectors-including-directional-information
    # https://docs.scipy.org/doc/numpy-1.10.4/reference/generated/numpy.arctan2.html

    # returns an array, only 2nd components needed
    return arctan2([directions[0][1], directions[1][1]],
                   [directions[0][0], directions[1][0]])[1]

    # return acos(dot_product(directions)/(magnitude(directions[0])* magnitude(directions[1])))


def dot_product(vectors):
    return vectors[0][0] * vectors[1][0] + vectors[0][1] * vectors[1][1]


def cross_product(vectors):
    return vectors[0][0] * vectors[1][1] - vectors[0][1] * vectors[1][0]


def are_parallel(lines):
    # this is the 2d cross product
    if abs(cross_product([lines[0]['direction'], lines[1]['direction']])) <= TOL:
        return True
    else:
        return False


def get_intersection(lines):
    if are_parallel(lines):
        print("The lines are PARALLEL")
        return None
    else:
        a1, b1, c1 = lines[0]['coefficients']
        a2, b2, c2 = lines[1]['coefficients']
        if abs(b2) <= TOL:  # line vertikal -> Teilen durch 0 -> vertauschen
            a1, b1, c1 = lines[1]['coefficients']
            a2, b2, c2 = lines[0]['coefficients']

        x = ((-1*(b2-b1)/b2+1)*c2-c1)/((a1-a2)+a2*(b2-b1)/b2)
        y = (-a2*x - c2)/b2

        # TODO: check for redundancy
        # http://www.pdas.com/lineint.html
        # denom:= a1*b2 - a2*b1
        # x:=(b1*c2 - b2*c1)/denom;
        # y:=(a2*c1 - a1*c2)/denom;

        a1, b1, c1 = lines[0]['coefficients']
        a2, b2, c2 = lines[1]['coefficients']

        denom = a1*b2 - a2*b1
        x = (b1*c2 - b2*c1)/denom
        y = (a2*c1 - a1*c2)/denom
        return [x, y]


def get_line_coefficients(points):
    p1 = points[0]
    p2 = points[1]
    # gibt a,b und c aus ax+by+c
    a = p1[1]-p2[1]
    b = p2[0]-p1[0]
    c = -(a * p1[0]+b*p1[1])
    return [a, b, c]


def get_line_by_point_and_direction(point, direction):
    points = [point]
    points.append([point[0] + direction[0],
                   point[1] + direction[1]])

    line = {}
    line['direction'] = direction
    line['coefficients'] = get_line_coefficients(points)
    return line
