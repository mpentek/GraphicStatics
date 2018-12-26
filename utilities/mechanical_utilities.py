"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

import matplotlib.pyplot as plt

from node2d import Node2D
from segment2d import Segment2D
from force2d import Force2D

from geometric_utilities import get_line_by_point_and_direction, get_intersection, are_parallel, TOL

# for debug
#from plot_utilities import plot_decomposed_forces, plot_force_diagram


def get_force_diagram(forces):
    force_diagram = {}
    force_diagram['forces'] = []
    force_diagram['force_segments'] = []
    force_diagram['force_base_points'] = []
    force_diagram['pole_segments'] = []
    # will be given an assumed (arbitrary) place
    force_diagram['pole'] = None
    # this is the main unkown
    force_diagram['resultant'] = None

    # initialize lists
    # with first force - maybe remove later as this information is somewhat redundant
    force_diagram['forces'].append(forces[0])
    # with first point - creating here a default with coordinates [0.0, 0,0]

    # start coordinates s_coord
    s_coord_x = 0.0
    s_coord_y = 0.0

    # ennd coordinates e_coord

    force_diagram['force_base_points'].append(
        Node2D('p' + force_diagram['forces'][-1].id, [s_coord_x, s_coord_y]))

    e_coord_x = s_coord_x + \
        force_diagram['forces'][-1].magnitude * \
        force_diagram['forces'][-1].direction[0]
    e_coord_y = s_coord_y + \
        force_diagram['forces'][-1].magnitude * \
        force_diagram['forces'][-1].direction[1]

    force_diagram['force_segments'].append(Segment2D('g' + forces[0].id, [Node2D('s', [s_coord_x, s_coord_y]),
                                                                          Node2D('e', [e_coord_x, e_coord_y])]))

    for i in range(len(forces)-1):
        force_diagram['forces'].append(forces[i+1])

        s_coord_x = e_coord_x
        s_coord_y = e_coord_y

        force_diagram['force_base_points'].append(
            Node2D('p_' + force_diagram['forces'][-1].id, [s_coord_x, s_coord_y]))

        e_coord_x = s_coord_x + \
            force_diagram['forces'][-1].magnitude * \
            force_diagram['forces'][-1].direction[0]
        e_coord_y = s_coord_y + \
            force_diagram['forces'][-1].magnitude * \
            force_diagram['forces'][-1].direction[1]

        force_diagram['force_segments'].append(Segment2D('g*_' + forces[0].id, [Node2D('s', [s_coord_x, s_coord_y]),
                                                                                Node2D('e', [e_coord_x, e_coord_y])]))

    resultant_start = force_diagram['force_base_points'][0].coordinates
    resultant_end = [e_coord_x, e_coord_y]
    force_diagram['resultant'] = Force2D('r_ext', force_diagram['force_base_points'][0], force_diagram['force_base_points'][0].coordinates, [
                                         resultant_end[0] - resultant_start[0], resultant_end[1] - resultant_start[1]])

    x = resultant_start[0]
    x += (resultant_end[0] - resultant_start[0])/2.
    x += force_diagram['resultant'].magnitude/2

    y = resultant_start[1]
    y += (resultant_end[1] - resultant_start[1])/2.
    y += force_diagram['resultant'].magnitude/2

    force_diagram['pole'] = Node2D('p', [x, y])

    counter = 0
    for i in range(len(force_diagram['force_base_points'])):
        force_diagram['pole_segments'].append(Segment2D('g0_' + str(counter),
                                                        [force_diagram['force_base_points'][i], force_diagram['pole']]))
        counter += 1

    # maybe add different id
    force_diagram['pole_segments'].append(Segment2D('g0_' + str(counter),
                                                    [Node2D(force_diagram['resultant'].id + 's', [e_coord_x, e_coord_y]), force_diagram['pole']]))

    return force_diagram


