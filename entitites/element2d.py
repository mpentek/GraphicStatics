"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from node2d import Node2D

from geometric_utilities import get_length, get_magnitude_and_direction, get_line_coefficients


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
        # TODO: magnitude redundant with length, clean up
        self.length = get_length(self.coordinates)

    def _get_midpoint(self):
        return Node2D('m',
                      [(self.coordinates[0][0] + self.coordinates[1][0]) / 2.,
                       (self.coordinates[0][1] + self.coordinates[1][1]) / 2.])

    def _get_line(self):
        line = {}
        # not normalized, for consistency normlize always, overall
        line['direction'] = [self.coordinates[1][0] - self.coordinates[0][0],
                             self.coordinates[1][1] - self.coordinates[0][1]]
        # TODO: magnitude redundant with length, clean up
        magnitude, line['direction'] = get_magnitude_and_direction(
            line['direction'])
        line['coefficients'] = get_line_coefficients(self.coordinates)
        return line
