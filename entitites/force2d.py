# -*- coding: utf-8 -*-
"""
Created on Wed May  2 13:03:45 2018

@author: Benedikt
"""

import numpy as np

from geometric_utilities import get_line_coefficients, get_magnitude_and_direction


class Force2D:

    def __init__(self, id, node_id, coordinates, components, force_type=None):
        self.id = id
        # node (point) of application
        self.node_id = node_id
        # maybe redundant
        self.coordinates = coordinates
        self.magnitude, self.direction = get_magnitude_and_direction(
            components)
        # type: one of internal, external, reaction
        self.force_type = force_type
        # application line - with direction and coefficients
        self.line = self._get_line()

    # TODO: line should be moved to geometric_utilities
    def _get_line(self):
        line = {}
        line['direction'] = self.direction
        line['coefficients'] = get_line_coefficients([self.coordinates, [self.coordinates[0] + self.direction[0] * self.magnitude,
                                                                         self.coordinates[1] + self.direction[1] * self.magnitude]])

        return line
