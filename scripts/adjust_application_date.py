# Kenneth Shinn
# kshinn@sas.upenn.edu
#
# This code realigns the dates of patents from 'firm_year_patent' by patent application date,
# rather than patent grant date. 
#
# Outputs a csv file with the same schema '[ipo_firm, year, patent_cnt, patent_ids]', 
# but with adjusted patent lists per year. 
#
#########################################################################################

import csv
import math
import time

# start time
start_time = time.ctime()

# create the output file
print('CREATING OUTPUT FILE\n')

# create an output file (firm year patent cnt)
output = open('outputs/firm_year_patentcnt_REVISED.csv', 'w', newline="\n", encoding='utf-8-sig')
fyp_2 = csv.writer(output, delimiter=',')
header = ['ipo_firm', 'year', 'patent_cnt', 'patent_ids']
fyp_2.writerow(header)


print('READING FILES\n')

# load in the application file
applications_file = open('dependent_data/application.tsv', encoding='utf-8-sig')
applications = csv.DictReader(applications_file, delimiter="\t")

# create an application dictionary
app_dict = {}
cnt = 0
for row in applications:
	cnt+=1

	patent_id = row['patent_id']
	date = row['date']

	app_dict[patent_id] = date

print('Application data size: ' + str(cnt))
print(len(app_dict))

# load in the firm_year_patentcnt data
fyp_file = open('dependent_data/firm_year_patentcnt.csv', encoding='utf-8-sig')
fyp = csv.DictReader(fyp_file, delimiter=",")

firm_patent_dict = {}
for row in fyp:
	ipo_firm = row['ipo_firm']
	patent_ids = row['patent_ids']

	if not patent_ids == '':
		patent_id_list = patent_ids.split('; ')

		if ipo_firm not in firm_patent_dict:
			firm_patent_dict[ipo_firm] = patent_id_list
		else:
			firm_patent_dict[ipo_firm] = firm_patent_dict[ipo_firm] + patent_id_list

print(len(firm_patent_dict['02 Micro International Limited']))
print(firm_patent_dict['02 Micro International Limited'])
print(app_dict[firm_patent_dict['02 Micro International Limited'][0]])

# load in the ipo file
ipo_file = open('dependent_data/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.DictReader(ipo_file, delimiter=",")

# go through the ipo file and get the start dates
# print('INGESTING IPOS\n')
ipo_start_dates = {}
for i in ipo:
	ipo_firm = i['firm'].strip()
	start_date = i['Founding'].strip()
	ipo_start_dates[ipo_firm] = start_date


# go through the ipo with patent and perform actions
print('STARTING COMPUTATION PROCESS\n')
for ipo, patent_list in firm_patent_dict.items():
	# print(ipo)
	start_date = int(ipo_start_dates[ipo])
	# print(start_date)

	#generate "buckets" for every year from start date to 2016
	year_patents = {}
	for year in range(start_date, 2017): # REMEMBER TO CHANGE THIS BACK TO 2017
		year_patents[year] = set() # starting with an empty set per patent

	# iterate through alias set finding patents
	# for a in alias_set:
	# 	# get set of patent_id for this assignee_alias
	# 	a_id = assignee_name_id[a]
	# 	p_id_set = assignee_patent_id_set[a_id]

	# iterate through the patent_id set and get patent dates
	for p_id in patent_list:
		# TODO: HERE TO ACCESS MORE INFORMATION ABOUT THE PATENT
		p_year = app_dict[p_id][:4]

		# patent year may be too recent or too early (from incorrect matching)
		# skip this patent_id if so
		if int(p_year) > 2016 or int(p_year) < start_date:
			continue

		year_patents[int(p_year)].add(p_id) # add this patent id to the relevant bucket

	# write the information into the output file
	for year, patent_id_set in year_patents.items():
		row = [ipo, year, len(patent_id_set), '; '.join(patent_id_set)]
		fyp_2.writerow(row)




# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)

