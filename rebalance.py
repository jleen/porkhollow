from tabulate import tabulate

import fileinput
import re

desired_ratio = {
        'VBTLX': 7.5,
        'VTABX': 2.5,
        'VTIAX': 22.5,
        'VTSAX': 67.5
        }
funds = desired_ratio.keys()

PARSE1 = re.compile(r'^(V[A-Z]*)\t')
PARSE2 = re.compile(r'^\$([0-9,]*\.[0-9][0-9])$')

fund = None
current_holdings = {}
current_ratio = {}
weight = {}
minimum_purchase = {}
new_holdings = {}

for line in list(fileinput.input()):
    if not fund:
        match = PARSE1.match(line)
        if match:
            fund = match.group(1)
            if fund not in funds:
                fund = None
    else:
        match = PARSE2.match(line)
        if not match:
            raise Exception('no cashooooola')
        current_holdings[fund] = int(
                match.group(1).replace(',', '').replace('.', ''))
        fund = None

total_holdings = sum(current_holdings.values())
current_ratio = {k: v / total_holdings for [k, v] in current_ratio.items()}
weight = {k: current_holdings[k] / desired_ratio[k] for k in funds}
max_weight = max(weight.values())
minimum_purchase = {k: max_weight * desired_ratio[k] - current_holdings[k]
                    for k in funds}
new_holdings = {k: minimum_purchase[k] + current_holdings[k] for k in funds}

def monetize(amt):
    return '${:,.2f}'.format(amt / 100)

print(tabulate(
        [[k, monetize(current_holdings[k]),
          monetize(minimum_purchase[k]), monetize(new_holdings[k])]
         for k in funds],
        headers=['fund', 'current', 'buy', 'new']))
