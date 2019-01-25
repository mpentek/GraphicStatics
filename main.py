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
input_files = {1 : 'sample_input',  # can be checked with Stiff
               2 : 'sample_input_mod1',
               3 : 'sample_input_mod2',
               4 : 'double_arch_kinematic_top_load',  # TODO: check the bug at nodes 6,7,8,9 due to wrong force (progpagation) from member 6 (member 5 is still correct)
               5 : 'double_arch_kinematic_top_load_mod1',  # TODO: check the bug at nodes 6,7,8,9 due to wrong force (progpagation) from member 6 (member 5 is still correct
               6 : 'double_arch_kinematic_bottom_load',  # TODO: check the bug at nodes 6,7,8,9 due to wrong force (progpagation) from member 6 (member 5 is still correct
               7 : 'double_arch_top_load',  # can be checked with Stiff
               8 : 'double_arch_bottom_load',  # can be checked with Stiff
               9 : 'double_arch_kinematic_top_load_mod2', # simple for debugging
               10 : 'BC belastet ',
               11 : 'geknicktes_System'}
selected_file_idx = 8

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
sample_analysis.postprocess()

sample_cremona_plan = cremona_plan(sample_analysis)

save_to_pdf(join_path(output_folder, output_file_name_prefix +
                      input_files[selected_file_idx]))

#save_to_pdf(output_file_path) PM

plt.show()
