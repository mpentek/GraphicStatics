"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""


class Fixity2D:
    def __init__(self, id, node_id, is_fixed):
        self.id = str(id)
        # node (point) of application
        self.node_id = node_id
        self.is_fixed = is_fixed
