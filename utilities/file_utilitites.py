"""
Created on Tuesday Dec 26 11:00 2018

@author: mate.pentek@tum.de

"""

import jsonpickle
jsonpickle.set_encoder_options('simplejson', sort_keys=True, indent=4)
jsonpickle.set_encoder_options('demjson', compactly=False)


def json_dump_model(model, file_path):
    with open(file_path + '.json', 'w') as outfile:
        outfile.write(jsonpickle.encode(model))