def get_space_diagram(force_diagram, initial_offset_factor=0.1):
    space_diagram = {}
    # check for redundancies with the force_diagram
    space_diagram['forces'] = []
    space_diagram['resultant'] = force_diagram['resultant']

    space_diagram['force_segments'] = []
    space_diagram['pole_segments'] = []
    # these are the main unknowns
    space_diagram['intersection_points'] = []

    space_diagram['forces'].append(force_diagram['forces'][0])

    # offset along the 1st force
    # will be the first intesection point
    # on the action line of the first force
    init_p_coords_x = force_diagram['forces'][0].coordinates[0] + \
        force_diagram['forces'][0].direction[0] * \
        force_diagram['forces'][0].magnitude * initial_offset_factor
    init_p_coords_y = force_diagram['forces'][0].coordinates[1] + \
        force_diagram['forces'][0].direction[1] * \
        force_diagram['forces'][0].magnitude * initial_offset_factor

    cur_p_coords_x = init_p_coords_x
    cur_p_coords_y = init_p_coords_y

    for i in range(len(force_diagram['forces'])-1):
        space_diagram['intersection_points'].append(
            Node2D(space_diagram['forces'][-1].id, [cur_p_coords_x, cur_p_coords_y]))

        [cur_p_coords_x, cur_p_coords_y] = get_intersection([get_line_by_point_and_direction([cur_p_coords_x, cur_p_coords_y],
                                                                                             force_diagram['pole_segments'][i+1].line['direction']),
                                                             force_diagram['forces'][i+1].line])

        space_diagram['forces'].append(force_diagram['forces'][i+1])

    # for the resultant
    # g_00 through p_initialline
    # g_last through p_last
    # intersect

    space_diagram['intersection_points'].append(
        Node2D(space_diagram['forces'][-1].id, [cur_p_coords_x, cur_p_coords_y]))

    [cur_p_coords_x, cur_p_coords_y] = get_intersection([get_line_by_point_and_direction([init_p_coords_x, init_p_coords_y],
                                                                                         force_diagram['pole_segments'][0].line['direction']),
                                                         get_line_by_point_and_direction([cur_p_coords_x, cur_p_coords_y],
                                                                                         force_diagram['pole_segments'][-1].line['direction'])])

    # set the resultant point of application to the last intersectio point
    space_diagram['resultant'].coordinates = [cur_p_coords_x, cur_p_coords_y]

    # append last intersection point to results
    space_diagram['intersection_points'].append(
        Node2D(force_diagram['resultant'].id, [cur_p_coords_x, cur_p_coords_y]))

    for i in range(len(space_diagram['intersection_points'])-1):
        space_diagram['pole_segments'].append(Segment2D(force_diagram['pole_segments'][i+1].id, [
                                              space_diagram['intersection_points'][i], space_diagram['intersection_points'][i+1]]))

    # add last segment as well
    space_diagram['pole_segments'].append(Segment2D(force_diagram['pole_segments'][0].id, [
                                          space_diagram['intersection_points'][0], space_diagram['intersection_points'][-1]]))

    return space_diagram


def decompose_force_into_components_by_directions(force, directions):
    '''
    Pure geometric operation:
    get the points as the start point of force (tail)
    and the end point of force (head)

    get the lines through the start point and direction 1 as well as
    for the one through the end point and direction 2

    get the instersection point of these lines

    the decomposed forces geometrically mean in order connecting
    the start point and the intersection point for the first one,
    the intersection point and end point for the second on

    TODO: implement some better workaround, as in some cases the 2 elements
    and respective directions might be colinear/parallel
    this method is only applicable for non-parallel directions
    otherwise will return None
    '''
    points = [force.coordinates,
              [force.coordinates[0] + force.direction[0] * force.magnitude,
               force.coordinates[1] + force.direction[1] * force.magnitude]]

    intersection_point = get_intersection([get_line_by_point_and_direction(points[0], directions[0]),
                                           get_line_by_point_and_direction(points[1], directions[1])])



    if intersection_point is not None:
        corrected_directions = [[intersection_point[0] - points[0][0], intersection_point[1] - points[0][1]],
                                [points[1][0] - intersection_point[0], points[1][1] - intersection_point[1]]]

        decomposed_forces = [Force2D('1', '-', force.coordinates, [corrected_directions[0][0],
                                                                    corrected_directions[0][1]]),
                             Force2D('1', '-', force.coordinates, [corrected_directions[1][0],
                                                                    corrected_directions[1][1]])]
        points.append(intersection_point)

        return decomposed_forces, points
    else:
        return None, None


