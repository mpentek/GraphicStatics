"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D as PLine2D
from matplotlib import colors as mcolors
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages

import numpy as np

from geometric_utilities import TOL

from entitites.segment2d import Segment2D

# TODO: make some dynamic adjustments of limits

def save_to_pdf(name, figures=None):
    name = name + '.pdf'
    multipage_pdf = PdfPages(name)

    if figures is None:
        figures = [plt.figure(n) for n in plt.get_fignums()]
    for fig in figures:
        fig.savefig(multipage_pdf, format='pdf')

    multipage_pdf.close()

def get_member_limits_and_segments_for_plot(model, offset_factor=0.1):
    x = []
    x_m = []
    y = []
    y_m = []

    m_id = []
    segments = []

    for id, element in model["elements"].items():
        x0 = model["nodes"][element.nodes[0]].coordinates[0]
        y0 = model["nodes"][element.nodes[0]].coordinates[1]

        x1 = model["nodes"][element.nodes[1]].coordinates[0]
        y1 = model["nodes"][element.nodes[1]].coordinates[1]

        x.append(x0)
        x.append(x1)

        y.append(y0)
        y.append(y1)

        segments.append([[x0, x1], [y0, y1]])

        x_m.append(element.midpoint.coordinates[0])
        y_m.append(element.midpoint.coordinates[1])
        m_id.append(element.id)

    x_lim = [min(x), max(x)]
    delta_x = x_lim[1] - x_lim[0]
    x_lim[0] -= offset_factor * delta_x
    x_lim[1] += offset_factor * delta_x

    y_lim = [min(y), max(y)]
    delta_y = y_lim[1] - y_lim[0]
    y_lim[0] -= offset_factor * delta_y
    y_lim[1] += offset_factor * delta_y

    return x_lim, y_lim, segments, x_m, y_m, m_id

def get_forces_for_plot(model, shift_to_head=False, scale=0.1):
    x = []
    y = []
    u = []
    v = []
    c = []

    for id, force in model["forces"].items():
        x.append(model["nodes"][force.node].coordinates[0])
        y.append(model["nodes"][force.node].coordinates[1])

        u.append(scale * force.direction[0] * force.magnitude)
        v.append(scale * force.direction[1] * force.magnitude)

        if shift_to_head:
            x[-1] -= u[-1]
            y[-1] -= v[-1]

        if force.force_type == "external":
            c.append('magenta')
        elif force.force_type == "reaction":
            c.append('green')
        elif force.force_type == "internal":
            c.append('blue')
        else:
            pass

    return x, y, u, v, c

def get_nodal_data_for_plot(model):
    x = []
    y = []
    n_id = []

    for id, node in model["nodes"].items():
        x.append(node.coordinates[0])
        y.append(node.coordinates[1])
        n_id.append(node.id)

    return x, y, n_id

def plot_input_system(input_system):

    x_lim, y_lim, segments, x_m, y_m, m_id = get_member_limits_and_segments_for_plot(input_system, offset_factor=0.25)

    fig, ax = plt.subplots()
    ax.set_title('Input system')
    # ax.set_xlim(x_lim)
    # ax.set_ylim(y_lim)

    # members
    for segment in segments:
        ax.add_line(
            PLine2D(segment[0], segment[1], alpha=0.5, color='grey'))
    for i, txt in enumerate(m_id):
        ax.annotate("m_" + str(txt), (x_m[i], y_m[i]))

    # nodes
    x_n, y_n, n_id = get_nodal_data_for_plot(input_system)
    ax.scatter(x_n, y_n)
    for i, txt in enumerate(n_id):
        ax.annotate("n_" + str(txt), (x_n[i], y_n[i]))

    # (external) forces
    x, y, u, v, c = get_forces_for_plot(input_system, True, 0.01)
    for i in range(len(x)):
        ax.arrow(x[i], y[i], u[i], v[i], color=c[i],
                    length_includes_head=True, head_width=0.25, head_length=0.25)

    # add boundary conditions
    scaling_factor = 0.25
    for key, fixity in input_system['fixities'].items():
        # ToDo: find way to plot ALR
        if fixity.is_fixed[0] is True:
            point = input_system['nodes'][fixity.node_id].coordinates
            dy = scaling_factor
            dx = dy*1.5
            x = [point[0], point[0]-dx, point[0]-dx]
            y = [point[1], point[1]+dy, point[1]-dy]
            xy = np.array([x,y])
            xy = np.transpose(xy)
            patch = patches.Polygon(xy, color = 'r')
            ax.add_patch(patch)
        if fixity.is_fixed[1] is True:
            point = input_system['nodes'][fixity.node_id].coordinates
            dx = scaling_factor
            dy = dx*1.5
            x = [point[0], point[0]+dx, point[0]-dx]
            y = [point[1], point[1]-dy, point[1]-dy]
            xy = np.array([x,y])
            xy = np.transpose(xy)
            patch = patches.Polygon(xy, color = 'r')
            ax.add_patch(patch)

