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

from utilities.mechanical_utilities import get_force_diagram, get_space_diagram, get_reactions, decompose_force_into_components_by_directions, get_nodal_equilibrium_by_method_of_joints, sort_clockwise
from utilities.geometric_utilities import TOL, are_parallel, get_intersection, get_length, get_midpoint, get_line_coefficients

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

        # get bel_chord:
        model["bel_chord"] = data['bel_chord']

        # get node_list:
        for node in data['nodes']:
            model["nodes"][node['id']] = Node2D(node['id'],
                                                node['coords'],
                                                node['is_constrain'])
        # get elements
        for element in data['elements']:
            model['elements'][element['id']] = Element2D(element['id'],
                                                         element['connect'],
                                                         # TODO: to be removed in future, should be only stored in 'nodes'
                                                         [model['nodes'][element['connect'][0]].coordinates,
                                                          model['nodes'][element['connect'][1]].coordinates],
                                                         element['opt_type'],
                                                         element['is_constrain'])

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

    def postprocess(self, cremona):
        # for example cremona-plan
        print("Cremona-plan to be implemented")
        plot_computation_model(self.computation_model)
        self.draw_system_from_cremona(cremona)
        # Steigungen anpassen
        elements = self.computation_model['elements']
        nodes = self.computation_model['nodes']
        members = cremona.members
        for i in elements:
            j = str(elements[i].id) + 'i'
            if j not in members:
                j = str(elements[i].id) + 'j'

            line1 = members[j].line
            elements[i].coordinates[0] = nodes[elements[i].nodes[0]].coordinates
            elements[i].coordinates[1] = nodes[elements[i].nodes[1]].coordinates
            elements[i]._get_line()
            elements[i].midpoint = get_midpoint(elements[i].coordinates)
            elements[i].length = get_length(elements[i].coordinates)
            lines = [elements[i].line, line1]
            jop = are_parallel(lines)
            if jop != True:
               
                print('Member', i, 'is incorrect')
                print('cremona:', line1['direction'],
                      'system', elements[i].line['direction'])
        self.get_system_volume(elements, members, cremona.at_member, cremona.one_member)
        #plot_computation_model(self.computation_model)

    def get_system_volume(self, elements, members, at_member, one_member):
        V = 0
        already_done = []
        #für jeden Stab Produkt aus Länge System und Länge Cremona
        for i in members:
            #Länge System
            el = at_member[i]
            L = elements[el].length
            #Prüfen ob Stab schon betrachtet
            other = one_member[i]
            if other in already_done:
                pass
            else:
                P = members[i].length
                V = V + (P*L)
                already_done.append(i)
        print('Volume of given System: ', V)




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
            self.computation_model['forces']['r' +
                                             str(idx)].id = 'r' + str(idx)

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
                    'Computation model not in equilibrium at node ' + str(node.id) + '!', Warning)

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
        # Was bedeutet key?
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

                                # PMT: here workaround for overconstrained geometry
                                if len(constrained_elements_at_other_node) != 1:
                                    # for 2d - plane - problems only 1 line should give the constraint
                                    # assumption for the current implementation
                                    print("# other node id: ",
                                          str(other_node_id))
                                    print(
                                        "# constrained elements at other node: ", constrained_elements_at_other_node)

                                    raise Exception(
                                        'Computation model (geometrically) over-(or under-)constrained at node ' + str(other_node_id) + ', cannot solve further!')
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
                            # Was ist o_idx?
                            for o_idx, element in enumerate(nodal_elements):
                                # Hier weitermachen

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
            warnings.warn(
                "System cannot be solved iteratively, needs other solution", Warning)

    def solve_system(self):
        self._solve_iteratively()
        plot_solved_system(self.computation_model)
        pass

    def draw_system_from_cremona(self, cremona):
        # #draw bel_chord first
        model = self.computation_model
        e_line = []
        #Liste mit allen externen Kraftlinien
        for i in cremona.ex_forces:
            self.computation_model['forces'][i].line = self.computation_model['forces'][i]._get_line()
            line = self.computation_model['forces'][i].line
            e_line.append(line)
        pass
        #sortiere Elemente bel-chord von links nach rechts
        #zeichne Elemente bel_chord
        bel_elements = get_elements_bel_chord(model, cremona)
        #Für alle außer letzten member Schnittpunkt memberlinie und Kraftlinie bestimmen
        last_one = bel_elements[-1]
        bel_elements.pop(-1)
        count = 0
        #an linkem Punkt von linkem member starten
        left_node, right_node = r_l_node(model['elements'][bel_elements[0]],model['nodes'],model['bel_chord'])
        start = model['nodes'][left_node].coordinates
        for i in bel_elements:
            #Koordinaten des linken Punkts anpassen
            left_node, right_node = r_l_node(model['elements'][i],model['nodes'],model['bel_chord'])
            model['nodes'][left_node].coordinates = start
            #Elementlinie mit Steigung aus Cremonaplan
            model['elements'][i].line = get_line_from_cremona(model['elements'][i],model['nodes'][left_node],cremona,cremona.bel_chord,model)
            #Schnittpunkt element- und external-force line
            new_point = get_intersection([model['elements'][i].line,e_line[count]])
            count = count+1
            #new_point als neue Koordinaten für den rechten Punkt
            model['nodes'][right_node].coordinates = new_point
            #von dort aus nächsten member zeichnen
            start = new_point
        #letzten member "einhängen"
        #in computation model speichern
        self.computation_model = model
        #überprüfen ob bel_chord richtig gezeichnet wurde
        check_bel_chord(last_one,start,model['nodes'],model,cremona,e_line)

        bel_elements.append(last_one)
        # Diagonalen und unbel_chord zeichnen
        unbel_elements = get_elements_unbel_chord(model, cremona)
        last_one = unbel_elements[-1]
        unbel_elements.pop(-1)
        Verbdg_elements = get_elements_Verbindung(model, cremona)
        # Falls keine Vernindungen mehr vorhanden -> System bleibt wie es war
        if Verbdg_elements == []:
            plot_computation_model(model)
        else:
            # Startpunkt für unbel_chord und Verbindung festlegen
            left_node, right_node = r_l_node(
                model['elements'][bel_elements[0]], model['nodes'], model['bel_chord'])
            start_ubc = model['nodes'][left_node].coordinates
            start_ver = model['nodes'][right_node].coordinates
            # Schnittpunkt von Verbindung und unbel-Member finden
            for i in range(len(Verbdg_elements)):
                # Elementlinie unbel_chord mit Steigung aus Cremonaplan
                left_node, right_node = r_l_node(
                    model['elements'][unbel_elements[i]], model['nodes'], model['bel_chord'])
                model['nodes'][left_node].coordinates = start_ubc
                model['elements'][unbel_elements[i]].line = get_line_from_cremona(
                    model['elements'][unbel_elements[i]], model['nodes'][left_node], cremona, cremona.unbel_chord, model)
                line1 = model['elements'][unbel_elements[i]].line
                # Elementlinie Vernindung mit Steigung aus Cremonaplan
                fix = u_o_node(
                    model['elements'][Verbdg_elements[i]], model['nodes'], cremona)
                # rechter Knoten des unbel_element soll beweglich sein
                move = right_node
                # model['nodes'][fix].coordinates = start_ver
                model['elements'][Verbdg_elements[i]].line = get_line_from_cremona(
                    model['elements'][Verbdg_elements[i]], model['nodes'][fix], cremona, cremona.Verbindung, model)
                line2 = model['elements'][Verbdg_elements[i]].line
                # Schnittpunkt der Linien bestimmen
                new_point = get_intersection([line1, line2])
                # Neuen Punkt in Elementen speichern
                model['nodes'][move].coordinates = new_point
                # neuen Start festlegen
                start_ubc = new_point
                left, right = r_l_node(
                    model['elements'][bel_elements[i+1]], model['nodes'], model['bel_chord'])
                start_ver = model['nodes'][right].coordinates
                # plot_computation_model(model)
            check_top_chord(
                last_one, start_ubc, model['nodes'], model, cremona, bel_elements[-1], Verbdg_elements[-1])


