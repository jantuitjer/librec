#!/usr/bin/python3

import subprocess
import os
import sys
import json

RUN_CONFIG_FILE = 'run_parameters.txt'
HYBRID_JAR = 'hybrid_librec.jar'
STARTING_CONFIG_FILE = 'current_config.properties'
#JAVA_PATH = 'C:\Program Files (x86)\Common Files\Oracle\Java\javapath'
runs = list()

with open(RUN_CONFIG_FILE) as conf:
    for line in conf:
        if not line.startswith('#') or line.startswith('//'):
            runs.append(line)
for run_config in runs:
    conf_name = run_config.split('.')[-2]
    print('starting', conf_name)
    if '/' in conf_name:
        conf_name = conf_name.split('/')[-1]
    output_header = 'Results of ' + run_config
    process = subprocess.run('java -jar {} {}'.format(HYBRID_JAR, run_config), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = process.stderr.decode()
    print(output)
    output_file = open('results/' + conf_name + '.dat', 'w+')
    output_file.write(output_header)
    output_file.writelines(output)
    output_file.close()
    
    
