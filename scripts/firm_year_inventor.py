#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firm and Year to Inventor

This script links firm + year to their patents and patents' inventors and 
details, including name, gender, and locations.

The files produced are outputs/firm_year_inventor.csv, which has the header:
    ipo_firm, year, inventor_id, patent_id, assignee_id, 
    name_last, name_first, gender, city, 
    state, country, latitude, longitude,
and outputs/inventor_patents, which has the header:
    inventor_id, patent_id, assignee_id

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load patent_assignee
patent_assignee_file = open('../patent_data/patent_assignee.tsv', 
                            encoding='utf-8-sig')
patent_assignee = csv.DictReader(patent_assignee_file, delimiter='\t')

# Create patent to assignee dictionary
print('Creating assignee dict\n...')
patent_to_assignee = {}
for row in patent_assignee:
    patent_to_assignee[row['patent_id']] = row['assignee_id']

# Load patent_inventor
patent_inventor_file = open('../patent_data/patent_inventor.tsv', 
                            encoding='utf-8-sig')
patent_inventor = csv.DictReader(patent_inventor_file, delimiter='\t')

# Create inventor to details dictionary
print('Creating patent to details dict\n...')
inventor_to_details = {} #id -> [name_last, name_first, location_id, male]

# Create patent to inventor dictionary
print('Creating patent to inventor dict\n...')
patent_to_inventors = {}
inventor_to_patents = {} 
for row in patent_inventor:
    inventor_lst = patent_to_inventors.get(row['patent_id'], [])
    inventor_lst.append(row['inventor_id'])
    patent_to_inventors[row['patent_id']] = inventor_lst
    
    patent_lst = inventor_to_patents.get(row['inventor_id'], [])
    patent_lst.append(row['patent_id'])
    inventor_to_patents[row['inventor_id']] = patent_lst
    
    # Get location id
    details = inventor_to_details.get(row['inventor_id'], [None] * 4)
    lst = details[2]
    if not lst:
        lst = []
    lst.append(row['location_id'])
    details[2] = lst
    inventor_to_details[row['inventor_id']] = details
    
# Load inventor
inventor_file = open('../patent_data/inventor.tsv', encoding='utf-8-sig')
inventor = csv.DictReader(inventor_file, delimiter='\t')

# Load inventor_gender
inventor_gender_file = open('../patent_data/inventor_gender.tsv', 
                            encoding='utf-8-sig')
inventor_gender = csv.DictReader(inventor_gender_file, delimiter='\t')

# Continue inventor to details dictionary
print('Continue creating patent to details dict\n...')
for row in inventor:
    if row['id'] in inventor_to_details:
        inventor_to_details[row['id']][0] = row['name_last']
        inventor_to_details[row['id']][1] = row['name_first']
    else:
        inventor_to_details[row['id']] = [
                row['name_last'], 
                row['name_first'], 
                None, 
                None
            ]
    
for row in inventor_gender:
    details = inventor_to_details.get(row['disamb_inventor_id_20200929'])
    if details:
        details[3] = row['male'] #0 is female, 1 is male
        inventor_to_details[row['disamb_inventor_id_20200929']] = details

# Load location
location_file = open('../patent_data/location.tsv', encoding='utf-8-sig')
location = csv.DictReader(location_file, delimiter='\t')

# Create location to details dictionary
print('Creating location to details dict\n...')
location_to_details = {} #id -> [city, state, country, latitude, longitude]
for row in location:
    location_to_details[row['id']] = [
            row['city'],
            row['state'], 
            row['country'], 
            row['latitude'], 
            row['longitude'], 
        ]

# Load Kenneth table
firm_year_patentcnt_file = open('../outputs/firm_year_patentcnt_REVISED.csv', 
                            encoding='utf-8-sig')
firm_year_patentcnt = csv.DictReader(firm_year_patentcnt_file, delimiter=',')

# Write to output file
print('Creating output file 1 (firm_year_inventor)\n...')
with open('../outputs/firm_year_inventor.csv', 'w', 
              newline="\n", encoding='utf-8-sig') as output_file1:
    output1 = csv.writer(output_file1, delimiter=',')
    header = ['ipo_firm', 'year', 'inventor_id', 'patent_id', 'assignee_id', 
              'name_last', 'name_first', 'gender', 'city', 
              'state', 'country', 'latitude', 'longitude']
    output1.writerow(header)
    
    print('Writing to output file\n...')
    na4 = ['N/A'] * 4
    na5 = ['N/A'] * 5
    for row in firm_year_patentcnt:
        for patent in row['patent_ids'].split('; '):
            for inventor in patent_to_inventors.get(patent, []):
                inv_details = inventor_to_details.get(inventor, na4)
                if inv_details[2]:
                    for loc in inv_details[2]:
                        loc_details = location_to_details.get(loc, na5)
                        output1.writerow([
                                row['ipo_firm'], 
                                row['year'],
                                inventor,
                                patent,
                                patent_to_assignee.get(patent, 'N/A'),
                                inv_details[0],
                                inv_details[1],
                                inv_details[3],
                                loc_details[0],
                                loc_details[1],
                                loc_details[2],
                                loc_details[3],
                                loc_details[4],
                            ])

print('Creating output file 2 (inventor_patent)\n...')
with open('../outputs/inventor_patent.csv', 'w', 
              newline="\n", encoding='utf-8-sig') as output_file2:
    output2 = csv.writer(output_file2, delimiter=',')
    header = ['inventor_id', 'patent_id', 'assignee_id']
    output2.writerow(header)
    
    print('Writing to output file\n...')
    for inventor, patents in inventor_to_patents.items():
        for patent in patents:
            output2.writerow([
                    inventor, 
                    patent, 
                    patent_to_assignee.get(patent, 'N/A')
                ])

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)