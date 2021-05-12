########################################################################################################################
# IPO and Assignee Matcher
#
# Kenneth Shinn
# kshinn@seas.upenn.edu
#
# Directions: put the patent data in a folder called 'patent_data', put the ipo data in a folder called 'firms'.
# This script should be in its own folder (and it can be called whatever).
#
# NOTE: IPO FILE MUST BE IN ALPHABETICAL ORDER (and the assignee file should be too!)
########################################################################################################################
import csv
import math
from fuzzywuzzy import fuzz
import re
import time
from wordfreq import word_frequency
import os.path


def remove_common_substrings(str):
    new_str = str.lower()
    # remove parts of the string, must be at the end
    new_str.replace(' holding', '')
    new_str.replace(' holdings', '')
    new_str = re.sub('\ technology$', '', new_str)
    new_str = re.sub('\ technologies$', '', new_str)
    new_str = re.sub('\ institute$', '', new_str)
    new_str = re.sub('\ uk$', '', new_str)
    new_str = re.sub('\ us$', '', new_str)
    new_str = re.sub('\ gmbh$', '', new_str)
    new_str = re.sub('\ co$', '', new_str)
    new_str = re.sub('\ co.$', '', new_str)
    new_str = re.sub('\ grp$', '', new_str)
    new_str = re.sub('\ incorporated', '', new_str)
    new_str = re.sub('\ inc.$', '', new_str)
    new_str = re.sub('\ inc$', '', new_str)
    new_str = re.sub('\ corp.$', '', new_str)
    new_str = re.sub('\ corp$', '', new_str)
    new_str = re.sub('\ ag$', '', new_str)
    new_str = re.sub('\ ltd$', '', new_str)
    new_str = re.sub('\ ag.$', '', new_str)
    new_str = re.sub('\ ltd.$', '', new_str)
    new_str = re.sub('\ limited$', '', new_str)
    new_str = re.sub('\ company$', '', new_str)

    return new_str


# start time
start_time = time.ctime()

# load in the files
assignee_file = open('../patent_data/assignee_firms.tsv', encoding='utf-8-sig')
assignee = csv.DictReader(assignee_file, delimiter="\t")

ipo_file = open('../firms/ipo_10000.csv', encoding='utf-8-sig')
ipo = csv.DictReader(ipo_file, delimiter=",")

# create an output file 
output = open('../outputs/name_matches.csv', 'w', newline="\n", encoding='utf-8-sig')
name_matches = csv.writer(output, delimiter=',')
header = ['ipo_firm', 'assignee_firm', 'ticker', 'is_common', 'patent_cnt']
name_matches.writerow(header)

# create a files of non-matches
output = open('../outputs/assignee_firms_unmatched.tsv', 'w', newline="\n", encoding='utf-8-sig')
non_assignee_matches = csv.writer(output, delimiter='\t')
header = ['id', 'type', 'firm']
non_assignee_matches.writerow(header)

output = open('../outputs/ipo_firms_unmatched.csv', 'w', newline="\n", encoding='utf-8-sig')
non_ipo_matches = csv.writer(output, delimiter=',')
header = ['firm','ipo_date','ticker','CUSIP','CRSP perm','post-issue shares','dual dum','Founding','Rollup dum']
# ['ipo_date', 'firm', 'ticker', 'offer_price', 'opening_price', 'first_day_close'] # old header
non_ipo_matches.writerow(header)

# count the number of patents per assignee
print('GENERATING PATENT COUNT PER ASSIGNEE')
patent_cnt = {}  # dictionary mapping assignee id to patent counts
# if not os.path.isfile('../patent_data/assignee_firms_patent_count.tsv'):  # first check to see if such a file exists
with open('../patent_data/patent_assignee.tsv', encoding='utf-8-sig') as patent_assignee_file:
    patent_assignee = csv.DictReader(patent_assignee_file, delimiter="\t")

    # iterate through the patent_assignee file and generate the dictionary
    for row in patent_assignee:
        patent_id = row['patent_id']
        assignee_id = row['assignee_id']

        if assignee_id not in patent_cnt:
            patent_cnt[assignee_id] = 1
        else:
            patent_cnt[assignee_id] += 1
