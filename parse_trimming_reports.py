#!/usr/bin/env python
# coding: utf-8

from argparse import ArgumentParser
import glob
import sys
import re
import csv
import pandas as pd


args = ArgumentParser('./parse_trimming_reports.py', description="""This program
has been designed to parse the output reports from trim_galore! into table format.

Example usage: ./parse_trimming_reports.py -r *trimming_report.txt
""")

args.add_argument(
	'-r',
	'--report_files',
	nargs='+', # This tells the program that if they specify this flag, they have to give it at least one input. If they don't specify it, then the default will go in.
	help="""\
	This is an optional way to use the command line to list the report files generated
	by trim_galore. The other option is to use the --text (-t) option to specify a text
	file that lists the report files. These files typically end in '_trimming_report.txt'.""",
	default=None
)

args.add_argument(
	'-o',
	'--output_file',
	help="""This is the name of the output csv file containing relevant information
	from the trimming report files generated by trim_galore! Default file is
	'trim_galore_combined_report.csv' """,
	default='trim_galore_combined_report.csv',
)

args = args.parse_args()
report_files = args.report_files
output_file = args.output_file

def error_message():
	print()
	print("""\tWelcome to parse_trimming_reports.py. This program has been designed
	to parse the output reports from trim_galore! into table format.""")
	print()
	print("\tExample usage: ./parse_trimming_reports.py -r *trimming_report.txt")
	print()

if not report_files:
	report_files = glob.glob("*trimming_report.txt")
	if len(report_files > 0):
		print()
		print("\tYou have not specified any trimming_report files to parse.")
		print()
		print("\tParsing files ending in 'trimming_report.txt' from your current working directory.")
		print()

if len(report_files) == 0:
	error_message()
	print("\tNo trimming report files were specified or found in your current working directory.")
	print()
	print("""\tPlease specify input files using the -r option or run parse_trimming_reports.py
	from a directory containing report files.""")
	print()
	sys.exit(1)

if not output_file.endswith(".csv"):
	output_file = output_file+".csv"

def parse_trimming_report(input_file):
	with open(input_file, 'r') as file:
		individual_dictionary = {}
		reader = csv.reader(file, delimiter = ':')
		for row in reader:
			if len(row) > 0:
				if row[0] == 'Input filename':
					individual_dictionary['file_name'] = row[1].strip()
				if row[0] == 'Adapter sequence':
					individual_dictionary['adapter_sequence'] = row[1].strip()
				if row[0] == 'Quality Phred score cutoff':
					individual_dictionary['quality_cutoff'] = row[1].strip()
				if row[0] == 'Quality encoding type selected':
					individual_dictionary['quality_type'] = row[1].strip()
				if row[0] == 'Maximum trimming error rate':
					individual_dictionary['max_error_rate'] = row[1].strip()
				if row[0] == 'Minimum required adapter overlap (stringency)':
					individual_dictionary['minimum_overlap'] = row[1].strip()
				if row[0] == 'Minimum required sequence length before a sequence gets removed':
					individual_dictionary['min_keep_length'] = row[1].strip()
				if row[0] == 'Command line parameters':
					individual_dictionary['command_line'] = row[1].strip()
				if row[0] == 'Total reads processed':
					individual_dictionary['reads_processed'] = int(re.sub("[^0-9]", "", row[1]))
				if row[0] == 'Reads with adapters':
					individual_dictionary['reads_with_adapters'] = int(re.sub("[^0-9]", "", re.search('(.+)\(',row[1]).group(1)))
					individual_dictionary['percent_with_adapters'] = 100*individual_dictionary['reads_with_adapters']/individual_dictionary['reads_processed']
					#re.search('\((.+)\)',row[1]).group(1)
				if row[0] == 'Reads written (passing filters)':
					individual_dictionary['reads_passing_filters'] = int(re.sub("[^0-9]", "", re.search('(.+)\(',row[1]).group(1)))
					individual_dictionary['percent_passing_filters'] = 100*individual_dictionary['reads_passing_filters']/individual_dictionary['reads_processed']
					#re.search('\((.+)\)',row[1]).group(1)
				if row[0] == 'Total basepairs processed':
					individual_dictionary['bases_processed'] = int(re.sub("[^0-9]", "", row[1]))
				if row[0] == 'Quality-trimmed':
					individual_dictionary['quality_trimmed_bases'] = int(re.sub("[^0-9]", "", re.search('(.+)\(',row[1]).group(1)))
					individual_dictionary['quality_trimmed_percent'] = 100*individual_dictionary['quality_trimmed_bases']/individual_dictionary['bases_processed']
					#re.search('\((.+)\)',row[1]).group(1)
				if row[0] == 'Total written (filtered)':
					individual_dictionary['total_kept_bases'] = int(re.sub("[^0-9]", "", re.search('(.+)\(',row[1]).group(1)))
					individual_dictionary['total_kept_percent'] = 100*individual_dictionary['total_kept_bases']/individual_dictionary['bases_processed']
					#re.search('\((.+)\)',row[1]).group(1) 99.2
		return individual_dictionary

parsed_dictionaries = []
for input_file in report_files:
	parsed_dictionaries.append(parse_trimming_report(input_file))

parsed_dataframe = pd.DataFrame(parsed_dictionaries)
parsed_dataframe.to_csv(output_file)
