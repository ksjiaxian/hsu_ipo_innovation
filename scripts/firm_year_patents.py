#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Firm + Year to Patents

This script aggregates all backward and forward citations for each patent 
and firm in firm_year_patentcnt.

The file produced is outputs/firm_year_patents.csv, with header:
    ipo_firm, assignee_patent, patent_id, date_patent, assignee_citation,
    citation_id, date_citation, subsection_id, group_id, sequence, citation_type
    
*Note: citation_type is 0 for backward citations and 1 for forward citations

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
print('Creating patent to assignee dict\n...')
patent_to_assignee = {}
for row in patent_assignee:
    patent_to_assignee[row['patent_id']] = row['assignee_id']

# Load cpc_current
cpc_current_file = open('../patent_data/cpc_current.tsv', 
                            encoding='utf-8-sig')
cpc_current = csv.DictReader(cpc_current_file, delimiter='\t')

# Create patent to subsection_id and sequence dictionary
print('Creating subsection dict\n...') 
patent_to_subsection = {}
for row in cpc_current:
    lst = patent_to_subsection.get(row['patent_id'], [])
    lst.append([row['subsection_id'], row['group_id'], row['sequence']])
    patent_to_subsection[row['patent_id']] = lst

# Load application
app_file = open('../patent_data/application.tsv', 
                        encoding='utf-8-sig')
application = csv.DictReader(app_file, delimiter='\t') 
    
# Create patent to year dictionary
print('Creating year dict and application to patent dict\n...')
patent_to_year = {}
app_to_patent = {}
for row in application:
    patent_to_year[row['patent_id']] = int(row['date'][:4])
    app_to_patent[row['number'][5:]] = row['patent_id']

# Load uspatentcitation
uspatentcitation_file = open('../patent_data/uspatentcitation.tsv', 
                            encoding='utf-8-sig')
uspatentcitation = csv.DictReader(uspatentcitation_file, delimiter='\t')

# Year range (for forward citations)
year_range = 7

# Create patent to citation dictionary, fw and bk
print('Creating patent citations dict\n...')
patent_to_citationbk = {}
patent_to_citationfw = {}
for row in uspatentcitation:
    # Adding to backward citations
    lstbk = patent_to_citationbk.get(row['patent_id'], [])
    lstbk.append(row['citation_id'])
    patent_to_citationbk[row['patent_id']] = lstbk
    
    # Adding to forward citations
    if row['date']:
        if (patent_to_year.get(row['patent_id'], 20000) - 
                patent_to_year.get(row['citation_id'], 0)) <= year_range:
            lstfw = patent_to_citationfw.get(row['citation_id'], [])
            lstfw.append(row['patent_id'])
            patent_to_citationfw[row['citation_id']] = lstfw

# Load usapplicationcitation
usappcitation_file = open('../patent_data/usapplicationcitation.tsv', 
                                encoding='utf-8-sig')
usappcitation = csv.DictReader(usappcitation_file, delimiter='\t')

# Add application citations
print('Adding application citation\n...')
for row in usappcitation:
    if row['date']:
        cit = app_to_patent.get(row['number'][5:])
        if cit and (patent_to_year.get(row['patent_id'], 20000) - 
                patent_to_year.get(cit, 0)) <= year_range:
            lstfw = patent_to_citationfw.get(cit, [])
            lstfw.append(row['patent_id'])
            patent_to_citationfw[cit] = lstfw

# Load Kenneth table
firm_year_patentcnt_file = open('../outputs/firm_year_patentcnt_REVISED.csv', 
                            encoding='utf-8-sig')
firm_year_patentcnt = csv.DictReader(firm_year_patentcnt_file, delimiter=',')

# Write to output file
with open('../outputs/firm_year_patents.csv', 'w', 
              newline="\n", encoding='utf-8-sig') as output_file:
    output = csv.writer(output_file, delimiter=',')
    header = ['ipo_firm', 
              'assignee_patent', 
              'patent_id', 
              'date_patent',
              'assignee_citation',
              'citation_id', 
              'date_citation', 
              'subsection_id', 
              'group_id',
              'sequence', 
              'citation_type',
              ]
    output.writerow(header)
    
    print('Writing to output file\n...')
    na = ['N/A', 'N/A', 'N/A']
    for row in firm_year_patentcnt:
        if int(row['patent_cnt']) > 0:
            for patent in row['patent_ids'].split('; '):
                # Writing backward citation (citation_type = 0)
                for cit in patent_to_citationbk.get(patent, []):
                    for sec in patent_to_subsection.get(cit, [na]):
                        output.writerow([
                                row['ipo_firm'], 
                                patent_to_assignee.get(patent, 'N/A'), 
                                patent,
                                row['year'],
                                patent_to_assignee.get(cit, 'N/A'), 
                                cit,
                                patent_to_year.get(cit),
                                'Design' if cit[0] == 'D' else sec[0],
                                'Design' if cit[0] == 'D' else sec[1],
                                0 if cit[0] == 'D' else sec[2],
                                0
                            ]) 
                
                # Writing forward citation (citation_type = 1)
                for cit in patent_to_citationfw.get(patent, []):
                    for sec in patent_to_subsection.get(cit, [na]):
                        output.writerow([
                                row['ipo_firm'], 
                                patent_to_assignee.get(patent, 'N/A'), 
                                patent,
                                row['year'],
                                patent_to_assignee.get(cit, 'N/A'), 
                                cit,
                                patent_to_year.get(cit),
                                'Design' if cit[0] == 'D' else sec[0],
                                'Design' if cit[0] == 'D' else sec[1],
                                0 if cit[0] == 'D' else sec[2],
                                1
                            ])

print('***\nEND OF PROCESS')
end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)
    