def plot_computation_model(computation_model):

    x_lim, y_lim, segments, x_m, y_m, m_id = get_member_limits_and_segments_for_plot(computation_model, offset_factor=0.25)

    fig, ax = plt.subplots()
    ax.set_title('Computational model')
    # ax.set_xlim(x_lim)
    # ax.set_ylim(y_lim)

    # members
    for segment in segments:
        ax.add_line(
            PLine2D(segment[0], segment[1], alpha=0.5, color='grey'))
    for i, txt in enumerate(m_id):
        ax.annotate("m_" + str(txt), (x_m[i], y_m[i]))

    # nodes
    x_n, y_n, n_id = get_nodal_data_for_plot(computation_model)
    ax.scatter(x_n, y_n)
    for i, txt in enumerate(n_id):
        ax.annotate("n_" + str(txt), (x_n[i], y_n[i]))

    # (external) forces
    x, y, u, v, c = get_forces_for_plot(computation_model, True, 0.01)
    for i in range(len(x)):
        if (u[i]**2 + v[i]**2)**0.5 > TOL:
            ax.arrow(x[i], y[i], u[i], v[i], color=c[i],
                        length_includes_head=True, head_width=0.25, head_length=0.25)

def plot_solved_system(computation_model):
    fig, ax = plt.subplots()
    ax.set_title('Results: normal force distribution in system')

    # todo: some better solution
    system_scale = 0.05

    results = []

    for key, element in computation_model['elements'].items():

        # add Rectangles and Elementnumbers
        segment = Segment2D(None,
                            [computation_model['nodes'][element.nodes[0]],
                                computation_model['nodes'][element.nodes[1]]])

        dx = segment.x[1] - segment.x[0]
        dy = segment.y[1] - segment.y[0]

        width = segment.length
        height = segment.length*0.3# ()system.largest_element_length*0.25
        if dy == 0:
            angle = 0
            # choose point with smaller x-coordinate as xy
            if segment.x[0] < segment.x[1]:
                xy = [segment.x[0],segment.y[0]]
            else:
                xy = [segment.x[1],segment.y[1]]

            center_text = [segment.x[0]+0.5*dx,segment.y[0]]

        elif dx == 0:
            angle = 90
            # choose node with smaller y-coordinate as xy
            if segment.y[0] < segment.y[1]:
                xy = [segment.x[0],segment.y[0]]
            else:
                xy = [segment.x[1],segment.y[1]]

            center_text = [segment.x[0],segment.y[0]+0.5*dy]
        else:
            # calculate angle

            angle = np.degrees(np.arctan(float(dy/dx)))
            # choose node at lower left
            if angle < 0:
                angle = angle + 360
            if (angle > 0) and (angle < 180):
                xy = [segment.x[0],segment.y[0]]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 180 and angle <= 270:
                xy = [segment.x[1],segment.y[1]]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)
            elif angle > 270:
                xy = [segment.x[0],segment.y[0]]
                angle = np.radians(angle)
                center_text = [xy[0]+0.5*(np.cos(angle)*width),xy[1]+0.5*(np.sin(angle)*width)]
                angle = np.degrees(angle)

        if abs(element.force_magnitude)  < TOL:
            center = segment.midpoint.coordinates
            radius = 0.05 * segment.length

            patch = patches.Circle(center,radius,ec=(0,0,0,0.9), fc=(1,0,0,0.25))

        elif element.element_type == 'tension':
            height = element.force_magnitude * system_scale*0.1
            patch = patches.Rectangle(xy, width, height, angle, ec=(0,0,0,0.9), fc=(0,0,1,0.5))

        elif element.element_type == 'compression':
            height = element.force_magnitude * system_scale*0.1
            patch = patches.Rectangle(xy, width, height, angle, ec=(0,0,0,0.9), fc=(1,0,0,0.5))

        ax.add_patch(patch)
        #ax.annotate('S %d' %element.id,(center_text[0],center_text[1]))

        #member
        ax.add_line(
            PLine2D(segment.x, segment.y, alpha=0.5, color='grey'))
        # member id
        ax.annotate('S_' + str(element.id), (segment.midpoint.coordinates[0], segment.midpoint.coordinates[1]))

        # create string with results and add to rectangle
        value = round(element.force_magnitude,3)
        if element.element_type == 'compression':
            value *= -1
        results.append('S_%d = %.2f kN \n' %(element.id,value))

    results = ''.join(results)
    # identify location dynamically
    results_loc = (17.0, 0.0)
    ax.annotate(results,(results_loc))

    # set limits dynamically
    ax.set_xlim([-2.5, 25])
    ax.set_ylim([-2.5, 8])

    pass

