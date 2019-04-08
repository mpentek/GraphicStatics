"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from matplotlib import pyplot as plt
from os.path import join as join_path

from utilities.plot_utilities import save_to_pdf

from analysis import Analysis
from cremona_plan import cremona_plan


# select the desired input file by index from the list
input_files = {1: 'sample_input',  # succesful
               2: 'sample_input_mod1',  # succesful
               3: 'sample_input_mod2',  # succesful, nur Diagonalen
               # Automatic topology update at nodes 7 and 8
               4: 'double_arch_kinematic_top_load',  # not in equilibrium
               # Automatic topology update at nodes 7 and 8
               5: 'double_arch_kinematic_top_load_mod1',  # not in equilibrium
               # TODO: should add extra constrain not just to elements but also to nodes (those that have external or reaction forces)
               # Automatic topology update at nodes 7 and 8
               6: 'double_arch_kinematic_bottom_load',  # succesful, keine Diagonalen
               7: 'double_arch_top_load',  # succesful, nur Diagonalen
               8: 'double_arch_bottom_load',  # succesful, nur Diagonalen
               9: 'double_arch_kinematic_top_load_mod2',  # succesful
               # PMT: need some is_contrain to be solved correctly
               # setting element 8 as is_contrain -> topology update at node 7
               # further erros -> DEBUG
               10: 'BC_belastet ',  # not in equilibrium
               11: 'geknicktes_System',  # succesful
               12: 'simple system'}  # succesful

selected_file_idx = 6

# filename for import
input_folder = 'input'
input_file_name = input_files[selected_file_idx] + '.json'
json_name = join_path(input_folder, input_file_name)

# output settings
output_folder = 'output'
output_file_name_prefix = 'report_'

# create analysis and run
#sample_analysis = Analysis(json_name,echo_level=1)
sample_analysis = Analysis(json_name)
sample_analysis.solve_system()

sample_cremona_plan = cremona_plan(sample_analysis)
sample_analysis.postprocess(sample_cremona_plan)

save_to_pdf(join_path(output_folder, output_file_name_prefix +
                      input_files[selected_file_idx]))

# save_to_pdf(output_file_path) PM

plt.show()