def check_top_chord(last_one, start, nodes, model, cremona, last_bel, last_Ver):
    # Linie des letzten unbel_chord Elements
    left_node, right_node = r_l_node(
        model['elements'][last_one], nodes, model['bel_chord'])
    line1 = get_line_from_cremona(
        model['elements'][last_one], model['nodes'][right_node], cremona, cremona.unbel_chord, model)
    model['elements'][last_one].coordinates[0] = nodes[model['elements']
                                                       [last_one].nodes[0]].coordinates
    model['elements'][last_one].coordinates[1] = nodes[model['elements']
                                                       [last_one].nodes[1]].coordinates
    model['elements'][last_one]._get_line()
    line1 = model['elements'][last_one].line
    # Linie der letzten Deviation
    left_node, right_node = r_l_node(
        model['elements'][last_bel], nodes, model['bel_chord'])
    line2 = get_line_from_cremona(
        model['elements'][last_Ver], model['nodes'][left_node], cremona, cremona.Verbindung, model)
    new_point = get_intersection([line1, line2])
    if start[0] - TOL <= new_point[0] <= start[0] + TOL and start[1] - TOL <= new_point[1] <= start[1] + TOL:
        print('unbel_chord succesful')
    else:
        print('unbel_chord wrong!')
        dx = start[0]-new_point[0]
        dy = start[1]-new_point[1]
        print('difference:', dx, dy)


