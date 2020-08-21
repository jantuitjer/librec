#!/usr/bin/python3

import subprocess
import os
import sys
import json
from datetime import date
from datetime import datetime

AMOUNT_OF_RAM='-Xmx16384m'
REC_LEN = 2
RUN_CONFIG_FILE = ''
HYBRID_JAR = 'hybrid_librec.jar'
STARTING_CONFIG_FILE = 'current_config.properties'
RUN_MODE_Ranking = False
#JAVA_PATH = 'C:\Program Files (x86)\Common Files\Oracle\Java\javapath'
runs = list()

def run_hybrid(mode, run_file):
	with open(run_file) as conf:
		for line in conf:
			if not line.startswith('#') or line.startswith('//') or line == '\n':
				runs.append(line)
	print(len(runs), runs)
	print(run_file)
	for run_config in runs:
		now = date.today()
		conf_name = run_config.split('.')[-2]
		if (mode == True or mode == 1 or mode == 'true' or mode == 'True'):
			print('starting ranking {} with {} at {}\n'.format(HYBRID_JAR, conf_name, datetime.now()))
			output_header = 'Results of ranking' + HYBRID_JAR + " for " + run_config + str(now)
		else:
			print('starting rating {} with {} at {}\n'.format(HYBRID_JAR, conf_name, datetime.now()))
			output_header = 'Results of ' + HYBRID_JAR + " for " + run_config + str(now)
		if '/' in conf_name:
			conf_name = conf_name.split('/')[-1]
		process = subprocess.run('java {} -jar {} {}'.format(AMOUNT_OF_RAM, HYBRID_JAR, run_config), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
		output = process.stderr.decode()
		print(output)
		if (mode == True or mode == 1 or mode == 'true' or mode == 'True'):
			output_file = open('results/ranking/' + conf_name +'-' + str(now) +  '.dat', 'w+')
		else:
			output_file = open('results/rating/' + conf_name +'-' + str(now) +  '.dat', 'w+')
		output_file.write(output_header)
		output_file.writelines(output)
		output_file.close()
	
	
def main():
	args = sys.argv
	if(len(args) != REC_LEN + 1):
		print('The {} parameters of rank_mode and run_parameters are needed.'.format(REC_LEN))
		exit(9)
	RUN_MODE_Ranking = args[1]
	RUN_CONFIG_FILE = args[2]
	print('RUN_MODE_Ranking', RUN_MODE_Ranking)
	print('RUN_CONFIG_FILE', RUN_CONFIG_FILE)
	run_hybrid(RUN_MODE_Ranking, RUN_CONFIG_FILE)
	print('done')

if __name__ == "__main__":
	main()