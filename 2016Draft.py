#!/usr/bin/python

import draft
import csv

(B,P)=draft.NL2016Draft()

with open('batter_values.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['first','last','pos','value','id', 'OBP','SLG','R', 'HR', 'RBI', 'SB', 'G', 'AB', 'H', '2B', '3B', 'CS', 'BB', 'SO', 'IBB', 'HBP', 'SH', 'SF', 'GIDP', 'age', 'years played', 'weight', 'height'])
    for x in B:
        writer.writerow(x)

with open('pitcher_values.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['first','last','pos','value','id','W', 'SV', 'SO', '-ERA', '-WHIP', 'QS(=1)', 'H', 'BB', 'IPOuts', 'HBP', 'IBB', 'L', 'G', 'GS', 'CG', 'SHO', 'ER', 'HR', 'WP', 'BK', 'BFP', 'GF','R', 'age', 'years played', 'weight', 'height'])
    for x in P:
        writer.writerow(x)
