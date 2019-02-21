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

from utilities.mechanical_utilities import get_force_diagram, get_space_diagram, get_reactions, decompose_force_into_components_by_directions, get_nodal_equilibrium_by_method_of_joints,sort_clockwise
from utilities.geometric_utilities import TOL,get_line_coefficients
from utilities.plot_utilities import plot_input_system, plot_computation_model, plot_solved_system, plot_force_diagram, plot_space_diagram, plot_decomposed_forces, plot_reaction_forces
from utilities.geometric_utilities import sort_left_to_right

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
        model['elements'] = {}
        model["forces"] = {}
        # rename to fixities (as forces are also boundary conditions)
        model["fixities"] = {}

        with open(input_model_file) as f:
            data = json.load(f)

        #get bel_chord:
        model["bel_chord"] = data['bel_chord']
        
        # get node_list:
        for node in data['nodes']:
            model["nodes"][node['id']] = Node2D(node['id'],
                                                node['coords'],
                                                node['is_constrain'])
        #get elements
        for element in data['elements']: 
            model['elements'][element['id']] = Element2D(element['id'], 
                                                         element['connect'], 
                                                         # TODO: to be removed in future, should be only stored in 'nodes' 
                                                         [model['nodes'][element['connect'][0]].coordinates, 
                                                          model['nodes'][element['connect'][1]].coordinates], 
                                                         element['type']) 

        # get (external) forces:
        for ext_force in data['external_forces']:
            model["forces"]['e' + str(ext_force['id'])] = Force2D('e' + str(ext_force['id']),
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

    def postprocess(self,cremona):
        # for example cremona-plan
        print("Cremona-plan to be implemented")
        plot_computation_model(self.computation_model)
        self.draw_system_from_cremona(cremona)

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
            self.computation_model['forces']['r' + str(idx)].id = 'r' + str(idx)

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
            raise Exception('Computation model not in equilibrium under external and reaction forces!')

    def _check_all_nodal_equilibrium(self):
        # checking equilibrium of each node under all forces
        for key, node in self.computation_model['nodes'].items():
            self._check_nodal_equilibrium(node.id)

    def _check_nodal_equilibrium(self, node_id):
            # TODO: remove need for casting from str to int
            node = self.computation_model['nodes'][int(node_id)]

            forces = [self.computation_model['forces'][force_id] for force_id in node.forces]

            ################
            # force diagram
            # to find the magnitude of the resultant of external forces
            force_diagram = get_force_diagram(forces)
            if self.echo_level == 1:
                plot_force_diagram(force_diagram)

            if force_diagram['resultant'].magnitude > TOL:
                warnings.warn('Computation model not in equilibrium at node ' + str(node.id) + '!', Warning)

    def _prepare_computation_model(self):
        self._calculate_reaction_forces()

        # update nodal information with existing forces: external and reaction
        for key, force in self.computation_model['forces'].items():
            self.computation_model['nodes'][force.node_id].forces.append(key)
        # update nodal information with elements: will link to internal forces
        for key, element in self.computation_model['elements'].items():
            self.computation_model['nodes'][element.nodes[0]
                                            ].unsolved_elements.append(key)
            self.computation_model['nodes'][element.nodes[1]
                                            ].unsolved_elements.append(key)

    def _solve_iteratively(self):
        current_system_unsolved_degree = 0
        # update nodal date with unsolved degree
        for key, node in self.computation_model['nodes'].items(): #Was bedeutet key?
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

                        ##
                        ##
                        ##
                        # could happen, here a workaround
                        # insufficient_unsolved = False
                        # if len(node.unsolved_elements) == 1:
                        #     insufficient_unsolved = True
                        #     # take an already solved element
                        #     # take care not to update values
                        #     nodal_elements.append(
                        #         self.computation_model['elements'][node.solved_elements[-1]])

                        forces = get_nodal_equilibrium_by_method_of_joints(
                            nodal_forces, nodal_elements)

                        if forces is not None:
                            # update force coordinates and line
                            for force in forces:
                                force.coordinates = node.coordinates
                                force.line = force._get_line()

                            # update element and nodal information
                            for o_idx, element in enumerate(nodal_elements): #Was ist o_idx?
                                #Hier weitermachen

                                ##
                                ##
                                ##
                                # if insufficient_unsolved and o_idx == 1:
                                #     # nothing needs to be done, already solved
                                #     pass
                                # else:

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
                                    ValueError("Case not permitted")

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
                                    # else:
                                    #     ValueError("Case not permitted")
                                    
                                    force = Force2D(str(element.id) + labels[i_idx],
                                                    node_id,
                                                    self.computation_model['nodes'][node_id].coordinates,
                                                    # direction will be computed correctly
                                                    components,
                                                    forces[o_idx].force_type,
                                                    element.element_type)              
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
            warnings.warn("System cannot be solved iteratively, needs other solution",Warning)
        
        
    def solve_system(self):
        self._solve_iteratively()
        plot_solved_system(self.computation_model)
        pass
   
    def draw_system_from_cremona(self,cremona):
        #draw bel_chord first
        model = self.computation_model
        e_line = []
        #Liste mit allen externen Kraftlinien
        for i in cremona.ex_forces:
            line = model['forces'][i].line
            e_line.append(line)
        print('eline',e_line)
        pass
        #sortiere Elemente bel-chord von links nach rechts
        #zeichne Elemente bel_chord
        bel_elements = get_elements_bel_chord(model,cremona)
        print('bel_elements', bel_elements)
        element_line = []
        for i in bel_elements:
            print('element', model['elements'][i])
            left_node, right_node = r_l_node(model['elements'][i],model['nodes'],model['bel_chord'])
            print('i', i, 'left_node',left_node)
            #Elementlinie mit Steigung aus Cremona
            print('line_element',model['elements'][i].line)
            model['elements'][i].line = get_line_from_cremona(model['elements'][i],model['nodes'][left_node],cremona)
            element_line.append(line)
            print('line_element',model['elements'][i].line)

def get_line_from_cremona(element,node,cremona):
    #Richtung
    line = {}
    j = str(element.id) + 'i'
    x = node.coordinates[0] + cremona.bel_chord[j].direction[0]
    y  = node.coordinates[1] + cremona.bel_chord[j].direction[1]
    line['direction'] = [x,y]
    #Koeffizienten
    print('node',node)
    x2 = node.coordinates[0] + line['direction'][0]
    y2 = node.coordinates[1] + line['direction'][1]
    p2 = [x2,y2]
    line['coefficients'] = get_line_coefficients([node.coordinates,p2])
    return line
    

def r_l_node(element,nodes, bel):
        #knoten von links nach rechts sortieren
        print('element',element)
        n1 =  element.nodes[0]
        n2 =  element.nodes[1]
        if nodes[n1].coordinates[0] < nodes[n2].coordinates[0]:
            return n1,n2 
        if nodes[n2].coordinates[0] < nodes[n1].coordinates[0]:
            return n2,n1
        if nodes[n1].coordinates[0] == nodes[n2].coordinates[0]:
            if bel == 'bottom':
                if nodes[n1].coordinates[1] < nodes[n2].coordinates[1]:
                    return n2, n1
                if nodes[n2].coordinates[1] < nodes[n1].coordinates[1]:
                    return n1, n2
            if bel == 'top':
                if nodes[n1].coordinates[1] < nodes[n2].coordinates[1]:
                    return n1,n2
                if nodes[n2].coordinates[1] < nodes[n1].coordinates[1]:
                    return n2,n1

def get_elements_bel_chord(model,cremona):
    bel_elements = {}
    for i in cremona.bel_chord:
        element = cremona.at_member[cremona.bel_chord[i].id]
        if element not in bel_elements:
            bel_elements[element] = cremona.bel_chord[i]
    bel_elements = sort_left_to_right(bel_elements,model['nodes'])
    return bel_elements


        

# if __name__ == "__main__":
    # '''
    # Mock to check equilibrium at node 6 - example 4
    # '''

    # element = Element2D('6', ['6', '7'], [[7.5, -0.9],[2.5, -1.5]])
    # elements = [element]

    # force_m13 = Force2D('13j', '6', [7.5, -0.9], [0.19996 * 1.599296, 0.9798 * 1.599296], 'internal')
    # force_m5 = Force2D('5j', '6', [7.5, -0.9], [0.98418 * 172.2154, 0.17771 * 172.2154], 'internal')
    # forces = [force_m13, force_m5]

    # force_diagram = get_force_diagram(forces)

    # plot_force_diagram(force_diagram)
    # plt.show()



    # print("## ARE PARALLEL: ", are_parallel([elements[0].line,force_diagram['resultant'].line]))
    # print("element id: ", elements[0].id)
    # print("element_dir: ",elements[0].line['direction'])
    # print("resultant_dir: ", force_diagram['resultant'].direction)
    # print("element_line: ",elements[0].line['coefficients'])
    # print("resultant_line: ", force_diagram['resultant'].line['coefficients'])
    # print("resultant_coordinates: ", force_diagram['resultant'].coordinates)
    # decomposed_forces, points = [force_diagram['resultant']], [force_diagram['resultant'].coordinates]