def decompose_force_by_inverse_proportion(acting_line, direction, fixity_locations, force, fixity_node_id):
    decomposed_forces = []

    if force.magnitude > TOL:
        normal_direction = [-direction[1], direction[0]]
        # moving to first fixity
        force_moved_to_fixity = force
        # shift starting point
        force_moved_to_fixity.coordinates = [fixity_locations[0][0] - force.direction[0] * force.magnitude,
                                             fixity_locations[0][1] - force.direction[1] * force.magnitude]

        intersect_direction = [fixity_locations[1][0] - force_moved_to_fixity.coordinates[0],
                               fixity_locations[1][1] - force_moved_to_fixity.coordinates[1]]

        # baseline at (moved) force head
        baseline = get_line_by_point_and_direction(
            fixity_locations[0], normal_direction)
        # parallel to base line
        # shifted_baseline at (moved) force tail
        shifted_baseline = get_line_by_point_and_direction(
            force_moved_to_fixity.coordinates, normal_direction)

        mid_line = get_line_by_point_and_direction(
            force_moved_to_fixity.coordinates, intersect_direction)

        actual_point_of_application = get_intersection([baseline, acting_line])
        force_line = get_line_by_point_and_direction(
            actual_point_of_application, force.direction)

        # first decomposed force - at first fixity# for fixity 0 - x -> check y coordinates
        start_point = get_intersection([mid_line, force_line])
        end_point = get_intersection([force_line, baseline])

        decomposed_forces.append(Force2D('-',
                                         fixity_node_id[0],
                                         fixity_locations[0],
                                         [end_point[0] - start_point[0],
                                          end_point[1] - start_point[1]]))

        # second decomposed force - at second fixity
        start_point = get_intersection([shifted_baseline, force_line])
        end_point = get_intersection([force_line, mid_line])

        decomposed_forces.append(Force2D('-',
                                         fixity_node_id[1],
                                         fixity_locations[1],
                                         [end_point[0] - start_point[0],
                                          end_point[1] - start_point[1]]))

    else:
        decomposed_forces.append(Force2D('-',
                                         fixity_node_id[0],
                                         fixity_locations[0],
                                         [0.0, 0.0]))

        decomposed_forces.append(Force2D('-',
                                         fixity_node_id[1],
                                         fixity_locations[1],
                                         [0.0, 0.0]))

    return decomposed_forces


