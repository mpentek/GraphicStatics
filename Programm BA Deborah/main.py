# -*- coding: utf-8 -*-
"""
Created on Sat May 26 13:57:06 2018

@author: Benedikt
"""
from matplotlib import pyplot as plt
from plot import plot_system, plot_results, safe_to_pdf
from Class_System import System
from functions import calculate_member_forces, cremona_plan

# close all open figures
plt.close('all')

# filename for import
json_name = 'sample_input.json'

#create system and some atrributes from json file
system = System(json_name)

# calculate reactions
fig_reactions = plt.figure('fr poly reactions',figsize = (11.69,8.27))
ax_fr_poly = fig_reactions.add_subplot(2,1,1)
ax_fun_poly= fig_reactions.add_subplot(2,1,2)

ax_fr_poly, ax_fun_poly = system.calculate_reactions(ax_fr_poly, ax_fun_poly)

ax_fr_poly.set_title('Force Polygon to calculate reactions')
ax_fun_poly.set_title('Funicular Polygon to calculate reactions')

ax_fr_poly.axis('equal')
ax_fun_poly.axis('equal')
plt.show()

# calculate member forces by loop over method_of_joints and solved_geometry, in case it can't be solved use method_of_sections
fig_member_forces = plt.figure('Method of joints',figsize = (11.69,8.27))
fig_member_forces.subplots_adjust(top=0.904,bottom=0.0,left=0.0,right=0.948,hspace=0.62,wspace=0.0)

fig_subsystem_forces = plt.figure('Method of sections - Resultant',figsize = (11.69,8.27))

ax_sub_fr_poly = fig_subsystem_forces.add_subplot(211)
ax_sub_fun_poly = fig_subsystem_forces.add_subplot(212)

ax_sub_fr_poly.axis('equal')
ax_sub_fun_poly.axis('equal')

ax_sub_fr_poly.set_title('Subsystem Force Polyon')
ax_sub_fun_poly.set_title('Subsystem Funicular Polygon')

ax_sub_fr_poly,ax_sub_fun_poly,fig_member_forces = calculate_member_forces(ax_sub_fr_poly,ax_sub_fun_poly,fig_member_forces,system)
 
# create cremona_plan
fig_cremona = plt.figure('cremona',figsize = (11.69,8.27))
ax_cremona = fig_cremona.add_subplot(111)
ax_cremona = cremona_plan(ax_cremona,system)

ax_cremona.set_title('Cremona Plan - Force Diagram')
ax_cremona.axis('equal')

# plot results
fig_system = plt.figure('system',figsize = (11.69,8.27))
ax_system = fig_system.add_subplot(111)

ax_system = plot_system(ax_system,system)

ax_system.set_title('System')
ax_system.axis('equal')

fig_results = plt.figure('Results',figsize = (11.69,8.27))
ax_results = fig_results.add_subplot(111)#

ax_results = plot_results(ax_results,system)
ax_results.axis('equal')

plt.show()

# Safe figures to pdf
safe_to_pdf([fig_system,fig_reactions,fig_member_forces,fig_subsystem_forces,fig_cremona,fig_results])

# ToDo: create output text document


