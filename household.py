import os
import re
import csv
import glob
import json
from collections import OrderedDict

'''
Type,Trans Date,Post Date,Description,Amount
Sale,06/08/2017,06/09/2017,SPEEDY'S TACOS,-12.27

Classify and add eat-out data
'''

fixed_payment_2016 = {
    #'mortgage' : -2116.05,
    'comcast' : -69.95,
    #hoa' : -341.22,
    'MINI COOPER' : -245.20,
    'verizon' : -170.47,
    'svpower_utility' : -75,
    'UMC' : -80,
    'farmers' : -123,
}

fixed_payment_2017 = {
    #'mortgage' : -2116.05,
    'comcast' : -74.45,
    #'hoa' : -352.05,
    'honda' : -245.20,
    'verizon' : -97.23,
    'svpower_utility' : -65,
    'UMC' : -90,
    'farmers' : -129.32,
}

def parse_trxs(csv_iter):
    ''' Remove + transactions
    '''
    eat_out_regex = r"(FALAFEL|EPICUREAN|PAD THAI|PHO RESTAURANT|BEIJING RESTAURANT|MYZEN|SPEEDY'S TACOS|IN-N-OUT BURGER|RAMEN MISOYA|SEN DAI SUSHI|BRIX RESTAURANT|MOOBONGRI|ST JOHNS BAR|CHAATS AND CURRYS|CHIPOTLE|BAMBOO LEAF VIETNAMESE|PATXI'S PIZZA-CRESCENT|STARBUCKS|COCOHODO|PARIS BAGUETTE|CHICK-FIL-A|SQ \*YAYOI|DIN TAI FUNG|GODIVA|CHUNGDAM|ANDY'S BAR-B-QUE|MCDONALD|SUPER DUPER BURGER|LA PALOMA RESTAURANT|COWBOY BAR|POPEYES|Red Hot Chilli Pepper|FIVE GUYS BURGERS AND FRI|JANG SU JANG|KUNJIP|KOREAN CHARCOAL SPRING BB|PANDA EXPRESS|HALF MOON BAY BREWING|VILLAGE CALIFORNIA|RAMEN SEAS|BOTTEGA RISTORANTE|KOI PALACE|RED ROBIN|HURLEY'S RESTAURANT|WENTE VINEYARDS|BOUCHON BAKERY YOUNTVILLE|PHILZ COFFEE|THE FISH HOPPER|PF CHANGS|MINAS KOREAN BBQ|SUMIKA|ORCHID AUTHENTIC THAI|MO DU RANG|FALLEN LEAF LAKE|TOUS LES|DISH N|SMASHBURGER|CURRY UP NOW|PEET'S|BONCHON|COCOLA|ARMADILLO|MASA NOODLE|BURGER PIT|HANUL KOREAN FOOD|SO GONG DONG TOFU|SUBWAY|SENOR TACO)"
    home_repair_regex = r"(LOWES|THE HOME DEPOT|ORCHARD SUPPLY|IKEA|CRATE|AUTONOMOUS INC)"

    #spendings = { item: 0 for item in ['safeway', 'costco', 'wholefood', 'amazon', 'koreanmarket', 'traderjoe', 'target', 'eatout', 'home_repair'] }
    spendings = { item: 0 for item in ['grocery', 'amazon', 'eatout', 'home_repair'] }
    index_name = None
    for name,desc,amount in csv_iter:
        index_name = name.split('/')[2].split('.')[0]
        if re.match(r'^.*WHOLEFDS', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*safeway', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*costco', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*amazon', desc, re.IGNORECASE):
            spendings['amazon'] += -amount
        elif re.match(r'^.*GALLERIA', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*HANKOOK', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*ANGUS', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*KYO-PO PLAZA', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*TRADER', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(r'^.*TARGET', desc, re.IGNORECASE):
            spendings['grocery'] += -amount
        elif re.match(eat_out_regex, desc, re.IGNORECASE):
            spendings['eatout'] += -amount
        elif re.match(home_repair_regex, desc, re.IGNORECASE):
            spendings['home_repair'] += -amount

    return index_name, spendings

def csv_to_dict(csv_file):
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for d in reader:
            yield (f.name, d['Description'], float(d['Amount']))


def run_household(year):
    monthly_pmt = {}
    csv_path = 'data/' + str(year) + '/*.CSV'
    for file in glob.glob(csv_path):
        csv_iterator = csv_to_dict(file)
        month, spendings = parse_trxs(csv_iterator)
        monthly_pmt[month] = spendings
        monthly_pmt[month]["total"] = sum(spendings.values())
    '''
    for root,_,files in os.walk('data/' + str(year)):
        for f_csv in files:
            csv_iterator = csv_to_dict(root + '/' + f_csv)
            month, spendings = parse_trxs(csv_iterator)
            monthly_pmt[month] = spendings
            monthly_pmt[month]["total"] = sum(spendings.values())

    '''
    #return json.dumps(monthly_pmt, indent=4)   # very bad because the return type becomes STRING not DICT !!
    #return OrderedDict(sorted(monthly_pmt.items(), key=lambda x:x[0]))
    return OrderedDict(sorted(monthly_pmt.items(), reverse=True))

if __name__ == '__main__':
    od = run_household()
    #print(od["06_2017"]["eatout"])

