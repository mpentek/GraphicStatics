"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""


class Node2D:
    def __init__(self, id, coordinates,  is_constrain=False):
        self.id = id
        self.coordinates = coordinates
        self.is_constrain = is_constrain
        # will be populated after initialize
        self.forces = []
        self.solved_elements = []
        self.unsolved_elements = []
        # representing how many forces (of which unknown)
        self.unsolved_degree = None
        # will be changed once solved
        self.is_solved = False
