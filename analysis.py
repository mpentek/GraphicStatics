"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

import json
import warnings
# still needed for plotting the (input) system, to be moved to plot_utilities

# from matplotlib import pyplot as plt
import numpy as np

from entitites.node2d import Node2D
from entitites.element2d import Element2D
from entitites.force2d import Force2D
from entitites.fixity2d import Fixity2D
from entitites.segment2d import Segment2D

from utilities.mechanical_utilities import get_force_diagram, get_space_diagram, get_reactions, decompose_force_into_components_by_directions, get_nodal_equilibrium_by_method_of_joints
from utilities.geometric_utilities import TOL, are_parallel, get_intersection, get_length, get_midpoint
from utilities.plot_utilities import plot_input_system, plot_computation_model, plot_solved_system, plot_force_diagram, plot_space_diagram, plot_decomposed_forces, plot_reaction_forces


class Analysis(object):
    def __init__(self, input_model_file, echo_level=0):
        self.echo_level = echo_level

        self.input_system = self._import_model(input_model_file)
        plot_input_system(self.input_system)

        # plt.show()

        self.computation_model = None
        self._prepare_computation_model()
        plot_computation_model(self.computation_model)

        # plt.show()

        # if it is set to 0, no additional plots will be done
        # if set to 1 additional plots will be shown

    def _import_model(self, input_model_file):

        model = {}
        model["nodes"] = {}
        model["elements"] = {}
        model["forces"] = {}
        # rename to fixities (as forces are also boundary conditions)
        model["fixities"] = {}

        with open(input_model_file) as f:
            data = json.load(f)

        # get node_list:
        for node in data['nodes']:
            model["nodes"][node['id']] = Node2D(node['id'],
                                                node['coords'])

        # get elements:
        for element in data['elements']:
            model["elements"][element['id']] = Element2D(element['id'],
                                                         element['connect'],
                                                         [model["nodes"][element['connect'][0]].coordinates,
                                                          model["nodes"][element['connect'][1]].coordinates],
                                                         element['is_constrain'])

        # get (external) forces:
        for ext_force in data['external_forces']:
            model["forces"]['e' + str(ext_force['id'])] = Force2D(ext_force['id'],
                                                                  ext_force['node_id'],
                                                                  # maybe remove once dependency is not needed
                                                                  model["nodes"][ext_force['node_id']
                                                                                 ].coordinates,
                                                                  ext_force['components'],
                                                                  force_type='external')

        # get fixitites
        for fixity in data['fixities']:
            model["fixities"][fixity['id']] = Fixity2D(fixity['id'],
                                                       fixity['node_id'],
                                                       fixity['is_fixed'])

        return model

    def postprocess(self):
        # for example cremona-plan
        print("Cremona-plan to be implemented")
        pass

    def _calculate_reaction_forces(self):
        forces = []
        for key, force in self.input_system["forces"].items():
            # if force.force_type == 'external':
            forces.append(force)

        ################
        # force diagram
        # to find the magnitude of the resultant of external forces
        force_diagram = get_force_diagram(forces)
        if self.echo_level == 1:
            plot_force_diagram(force_diagram)

        ################
        # funicular or space diagram
        # to find the acting line of the resultant of external forces

        space_diagram = get_space_diagram(force_diagram)
        if self.echo_level == 1:
            plot_space_diagram(space_diagram)

        # for now diractions hard-coded
        directions = [[1, 0], [0, 1]]

        decomposed_forces, points = decompose_force_into_components_by_directions(
            space_diagram['resultant'], directions)
        if self.echo_level == 1:
            plot_decomposed_forces(
                space_diagram['resultant'], decomposed_forces, points)

        ################
        # from decomposed resultant get reactions based upon fixities
        # use inverse proportion
        fixity_node_id = []
        fixity_locations = []
        fixity_type = []
        for key, fixity in self.input_system['fixities'].items():
            fixity_locations.append(
                self.input_system['nodes'][fixity.node_id].coordinates)
            fixity_node_id.append(fixity.node_id)
            fixity_type.append(fixity.is_fixed)

        # resultant line needs to be re-calculated! (as it is a copy and _get_line() is in the constructor)
        space_diagram['resultant'].line = space_diagram['resultant']._get_line()
        reactions = get_reactions(space_diagram['resultant'].line, decomposed_forces,
                                  directions, fixity_locations, fixity_type, fixity_node_id)
        if self.echo_level == 1:
            plot_reaction_forces(reactions, space_diagram['resultant'])

        ################
        # setup the computational model
        # by discarding fixities and adding reaction into force dictionary
        self.computation_model = self.input_system
        key = 'fixities'
        try:
            del self.computation_model[key]
        except KeyError:
            print('Key ' + key + ' not found')

        for idx, reaction in enumerate(reactions):
            self.computation_model['forces']['r' + str(idx)] = reaction

        self._check_system_equilibrium()

    def _check_system_equilibrium(self):
        # for checking equilibrium under external loads
        # and reaction forces once calculated

        forces = []
        for key, force in self.computation_model["forces"].items():
            # if force.force_type == 'external' or force.force_type == 'reaction':
            forces.append(force)

        ################
        # force diagram
        # to find the magnitude of the resultant of external forces
        force_diagram = get_force_diagram(forces)
        if self.echo_level == 1:
            plot_force_diagram(force_diagram)

        if force_diagram['resultant'].magnitude > TOL:
            raise Exception(
                'Computation model not in equilibrium under external and reaction forces!')

    def _check_all_nodal_equilibrium(self):
        # checking equilibrium of each node under all forces
        for key, node in self.computation_model['nodes'].items():
            self._check_nodal_equilibrium(node.id)

    def _check_nodal_equilibrium(self, node_id):
            # TODO: remove need for casting from str to int
        node = self.computation_model['nodes'][int(node_id)]

        forces = [self.computation_model['forces'][force_id]
                  for force_id in node.forces]

        ################
        # force diagram
        # to find the magnitude of the resultant of external forces
        force_diagram = get_force_diagram(forces)
        if self.echo_level == 1:
            plot_force_diagram(force_diagram)

        if force_diagram['resultant'].magnitude > TOL:
            warnings.warn(
                'Computation model not in equilibrium at node ' + node.id + '!', Warning)

    def _prepare_computation_model(self):
        self._calculate_reaction_forces()

        # update nodal information with existing forces: external and reaction
        for key, force in self.computation_model['forces'].items():
            self.computation_model['nodes'][force.node].forces.append(key)
        # update nodal information with elements: will link to internal forces
        for key, element in self.computation_model['elements'].items():
            self.computation_model['nodes'][element.nodes[0]
                                            ].unsolved_elements.append(key)
            self.computation_model['nodes'][element.nodes[1]
                                            ].unsolved_elements.append(key)

    def _solve_iteratively(self):
        current_system_unsolved_degree = 0
        # update nodal date with unsolved degree
        for key, node in self.computation_model['nodes'].items():
            node.unsolved_degree = len(node.unsolved_elements)
            current_system_unsolved_degree += node.unsolved_degree

        # attention: infinite loop! premise that system is solvable (so no Ritter-cut needed!)
        # todo: make more robust by ranking unsolved, having only one go through (if not solved, do ritter-cut)
        old_system_unsolved_degree = current_system_unsolved_degree

        system_solved = False
        counter = 0

        if self.echo_level == 1:
            print("## System solve - iteratively")

        change = 1
        while (not(system_solved) and change > 0):
            counter += 1

            # setup initial values
            system_solved = True
            current_system_unsolved_degree = 0

            # computation loop
            for key, node in self.computation_model['nodes'].items():

                # should work from python3.5 onwards
                # for key, node in reversed(self.computation_model['nodes'].items()):

                # reversed_keys = list(reversed([key for key, node in self.computation_model['nodes'].items()]))
                # sel_key = 0
                # reversed_keys.remove(sel_key)
                # reversed_keys.insert(0, sel_key)
                # for r_key in reversed_keys:
                #     node = self.computation_model['nodes'][r_key]

                if node.unsolved_degree > 0:
                    # for any unsolved node set to False
                    system_solved = False

                    if node.unsolved_degree < 3:
                        # node solvable

                        # create list of foces and elements relevant to node
                        nodal_forces = []
                        for force_id in node.forces:
                            nodal_forces.append(
                                self.computation_model['forces'][force_id])
                        nodal_elements = []

                        for element_id in node.unsolved_elements:
                            nodal_elements.append(
                                self.computation_model['elements'][element_id])

                        if len(nodal_elements) == 2:
                            # for this case we can always decomponse the resultant at the node
                            # into the 2 elements by the method of joints

                            forces = get_nodal_equilibrium_by_method_of_joints(
                                nodal_forces, nodal_elements)

                        elif len(nodal_elements) == 1:
                            # for this case we need to calculate the existing resultant
                            # at the node and see if this matches the prescribed topology
                            # so resultant parallel with member
                            # otherwise topology needs to be updated/modified ONLY IF
                            # this is permitted

                            force_diagram = get_force_diagram(nodal_forces)
                            # move resultant to actual nodal coordinate, recalculate line
                            force_diagram['resultant'].coordinates = node.coordinates
                            # update line equation
                            force_diagram['resultant'].line = force_diagram['resultant']._get_line(
                            )

                            if not(are_parallel([nodal_elements[0].line, force_diagram['resultant'].line])):
                                # get the next node id - other end of the nodal_elements[0]
                                tmp = nodal_elements[0].nodes.copy()
                                # TODO: make consistent type for id - probably overall as str() and not int()
                                tmp.remove(int(node.id))
                                other_node_id = tmp[0]
                                # get list of all elements at node - for now ids
                                # using .copy() to create value copy of list
                                elements_at_other_node = self.computation_model['nodes'][other_node_id].unsolved_elements.copy(
                                )
                                elements_at_other_node += self.computation_model['nodes'][other_node_id].solved_elements.copy(
                                )
                                # now elements instead of ids
                                elements_at_other_node = [
                                    self.computation_model['elements'][element_id] for element_id in elements_at_other_node]
                                constrained_elements_at_other_node = [
                                    element.id for element in elements_at_other_node if element.is_constrain]
                                if len(constrained_elements_at_other_node) != 1:
                                    # for 2d - plane - problems only 1 line should give the constraint
                                    # assumption for the current implementation
                                    raise Exception(
                                        'Computation model (geometrically) over-(or under-)constrained at node ' + other_node_id + ', cannot solve further!')
                                else:
                                    # node will be move along constrained line
                                    other_node_new_coord = get_intersection(
                                        [self.computation_model['elements'][constrained_elements_at_other_node[0]].line, force_diagram['resultant'].line])

                                    msg = '## Topology update:\n'
                                    msg += 'node with id ' + \
                                        str(other_node_id) + \
                                        ' and coordinates '
                                    msg += ", ".join("%.3f" % coord
                                                     for coord in self.computation_model['nodes'][other_node_id].coordinates) + '\n'
                                    msg += 'updated to coordinates ' + \
                                        ", ".join("%.3f" % coord
                                                  for coord in other_node_new_coord) + '\n'
                                    print(msg)

                                    # TODO - WIP: introduce model part utilities
                                    # all model data should only be stored once in the model part
                                    # similar changes - such as the following - should be carried out by these

                                    # node needs to be updated in the model part
                                    self.computation_model['nodes'][other_node_id].coordinates = other_node_new_coord

                                    # affected elements need to be updated in the model part
                                    for element_id in [element.id for element in elements_at_other_node]:
                                        # get index of node which needs to be updated
                                        # local index from the attribute of elements
                                        idx = self.computation_model['elements'][element_id].nodes.index(
                                            other_node_id)

                                        # set new node coordinate
                                        self.computation_model['elements'][element_id].coordinates[idx] = other_node_new_coord

                                        # update midpoint
                                        self.computation_model['elements'][element_id].midpoint = get_midpoint(
                                            self.computation_model['elements'][element_id].coordinates)
                                        # update line
                                        self.computation_model['elements'][element_id].line = self.computation_model['elements'][element_id]._get_line(
                                        )
                                        # update length
                                        self.computation_model['elements'][element_id].length = get_length(
                                            self.computation_model['elements'][element_id].coordinates)

                            else:
                                print()
                                # carry on if parallel, no topology update needed
                                pass

                            forces = [force_diagram['resultant']]

                        else:
                            # TODO implement some special warning, should not be the case
                            pass

                        if forces is not None:
                            # update force coordinates and line
                            for force in forces:
                                force.coordinates = node.coordinates
                                force.line = force._get_line()

                            # update element and nodal information
                            for o_idx, element in enumerate(nodal_elements):
                                # TODO: note, that by this point the force -> so forces[o_idx]
                                # has to be parallel to the element !!!

                                # use a parameter xi to determine internal force type
                                dir_u = forces[o_idx].direction[0]
                                dir_v = forces[o_idx].direction[1]
                                if abs(dir_u) > 0.0:
                                    xi_x = (
                                        element.midpoint[0] - forces[o_idx].coordinates[0]) / dir_u
                                else:
                                    xi_x = 0.0
                                if abs(dir_v) > 0.0:
                                    xi_y = (
                                        element.midpoint[1] - forces[o_idx].coordinates[1]) / dir_v
                                else:
                                    xi_y = 0.0

                                if xi_x >= 0.0 and xi_y >= 0:
                                    # force points towards midpoint
                                    element.element_type = 'compression'
                                    element.force_magnitude = forces[o_idx].magnitude

                                elif xi_x <= 0.0 and xi_y <= 0:
                                    # force points away from midpoint
                                    element.element_type = 'tension'
                                    element.force_magnitude = forces[o_idx].magnitude
                                else:
                                    raise Exception(
                                        'Case not permitted: xi_x and xi_y must have same sign!')

                                # update node and force lists:
                                labels = ['i', 'j']
                                for i_idx, node_id in enumerate(element.nodes):
                                    # if element.element_type == 'tension':
                                    #     components = []
                                    # elif element.element_type == 'compression':
                                    components = [self.computation_model['nodes'][node_id].coordinates[0] - element.midpoint[0],
                                                  self.computation_model['nodes'][node_id].coordinates[1] - element.midpoint[1]]
                                    if element.element_type == 'tension':
                                        components = [-components[0], -
                                                      components[1]]

                                    force = Force2D(str(element.id) + labels[i_idx],
                                                    node_id,
                                                    self.computation_model['nodes'][node_id].coordinates,
                                                    # direction will be computed correctly
                                                    components,
                                                    'internal')
                                    # overwriting magnitude with the correct value
                                    force.magnitude = forces[o_idx].magnitude

                                    # update forces
                                    self.computation_model['forces'][force.id] = force

                                    # update nodes - force list and node unsolved degree
                                    self.computation_model['nodes'][node_id].forces.append(
                                        force.id)
                                    self.computation_model['nodes'][node_id].unsolved_degree -= 1
                                    # also pop elemnt id once solve
                                    # using remove as ID should be unique in list
                                    self.computation_model['nodes'][node_id].unsolved_elements.remove(
                                        element.id)
                                    self.computation_model['nodes'][node_id].solved_elements.append(
                                        element.id)
                        else:
                            # TODO: implement some better workaround, as in some cases the 2 elements
                            # and respective directions might be colinear/parallel
                            pass

                        # once the node is solved
                        # check for nodal equilibrium
                        self._check_nodal_equilibrium(node.id)

                current_system_unsolved_degree += node.unsolved_degree

            change = old_system_unsolved_degree - current_system_unsolved_degree
            ##
            if self.echo_level == 1:
                print("At iteration: ", counter)
                print("System unsolved degree - old: ",
                      old_system_unsolved_degree)
                print("System unsolved degree - current: ",
                      current_system_unsolved_degree)
                print("System unsolved degree - change: ",
                      change)

            old_system_unsolved_degree = current_system_unsolved_degree

        if current_system_unsolved_degree == 0:
            print("## System solved successfully!")
            self._check_all_nodal_equilibrium()
        else:
            warnings.warn(
                "System cannot be solved iteratively, needs other solution", Warning)

    def solve_system(self):
        self._solve_iteratively()
        plot_solved_system(self.computation_model)
        pass
