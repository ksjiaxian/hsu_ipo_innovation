# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This code generates poison pill coverage given poison pill raw data. 
# Also generates coverage data for staggered board
# 
# Uses the keys firm, year
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
output = open('outputs/firm_year_pp_sb_coverage.csv', 'w', newline="\n", encoding='utf-8-sig')
fy_pp_sb= csv.writer(output, delimiter=',')
header = ['ipo_firm', 'year', 'is_pp', 'is_sb']
fy_pp_sb.writerow(header)

print('READING FILES\n')

# load in the poison pill and staggered board file
pp_sb_file = open('dependent_data/poison_pill_coverage.csv', encoding='utf-8-sig')
pp_sb = csv.DictReader(pp_sb_file, delimiter=",")

# load in the cusips file
cusips_file = open('dependent_data/cusips_8_with_firms.csv', encoding='utf-8-sig')
cusips = csv.DictReader(cusips_file, delimiter=",")

# load in the firm_year_patentcnt data - to get the firm years
fyp_file = open('dependent_data/firm_year_patentcnt.csv', encoding='utf-8-sig')
fyp = csv.DictReader(fyp_file, delimiter=",")

cusip_dict = {}
for row in cusips:
	firm = row['firm']
	ticker = row['ticker']
	cusip = row['cusip']

	cusip_dict[firm] = (ticker, cusip)

# process poison pill, staggered board
pp_sb_dict = {}
# sb_dict = {}
for row in pp_sb:
	firm = row['IPO_name']
	# this one is 6 digit cusip
	cusip = row['Issuer_CUSIP_SDC']
	is_sb = row['Staggered_Board']

	start_year = row['Date_of_Adoption'][-4:]
	end_year = row['Withdrawn_Date'][-4:]
	start_month = row['Date_of_Adoption'].split('/')[0]
	# print(start_month)
	if end_year == '':
		end_year = row['Expiration_Date'][-4:]
	else:
		end_year = end_year

	if (firm, cusip) in pp_sb_dict:
		pp_sb_dict[(firm, cusip)].append((start_month, start_year, end_year, is_sb))
	else:
		pp_sb_dict[(firm, cusip)] = [(start_month, start_year, end_year, is_sb)]

# print(pp_sb_dict[('3COM CORP.', '885535')]) # passes this test correctly
# print(pp_sb_dict)
f_pp_dict = {}
f_sb_dict = {}
for (firm, cusip), dates in pp_sb_dict.items():
	sb_set = set()
	pp_set = set()
	for i in range(len(dates)-1):
		start_month, start_year, end_year, is_sb = dates[i]
		last_end = end_year
		next_start_month, next_start_year, next_end_year, next_is_sb = dates[i+1]
		if end_year == '':
			true_end = next_start_year
		elif next_start_year == '':
			true_end = end_year
		else:
			true_end = min(end_year, next_start_year)

		if true_end == '':
			continue

		for i in range(int(start_year), int(true_end)):
			pp_set.add(i)
			# f_pp_dict
			# f_y_pp_sb_dict[(firm, i)] = 1
			if is_sb == 'Yes':
				sb_set.add(i)
		# broken_next_start = next_start.split('/')
		# if next_start
		if int(next_start_month) > 6 and is_sb == 'Yes':
			sb_set.add(int(true_end))
		# print(broken_next_start)

	start_month, start_year, end_year, is_sb = dates[len(dates)-1]
	if end_year == '':
		end_year = last_end
	for i in range(int(start_year), int(end_year)+1):
		pp_set.add(i)
		# f_y_pp_sb_dict[(firm, i)] = (1, is_sb)
		if is_sb == 'Yes':
			sb_set.add(i)
	f_sb_dict[firm] = sb_set
	f_pp_dict[firm] = pp_set

# print(f_sb_dict['DATAKEY, INC.'])
# print(f_pp_dict['DATAKEY, INC.'])
# print(f_y_pp_sb_dict[('3COM CORP.', 2002)])


for row in fyp:
	firm = row['ipo_firm']
	year = int(row['year'])

	is_pp = 0
	is_sb = 0

	if firm in f_pp_dict:
		# print(firm + ': ' + str(year))
		pp_set = f_pp_dict[firm]
		sb_set = f_sb_dict[firm]
		# print(pp_set)

		if year in pp_set:
			is_pp = 1
		if year in sb_set:
			is_sb = 1

	fy_pp_sb.writerow([firm, year, is_pp, is_sb])


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)
