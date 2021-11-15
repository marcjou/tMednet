import math
import time
import numpy as np
import pandas as pd
from statistics import stdev, mean
from datetime import datetime

df = pd.read_csv("../src/output_files/mergo.txt", '\t')
n = 0
total = {}
firstdate = df['Date'][0]
lastdate = df['Date'][len(df) - 1]

mydf = pd.DataFrame(columns=['date','depth(m)', 'N', 'mean', 'std', 'max', 'min'])

appendict = {}
df = df.fillna(0)
for column in df:
    if column != 'Date' and column != 'Time':
        total[column] = []
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
                total[column].append(df[column][i])
    else:
        for column in df:
            if column != 'Date' and column != 'Time':
                appendict[column]['depth(m)'] = column
                if appendict[column]['N'] == 0:
                    appendict[column]['mean'] = 0
                else:
                    total[column] = [np.nan if tot == 0 else tot for tot in total[column]]
                    appendict[column]['mean'] = round(np.nanmean(total[column]), 3)
                    appendict[column]['std'] = round(stdev(total[column]), 3)
                    appendict[column]['max'] = round(max(total[column]), 3)
                    appendict[column]['min'] = round(min(total[column]), 3)
                mydf = mydf.append(appendict[column], ignore_index=True)
                appendict[column]['N'] = 0
                total[column] = []

    print(str(i) + ' de ' + str(len(df)))



print('me')


