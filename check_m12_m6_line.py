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

# defining member 12
element_m12 = Element2D('12', ['3', '7'], [[3.5, 6.0], [2.5, -1.5]], False)
element_m12mod = Element2D(
    '12m', ['3', '7'], [[3.5, 6.0], [2.769, 0.523]], False)
elements = [element_m12, element_m12mod]

for element in elements:
    print('element')
    print('id ', element.id)
    print('midpoint ', element.midpoint)
    print('line coef ', element.line['coefficients'])
    print('line coef ', element.line['direction'])

# defining member 6
element_m6 = Element2D('6', ['6', '7'], [[7.5, -0.9], [2.5, -1.5]], False)
element_m6mod = Element2D(
    '6m', ['6', '7'], [[7.5, -0.9], [2.769, 0.523]], False)
elements = [element_m6, element_m6mod]

for element in elements:
    print('element')
    print('id ', element.id)
    print('midpoint ', element.midpoint)
    print('line coef ', element.line['coefficients'])
    print('line coef ', element.line['direction'])
