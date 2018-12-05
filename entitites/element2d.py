"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from node2d import Node2D

class Element2D:
    def __init__(self, id, nodes, coordinates):
        self.id = id
        # id of nodes at i and j
        self.nodes = nodes
        self.coordinates = coordinates
        # will be tension or compression
        self.element_type = None
        # will be assigned after initialize
        self.midpoint = self._get_midpoint()
        # will be added once read/calculated
        # force id at nodes i and j
        self.force_magnitude = None

        # self.x = [nodes[0].coordinates[0], nodes[1].coordinates[0]]
        # self.y = [nodes[0].coordinates[1], nodes[1].coordinates[1]]
        self.line = self._get_line()
        self.length = self._get_length()

    def _get_length(self):
        return ((self.coordinates[1][0] - self.coordinates[0][0])**2 + (self.coordinates[1][1] - self.coordinates[0][1])**2)**0.5

    def _get_midpoint(self):
        return Node2D('m',
                    [(self.coordinates[0][0] + self.coordinates[1][0]) / 2.,
                     (self.coordinates[0][1] + self.coordinates[1][1]) / 2.])

    def _get_line_coefficients(self):
        p1 = self.coordinates[0]
        p2 = self.coordinates[1]
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

    def _get_line(self):
        line = {}
        # not normalized, for consistency normlize always, overall
        line['direction'] = [self.coordinates[1][0] - self.coordinates[0][0],
                             self.coordinates[1][1] - self.coordinates[0][1]]
        line['coefficients'] = self._get_line_coefficients()
        return line
