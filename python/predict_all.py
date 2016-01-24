# -*- coding: utf-8 -*-
"""
Created on Sun Jan 17 09:56:24 2016

@author: Corey
"""

import os
import subprocess

models = ['triangulate', 'flocking']
inputs = {'xlsx': ['D:/repos/ptolemy/input/ArabiaPetraea.xlsx',
                   'D:/repos/ptolemy/input/ArabiaDeserta.xlsx',
                   'D:/repos/ptolemy/input/ArabiaFelix.xlsx',
                   'D:/repos/ptolemy/input/JudaeaPalestina.xlsx',
                   'D:/repos/ptolemy/input/Syria.xlsx']}
output_dir = 'D:/repos/ptolemy/output'

for model in models:
    all_csvs = []
    for input_type in inputs.keys():
        for input_name in inputs[input_type]:
            region = os.path.split(os.path.splitext(input_name)[0])[1]
            output_name = '%s/%s_%s.kml' % (output_dir, model, region)
            csv_name = '%s/%s_%s.csv' % (output_dir, model, region)
            all_csvs.append(csv_name)
            title = '%s %s' % (model, region)
            command = []
            command.append('python predict.py')
            command.append('--model %s' % model)
            command.append('--%s %s' % (input_type, input_name))
            command.append('--output %s' % output_name)
            print ' '.join(command)
            process = subprocess.Popen(' '.join(command), shell=True, stdout=subprocess.PIPE)
            process.wait()
    for map_out_type in ['pdf', 'png']:
        command = []
        command.append('python visualize_matplotlib.py')
        command.append('--dpi 300')
        command.append('--labels ptol_name')
        command.append('--output %s/%s.%s' % (output_dir, model, map_out_type))
        command.append(' '.join(all_csvs))
        print ' '.join(command)
        process = subprocess.Popen(' '.join(command), shell=True, stdout=subprocess.PIPE)
        process.wait()
