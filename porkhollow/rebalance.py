from collections import OrderedDict
from tabulate import tabulate

import fileinput
import re
import sys

TOTAL_PURCHASE = float(sys.argv[1])

desired_ratio = OrderedDict([
        ('VBTLX', 7.5 / 100),
        ('VTABX', 2.5 / 100),
        ('VTIAX', 22.5 / 100),
        ('VTSAX', 67.5 / 100)
        ])


def monetize(amt):
    return '${: >10,.2f}'.format(amt)


def percentize(rat):
    return '{:>8.2f}%'.format(rat * 100)


def rebalance():
    funds = desired_ratio.keys()

    PARSE1 = re.compile(r'^(V[A-Z]*)\s')
    PARSE2 = re.compile(r'^.*\$([0-9,]*,\d\d\d\.\d\d)')

    fund = None
    current_holdings = {}
    current_ratio = {}
    new_holdings = {}

    for line in list(fileinput.input(sys.argv[2:])):
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

    # Iterate through the funds in order from most underbalanced to most
    # overbalanced. For each one, top off the funds that are *more underbalanced*
    # until they balance with the current fund. Continue in this manner until all
    # funds are balanced with the most overbalanced fund, or until we run out of
    # money.
    weights = {k: current_holdings[k] / desired_ratio[k] for k in funds}
    purchase = {k: 0 for k in funds}
    remaining_purchase = TOTAL_PURCHASE
    recipient_funds = []

    for (fund, weight) in sorted(weights.items(), key=lambda t: t[1]):
        if len(recipient_funds) > 0:
            tentative_holdings = {k: current_holdings[k] + purchase[k]
                                  for k in funds}
            min_purchase = {k: weight * desired_ratio[k] - tentative_holdings[k]
                            for k in recipient_funds}
            min_total_purchase = sum(min_purchase.values())

            if remaining_purchase > min_total_purchase:
                # So far we've managed to do a partial rebalance without running
                # out of money, so tally up what we're buying so far, and continue.
                for [k, v] in min_purchase.items():
                    purchase[k] += v
                remaining_purchase -= min_total_purchase
            else:
                # We haven't got enough money left to finish this (or any future)
                # stage of the rebalance, so allocate the remaining money
                # proportionally, and we're done.
                for [k, v] in min_purchase.items():
                    purchase[k] += v * (remaining_purchase / min_total_purchase)
                remaining_purchase = 0
                break

        recipient_funds += [fund]

    if remaining_purchase > 0:
        # We're purchasing more than enough to reach the target ratio,
        # so distribute the rest proportionally to maintain the target ratio.
        for k in funds:
            purchase[k] += remaining_purchase * desired_ratio[k]

    new_holdings = {k: purchase[k] + current_holdings[k] for k in funds}
    total_new_holdings = sum(new_holdings.values())
    new_ratio = {k: v / total_new_holdings for [k, v] in new_holdings.items()}

    print(tabulate(
            [[k, monetize(current_holdings[k]),
              monetize(purchase[k]), monetize(new_holdings[k]),
              percentize(current_ratio[k]), percentize(new_ratio[k]), percentize(desired_ratio[k])]
             for k in funds],
            headers=['fund', 'current', 'buy', 'new', 'crnt%', 'new%', 'trgt%'],
            stralign='right'))
