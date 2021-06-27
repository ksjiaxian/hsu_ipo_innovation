# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This code aggregates the analyst data by firm year. Generates two pieces of data per firm year
# 1) The number of unique analysts per firm year
# 2) The number of analyst opinions per firm year
#
# Outputs a csv file with the same schema '[ipo_firm, year, patent_cnt, patent_ids]', 
# but with adjusted patent lists per year. 
# 
# Needs a file with the (firm, years) in interest. 
#
#########################################################################################


import csv
import math
import time

# start time
start_time = time.ctime()

# create the output file
print('CREATING OUTPUT FILE\n')

# create an output file
output = open('outputs/firm_year_analyst_coverage.csv', 'w', newline="\n", encoding='utf-8-sig')
fyanalyst = csv.writer(output, delimiter=',')
header = ['ipo_firm', 'year', 'ticker', 'analyst_opinion_cnt', 'unique_analysts', 'analyst_list']
fyanalyst.writerow(header)


print('READING FILES\n')

# load in the analyst coverage file
analyst_file = open('dependent_data/analyst_coverage.csv', encoding='utf-8-sig')
analyst = csv.DictReader(analyst_file, delimiter=",")

# load in the ipo file (needed to convert ipo name to tickers)
ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.DictReader(ipo_file, delimiter=",")

# load in the firm_year_patentcnt data
fyp_file = open('dependent_data/firm_year_patentcnt.csv', encoding='utf-8-sig')
fyp = csv.DictReader(fyp_file, delimiter=",")

# create an analyst coverage dictionary
analyst_dict = {}
analyst_cnt_dict = {}
cnt = 0
for row in analyst:
	cnt+=1

	firm = row['TICKER']
	year = row['ANNDATS'][:4]
	analyst = row['ANALYS']

	if (firm, year) in analyst_dict:
		analyst_dict[(firm, year)].add(analyst)
	else:
		analyst_dict[(firm, year)] = {analyst}

	if (firm, year) in analyst_cnt_dict:
		analyst_cnt_dict[(firm, year)] = analyst_cnt_dict[(firm, year)] + 1
	else:
		analyst_cnt_dict[(firm, year)] = 1

print('Analyst data size: ' + str(cnt))


# create an name to ticker dictionary
ticker_dict = {}
cnt = 0
for row in ipo:
	cnt += 1

	firm = row['firm'].strip()
	ticker = row['ticker']

	ticker_dict[firm] = ticker
print('IPO data size: ' + str(cnt))


print('STARTING COMPUTATION PROCESS\n')

for row in fyp:
	firm = row['ipo_firm']
	year = row['year']
	ticker = ticker_dict[firm]
	key = (ticker, year)

	if key in analyst_cnt_dict:
		analyst_opinion_cnt = analyst_cnt_dict[(ticker, year)]
	else:
		analyst_opinion_cnt = 0

	if key in analyst_dict:
		analysts = analyst_dict[(ticker, year)]
	else:
		analysts = set()

	analyst_string = '; '.join(analysts)
	unique_analysts_cnt = len(analysts)

	fyanalyst.writerow([firm, year, ticker, analyst_opinion_cnt, unique_analysts_cnt, analyst_string])


# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)













