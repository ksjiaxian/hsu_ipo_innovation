#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inventor Foward Citation Count

This script counts the forward citations per patent for 4 different year 
ranges. The year ranges are 4, 5, and 7 years after the publication year 
of the patent.

Ths file produced is outputs/inventor_forward_citation_cnt.csv, which has the header:
    inventor, year, forward_cnt4, forward_cnt5, forward_cnt7.

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load in citations_forward_backward.csv
citations_file = open('../outputs/inventor_year_patents_fw.csv', 
                      encoding='utf-8-sig')
citations = csv.DictReader(citations_file, delimiter=',')

this_year = 2021

# Create output file
print('WRITING TO FILE\n...')
with open('../outputs/inventor_forward_citation_cnt.csv', 'w', 
          newline='\n', encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['inventor', 'year', 'forward_cnt4', 'forward_cnt5', 
              'forward_cnt7']
    output.writerow(header)

    # Keep track of current state 
    last_year = 0
    last_inventor = ''
    last_patent = ''
    count4, count5, count7 = 0, 0, 0
    
    for row in citations: 
        if not row['app_year'].isnumeric():
            continue        
        if not (int(row['app_year']) == last_year and 
                row['inventor_id'] == last_inventor):
            # Write to file
            if last_year:
                if last_year > this_year - 4: 
                    output.writerow([
                            last_inventor, 
                            last_year, 
                            'N/A',
                            'N/A',
                            'N/A'
                        ])
                elif last_year > this_year - 5: 
                    output.writerow([
                            last_inventor, 
                            last_year, 
                            count4,
                            'N/A',
                            'N/A'
                        ])
                elif last_year > this_year - 7:
                    output.writerow([
                            last_inventor, 
                            last_year, 
                            count4, 
                            count5,
                            'N/A'
                        ])
                else:
                    output.writerow([
                            last_inventor, 
                            last_year, 
                            count4, 
                            count5,
                            count7
                        ])

            # Reset + update
            last_year = int(row['app_year'])
            last_inventor = row['inventor_id']
            count4, count5, count7 = 0, 0, 0
            
        curr = int(row['citation_app_year']) if (not 
                  row['citation_app_year'] == 'N/A') else 20000
        if curr - last_year <= 4:
            count4 += 1
        if curr - last_year <= 5:
            count5 += 1
        if curr - last_year <= 7:
            count7 += 1   
    
    # Write last thing            
    if last_year:
        output.writerow([
                last_inventor, 
                last_year, 
                count4, 
                count5,
                count7
            ])
        
print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)