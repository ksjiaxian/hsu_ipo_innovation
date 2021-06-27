# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This code gets the subset of IPO firms that have patent information
#
#########################################################################################

import csv
import math

# start time
start_time = time.ctime()

print('READING FILES\n')

# load in the ipo firms file
ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.reader(ipo_file, delimiter=",")

# load in the firm_year_innovation file (this file contains the relevant firms)
# load in the ipo firms file
innovation_file = open('outputs/firm_year_innovation.csv', encoding='utf-8-sig')
innovation = csv.DictReader(innovation_file, delimiter=",")

# create an output file (essential the ipo_10000 file with )
output = open('outputs/relevant_ipo_firms.csv', 'w', newline="\n", encoding='utf-8-sig')
relevant_ipo_firms = csv.writer(output, delimiter=',')
header = ['firm','ipo_date','ticker','CUSIP','CRSP perm','post-issue shares','dual dum','Founding','Rollup dum']
relevant_ipo_firms.writerow(header)

innovative_firms = set()
for row in innovation:
	innovative_firms.add(row['ipo_firm'].strip())

# go through the IPO 10000 file and copy over the patent holding firms to a new document
for row in ipo:
	firm = row[0]
	if firm in innovative_firms:
		relevant_ipo_firms.writerow(row)


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time + '\n')