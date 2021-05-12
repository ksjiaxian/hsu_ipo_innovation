########################################################################################################################
# Firm Year Patent
#
# Kenneth Shinn
# kshinn@seas.upenn.edu
#
# Directions: Run this file after running the file called ipo_assignee_merger.py. DO NOT move the 
# 			  matches file out of the outputs folder. 
#
# This script will return a csv file that includes the patent counts per year for each IPO firm with a patent
# There will also be a column of patent ID for checking and testing.
#
# NOTE: Patents outside of the relevant date range are ignored. 
# 		Patent counts returned by this script will be lower than the counts in the matching file.
#
########################################################################################################################

import csv
import math
import time

# start time
start_time = time.ctime()

# load in the ipo_match file
ipo_match_file = open('../outputs/name_matches.csv', encoding='utf-8-sig')
ipo_match = csv.DictReader(ipo_match_file, delimiter=",")

# load in the ipo file
ipo_file = open('../firms/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.DictReader(ipo_file, delimiter=",")

# load in the assignee file
assignee_file = open('../patent_data/assignee_firms.tsv', encoding='utf-8-sig')
assignee = csv.DictReader(assignee_file, delimiter="\t")

# load in the patent_assignee file
patent_assignee_file = open('../patent_data/patent_assignee.tsv', encoding='utf-8-sig')
patent_assignee = csv.DictReader(patent_assignee_file, delimiter="\t")

# load in the patent file
patent_file = open('../patent_data/patent.tsv', encoding='utf-8-sig')
patent = csv.DictReader(patent_file, delimiter="\t")

# create an output file (firm year patent cnt)
output = open('../outputs/firm_year_patentcnt.csv', 'w', newline="\n", encoding='utf-8-sig')
firm_year_patentcnt = csv.writer(output, delimiter=',')
header = ['ipo_firm', 'year', 'patent_cnt', 'patent_ids']
firm_year_patentcnt.writerow(header)

# go through the ipo_match file and create a dictionary, key ipo, value set of assignee alias
# also create a set of (relevant) assignee aliases 
print('INGESTING IPO ASSIGNEE MATCHES\n')
ipo_alias = {}
all_assignee_alias = set()
for i in ipo_match:
	ipo_firm = i['ipo_firm'].strip()
	assignee_alias = i['assignee_firm'].strip()

	all_assignee_alias.add(assignee_alias)

	if ipo_firm in ipo_alias:
		ipo_alias[ipo_firm].add(assignee_alias)
	else:
		ipo_alias[ipo_firm] = {assignee_alias}


# go through the ipo file and get the start dates
print('INGESTING IPOS\n')
ipo_start_dates = {}
for i in ipo:
	ipo_firm = i['firm'].strip()
	start_date = i['Founding'].strip()
	ipo_start_dates[ipo_firm] = start_date


# go through the patent data, generate a patent_id - year dictionary
print('INGESTING PATENTS\n')
patent_id_year = {}
for p in patent:
	patent_id = p['id'].strip()
	year = int(p['date'][0:4]) # TODO: HERE TO GET MORE INFO ABOUT PATENT, just want to get the year now
	patent_id_year[patent_id] = year

# generate a set of relevant assignee_id from set of relevant assignee aliases
# also generate assignee name to id
print('INGESTING ASSIGNEES\n')
assignee_name_id = {}
all_assignee_ids = set()
for a in assignee:
	assignee_firm = a['firm'].strip()
	assignee_id = a['id'].strip()
	assignee_name_id[assignee_firm] = assignee_id
	if assignee_firm in all_assignee_alias:
		all_assignee_ids.add(assignee_id)


# go through the assignee - patent connector, generate a assignee - patent_id set dictionary
print('INGESTING PATENT ASSIGNEES\n')
assignee_patent_id_set = {}
for pa in patent_assignee:
	patent_id = pa['patent_id'].strip()
	assignee_id = pa['assignee_id'].strip()

	if assignee_id in all_assignee_ids:
		if assignee_id in assignee_patent_id_set:
			assignee_patent_id_set[assignee_id].add(patent_id)
		else:
			assignee_patent_id_set[assignee_id] = {patent_id}

# go through the ipo with patent and perform actions
print('STARTING COMPUTATION PROCESS\n')
for ipo, alias_set in ipo_alias.items():
	start_date = int(ipo_start_dates[ipo])

	#generate "buckets" for every year from start date to 2016
	year_patents = {}
	for year in range(start_date, 2021): # REMEMBER TO CHANGE THIS BACK TO 2017
		year_patents[year] = set() # starting with an empty set per patent

	# iterate through alias set finding patents
	for a in alias_set:
		# get set of patent_id for this assignee_alias
		a_id = assignee_name_id[a]
		p_id_set = assignee_patent_id_set[a_id]

		# iterate through the patent_id set and get patent dates
		for p_id in p_id_set:
			# TODO: HERE TO ACCESS MORE INFORMATION ABOUT THE PATENT
			p_year = patent_id_year[p_id]

			# patent year may be too recent or too early (from incorrect matching)
			# skip this patent_id if so
			if p_year > 2016 or p_year < start_date:
				continue

			year_patents[p_year].add(p_id) # add this patent id to the relevant bucket

	# write the information into the output file
	for year, patent_id_set in year_patents.items():
		row = [ipo, year, len(patent_id_set), '; '.join(patent_id_set)]
		firm_year_patentcnt.writerow(row)


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)


















