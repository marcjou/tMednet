import numpy as np
import pandas as pd
from datetime import datetime

df = pd.read_csv("../src/output_files/mergy.txt", '\t')
n = 0
total5 = 0
firstdate = df['Date'][0]
lastdate = df['Date'][len(df) - 1]

mydf = pd.DataFrame(columns=['date','depth(m)', 'N', 'mean', 'std', 'max', 'min'])

appendict = {'date': 0, 'depth(m)':0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min':0}
for i in range(len(df)):
    if df['Date'][i] == firstdate or df['Date'][i] == df['Date'][i-1]:
        total5 = df['5'][i] + total5
        n = n+1
    else:
        appendict['N'] = n
        appendict['depth(m)'] = 5
        appendict['mean'] = round(total5/n, 3)
        mydf = mydf.append(appendict, ignore_index=True)
        total5=0
        n = 0
    print("me")

print('me')