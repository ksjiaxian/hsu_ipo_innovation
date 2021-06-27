# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This code connects the firm_year_innovation "y variables" with the analyst "x variables"
# This code also adds an additional column for ipo year. 1 for yes, 0 for no. dummy variable. 
#
# Needs both files in the dependent data folder
#
#########################################################################################

import csv
import math
import time

# start time
start_time = time.ctime()

# create the output file
print('CREATING OUTPUT FILE\n')

# create an output file (innovation_analyst)
output = open('outputs/f_y_i_analyst.csv', 'w', newline="\n", encoding='utf-8-sig')
fyi_analyst = csv.writer(output, delimiter=',')
header = ['ipo_firm', 'year', 'is_ipo_year', 'dual_dum', 'originality', 'generality4', 'generality5', 'generality7', 'patent_cnt', 'patent_ids', 'forward_cnt4', 'forward_cnt5', 'forward_cnt7', 'analyst_opinion_cnt', 'unique_analysts']
fyi_analyst.writerow(header)

print('READING FILES\n')

# load in the firm year innovation file
f_y_i_file = open('dependent_data/firm_year_innovation.csv', encoding='utf-8-sig')
f_y_i = csv.DictReader(f_y_i_file, delimiter=",")

# load in the firm year analyst coverage file
analyst_file = open('dependent_data/firm_year_analyst_coverage.csv', encoding='utf-8-sig')
analyst = csv.DictReader(analyst_file, delimiter=",")

# load in the ipo file (needed to convert ipo name to tickers)
ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.DictReader(ipo_file, delimiter=",")

print('BEGINNING PROCESSING\n')
analyst_dict = {}
for row in analyst:
	firm = row['ipo_firm']
	year = row['year']
	op_num = row['analyst_opinion_cnt']
	analyst_cnt = row['unique_analysts']

	analyst_dict[(firm,year)] = (op_num, analyst_cnt)

# create a name to ipo_year, dual dum dictionary
ipo_year_dict = {}
cnt = 0
for row in ipo:
	cnt += 1

	firm = row['firm'].strip()
	ipo_year = row['Offer date'][:4]
	dual_dum = row['dual dum']

	ipo_year_dict[firm] = (ipo_year, dual_dum)

for row in f_y_i:
	firm = row['ipo_firm']
	year = row['year']
	is_ipo_year = 0
	ipo_year, dual_dum = ipo_year_dict[firm]

	if year == ipo_year:
		is_ipo_year = 1

	row_contents = list(row.values())
	row_contents = row_contents[:2] + [is_ipo_year, dual_dum] + row_contents[2:] + list(analyst_dict[(firm,year)])
	# print(row_contents)
	fyi_analyst.writerow(row_contents)

# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time + '\n')
