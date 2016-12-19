import fileinput
import re

FUNDS = { 'VBTLX': 7.5,
          'VTABX': 2.5,
          'VTIAX': 22.5,
          'VTSAX': 67.5 }

PARSE1 = re.compile(r'^(V[A-Z]*)\t')
PARSE2 = re.compile(r'^\$([0-9,]*\.[0-9][0-9])$')

fund = None
holdings = {}

for line in list(fileinput.input()):
    if not fund:
        match = PARSE1.match(line)
        if match:
            fund = match.group(1)
    else:
        match = PARSE2.match(line)
        if not match:
            raise Exception('no cashooooola')
        holdings[fund] = int(match.group(1).replace(',', '').replace('.', ''))
        fund = None

print(holdings)