def plot_force_diagram(force_diagram):
    fig, ax = plt.subplots()

    # force segments
    segments = []
    for segment in force_diagram['force_segments']:
        seg = segment.get_scaled_segment(1.25,'both')
        segments.append([seg.x, seg.y])

    counter = 0
    for segment in segments:
        ax.add_line(PLine2D(segment[0], segment[1], alpha=0.5, color='grey', linestyle='--'))

    # pole segments
    segments = []
    s_id = []
    s_x = []
    s_y = []
    for segment in force_diagram['pole_segments']:
        seg = segment.get_scaled_segment(1.25,'both')
        segments.append([seg.x, seg.y])
        s_id.append(segment.id)
        s_x.append(segment.midpoint.coordinates[0])
        s_y.append(segment.midpoint.coordinates[1])

    for segment in segments:
        ax.add_line(PLine2D(segment[0], segment[1], alpha=0.5, color='black', linestyle='-.'))

    for i, txt in enumerate(s_id):
        ax.annotate(txt, (s_x[i], s_y[i]))

    # forces
    x = []
    y = []
    u = []
    v = []
    c = []

    for base_point in force_diagram['force_base_points']:
        x.append(base_point.coordinates[0])
        y.append(base_point.coordinates[1])
    for force in force_diagram['forces']:
        u.append(force.direction[0] * force.magnitude)
        v.append(force.direction[1] * force.magnitude)
        if force.force_type == 'external':
            c.append('magenta')
        elif force.force_type == 'reaction':
            c.append('green')
        elif force.force_type == 'internal':
            c.append('blue')

    for i in range(len(x)):
        if (u[i]**2 + v[i]**2)**0.5 > TOL:
            ax.arrow(x[i], y[i], u[i], v[i], color=c[i],
                        length_includes_head=True, head_width=12.5, head_length=12.5)

    # reaction
    custom_str = ''

    if force_diagram['resultant'].magnitude > TOL:
        x = force_diagram['force_base_points'][0].coordinates[0]
        y = force_diagram['force_base_points'][0].coordinates[1]
        u = force_diagram['resultant'].direction[0] * force_diagram['resultant'].magnitude
        v = force_diagram['resultant'].direction[1] * force_diagram['resultant'].magnitude

        ax.arrow(x, y, u, v, color='red',
                    length_includes_head=True, head_width=12.5, head_length=12.5)


        custom_str += '\n Resultant location - x: ' + str(round(x,2)) + ' y: ' + str(round(y,2))
        custom_str += '\n and components - u: ' + str(round(u,2)) + ' v: ' + str(round(v,2))
    else:
        custom_str += '\n Resultant has zero magnitude (equilibrium)'
    ax.set_title('Forces - force diagram: ' + custom_str)

    #ax.autoscale() #does not seem to work properly
    ax.set_xlim([-100, 100])
    ax.set_ylim([-175, 100])

