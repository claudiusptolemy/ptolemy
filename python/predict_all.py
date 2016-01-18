# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 09:56:24 2016

@author: Corey
"""

import os

models = ['triangulate', 'flocking']
inputs = {'xlsx': ['D:/repos/ptolemy/input/ArabiaPetraea.xlsx',
                   'D:/repos/ptolemy/input/ArabiaDeserta.xlsx',
                   'D:/repos/ptolemy/input/ArabiaFelix.xlsx',
                   'D:/repos/ptolemy/input/JudaeaPalestina.xlsx']}
output_dir = 'D:/repos/ptolemy/output'

for model in models:
    for input_type in inputs.keys():
        for input_name in inputs[input_type]:
            region = os.path.split(os.path.splitext(input_name)[0])[1]
            output_name = '%s/%s_%s.kml' % (output_dir, model, region)
            command = []
            command.append('python predict.py')
            command.append('--model %s' % model)
            command.append('--%s %s' % (input_type, input_name))
            command.append('--output %s' % output_name)
            print ' '.join(command)
            os.system(' '.join(command))
