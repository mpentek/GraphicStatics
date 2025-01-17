"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from node2d import Node2D

from geometric_utilities import get_line_coefficients, get_magnitude_and_direction, get_length, get_midpoint


class Segment2D(object):
    def __init__(self, id, nodes):
        self.id = str(id)
        # id of nodes at i and j
        self.nodes = nodes
        self.midpoint = get_midpoint(
            [self.nodes[0].coordinates, self.nodes[1].coordinates])
        self.x = [nodes[0].coordinates[0], nodes[1].coordinates[0]]
        self.y = [nodes[0].coordinates[1], nodes[1].coordinates[1]]
        self.line = self._get_line()
        # TODO: magnitude redundant with length, clean up
        self.length = get_length(
            [[self.x[0], self.y[0]], [self.x[1], self.y[1]]])

    # TODO: line and scaled_segment should be moved to
    # geometric_utilities

    #Nach verschieben der Knoten Segment anpassen
    def update_from_node(self):
        n1 = self.nodes[0]
        n2 = self.nodes[1]
        self.x = [n1.coordinates[0],n2.coordinates[0]]
        self.y = [n1.coordinates[1], n1.coordinates[1]]
        self.line = self._get_line()
        self.length = get_length(
            [[self.x[0], self.y[0]], [self.x[1], self.y[1]]])


    def _get_line(self):
        line = {}
        # not normalized, for consistency normlize always, overall
        line['direction'] = [self.nodes[1].coordinates[0] - self.nodes[0].coordinates[0],
                             self.nodes[1].coordinates[1] - self.nodes[0].coordinates[1]]
        # TODO: magnitude redundant with length, clean up
        magnitude, line['direction'] = get_magnitude_and_direction(
            line['direction'])
        line['coefficients'] = get_line_coefficients(
            [self.nodes[0].coordinates, self.nodes[1].coordinates])
        return line

    def get_scaled_segment(self, scaling_factor=1.0, scale_ends='both'):
        # move to geometric operations
        if scale_ends == 'both':
            delta_start = [(self.nodes[0].coordinates[0] - self.midpoint[0]) * scaling_factor,
                           (self.nodes[0].coordinates[1] - self.midpoint[1]) * scaling_factor]

            delta_end = [(self.nodes[1].coordinates[0] - self.midpoint[0]) * scaling_factor,
                         (self.nodes[1].coordinates[1] - self.midpoint[1]) * scaling_factor]

            return Segment2D(self.id + 'b',
                             [Node2D(self.nodes[0].id + 's', [self.midpoint[0] + delta_start[0],
                                                              self.midpoint[1] + delta_start[1]]),
                              Node2D(self.nodes[1].id + 'e', [self.midpoint[0] + delta_end[0],
                                                              self.midpoint[1] + delta_end[1]])])

        elif scale_ends == 'start':
            delta_start = [(self.nodes[0].coordinates[0] - self.midpoint[0]) * scaling_factor,
                           (self.nodes[0].coordinates[1] - self.midpoint[1]) * scaling_factor]

            return Segment2D(self.id + 's',
                             [Node2D(self.nodes[0].id + 's', [self.midpoint[0] + delta_start[0],
                                                              self.midpoint[1] + delta_start[1]]),
                              self.nodes[1]])

        elif scale_ends == 'end':
            delta_end = [(self.nodes[1].coordinates[0] - self.midpoint[0]) * scaling_factor,
                         (self.nodes[1].coordinates[1] - self.midpoint[1]) * scaling_factor]

            return Segment2D(self.id + 'e',
                             [self.nodes[0],
                              Node2D(self.nodes[1].id + 'e', [self.midpoint[0] + delta_end[0],
                                                              self.midpoint[1] + delta_end[1]])])
        else:
            # throw error
            pass

def update(self):
    self.midpoint = get_midpoint(
            [self.nodes[0].coordinates, self.nodes[1].coordinates])
    self.x = [self.nodes[0].coordinates[0], self.nodes[1].coordinates[0]]
    self.y = [self.nodes[0].coordinates[1], self.nodes[1].coordinates[1]]
    self.line = self._get_line()
        # TODO: magnitude redundant with length, clean up
    self.length = get_length(
            [[self.x[0], self.y[0]], [self.x[1], self.y[1]]])

