import math
import time
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from statistics import stdev, mean
from xlwt.Workbook import *
import xlsxwriter
from datetime import datetime

df = pd.read_csv("../src/output_files/mergo.txt", '\t')
n = 0
total = {}
total2 = {}
total3 = {}
firstdate = df['Date'][0]
lastdate = df['Date'][len(df) - 1]

mydf = pd.DataFrame(columns=['date','depth(m)', 'N', 'mean', 'std', 'max', 'min'])

mydf2 = pd.DataFrame(columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                              'Ndays>=26'])
mydf3 = pd.DataFrame(columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                              'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])

appendict = {}
appendict2 = {}
appendict3 = {}
df = df.fillna(0)
for column in df:
    if column != 'Date' and column != 'Time':
        total[column] = []
        total2[column] = []
        appendict[column] = {'date': 0, 'depth(m)':0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min':0}
        appendict2[column] = {'year': 0, 'month': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0,
                              'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0}
        appendict3[column] = {'year': 0, 'season': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0,
                              'Ndays>=23': 0, 'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0, 'Ndays>=27': 0,
                              'Ndays>=28': 0}

flag = False
firstmonth = datetime.strftime(datetime.strptime(df['Date'][0], '%d/%m/%Y'), '%m')
for i in range(len(df)):
    year = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%Y')
    month = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%m')
    if month == firstmonth or month == datetime.strftime(datetime.strptime(df['Date'][i - 1], '%d/%m/%Y'), '%m'):
        if df['Date'][i] == firstdate or df['Date'][i] == df['Date'][i-1]:
            for column in df:
                if column != 'Date' and column != 'Time':
                    appendict[column]['date'] = df['Date'][i]
                    appendict2[column]['year'] = year
                    appendict2[column]['month'] = month
                    if df[column][i] <= 0 or math.isnan(df[column][i]):
                        pass
                    else:
                        appendict[column]['N'] = appendict[column]['N'] + 1
                        appendict2[column]['N'] = appendict2[column]['N'] + 1
                    appendict[column]['depth(m)'] = column
                    appendict2[column]['depth(m)'] = column
                    total[column].append(df[column][i])
                    total2[column].append(df[column][i])
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
            for column in df:
                if column != 'Date' and column != 'Time':
                    appendict[column]['date'] = df['Date'][i]
                    appendict2[column]['year'] = year
                    appendict2[column]['month'] = month
                    if df[column][i] <= 0 or math.isnan(df[column][i]):
                        pass
                    else:
                        appendict[column]['N'] = appendict[column]['N'] + 1
                        appendict2[column]['N'] = appendict2[column]['N'] + 1
                    appendict[column]['depth(m)'] = column
                    appendict2[column]['depth(m)'] = column
                    total[column].append(df[column][i])
                    total2[column].append(df[column][i])
    else:
        for column in df:
            if column != 'Date' and column != 'Time':
                # Appendict1 part
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
                # Appendict2 part
                appendict2[column]['depth(m)'] = column
                if appendict2[column]['N'] == 0:
                    appendict2[column]['mean'] = 0
                else:
                    total2[column] = [np.nan if tot == 0 else tot for tot in total2[column]]
                    appendict2[column]['mean'] = round(np.nanmean(total2[column]), 3)
                    appendict2[column]['std'] = round(stdev(total2[column]), 3)
                    appendict2[column]['max'] = round(max(total2[column]), 3)
                    appendict2[column]['min'] = round(min(total2[column]), 3)
                mydf2 = mydf2.append(appendict2[column], ignore_index=True)
                appendict2[column]['N'] = 0
                total2[column] = []
        for column in df:
            if column != 'Date' and column != 'Time':
                appendict[column]['date'] = df['Date'][i]
                appendict2[column]['year'] = year
                appendict2[column]['month'] = month
                if df[column][i] <= 0 or math.isnan(df[column][i]):
                    pass
                else:
                    appendict[column]['N'] = appendict[column]['N'] + 1
                    appendict2[column]['N'] = appendict2[column]['N'] + 1
                appendict[column]['depth(m)'] = column
                appendict2[column]['depth(m)'] = column
                total[column].append(df[column][i])
                total2[column].append(df[column][i])

    print(str(i) + ' de ' + str(len(df)))



print('Now writing to excel')
writer = ExcelWriter('example.xlsx')
mydf.to_excel(writer, 'papapa')
writer.save()

print('me')


