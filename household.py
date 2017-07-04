import re
import csv
import glob
import json
from collections import OrderedDict

'''
Type,Trans Date,Post Date,Description,Amount
Sale,06/08/2017,06/09/2017,SPEEDY'S TACOS,-12.27
'''

def csv_to_dict(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for d in reader:
            yield (f.name, d['Description'], float(d['Amount']))

def parse_trxs(csv_iter):
    grocery = { item: 0 for item in ['safeway', 'costco', 'wholefood', 'amazon', 'koreanmarket', 'traderjoe'] }
    index_name = None
    for name,desc,amount in csv_iter:
        index_name = name.split('/')[1].split('.')[0]
        if re.match(r'^.*WHOLEFDS', desc, re.IGNORECASE):
            grocery['wholefood'] += -amount
        elif re.match(r'^.*safeway', desc, re.IGNORECASE):
            grocery['safeway'] += -amount
        elif re.match(r'^.*costco', desc, re.IGNORECASE):
            grocery['costco'] += -amount
        elif re.match(r'^.*amazon', desc, re.IGNORECASE):
            grocery['amazon'] += -amount
        elif re.match(r'^.*GALLERIA', desc, re.IGNORECASE):
            grocery['koreanmarket'] += -amount
        elif re.match(r'^.*HANKOOK', desc, re.IGNORECASE):
            grocery['koreanmarket'] += -amount
        elif re.match(r'^.*ANGUS', desc, re.IGNORECASE):
            grocery['koreanmarket'] += -amount
        elif re.match(r'^.*TRADER', desc, re.IGNORECASE):
            grocery['traderjoe'] += -amount

    return index_name, grocery

def run_household():
    monthly_pmt = {}
    for file in glob.glob('data/*.CSV'):
        csv_iterator = csv_to_dict(file)
        month, grocery = parse_trxs(csv_iterator)
        monthly_pmt[month] = grocery
        monthly_pmt[month]["total"] = sum(grocery.values())

    #return json.dumps(monthly_pmt, indent=4)   # very bad because the return type becomes STRING not DICT !!
    #return OrderedDict(sorted(monthly_pmt.items(), key=lambda x:x[0]))
    return OrderedDict(sorted(monthly_pmt.items()))

if __name__ == '__main__':
    print(run_household())