print('COMPLETED')

print('*** IPO and ASSIGNEE INPUT SIZES ***')
# calculate the size of both input files
assignee_size = len([1 for i in assignee])
print('assignee size: ' + str(assignee_size))
assignee_file.seek(0)  # rewind file
assignee.__next__()

ipo_size = len([1 for i in ipo])
print('ipo size: ' + str(ipo_size) + '\n')
ipo_file.seek(0)  # rewind file
ipo.__next__()

# set of IPO to keep track of what has been matched
unmatched_ipo = set()

for row in ipo:
    ipo_firm = row['firm'].strip()
    unmatched_ipo.add(ipo_firm)

ipo_file.seek(0)  # rewind file
ipo.__next__()

# count for progress
cnt = 0
previous_percent = 0
curr_letter = '0'  # to allow for firms that start with numbers

for row in assignee:
    # calculate progress
    percent_complete = math.floor((cnt / assignee_size) * 100)
    if percent_complete > previous_percent:
        print(str(percent_complete) + '% complete')
        previous_percent = percent_complete

    # .strip() removes the white space around the string (some name have spaces after)
    id = row['id'].strip()
    type = row['type'].strip()
    firm = row['firm'].strip()
    found_match = False

    # set the curr_letter as the first letter of this string
    if not firm.lower().startswith(curr_letter):
        curr_letter = firm[0].lower()
        print(curr_letter)

    for i in ipo:
        ipo_firm = i['firm'].strip()

        if not ipo_firm.lower().startswith(curr_letter):
            if ipo_firm[0] < curr_letter:  # continue through if we're before the current assignee letter
                continue
            else:
                break  # if we're after the current assignee letter, break out of loop

        # remove the common substrings
        modified_firm = remove_common_substrings(firm)
        modified_ipo_firm = remove_common_substrings(ipo_firm)

        # 1. check that the ipo string prefixes the assignee string
        # 2. check that the ipo string first word is in the words of the assignee string
        # 3. check that the ipo and assignee have string similarity by substring or by similarity of word sets
        if modified_firm.startswith(modified_ipo_firm) and \
                re.sub("[^\w]", " ", modified_ipo_firm).split()[0] in re.sub("[^\w]", " ", modified_firm).split() and \
                (fuzz.partial_ratio(modified_firm, modified_ipo_firm) >= 90 or
                 fuzz.token_sort_ratio(modified_firm, modified_ipo_firm) >= 90):
            print('ipo: ' + ipo_firm)
            print('assignee: ' + firm + '\n')
            # print(modified_ipo_firm)
            # print(modified_firm)
            # print(fuzz.partial_ratio(modified_firm, modified_ipo_firm))
            # print(fuzz.token_sort_ratio(modified_firm, modified_ipo_firm))

            is_common = 1
            # check if the IPO name is common
            if word_frequency(modified_ipo_firm, 'en') < 0.000001:
                is_common = 0

            # write it to the matches output, and record a found match
            if id not in patent_cnt:
                patent_cnt[id] = 0

            name_matches.writerow([ipo_firm, firm, i['ticker'].strip(), is_common, patent_cnt[id]])

            found_match = True

            # remove from list of unmatched ipo
            if ipo_firm in unmatched_ipo:
                unmatched_ipo.remove(ipo_firm)

    # if a match isn't found, return it to the "non-matched" pile
    if not found_match:
        non_assignee_matches.writerow([id, type, firm])
    # this rewinds the csv reader
    ipo_file.seek(0)
    ipo.__next__()

    cnt += 1

for i in ipo:
    ipo_firm = i['firm'].strip()
    if ipo_firm in unmatched_ipo:
        non_ipo_matches.writerow(
            [i['firm'], i['ipo_date'], i['ticker'], i['CUSIP'], i['CRSP perm'], i['post-issue shares'], i['dual dum'],
             i['Founding'], i['Rollup dum']])
        # [i['ipo_date'], i['firm'], i['ticker'], i['offer_price'], i['opening_price'], i['first_day_close']] # using
        # old header

# END OF PROCESS ##
print('\nEND OF PROCESS\n')

end_time = time.ctime()

print('Start Time: ' + start_time)
print('End Time: ' + end_time)