def check_bel_chord(last_one, start, nodes, model, cremona, e_line):
    left_node, right_node = r_l_node(
        model['elements'][last_one], nodes, model['bel_chord'])
    line = get_line_from_cremona(
        model['elements'][last_one], model['nodes'][right_node], cremona, cremona.bel_chord, model)
    new_point = get_intersection([line, e_line[-1]])
    model['nodes'][left_node].coordinates = new_point
    if start[0] - TOL <= new_point[0] <= start[0] + TOL and start[1] - TOL <= new_point[1] <= start[1] + TOL:
        print('bel_chord succesful')
    else:
        print('bel_chord wrong!')


def get_line_from_cremona(element, node, cremona, chord, model):
    # Richtung
    line = {}
    i = str(element.id) + 'i'
    j = str(element.id) + 'j'
    # Vorzeichen der Richtung anpassen
    if i in node.forces:
        line['direction'] = chord[i].line['direction']
    if j in node.forces:
        line['direction'] = chord[j].line['direction']

    # Koeffizienten
    x2 = node.coordinates[0] - line['direction'][0]
    y2 = node.coordinates[1] - line['direction'][1]
    p2 = [x2, y2]
    line['coefficients'] = get_line_coefficients([node.coordinates, p2])
    return line


def r_l_node(element, nodes, bel):
        # knoten von links nach rechts sortieren
    n1 = element.nodes[0]
    n2 = element.nodes[1]
    if nodes[n1].coordinates[0] < nodes[n2].coordinates[0]:
        return n1, n2
    if nodes[n2].coordinates[0] < nodes[n1].coordinates[0]:
        return n2, n1
    if nodes[n1].coordinates[0] == nodes[n2].coordinates[0]:
        if bel == 'bottom':
            if nodes[n1].coordinates[1] < nodes[n2].coordinates[1]:
                return n2, n1
            if nodes[n2].coordinates[1] < nodes[n1].coordinates[1]:
                return n1, n2
        if bel == 'top':
            if nodes[n1].coordinates[1] < nodes[n2].coordinates[1]:
                return n1, n2
            if nodes[n2].coordinates[1] < nodes[n1].coordinates[1]:
                return n2, n1


def u_o_node(element, nodes, cremona):
     # knoten von oben nach unten sortieren
    n1 = element.nodes[0]
    n2 = element.nodes[1]
    # Knoten an belastetem Gurt fix
    for i in cremona.bel_chord:
        if i in nodes[n1].forces:
            fix = n1
        if i in nodes[n2].forces:
            fix = n2
    # rechter Knoten des unbelasteten Elements soll verschoben werden

    return fix


def get_elements_bel_chord(model, cremona):
    bel_elements = {}
    for i in cremona.bel_chord:
        element = cremona.at_member[cremona.bel_chord[i].id]
        if element not in bel_elements:
            bel_elements[element] = cremona.bel_chord[i]
    bel_elements = sort_left_to_right(bel_elements, model['nodes'])
    return bel_elements


def get_elements_unbel_chord(model, cremona):
    unbel_elements = {}
    for i in cremona.unbel_chord:
        element = cremona.at_member[cremona.unbel_chord[i].id]
        if element not in unbel_elements:
            unbel_elements[element] = cremona.unbel_chord[i]
    unbel_elements = sort_left_to_right(unbel_elements, model['nodes'])
    return unbel_elements


def get_elements_Verbindung(model, cremona):
    Verbdg_elements = {}
    for i in cremona.Verbindung:
        element = cremona.at_member[cremona.Verbindung[i].id]
        if element not in Verbdg_elements:
            Verbdg_elements[element] = cremona.Verbindung[i]
    Verbdg_elements = sort_left_to_right(Verbdg_elements, model['nodes'])
    return Verbdg_elements


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
