from tabulate import tabulate

import fileinput
import re

TOTAL_PURCHASE = 9999
desired_ratio = {
        'VBTLX': 7.5 / 100,
        'VTABX': 2.5 / 100,
        'VTIAX': 22.5 / 100,
        'VTSAX': 67.5 / 100
        }


def monetize(amt):
    return '${: >10,.2f}'.format(amt)


def percentize(rat):
    return '{:>8.2f}%'.format(rat * 100)


funds = desired_ratio.keys()

PARSE1 = re.compile(r'^(V[A-Z]*)\s')
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
        if match:
            current_holdings[fund] = float(match.group(1).replace(',', ''))
            fund = None

total_holdings = sum(current_holdings.values())
current_ratio = {k: v / total_holdings for [k, v] in current_holdings.items()}
weight = {k: current_holdings[k] / desired_ratio[k] for k in funds}
max_weight = max(weight.values())
minimum_purchase = {k: max_weight * desired_ratio[k] - current_holdings[k]
                    for k in funds}
min_total_purchase = sum(minimum_purchase.values())
extra_total_purchase = TOTAL_PURCHASE - min_total_purchase

if extra_total_purchase >= 0:
    # We're purchasing more than enough to reach the target ratio,
    # so distribute the rest proportionally to maintain the target ratio.
    extra_purchase = {k: extra_total_purchase * desired_ratio[k]
                      for k in funds}
    purchase = {k: minimum_purchase[k] + extra_purchase[k] for k in funds}
else:
    # We're not going to reach the target, so allocate funds in proportion to
    # the purchases that *would* reach the target.
    purchase = {
            k: minimum_purchase[k] * TOTAL_PURCHASE / min_total_purchase
            for k in funds}

new_holdings = {k: purchase[k] + current_holdings[k] for k in funds}
total_new_holdings = sum(new_holdings.values())
new_ratio = {k: v / total_new_holdings for [k, v] in new_holdings.items()}

print(tabulate(
        [[k, monetize(current_holdings[k]),
          monetize(purchase[k]), monetize(new_holdings[k]),
          percentize(current_ratio[k]), percentize(new_ratio[k])]
         for k in funds],
        headers=['fund', 'current', 'buy', 'new', 'crnt%', 'new%'],
        stralign='right'))
