#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Patent Originality and Generality By Inventor

This script uses inventor_year_patents to get the the number of citations
per subsection. It then generates the Herfindahl measures for originality and
generality (4, 5, and 7 years) for each patent.

The file produced is outputs/firm_originality_generality.csv, with header:
    inventor_id, year, patent_id, originality, generality4, 
    generality5, generality7.

*Note: only sequence 0 subsections are counted and N/A subsections are ignored 

@author: Audrey Yang (auyang@seas.upenn.edu)
"""

import time
import csv
from collections import Counter

print('***\nBEGIN PROCESS')
start_time = time.ctime()

# Load patent
patent_file = open('../patent_data/patent.tsv', 
                        encoding='utf-8-sig')
patent_details = csv.DictReader(patent_file, delimiter='\t') 
    
# Create patent to year dictionary
print('Creating year dict\n...')
patent_to_year = {}
for row in patent_details:
    patent_to_year[row['number']] = int(row['date'][:4])

# Load inventor_year_patents_bk
bk_citations_file = open('../outputs/inventor_year_patents_bk.csv', 
                            encoding='utf-8-sig')
bk_citations = csv.DictReader(bk_citations_file, delimiter=',')

print('Creating originality dicts\n...')
originality = {}

# Backward citations -> originality
for row in bk_citations:
    # Only processing citations where sequence is 0 and has subsection_id
    if not row['subsection_id'] == 'N/A':
        # Track subsection_id -> freq
        c = originality.get(row['patent_id'], {})
        c[row['subsection_id']] = c.get(row['subsection_id'], 0) + 1
        originality[row['patent_id']] = c

# Load inventor_year_patents_fw
fw_citations_file = open('../outputs/inventor_year_patents_fw.csv', 
                         encoding='utf-8-sig')
fw_citations = csv.DictReader(fw_citations_file, delimiter=',')

print('Creating generality dicts\n...')
generality4 = {} # contains data for patents <= 4 years into the future
generality5 = {} # contains data for patents 5 years into the future
generality7 = {} # contains data for patents 6 and 7 years into the future

# Forward citations -> generality
for row in fw_citations:
    # Track subsection_id -> freq
    if not row['citation_app_year'].isnumeric() or not row['app_year'].isnumeric():
        continue
    diff = int(row['citation_app_year']) - int(row['app_year'])
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
inventor_patent_file = open('../outputs/inventor_patent.csv', 
                            encoding='utf-8-sig')
inventor_patent = csv.DictReader(inventor_patent_file, delimiter=',')
  
# Creating output file     
with open('../outputs/inventor_originality_generality.csv', 'w', 
              newline="\n", encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['inventor_id', 'year', 'patent_id', 'originality', 'generality4', 
              'generality5', 'generality7']
    output.writerow(header)
    
    print('Writing to output file\n...')
    for row in inventor_patent:
        orig = 0
        gen4, gen5, gen7 = 0, 0, 0
        patent = row['patent_id']
        counter5, counter7 = Counter(), Counter()
        
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
                row['inventor_id'],
                patent_to_year.get(patent, 'N/A'),
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