def get_reactions(acting_line, decomposed_forces, directions, fixity_locations, fixity_type, fixity_node_id):
    # directions:
    # directions = [[1,0],[0,1]]x = [1,0]
    # y = [0,1]
    # fixities:
    # [x,y] = [true or false, true or false]

    # currently check:
    # n_x_fixed - number of times x fixed
    # n_y_fixed - number of times y fixed
    n_fixed = [0, 0]
    for fixity in fixity_type:
        if fixity[0] == True:
            n_fixed[0] += 1
        if fixity[1] == True:
            n_fixed[1] += 1

    reactions = []

    # assumtion: for now that there are 2 y-fixities and 1 x-fixity
    # todo: make more robust
    # decomposed forces: decomposed_force[0] is only the x-component
    # decomposed_force[1] is only the y-component

    # TODO: refactor, code duplication
    # x-components
    if n_fixed[0] == 1:
        # should only return one element - [0] needed in the end
        idx = [i for i in range(len(fixity_type))
               if fixity_type[i][0] == True][0]
        loc = fixity_locations[idx]
        reactions.append(Force2D('-',
                                 fixity_node_id[0],
                                 loc,
                                 [decomposed_forces[0].magnitude * decomposed_forces[0].direction[0],
                                  decomposed_forces[0].magnitude * decomposed_forces[0].direction[1]]))
    elif n_fixed[0] == 2:
        # for fixity 0 - x -> check y coordinates
        # if on the same line -> same y coord
        if abs(fixity_locations[0][1]-fixity_locations[1][1]) < TOL:
            reaction_forces = [Force2D('-',
                                       fixity_node_id[0],
                                       fixity_locations[0],
                                       [decomposed_forces[0].magnitude * .5 * decomposed_forces[0].direction[0],
                                        decomposed_forces[0].magnitude * .5 * decomposed_forces[0].direction[1]]),
                               Force2D('-',
                                       fixity_node_id[1],
                                       fixity_locations[1],
                                       [decomposed_forces[0].magnitude * .5 * decomposed_forces[0].direction[0],
                                        decomposed_forces[0].magnitude * .5 * decomposed_forces[0].direction[1]])]
        else:
            reaction_forces = decompose_force_by_inverse_proportion(
                acting_line, directions[0], fixity_locations, decomposed_forces[0], fixity_node_id)

        reactions.extend(reaction_forces)
    else:
        # implement error
        pass

    # y-componentsreactions.append
    if n_fixed[1] == 1:
        # should only return one element - [0] needed in the end
        idx = [i for i in range(len(fixity_type))
               if fixity_type[i][1] == True][0]
        loc = fixity_locations[idx]
        reactions.append(Force2D('-',
                                 fixity_node_id[1],
                                 loc,
                                 [-decomposed_forces[1].magnitude * decomposed_forces[1].direction[0],
                                  -decomposed_forces[1].magnitude * decomposed_forces[1].direction[1]]))
    elif n_fixed[1] == 2:
        # for fixity 1 - y -> check x coordinates
        # if on the same line -> same x coord
        if abs(fixity_locations[0][0]-fixity_locations[1][0]) < TOL:
            reaction_forces = [Force2D('-',
                                       fixity_node_id[0],
                                       fixity_locations[0],
                                       [decomposed_forces[1].magnitude * .5 * decomposed_forces[1].direction[0],
                                        decomposed_forces[1].magnitude * .5 * decomposed_forces[1].direction[1]]),
                               Force2D('-',
                                       fixity_node_id[1],
                                       fixity_locations[1],
                                       [decomposed_forces[1].magnitude * .5 * decomposed_forces[1].direction[0],
                                        decomposed_forces[1].magnitude * .5 * decomposed_forces[1].direction[1]])]
        else:
            reaction_forces = decompose_force_by_inverse_proportion(
                acting_line, directions[1], fixity_locations, decomposed_forces[1], fixity_node_id)

        reactions.extend(reaction_forces)
    else:
        # implement error
        pass

    # flip sign for all directions as it has to have the meaning of reaction
    for reaction in reactions:
        reaction.direction[0] *= -1
        reaction.direction[1] *= -1
        reaction.force_type = 'reaction'

    return reactions


def get_nodal_equilibrium_by_method_of_joints(forces, elements):
    # force diagram
    # to find the magnitude of the resultant of existing nodal forces
    force_diagram = get_force_diagram(forces)

    # # TODO: for debuging
    # from plot_utilities import plot_force_diagram
    # plot_force_diagram(force_diagram)
    # plt.show()



    # decompose resultant
    # into two non-parallel components
    directions = [elements[0].line['direction'], elements[1].line['direction']]
    decomposed_forces, points = decompose_force_into_components_by_directions(force_diagram['resultant'],
                                                                            directions)

    # for debug
    # plot_force_diagram(force_diagram)
    #plot_decomposed_forces(force_diagram['resultant'], decomposed_forces, points)
    # plt.show()

    # TODO: because it is nodal equilibrium, here the signs should be flipped
    # and not in the function calling this one

    return decomposed_forces
