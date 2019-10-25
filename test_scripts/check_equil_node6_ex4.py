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

from utilities.mechanical_utilities import get_force_diagram
from utilities.plot_utilities import plot_force_diagram
from utilities.geometric_utilities import are_parallel, TOL

#
node_id = '6'

# defining member 6
element_m6 = Element2D('6', ['6', '7'], [[7.5, -0.9], [2.5, -1.5]])
elements = [element_m6]

# defining the force at node 6 from member 13

## NOTE: what currently is given as a result
force_m13 = Force2D(
    '13j', '6', [7.5, -0.9], [0.19996 * 1.599296, 0.9798 * 1.599296], 'internal')

## NOTE: what should be the result
# force_m13 = Force2D(
#     '13j', '6', [7.5, -0.9], [-0.19996 * 10.7401, -0.9798 * 10.7401], 'internal')

# defining the force at node 6 from member 5
force_m5 = Force2D(
    '5j', '6', [7.5, -0.9], [0.98418 * 172.2154, 0.17771 * 172.2154], 'internal')
forces = [force_m13, force_m5]

force_diagram = get_force_diagram(forces)

plot_force_diagram(force_diagram)

force_and_member_parallel = are_parallel(
    [elements[0].line, force_diagram['resultant'].line])

print("## ARE PARALLEL: ", force_and_member_parallel)
if not(force_and_member_parallel):
    warnings.warn('Force and member not parallel at node ' +
                  node_id + '!', Warning)

    print("element id: ", elements[0].id)
    print("element_dir: ", elements[0].line['direction'])
    print("resultant_dir: ", force_diagram['resultant'].direction)
    print("element_line: ", elements[0].line['coefficients'])
    print("resultant_line: ", force_diagram['resultant'].line['coefficients'])
    print("resultant_magnitude: ", force_diagram['resultant'].magnitude)
else:
    print("Results for member 6")
    print("resultant_dir: ", force_diagram['resultant'].direction)
    print("resultant_line: ", force_diagram['resultant'].line['coefficients'])
    print("resultant_magnitude: ", force_diagram['resultant'].magnitude)

'''
Result for member 6
resultant_dir:  [0.9928768066801669, 0.11914548567442484]
resultant_line:  [-20.081248754, 167.343361976, -0.0]
resultant_magnitude:  168.54393299359842

With the correct internal member forc in member 13 we get the good result
So problem seems to be at the force calculation at nodes 1 and 4 (definitely)
resulting in wrong forces in member 10 and 13
propagating these to member 5 and 9 (and possibly others)
'''

# check nodal equilibrium#
# get reaction
reaction = force_diagram['resultant']
# flip sign
reaction.direction = [- reaction.direction[0], - reaction.direction[1]]
forces.append(reaction)
force_diagram = get_force_diagram(forces)
plot_force_diagram(force_diagram)

if force_diagram['resultant'].magnitude > TOL:
    warnings.warn(
        'Computation model not in equilibrium at node ' + node_id + '!', Warning)
else:
    print('Node ' + node_id + 'in equilibrium')

plt.show()
