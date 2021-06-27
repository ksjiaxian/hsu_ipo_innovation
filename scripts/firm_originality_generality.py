#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patent Originality and Generality By Firm

This script uses firm_year_patents to get the the number of citations
per subsection. It then generates the Herfindahl measures for originality and
generality (4, 5, and 7 years) for each patent.

The file produced is outputs/firm_originality_generality.csv, with header:
    ipo_firm, year, patent_id, originality, generality4, 
    generality5, generality7.

*Note: only sequence 0 subsections are counted and N/A subsections are ignored 

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv
from collections import Counter

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load citations_forward_backward
citations_file = open('../outputs/firm_year_patents.csv', 
                            encoding='utf-8-sig')
citations = csv.DictReader(citations_file, delimiter=',')

print('Creating originality and generality dicts\n...')
originality = {}
generality4 = {} # contains data for patents <= 4 years into the future
generality5 = {} # contains data for patents 5 years into the future
generality7 = {} # contains data for patents 6 and 7 years into the future

for row in citations:
    # Only processing citations where sequence is 0 and has subsection_id
    if row['sequence'] == '0' and not row['subsection_id'] == 'N/A':
        # Backward citations -> originality
        if row['citation_type'] == '0':
            # Track subsection_id -> freq
            c = originality.get(row['patent_id'], {})
            c[row['subsection_id']] = c.get(row['subsection_id'], 0) + 1
            originality[row['patent_id']] = c
        # Forward citations -> generality
        elif row['citation_type'] == '1':
             # Track subsection_id -> freq
            diff = int(row['date_citation']) - int(row['date_patent'])
            if diff <= 4:
                c = generality4.get(row['patent_id'], {})
                c[row['subsection_id']] = c.get(row['subsection_id'], 0) + 1
                generality4[row['patent_id']] = c
            elif diff <= 5:
                c = generality5.get(row['patent_id'], {})
                c[row['subsection_id']] = c.get(row['subsection_id'], 0) + 1
                generality5[row['patent_id']] = c
            elif diff <= 7:
                c = generality7.get(row['patent_id'], {})
                c[row['subsection_id']] = c.get(row['subsection_id'], 0) + 1
                generality7[row['patent_id']] = c
                
# Load Kenneth table
firm_year_patentcnt_file = open('../outputs/firm_year_patentcnt_REVISED.csv', 
                            encoding='utf-8-sig')
firm_year_patentcnt = csv.DictReader(firm_year_patentcnt_file, delimiter=',')
  
# Creating output file     
with open('../outputs/firm_originality_generality.csv', 'w', 
              newline="\n", encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['ipo_firm', 'year', 'patent_id', 'originality', 'generality4', 
              'generality5', 'generality7']
    output.writerow(header)
    
    print('Writing to output file\n...')
    for row in firm_year_patentcnt:
        if not row['patent_cnt'] == '0':
            for patent in row['patent_ids'].split('; '):
                orig = 0
                gen4, gen5, gen7 = 0, 0, 0
                
                # Calculating originality measure
                if patent in originality:
                    len_cit = sum(originality.get(patent).values())
                    for _, sec in originality.get(patent).items():
                        orig += (sec / len_cit) ** 2
                    orig = 1 - orig
                else:
                    # N/A if doesn't cite anything (with a subsection_id)
                    orig = 'N/A'
                
                # Calculating generality4 measure
                if patent in generality4:
                    len_cit = sum(generality4.get(patent, {}).values())
                    for _, sec in generality4.get(patent, {}).items():
                        gen4 += (sec / len_cit) ** 2
                    gen4 = 1 - gen4
                else:
                    # N/A if isn't cited by anything (with a subsection_id)
                    gen4 = 'N/A'
                
                
                # Calculating generality5 measure
                if patent in generality5:
                    counter5 = Counter(generality4.get(patent, {})) + Counter(
                        generality5.get(patent, {}))
                    len_cit = sum(counter5.values())
                    for _, sec in counter5.items():
                        gen5 += (sec / len_cit) ** 2
                    gen5 = 1 - gen5
                else:
                    # N/A if isn't cited by anything (with a subsection_id)
                    gen5 = gen4
                    
                # Calculating generality7 measure
                if patent in generality7:
                    counter7 = counter5 + Counter(generality7.get(patent, {}))
                    len_cit = sum(counter7.values())
                    for _, sec in counter7.items():
                        gen7 += (sec / len_cit) ** 2
                    gen7 = 1 - gen7
                else:
                    # N/A if isn't cited by anything (with a subsection_id)
                    gen7 = gen5
                
                output.writerow([
                        row['ipo_firm'],
                        row['year'],
                        patent,
                        orig,
                        gen4, 
                        gen5, 
                        gen7
                    ])
        

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)