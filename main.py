"""
Created on Tuesday Dec 4 18:00 2018

@author: mate.pentek@tum.de

Partially based on the BSc Thesis of Benedikt Schatz (TUM, Statik 2018)
"""

from matplotlib import pyplot as plt
from os.path import join as join_path

from utilities.plot_utilities import save_to_pdf

from analysis import Analysis

# filename for import
input_folder = 'input'
input_file_name = 'sample_input.json'
json_name = join_path(input_folder, input_file_name)

# output settings
output_folder = 'output'
output_file_name_prefix = 'report_'

# create analysis and run
# sample_analysis = Analysis(json_name,echo_level=1)
sample_analysis = Analysis(json_name)
sample_analysis.solve_system()
sample_analysis.postprocess()

save_to_pdf(join_path(output_folder, output_file_name_prefix + input_file_name[:-5]))

plt.show()