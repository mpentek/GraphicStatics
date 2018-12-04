# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:03:45 2018

@author: Benedikt
"""

import numpy as np

# PMT remove sympy dependency
#from sympy import Point2D, Line2D

# own geometric entities
# from point import Point2D
# from line import Line2D

# own modules
# from geometric_utilities import translate_to_point

## PMT
'''
A line is defined by a point and a direction ==>> Line2D

A segment by 2 points (no specific direction) ==>> Segment2D (special case a a line)

A vector2d is a segment with a specific direction (special case of a segment)
==>> Force should be changed to Vector2D, whic maybe inherits from Segment2D

CHECK naming, maybe not better
head ==>> was renamed to start: head_to_point -> start_to_point
food(t) ==>> was renamed to end: foot_to_point -> end_to_point
MAYBE rather head and tail?
'''

class Force2D:

    def __init__(self, id, node, coordinates, components, force_type=None):
        self.id = str(id)
        # node (point) of application
        self.node = node
        # maybe redundant
        self.coordinates = coordinates
        self.magnitude, self.direction = self._get_magnitude_and_direction(components)
        # type: one of internal, external, reaction
        self.force_type = force_type
        # application line - with direction and coefficients
        self.line = self._get_line()

    def _get_magnitude_and_direction(self, components):
        magnitude = self._norm(components)
        return magnitude, self._normalized_components(components, magnitude)

    def _norm(self, components):
        return (components[0]**2 + components[1]**2)**0.5

    def _normalized_components(self, components, magnitude):
        if magnitude < 1e-8:
            return [components[0], components[1]]
        else:
            return [components[0] / magnitude, components[1] / magnitude]

    def _get_line(self):
        line = {}
        line['direction'] = self.direction
        line['coefficients'] = self._get_line_coefficients()

        return line

    def _get_line_coefficients(self):
        p1 = self.coordinates
        p2 = [p1[0] + self.direction[0] * self.magnitude,
              p1[1] + self.direction[1] * self.magnitude]

        # gibt a,b und c aus ax+by+c
        a = p1[1]-p2[1]
        b = p2[0]-p1[0]
        c = -(a* p1[0]+b*p1[1])

        # http://www.pdas.com/lineint.html
        # a1:= y2-y1;
        # b1:= x1-x2;
        # c1:= x2*y1 - x1*y2;  { a1*x + b1*y + c1 = 0 is line 1 }
        a1 = p2[1]-p1[1]
        b1 = p1[0]-p2[0]
        c1 = p2[0] * p1[1] - p1[0] * p2[1]

        # return [a,b,c]
        return [a1,b1,c1]


