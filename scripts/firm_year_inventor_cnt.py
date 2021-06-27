#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Maps firm, year to the number of inventors

Outputs file firm_year_inventor_cnt.csv with header: 
    ipo_firm, year, num_inventors, loss, gain, 
    ipo_inventors_left, ipo_inventors_returned

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load ipo_10000
ipo_10000_file = open('../firms/ipo_10000.csv')
ipo_10000 = csv.DictReader(ipo_10000_file, delimiter=',')

# Create ipo year dict
print('Creating IPO year dict\n...')
firm_ipo_year = {}
for row in ipo_10000:
    firm = row['ï»¿firm'].strip()
    firm_ipo_year[firm] = int(row['ipo_date'][:4])

# Load inventor_year_dominant_firm
dominant_firm_file = open('../outputs/inventor_year_dominant_firm.csv', 
                      encoding='utf-8-sig')
dominant_firm = csv.DictReader(dominant_firm_file, delimiter=',')

# Create firm year to inventor dict
print('Creating firm year to inventors dict\n...')
firm_year_inventor = {}
for row in dominant_firm:
    # Skip if N/A or non-ipo firm
    if (row['extrapolated_dominant_assignee'] == 'N/A' or
        row['extrapolated_dominant_assignee'] not in firm_ipo_year):
        continue

    # Get firms -> years
    years = firm_year_inventor.get(row['extrapolated_dominant_assignee'], {})
    # Get years -> inventors
    inventors = years.get(int(row['year']), set())
    # Add to inventor set
    inventors.add(row['inventor_id'])
    years[int(row['year'])] = inventors
    firm_year_inventor[row['extrapolated_dominant_assignee']] = years

this_year = 2021

# Write to output file
print('Writing to output file\n...')
with open('../outputs/firm_year_inventor_cnt.csv', 'w', 
          newline='\n', encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['ipo_firm', 'year', 'num_inventors', 
    'loss', 'gain', 'ipo_inventors_left', 'ipo_inventors_returned']
    output.writerow(header)

    for firm, years in firm_year_inventor.items():
        ipo_year = firm_ipo_year.get(firm)
        if not ipo_year: # Skip if non-ipo firm
            continue
        while ipo_year not in years and ipo_year <= this_year:
            ipo_year += 1

        if ipo_year == this_year + 1:
            print(firm)
            continue    

        ipo_inventors = years[ipo_year]
        start = min(years.keys())
        output.writerow([firm, start, len(years[start]), 0, 0])
        last = start
        for i in range(start + 1, ipo_year):
            if i not in years:
                output.writerow([firm, i, len(years[last]), 0, 0, 
                    'N/A', 'N/A'])
            else:
                intersect = years[i].intersection(years[last])
                loss = len(years[last].difference(intersect))
                gain = len(years[i].difference(intersect))
                output.writerow([firm, i, len(years[i]), loss, gain, 
                    'N/A', 'N/A'])
                last = i

        for i in range(ipo_year, this_year):
            if i not in years:
                ipo_year_intersect = years[last].intersection(ipo_inventors)
                ipo_loss = len(ipo_inventors.difference(ipo_year_intersect))
                output.writerow([firm, i, len(years[last]), 0, 0, ipo_loss, 0])
            else:
                last_intersect = years[i].intersection(years[last])
                loss = len(years[last].difference(last_intersect))
                gain = len(years[i].difference(last_intersect))

                ipo_year_intersect = years[i].intersection(ipo_inventors)
                ipo_loss = len(ipo_inventors.difference(ipo_year_intersect))
                # ipo inventors in year i that weren't there in the last year
                ipo_return = len(ipo_year_intersect.difference(years[last]))

                if i == ipo_year:
                    ipo_return = 0

                output.writerow([firm, i, len(years[i]), loss, gain, 
                    ipo_loss, ipo_return])
                last = i

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)