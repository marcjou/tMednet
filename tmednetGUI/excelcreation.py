import math

import numpy as np
import pandas as pd
from datetime import datetime

df = pd.read_csv("../src/output_files/mergy.txt", '\t')
n = 0
total = {}
firstdate = df['Date'][0]
lastdate = df['Date'][len(df) - 1]

mydf = pd.DataFrame(columns=['date','depth(m)', 'N', 'mean', 'std', 'max', 'min'])

appendict = {}

for column in df:
    if column != 'Date' and column != 'Time':
        total[column] = 0
        appendict[column] = {'date': 0, 'depth(m)':0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min':0}

for i in range(len(df)):
    if df['Date'][i] == firstdate or df['Date'][i] == df['Date'][i-1]:
        for column in df:
            if column != 'Date' and column != 'Time':
                appendict[column]['date'] = df['Date'][i]
                if df[column][i] <= 0 or math.isnan(df[column][i]):
                    pass
                else:
                    appendict[column]['N'] = appendict[column]['N'] + 1
                appendict[column]['depth(m)'] = column
                total[column] = total[column] + df[column][i]
    else:
        for column in df:
            if column != 'Date' and column != 'Time':
                appendict[column]['depth(m)'] = column
                appendict[column]['mean'] = round(total[column]/appendict[column]['N'], 3)
                mydf = mydf.append(appendict[column], ignore_index=True)

    print("me")

print('me')