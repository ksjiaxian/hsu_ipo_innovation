#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Captures time ranges for which an inventor was at a firm based on earliest and
    latest patent dates.

Outputs file inventor_timeline.csv with header: 
    inventor_id, assignee, earliest_date, latest_date

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load application
app_file = open('../patent_data/application.tsv', 
                        encoding='utf-8-sig')
application = csv.DictReader(app_file, delimiter='\t') 
    
# Create patent to year dictionary
print('Creating year dict\n...')
patent_to_year = {}
for row in application:
    patent_to_year[row['patent_id']] = int(row['date'][:4])

# Load inventor_year_patents
inventor_patents_file = open('../outputs/inventor_patent.csv', 
                      encoding='utf-8-sig')
inventor_patents = csv.DictReader(inventor_patents_file, delimiter=',')

# Load assignee_firms
assignee_firms_file = open('../patent_data/assignee.tsv', 
                      encoding='utf-8-sig')
assignee_firms = csv.DictReader(assignee_firms_file, delimiter='\t') 

# Create assignee id to firm name dict
print('Creating assignee_id to firm dict\n...')
assignee_id_to_name = {}
for row in assignee_firms:
    if row['organization']:
        assignee_id_to_name[row['id']] = row['organization']

# Load name_matches
name_matches_file = open('../outputs/name_matches_2.csv', 
                      encoding='utf-8-sig')
name_matches = csv.DictReader(name_matches_file, delimiter=',')

# Create assignee name to ipo firm dict
print('Creating assignee name to ipo name dict\n...')
ipo_name = {}
for row in name_matches:
    ipo_name[row['assignee_id']] = row['ipo_firm']
    
# Get first inventor
next(inventor_patents)
curr_inv = next(inventor_patents)['inventor_id']
inventor_patents_file.seek(0)
next(inventor_patents)

# Create output file
print('WRITING TO FILE\n')
with open('../outputs/inventor_timeline.csv', 'w', 
          newline='\n', encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['inventor_id', 'assignee', 'earliest_date', 'latest_date']
    output.writerow(header)
    
    assignee_year = {}

    for row in inventor_patents:
        # Write to file (first year -> this year)
        if not row['inventor_id'] == curr_inv:
            for assignee, year_range in assignee_year.items():
                output.writerow([curr_inv, assignee] + year_range) 
            curr_inv = row['inventor_id']
            assignee_year = {}
        
        # Track assignees
        ipo = ipo_name.get(
                row['assignee_id'], 
                assignee_id_to_name.get(row['assignee_id'], 'N/A')
        )
        year = patent_to_year.get(row['patent_id'])
        rng = assignee_year.get(ipo, [3000, 0])
        if year:
            if year < rng[0]:
                rng[0] = year
            if year > rng[1]:
                rng[1] = year
        
        assignee_year[ipo] = rng
    
    for assignee, year_range in assignee_year.items():
        output.writerow([curr_inv, assignee] + year_range)

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)