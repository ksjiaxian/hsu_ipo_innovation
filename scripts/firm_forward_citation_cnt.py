 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firm Foward Citation Count

This script counts the forward citations per patent for 4 different year 
ranges. The year ranges are 4, 5, and 7 years after the publication year 
of the patent.

Ths file produced is outputs/firm_forward_citation_cnt.csv, which has the header:
    ipo_firm, year, forward_cnt4, forward_cnt5, forward_cnt7.

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load in firm_year_patentcnt.csv
firm_year_patent_file = open('../outputs/firm_year_patentcnt_REVISED.csv', 
                             encoding='utf-8-sig')
firm_year_patents = csv.DictReader(firm_year_patent_file, delimiter=',')

# Load in firm_year_patents.csv
citations_file = open('../outputs/firm_year_patents.csv', 
                      encoding='utf-8-sig')
citations = csv.DictReader(citations_file, delimiter=',')

this_year = 2020

# Create output file
print('WRITING TO FILE\n...')
with open('../outputs/firm_forward_citation_cnt.csv', 'w', 
          newline='\n', encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['ipo_firm', 'year', 'forward_cnt4', 'forward_cnt5', 
              'forward_cnt7']
    output.writerow(header)
    
    # Keep track of current state 
    nxt = next(citations)
    count4, count5, count7 = 0, 0, 0
    
    # Iterate through firm_year_patentcnt
    for row in firm_year_patents:
        count4, count5, count7 = 0, 0, 0
        firm = row['ipo_firm']
        curr_year = int(row['year'])
        if row['patent_cnt'] == '0' and curr_year < this_year - 7:
            output.writerow([
                    firm, 
                    curr_year, 
                    0,
                    0,
                    0
                ])
            continue
        
        while int(nxt['date_patent']) == curr_year:
            # Counting forward citations
            if nxt['citation_type'] == '1':
                if nxt['sequence'] == '0' or nxt['sequence'] == 'N/A':    
                    cit_year = int(nxt['date_citation'])
                    if cit_year - curr_year <= 4:
                        count4 += 1
                    if cit_year - curr_year <= 5:
                        count5 += 1
                    if cit_year - curr_year <= 7:
                        count7 += 1   
            
            # Stop if we reach the end of the citations file
            try:
                nxt = next(citations)
            except StopIteration:
                break
        
        if curr_year > this_year - 4: 
            output.writerow([
                    firm, 
                    curr_year, 
                    'N/A',
                    'N/A',
                    'N/A'
                ])
        elif curr_year > this_year - 5: 
            output.writerow([
                    firm, 
                    curr_year, 
                    count4,
                    'N/A',
                    'N/A'
                ])
        elif curr_year > this_year - 7:
            output.writerow([
                    firm, 
                    curr_year, 
                    count4, 
                    count5,
                    'N/A'
                ])
        else:
            output.writerow([
                    firm, 
                    curr_year, 
                    count4, 
                    count5,
                    count7
                ])

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)