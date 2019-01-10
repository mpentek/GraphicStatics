"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from matplotlib import pyplot as plt
from os.path import join as join_path

from utilities.plot_utilities import save_to_pdf

from analysis import Analysis

# select the desired input file by index from the list
input_files = {1: 'sample_input',  # can be checked with Stiff
               2: 'sample_input_mod1',
               3: 'sample_input_mod2',
               # TODO: should add extra constrain not just to elements but also to nodes
               # those that have external or reaction forces - partially done
               # Automatic topology update at nodes 7 and 8
               4: 'double_arch_kinematic_top_load',
               # Automatic topology update at nodes 7 and 8
               5: 'double_arch_kinematic_top_load_mod1',
               # Automatic topology update at nodes 7 and 8
               6: 'double_arch_kinematic_bottom_load',
               7: 'double_arch_top_load',  
               8: 'double_arch_bottom_load',
               9: 'double_arch_kinematic_top_load_mod2'}  # simple for debugging
selected_file_idx = 4

# filename for import
input_folder = 'input'
input_file_name = input_files[selected_file_idx] + '.json'
json_name = join_path(input_folder, input_file_name)

# output settings
output_folder = 'output'
output_file_name_prefix = 'report_'

output_file_path = join_path(output_folder, output_file_name_prefix +
                      input_files[selected_file_idx])

# create analysis and run
#sample_analysis = Analysis(json_name,echo_level=1)
sample_analysis = Analysis(json_name)
sample_analysis.solve_system()
sample_analysis.export_computation_results(output_file_path)
sample_analysis.postprocess()

save_to_pdf(output_file_path)

plt.show()
