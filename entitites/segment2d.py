"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from node2d import Node2D


class Segment2D(object):
    def __init__(self, id, nodes):
        self.id = str(id)
        # id of nodes at i and j
        self.nodes = nodes
        self.midpoint = self._get_midpoint()
        self.x = [nodes[0].coordinates[0], nodes[1].coordinates[0]]
        self.y = [nodes[0].coordinates[1], nodes[1].coordinates[1]]
        self.line = self._get_line()
        # TODO: magnitude redundant with length, clean up
        self.length = self._get_length()

    # TODO: magnitude redundant with length, clean up
    def _get_length(self):
        return ((self.x[1] - self.x[0])**2 + (self.y[1] - self.y[0])**2)**0.5

    def _get_midpoint(self):
        return Node2D('m',
                      [(self.nodes[0].coordinates[0] + self.nodes[1].coordinates[0]) / 2.,
                       (self.nodes[0].coordinates[1] + self.nodes[1].coordinates[1]) / 2.])

    def _get_line_coefficients(self):
        p1 = self.nodes[0].coordinates
        p2 = self.nodes[1].coordinates
        # gibt a,b und c aus ax+by+c
        a = p1[1]-p2[1]
        b = p2[0]-p1[0]
        c = -(a * p1[0]+b*p1[1])

        # http://www.pdas.com/lineint.html
        # a1:= y2-y1;
        # b1:= x1-x2;
        # c1:= x2*y1 - x1*y2;  { a1*x + b1*y + c1 = 0 is line 1 }
        a1 = p2[1]-p1[1]
        b1 = p1[0]-p2[0]
        c1 = p2[0] * p1[1] - p1[0] * p2[1]

        # return [a,b,c]
        return [a1, b1, c1]

    def _get_line(self):
        line = {}
        # not normalized, for consistency normlize always, overall
        line['direction'] = [self.nodes[1].coordinates[0] - self.nodes[0].coordinates[0],
                             self.nodes[1].coordinates[1] - self.nodes[0].coordinates[1]]
        # TODO: magnitude redundant with length, clean up
        magnitude, line['direction'] = self._get_magnitude_and_direction(line['direction'])
        line['coefficients'] = self._get_line_coefficients()
        return line

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

    def get_scaled_segment(self, scaling_factor=1.0, scale_ends='both'):
        # move to geometric operations
        if scale_ends == 'both':
            delta_start = [(self.nodes[0].coordinates[0] - self.midpoint.coordinates[0]) * scaling_factor,
                           (self.nodes[0].coordinates[1] - self.midpoint.coordinates[1]) * scaling_factor]

            delta_end = [(self.nodes[1].coordinates[0] - self.midpoint.coordinates[0]) * scaling_factor,
                         (self.nodes[1].coordinates[1] - self.midpoint.coordinates[1]) * scaling_factor]

            return Segment2D(self.id + 'b',
                             [Node2D(self.nodes[0].id + 's', [self.midpoint.coordinates[0] + delta_start[0],
                                                              self.midpoint.coordinates[1] + delta_start[1]]),
                              Node2D(self.nodes[1].id + 'e', [self.midpoint.coordinates[0] + delta_end[0],
                                                              self.midpoint.coordinates[1] + delta_end[1]])])

        elif scale_ends == 'start':
            delta_start = [(self.nodes[0].coordinates[0] - self.midpoint.coordinates[0]) * scaling_factor,
                           (self.nodes[0].coordinates[1] - self.midpoint.coordinates[1]) * scaling_factor]

            return Segment2D(self.id + 's',
                             [Node2D(self.nodes[0].id + 's', [self.midpoint.coordinates[0] + delta_start[0],
                                                              self.midpoint.coordinates[1] + delta_start[1]]),
                              self.nodes[1]])

        elif scale_ends == 'end':
            delta_end = [(self.nodes[1].coordinates[0] - self.midpoint.coordinates[0]) * scaling_factor,
                         (self.nodes[1].coordinates[1] - self.midpoint.coordinates[1]) * scaling_factor]

            return Segment2D(self.id + 'e',
                             [self.nodes[0],
                              Node2D(self.nodes[1].id + 'e', [self.midpoint.coordinates[0] + delta_end[0],
                                                              self.midpoint.coordinates[1] + delta_end[1]])])
        else:
            # throw error
            pass
