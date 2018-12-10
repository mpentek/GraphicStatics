'''
Mock to check equilibrium at node 6 - example 4
'''

from matplotlib import pyplot as plt
import warnings

# needed to call the __init__.py in utilitites folder
# so that later element2d - Element2D can have it on path
# to be able to call it
from utilities import *

from entitites.element2d import Element2D
from entitites.force2d import Force2D

from utilities.mechanical_utilities import get_force_diagram, decompose_force_into_components_by_directions
from utilities.plot_utilities import plot_force_diagram
from utilities.geometric_utilities import are_parallel, TOL

#
node_id = '9'

# defining members 8 and 10
element_m8 = Element2D('8', ['8', '9'], [[-2.5, -1.5], [-7.5, -0.9]])
element_m10 = Element2D('10', ['1', '9'], [[-8.5, 4.0], [-7.5, -0.9]])
elements = [element_m8, element_m10]

# defining the force at node 9 from member 9
force_m9 = Force2D(
    '9i', '6', [-7.5, -0.9], [-0.98418 * 172.2154, 0.17771 * 172.2154], 'internal')
forces = [force_m9]

force_diagram = get_force_diagram(forces)

plot_force_diagram(force_diagram)

directions = [elements[0].line['direction'], elements[1].line['direction']]
decomposed_forces, points = decompose_force_into_components_by_directions(force_diagram['resultant'],
                                                                          directions)


# check nodal equilibrium#
for idx, df in enumerate(decomposed_forces):
    # get reaction
    reaction = df
    # flip sign
    reaction.direction = [- reaction.direction[0], - reaction.direction[1]]
    forces.append(reaction)

    # check if parallel
    force_and_member_parallel = are_parallel(
        [elements[idx].line, df.line])
    print("## ARE PARALLEL: ", force_and_member_parallel)
    if not(force_and_member_parallel):
        warnings.warn('Force and member not parallel at node ' +
                    node_id + '!', Warning)

        print("element id: ", elements[idx].id)
        print("element_dir: ", elements[idx].line['direction'])
        print("resultant_dir: ", df.direction)
        print("element_line: ", elements[idx].line['coefficients'])
        print("resultant_line: ", df.line['coefficients'])
        print("resultant_coordinates: ", df.coordinates)
    else:
        print("Results for reaction "+ str(idx)+": ")
        print("Direction: ", reaction.direction)
        print("Magnitude: ", reaction.magnitude)
        print("Should match element " + elements[idx].id)
        print("Direction: ", elements[idx].line['direction'])

'''
In member 8 we get for reaction 0 - so force in member 8:
Results for reaction 0:
Direction:  [0.9928768384869221, -0.11914522061843064]
Magnitude:  168.54392709777838
Should match element 8
Direction:  [-0.992876838486922, 0.11914522061843064]
'''


force_diagram = get_force_diagram(forces)
plot_force_diagram(force_diagram)

if force_diagram['resultant'].magnitude > TOL:
    warnings.warn(
        'Computation model not in equilibrium at node ' + node_id + '!', Warning)
else:
    print('Node ' + node_id + ' in equilibrium')

plt.show()

print()
