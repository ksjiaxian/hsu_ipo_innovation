# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This simple script extracts the cusips from the IPO data set. This is used to avoid Excel's 
# type conversions (string to int)
#
# This script only extracts the first 8 digits of the cusips (also known as the 8 dig cusip)
# THis script will skip rows with no cusips, so expect the size to be smaller than the ipo dataset
#
#########################################################################################

import csv
import math
import time

# CHANGE TRUE TO FALSE IF YOU ONLY WANT CUSIPS
include_firms = True

# start time
start_time = time.ctime()

if include_firms:
	# create the output file
	print('CREATING OUTPUT FILE\n')

	# create an output file (innovation_analyst)
	output = open('outputs/cusips_8_with_firms.csv', 'w', newline="\n", encoding='utf-8-sig')
	cusips = csv.writer(output, delimiter=',')
	header = ['firm', 'ticker','cusip']
	cusips.writerow(header)

	print('READING FILES\n')

	# load in the ipo file
	ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
	ipo = csv.DictReader(ipo_file, delimiter=",")


	for row in ipo:
		cusip = row['CUSIP'][:8]
		firm = row['firm']
		ticker = row['ticker']
		cusips.writerow([firm, ticker, cusip])

else:
	# create the output file
	print('CREATING OUTPUT FILE\n')

	# create an output file (innovation_analyst)
	output = open('outputs/cusips_8.csv', 'w', newline="\n", encoding='utf-8-sig')
	cusips = csv.writer(output, delimiter=',')
	header = ['cusip']
	cusips.writerow(header)

	print('READING FILES\n')

	# load in the ipo file
	ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
	ipo = csv.DictReader(ipo_file, delimiter=",")


	for row in ipo:
		cusip = row['CUSIP']
		if cusip == '':
			continue
		cusips.writerow([cusip[:8]])


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time + '\n')