def plot_space_diagram(space_diagram):
    ##
    fig, ax = plt.subplots()
    custom_str = '\n with resultant along line (a,b,c): ' + str(space_diagram['resultant'].line['coefficients'])
    ax.set_title('Forces - space diagram, '+ custom_str)

    # # force segments
    # segments = []
    # for segment in force_diagram['force_segments']:
    #     seg = segment.get_scaled_segment(1.25,'both')
    #     segments.append([seg.x, seg.y])

    # counter = 0
    # for segment in segments:
    #     ax.add_line(PLine2D(segment[0], segment[1], alpha=0.5, color='grey', linestyle='--'))

    # pole segments
    segments = []
    s_id = []
    s_x = []
    s_y = []
    for segment in space_diagram['pole_segments']:
        seg = segment.get_scaled_segment(1.25,'both')
        segments.append([seg.x, seg.y])
        s_id.append(segment.id)
        s_x.append(segment.midpoint.coordinates[0])
        s_y.append(segment.midpoint.coordinates[1])

    for segment in segments:
        ax.add_line(PLine2D(segment[0], segment[1], alpha=0.5, color='black', linestyle='-.'))

    for i, txt in enumerate(s_id):
        ax.annotate(txt, (s_x[i], s_y[i]))

    # nodes
    x = []
    y = []

    for point in space_diagram['intersection_points']:
        x.append(point.coordinates[0])
        y.append(point.coordinates[1])
    ax.scatter(x, y)

    # forces
    x = []
    y = []
    u = []
    v = []

    for force in space_diagram['forces']:
        x.append(force.coordinates[0])
        y.append(force.coordinates[1])
        u.append(force.direction[0] * force.magnitude)
        v.append(force.direction[1] * force.magnitude)

    for i in range(len(x)):
        if (u[i]**2 + v[i]**2)**0.5 > TOL:
            ax.arrow(x[i], y[i], u[i], v[i], color='magenta',
                        length_includes_head=True, head_width=12.5, head_length=12.5)

    # reaction
    x = space_diagram['resultant'].coordinates[0]
    y = space_diagram['resultant'].coordinates[1]
    u = space_diagram['resultant'].direction[0] * space_diagram['resultant'].magnitude
    v = space_diagram['resultant'].direction[1] * space_diagram['resultant'].magnitude

    ax.arrow(x, y, u, v, color='red',
                length_includes_head=True, head_width=12.5, head_length=12.5)

    #ax.autoscale() #does not seem to work properly
    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])

def plot_decomposed_forces(resultant, decomposed_forces, points):
    ##
    fig, ax = plt.subplots()
    ax.set_title('Force - decomposed')

    # forces
    x = []
    y = []
    u = []
    v = []

    for force in decomposed_forces:
        x.append(force.coordinates[0])
        y.append(force.coordinates[1])
        u.append(force.direction[0] * force.magnitude)
        v.append(force.direction[1] * force.magnitude)

    for i in range(len(x)):
        if (u[i]**2 + v[i]**2)**0.5 > TOL:
            ax.arrow(x[i], y[i], u[i], v[i], color='green',
                    length_includes_head=True, head_width=12.5, head_length=12.5)

    # resultant
    x = resultant.coordinates[0]
    y = resultant.coordinates[1]
    u = resultant.direction[0] * resultant.magnitude
    v = resultant.direction[1] * resultant.magnitude

    ax.arrow(x, y, u, v, color='red',
                length_includes_head=True, head_width=12.5, head_length=12.5)

    # nodes
    x = []
    y = []

    for point in points:
        x.append(point[0])
        y.append(point[1])
    ax.scatter(x, y)

    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])

def plot_reaction_forces(reactions, resultant):
    ##
    fig, ax = plt.subplots()
    ax.set_title('Resultant and reaction(s)')

    # forces
    x = []
    y = []
    u = []
    v = []

    for force in reactions:
        x.append(force.coordinates[0])
        y.append(force.coordinates[1])
        u.append(force.direction[0] * force.magnitude)
        v.append(force.direction[1] * force.magnitude)

    for i in range(len(x)):
        if (u[i]**2 + v[i]**2)**0.5 > TOL:
            ax.arrow(x[i], y[i], u[i], v[i], color='green',
                    length_includes_head=True, head_width=12.5, head_length=12.5)

    # resultant
    x = resultant.coordinates[0]
    y = resultant.coordinates[1]
    u = resultant.direction[0] * resultant.magnitude
    v = resultant.direction[1] * resultant.magnitude

    ax.arrow(x, y, u, v, color='red',
                length_includes_head=True, head_width=12.5, head_length=12.5)

    ax.set_xlim([-200, 200])
    ax.set_ylim([-200, 200])