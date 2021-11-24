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

mydf = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])

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
        total3[column] = []
        appendict[column] = {'date': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0}
        appendict2[column] = {'year': 0, 'month': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0,
                              'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0}
        appendict3[column] = {'year': 0, 'season': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0,
                              'Ndays>=23': 0, 'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0, 'Ndays>=27': 0,
                              'Ndays>=28': 0}

firstmonth = datetime.strftime(datetime.strptime(df['Date'][0], '%d/%m/%Y'), '%m')
firstyear = datetime.strftime(datetime.strptime(df['Date'][0], '%d/%m/%Y'), '%Y')
for i in range(len(df)):
    if type(df['Date'][i]) != type('27/12/1995'):
        pass
    elif i >= 1 and type(df['Date'][i - 1]) != type('27/12/1995'):
        year = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%Y')
        month = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%m')
        if year == firstyear or year == datetime.strftime(datetime.strptime(df['Date'][i - 2], '%d/%m/%Y'), '%Y'):

            if month == firstmonth or month == datetime.strftime(datetime.strptime(df['Date'][i - 2], '%d/%m/%Y'), '%m'):
                if df['Date'][i] == firstdate or df['Date'][i] == df['Date'][i - 2]:
                    for column in df:
                        if column != 'Date' and column != 'Time':
                            appendict[column]['date'] = df['Date'][i]
                            appendict2[column]['year'] = year
                            appendict2[column]['month'] = month
                            if month == '07' or month == '08' or month == '09':
                                appendict3[column]['season'] = 3
                                appendict3[column]['year'] = year
                                if df[column][i] <= 0 or math.isnan(df[column][i]):
                                    pass
                                else:
                                    appendict3[column]['N'] = appendict3[column]['N'] + 1
                                appendict3[column]['depth(m)'] = column
                                total3[column].append(df[column][i])
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
                            if month == '07' or month == '08' or month == '09':
                                appendict3[column]['season'] = 3
                                appendict3[column]['year'] = year
                                if df[column][i] <= 0 or math.isnan(df[column][i]):
                                    pass
                                else:
                                    appendict3[column]['N'] = appendict3[column]['N'] + 1
                                appendict3[column]['depth(m)'] = column
                                total3[column].append(df[column][i])
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
                            appendict2[column]['max'] = round(np.nanmax(total2[column]), 3)
                            appendict2[column]['min'] = round(np.nanmin(total2[column]), 3)
                            appendict2[column]['Ndays>=24'] = len([days for days in total2[column] if days >= 24])
                            appendict2[column]['Ndays>=25'] = len([days for days in total2[column] if days >= 25])
                            appendict2[column]['Ndays>=26'] = len([days for days in total2[column] if days >= 26])
                        mydf2 = mydf2.append(appendict2[column], ignore_index=True)
                        appendict2[column]['N'] = 0
                        total2[column] = []
                for column in df:
                    if column != 'Date' and column != 'Time':
                        appendict[column]['date'] = df['Date'][i]
                        appendict2[column]['year'] = year
                        appendict2[column]['month'] = month
                        if month == '07' or month == '08' or month == '09':
                            appendict3[column]['season'] = 3
                            appendict3[column]['year'] = year
                            if df[column][i] <= 0 or math.isnan(df[column][i]):
                                pass
                            else:
                                appendict3[column]['N'] = appendict3[column]['N'] + 1
                            appendict3[column]['depth(m)'] = column
                            total3[column].append(df[column][i])
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
                        appendict2[column]['max'] = round(np.nanmax(total2[column]), 3)
                        appendict2[column]['min'] = round(np.nanmin(total2[column]), 3)
                        appendict2[column]['Ndays>=24'] = len([days for days in total2[column] if days >= 24])
                        appendict2[column]['Ndays>=25'] = len([days for days in total2[column] if days >= 25])
                        appendict2[column]['Ndays>=26'] = len([days for days in total2[column] if days >= 26])
                    mydf2 = mydf2.append(appendict2[column], ignore_index=True)
                    appendict2[column]['N'] = 0
                    total2[column] = []
                    # Appendict3 part
                    appendict3[column]['depth(m)'] = column
                    if appendict3[column]['N'] == 0:
                        appendict3[column]['mean'] = 0
                    else:
                        total3[column] = [np.nan if tot == 0 else tot for tot in total3[column]]
                        appendict3[column]['mean'] = round(np.nanmean(total3[column]), 3)
                        appendict3[column]['std'] = round(stdev(total3[column]), 3)
                        appendict3[column]['max'] = round(np.nanmax(total3[column]), 3)
                        appendict3[column]['min'] = round(np.nanmin(total3[column]), 3)
                        appendict3[column]['Ndays>=24'] = len([days for days in total3[column] if days >= 24])
                        appendict3[column]['Ndays>=25'] = len([days for days in total3[column] if days >= 25])
                        appendict3[column]['Ndays>=26'] = len([days for days in total3[column] if days >= 26])
                    mydf3 = mydf3.append(appendict3[column], ignore_index=True)
                    appendict3[column]['N'] = 0
                    total3[column] = []
            for column in df:
                if column != 'Date' and column != 'Time':
                    appendict[column]['date'] = df['Date'][i]
                    appendict2[column]['year'] = year
                    appendict2[column]['month'] = month
                    if month == '07' or month == '08' or month == '09':
                        appendict3[column]['season'] = 3
                        appendict3[column]['year'] = year
                        if df[column][i] <= 0 or math.isnan(df[column][i]):
                            pass
                        else:
                            appendict3[column]['N'] = appendict3[column]['N'] + 1
                        appendict3[column]['depth(m)'] = column
                        total3[column].append(df[column][i])
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
        year = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%Y')
        month = datetime.strftime(datetime.strptime(df['Date'][i], '%d/%m/%Y'), '%m')
        if year == firstyear or year == datetime.strftime(datetime.strptime(df['Date'][i - 1], '%d/%m/%Y'), '%Y'):

            if month == firstmonth or month == datetime.strftime(datetime.strptime(df['Date'][i - 1], '%d/%m/%Y'),
                                                                 '%m'):
                if df['Date'][i] == firstdate or df['Date'][i] == df['Date'][i - 1]:
                    for column in df:
                        if column != 'Date' and column != 'Time':
                            appendict[column]['date'] = df['Date'][i]
                            appendict2[column]['year'] = year
                            appendict2[column]['month'] = month
                            if month == '07' or month == '08' or month == '09':
                                appendict3[column]['season'] = 3
                                appendict3[column]['year'] = year
                                if df[column][i] <= 0 or math.isnan(df[column][i]):
                                    pass
                                else:
                                    appendict3[column]['N'] = appendict3[column]['N'] + 1
                                appendict3[column]['depth(m)'] = column
                                total3[column].append(df[column][i])
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
                            if month == '07' or month == '08' or month == '09':
                                appendict3[column]['season'] = 3
                                appendict3[column]['year'] = year
                                if df[column][i] <= 0 or math.isnan(df[column][i]):
                                    pass
                                else:
                                    appendict3[column]['N'] = appendict3[column]['N'] + 1
                                appendict3[column]['depth(m)'] = column
                                total3[column].append(df[column][i])
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
                            appendict2[column]['max'] = round(np.nanmax(total2[column]), 3)
                            appendict2[column]['min'] = round(np.nanmin(total2[column]), 3)
                            appendict2[column]['Ndays>=24'] = len([days for days in total2[column] if days >= 24])
                            appendict2[column]['Ndays>=25'] = len([days for days in total2[column] if days >= 25])
                            appendict2[column]['Ndays>=26'] = len([days for days in total2[column] if days >= 26])
                        mydf2 = mydf2.append(appendict2[column], ignore_index=True)
                        appendict2[column]['N'] = 0
                        total2[column] = []
                for column in df:
                    if column != 'Date' and column != 'Time':
                        appendict[column]['date'] = df['Date'][i]
                        appendict2[column]['year'] = year
                        appendict2[column]['month'] = month
                        if month == '07' or month == '08' or month == '09':
                            appendict3[column]['season'] = 3
                            appendict3[column]['year'] = year
                            if df[column][i] <= 0 or math.isnan(df[column][i]):
                                pass
                            else:
                                appendict3[column]['N'] = appendict3[column]['N'] + 1
                            appendict3[column]['depth(m)'] = column
                            total3[column].append(df[column][i])
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
                        appendict2[column]['max'] = round(np.nanmax(total2[column]), 3)
                        appendict2[column]['min'] = round(np.nanmin(total2[column]), 3)
                        appendict2[column]['Ndays>=24'] = len([days for days in total2[column] if days >= 24])
                        appendict2[column]['Ndays>=25'] = len([days for days in total2[column] if days >= 25])
                        appendict2[column]['Ndays>=26'] = len([days for days in total2[column] if days >= 26])
                    mydf2 = mydf2.append(appendict2[column], ignore_index=True)
                    appendict2[column]['N'] = 0
                    total2[column] = []
                    # Appendict3 part
                    appendict3[column]['depth(m)'] = column
                    if appendict3[column]['N'] == 0:
                        appendict3[column]['mean'] = 0
                    else:
                        total3[column] = [np.nan if tot == 0 else tot for tot in total3[column]]
                        appendict3[column]['mean'] = round(np.nanmean(total3[column]), 3)
                        appendict3[column]['std'] = round(stdev(total3[column]), 3)
                        appendict3[column]['max'] = round(np.nanmax(total3[column]), 3)
                        appendict3[column]['min'] = round(np.nanmin(total3[column]), 3)
                        appendict3[column]['Ndays>=23'] = len([days for days in total3[column] if days >= 23])
                        appendict3[column]['Ndays>=24'] = len([days for days in total3[column] if days >= 24])
                        appendict3[column]['Ndays>=25'] = len([days for days in total3[column] if days >= 25])
                        appendict3[column]['Ndays>=26'] = len([days for days in total3[column] if days >= 26])
                        appendict3[column]['Ndays>=27'] = len([days for days in total3[column] if days >= 27])
                        appendict3[column]['Ndays>=28'] = len([days for days in total3[column] if days >= 28])
                    mydf3 = mydf3.append(appendict3[column], ignore_index=True)
                    appendict3[column]['N'] = 0
                    total3[column] = []
            for column in df:
                if column != 'Date' and column != 'Time':
                    appendict[column]['date'] = df['Date'][i]
                    appendict2[column]['year'] = year
                    appendict2[column]['month'] = month
                    if month == '07' or month == '08' or month == '09':
                        appendict3[column]['season'] = 3
                        appendict3[column]['year'] = year
                        if df[column][i] <= 0 or math.isnan(df[column][i]):
                            pass
                        else:
                            appendict3[column]['N'] = appendict3[column]['N'] + 1
                        appendict2[column]['depth(m)'] = column
                        total3[column].append(df[column][i])
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
writer = ExcelWriter('../tmednetGUI/example.xlsx')
mydf.to_excel(writer, 'Daily')
mydf2.to_excel(writer, 'Monthly')
mydf3.to_excel(writer, 'Seasonal')
writer.save()

print('me')
