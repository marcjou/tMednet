import math
from datetime import datetime
from statistics import stdev

import numpy as np
import pandas as pd
from pandas import ExcelWriter


class Excel:

    def __init__(self, input_path, output_path='', write_excel=True, seasonal=True):
        self.df = pd.read_csv(input_path, '\t')
        self.n = 0
        self.total = {}
        self.total2 = {}
        self.total3 = {}
        self.firstdate = self.df['Date'][0]
        self.lastdate = self.df['Date'][len(self.df) - 1]

        self.mydf = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])

        self.mydf2 = pd.DataFrame(
            columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                     'Ndays>=26'])
        self.mydf3 = pd.DataFrame(
            columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                     'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])

        self.appendict = {}
        self.appendict2 = {}
        self.appendict3 = {}
        self.df = self.df.fillna(0)

        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.total[column] = []
                self.total2[column] = []
                self.total3[column] = []
                self.appendict[column] = {'date': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0, 'min': 0}
                self.appendict2[column] = {'year': 0, 'month': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0,
                                           'min': 0,
                                           'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0}
                self.appendict3[column] = {'year': 0, 'season': 0, 'depth(m)': 0, 'N': 0, 'mean': 0, 'std': 0, 'max': 0,
                                           'min': 0,
                                           'Ndays>=23': 0, 'Ndays>=24': 0, 'Ndays>=25': 0, 'Ndays>=26': 0,
                                           'Ndays>=27': 0,
                                           'Ndays>=28': 0}

        self.firstmonth = datetime.strftime(datetime.strptime(self.df['Date'][0], '%d/%m/%Y'), '%m')
        self.firstyear = datetime.strftime(datetime.strptime(self.df['Date'][0], '%d/%m/%Y'), '%Y')
        if write_excel:
            self.excel_writer(output_path)
        elif seasonal:
            self.only_seasonal()
        else:
            self.multiyear_mean_calculator()

    def txt_getter(self, year, month, i):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.appendict[column]['date'] = self.df['Date'][i]
                self.appendict2[column]['year'] = year
                self.appendict2[column]['month'] = month
                if month == '07' or month == '08' or month == '09':
                    self.appendict3[column]['season'] = 3
                    self.appendict3[column]['year'] = year
                    if self.df[column][i] <= 0 or math.isnan(self.df[column][i]):
                        pass
                    else:
                        self.appendict3[column]['N'] = self.appendict3[column]['N'] + 1
                    self.appendict3[column]['depth(m)'] = column
                    self.total3[column].append(self.df[column][i])
                if self.df[column][i] <= 0 or math.isnan(self.df[column][i]):
                    pass
                else:
                    self.appendict[column]['N'] = self.appendict[column]['N'] + 1
                    self.appendict2[column]['N'] = self.appendict2[column]['N'] + 1
                self.appendict[column]['depth(m)'] = column
                self.appendict2[column]['depth(m)'] = column
                self.total[column].append(self.df[column][i])
                self.total2[column].append(self.df[column][i])

    def excel_setter(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.appendict[column]['depth(m)'] = column
                if self.appendict[column]['N'] == 0:
                    self.appendict[column]['mean'] = 0
                else:
                    self.total[column] = [np.nan if tot == 0 else tot for tot in self.total[column]]
                    self.appendict[column]['mean'] = round(np.nanmean(self.total[column]), 3)
                    self.appendict[column]['std'] = round(stdev(self.total[column]), 3)
                    self.appendict[column]['max'] = round(max(self.total[column]), 3)
                    self.appendict[column]['min'] = round(min(self.total[column]), 3)
                self.mydf = self.mydf.append(self.appendict[column], ignore_index=True)
                self.appendict[column]['N'] = 0
                self.total[column] = []

    def excel_setter2(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict1 part
                self.appendict[column]['depth(m)'] = column
                if self.appendict[column]['N'] == 0:
                    self.appendict[column]['mean'] = 0
                else:
                    self.total[column] = [np.nan if tot == 0 else tot for tot in self.total[column]]
                    self.appendict[column]['mean'] = round(np.nanmean(self.total[column]), 3)
                    self.appendict[column]['std'] = round(stdev(self.total[column]), 3)
                    self.appendict[column]['max'] = round(max(self.total[column]), 3)
                    self.appendict[column]['min'] = round(min(self.total[column]), 3)
                self.mydf = self.mydf.append(self.appendict[column], ignore_index=True)
                self.appendict[column]['N'] = 0
                self.total[column] = []
                # Appendict2 part
                self.appendict2[column]['depth(m)'] = column
                if self.appendict2[column]['N'] == 0:
                    self.appendict2[column]['mean'] = 0
                else:
                    self.total2[column] = [np.nan if tot == 0 else tot for tot in self.total2[column]]
                    self.appendict2[column]['mean'] = round(np.nanmean(self.total2[column]), 3)
                    self.appendict2[column]['std'] = round(stdev(self.total2[column]), 3)
                    self.appendict2[column]['max'] = round(np.nanmax(self.total2[column]), 3)
                    self.appendict2[column]['min'] = round(np.nanmin(self.total2[column]), 3)
                    self.appendict2[column]['Ndays>=24'] = len([days for days in self.total2[column] if days >= 24])
                    self.appendict2[column]['Ndays>=25'] = len([days for days in self.total2[column] if days >= 25])
                    self.appendict2[column]['Ndays>=26'] = len([days for days in self.total2[column] if days >= 26])
                self.mydf2 = self.mydf2.append(self.appendict2[column], ignore_index=True)
                self.appendict2[column]['N'] = 0
                self.total2[column] = []

    def excel_setter3(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict1 part
                self.appendict[column]['depth(m)'] = column
                if self.appendict[column]['N'] == 0:
                    self.appendict[column]['mean'] = 0
                else:
                    self.total[column] = [np.nan if tot == 0 else tot for tot in self.total[column]]
                    self.appendict[column]['mean'] = round(np.nanmean(self.total[column]), 3)
                    self.appendict[column]['std'] = round(stdev(self.total[column]), 3)
                    self.appendict[column]['max'] = round(max(self.total[column]), 3)
                    self.appendict[column]['min'] = round(min(self.total[column]), 3)
                self.mydf = self.mydf.append(self.appendict[column], ignore_index=True)
                self.appendict[column]['N'] = 0
                self.total[column] = []
                # Appendict2 part
                self.appendict2[column]['depth(m)'] = column
                if self.appendict2[column]['N'] == 0:
                    self.appendict2[column]['mean'] = 0
                else:
                    self.total2[column] = [np.nan if tot == 0 else tot for tot in self.total2[column]]
                    self.appendict2[column]['mean'] = round(np.nanmean(self.total2[column]), 3)
                    self.appendict2[column]['std'] = round(stdev(self.total2[column]), 3)
                    self.appendict2[column]['max'] = round(np.nanmax(self.total2[column]), 3)
                    self.appendict2[column]['min'] = round(np.nanmin(self.total2[column]), 3)
                    self.appendict2[column]['Ndays>=24'] = len([days for days in self.total2[column] if days >= 24])
                    self.appendict2[column]['Ndays>=25'] = len([days for days in self.total2[column] if days >= 25])
                    self.appendict2[column]['Ndays>=26'] = len([days for days in self.total2[column] if days >= 26])
                self.mydf2 = self.mydf2.append(self.appendict2[column], ignore_index=True)
                self.appendict2[column]['N'] = 0
                self.total2[column] = []
                # Appendict3 part
                self.appendict3[column]['depth(m)'] = column
                if self.appendict3[column]['N'] == 0:
                    self.appendict3[column]['mean'] = 0
                else:
                    self.total3[column] = [np.nan if tot == 0 else tot for tot in self.total3[column]]
                    self.appendict3[column]['mean'] = round(np.nanmean(self.total3[column]), 3)
                    self.appendict3[column]['std'] = round(stdev(self.total3[column]), 3)
                    self.appendict3[column]['max'] = round(np.nanmax(self.total3[column]), 3)
                    self.appendict3[column]['min'] = round(np.nanmin(self.total3[column]), 3)
                    self.appendict3[column]['Ndays>=23'] = len([days for days in self.total3[column] if days >= 23])
                    self.appendict3[column]['Ndays>=24'] = len([days for days in self.total3[column] if days >= 24])
                    self.appendict3[column]['Ndays>=25'] = len([days for days in self.total3[column] if days >= 25])
                    self.appendict3[column]['Ndays>=26'] = len([days for days in self.total3[column] if days >= 26])
                    self.appendict3[column]['Ndays>=27'] = len([days for days in self.total3[column] if days >= 27])
                    self.appendict3[column]['Ndays>=28'] = len([days for days in self.total3[column] if days >= 28])
                self.mydf3 = self.mydf3.append(self.appendict3[column], ignore_index=True)
                self.appendict3[column]['N'] = 0
                self.total3[column] = []

    def main(self):
        for i in range(len(self.df)):

            if type(self.df['Date'][i]) != type('27/12/1995'):
                pass
            elif i >= 1 and type(self.df['Date'][i - 1]) != type('27/12/1995'):
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')
                if year == self.firstyear or year == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 2], '%d/%m/%Y'),
                        '%Y'):

                    if month == self.firstmonth or month == datetime.strftime(
                            datetime.strptime(self.df['Date'][i - 2], '%d/%m/%Y'), '%m'):

                        if self.df['Date'][i] == self.firstdate or self.df['Date'][i] == self.df['Date'][i - 2]:
                            self.txt_getter(year, month, i)
                        else:
                            self.excel_setter()
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter2()
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter3()
                    self.txt_getter(year, month, i)
            else:
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')
                if year == self.firstyear or year == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 1], '%d/%m/%Y'),
                        '%Y'):

                    if month == self.firstmonth or month == datetime.strftime(
                            datetime.strptime(self.df['Date'][i - 1], '%d/%m/%Y'),
                            '%m'):
                        if self.df['Date'][i] == self.firstdate or self.df['Date'][i] == self.df['Date'][i - 1]:
                            self.txt_getter(year, month, i)
                        else:
                            self.excel_setter()
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter2()
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter3()
                    self.txt_getter(year, month, i)
            if i == len(self.df) - 1:
                self.excel_setter3()

            print(str(i) + ' de ' + str(len(self.df)))

    def excel_writer(self, path):
        writer = ExcelWriter(path)
        self.main()
        self.mydf.to_excel(writer, 'Daily')
        self.mydf2.to_excel(writer, 'Monthly')
        self.mydf3.to_excel(writer, 'Seasonal')
        writer.save()

    def calculate_seasonal(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict3 part
                self.appendict3[column]['depth(m)'] = column
                if self.appendict3[column]['N'] == 0:
                    self.appendict3[column]['mean'] = 0
                else:
                    self.total3[column] = [np.nan if tot == 0 else tot for tot in self.total3[column]]
                    self.appendict3[column]['mean'] = round(np.nanmean(self.total3[column]), 3)
                    self.appendict3[column]['std'] = round(stdev(self.total3[column]), 3)
                    self.appendict3[column]['max'] = round(np.nanmax(self.total3[column]), 3)
                    self.appendict3[column]['min'] = round(np.nanmin(self.total3[column]), 3)
                    self.appendict3[column]['Ndays>=23'] = len([days for days in self.total3[column] if days >= 23])
                    self.appendict3[column]['Ndays>=24'] = len([days for days in self.total3[column] if days >= 24])
                    self.appendict3[column]['Ndays>=25'] = len([days for days in self.total3[column] if days >= 25])
                    self.appendict3[column]['Ndays>=26'] = len([days for days in self.total3[column] if days >= 26])
                    self.appendict3[column]['Ndays>=27'] = len([days for days in self.total3[column] if days >= 27])
                    self.appendict3[column]['Ndays>=28'] = len([days for days in self.total3[column] if days >= 28])
                self.mydf3 = self.mydf3.append(self.appendict3[column], ignore_index=True)
                self.appendict3[column]['N'] = 0
                self.total3[column] = []

    def txt_getter_seasonal(self, year, month, i):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                if month == '07' or month == '08' or month == '09':
                    self.appendict3[column]['season'] = 3
                    self.appendict3[column]['year'] = year
                    if self.df[column][i] <= 0 or math.isnan(self.df[column][i]):
                        pass
                    else:
                        self.appendict3[column]['N'] = self.appendict3[column]['N'] + 1
                    self.appendict3[column]['depth(m)'] = column
                    self.total3[column].append(self.df[column][i])

    def only_seasonal(self):
        for i in range(len(self.df)):
            if type(self.df['Date'][i]) != type('27/12/1995'):
                pass
            elif i >= 1 and type(self.df['Date'][i - 1]) != type('27/12/1995'):
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')
                if year == self.firstyear or year == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 2], '%d/%m/%Y'),
                        '%Y'):

                    self.txt_getter_seasonal(year, month, i)
                else:
                    self.calculate_seasonal()
                    self.txt_getter_seasonal(year, month, i)
            else:
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')
                if year == self.firstyear or year == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 1], '%d/%m/%Y'),
                        '%Y'):

                    self.txt_getter_seasonal(year, month, i)
                else:
                    self.calculate_seasonal()
                    self.txt_getter_seasonal(year, month, i)
            if i == len(self.df) - 1:
                self.calculate_seasonal()

            print(str(i) + ' de ' + str(len(self.df)))

    def monthly_getter(self, year, month, i):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.appendict2[column]['year'] = year
                self.appendict2[column]['month'] = month
                if self.df[column][i] <= 0 or math.isnan(self.df[column][i]):
                    pass
                else:
                    self.appendict2[column]['N'] = self.appendict2[column]['N'] + 1
                self.appendict2[column]['depth(m)'] = column
                self.total2[column].append(self.df[column][i])

    def monthly_setter(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict2 part
                self.appendict2[column]['depth(m)'] = column
                if self.appendict2[column]['N'] == 0:
                    self.appendict2[column]['mean'] = 0
                else:
                    self.total2[column] = [np.nan if tot == 0 else tot for tot in self.total2[column]]
                    self.appendict2[column]['mean'] = round(np.nanmean(self.total2[column]), 3)
                    self.appendict2[column]['std'] = round(stdev(self.total2[column]), 3)
                    self.appendict2[column]['max'] = round(np.nanmax(self.total2[column]), 3)
                    self.appendict2[column]['min'] = round(np.nanmin(self.total2[column]), 3)
                    self.appendict2[column]['Ndays>=24'] = len([days for days in self.total2[column] if days >= 24])
                    self.appendict2[column]['Ndays>=25'] = len([days for days in self.total2[column] if days >= 25])
                    self.appendict2[column]['Ndays>=26'] = len([days for days in self.total2[column] if days >= 26])
                self.mydf2 = self.mydf2.append(self.appendict2[column], ignore_index=True)
                self.appendict2[column]['N'] = 0
                self.total2[column] = []

    def multiyear_mean_calculator(self):
        #Calculates the multiyear mean for the annual t-cycles plot
        for i in range(len(self.df)):
            if type(self.df['Date'][i]) != type('27/12/1995'):
                pass
            elif i >= 1 and type(self.df['Date'][i - 1]) != type('27/12/1995'):
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')

                if month == self.firstmonth or month == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 2], '%d/%m/%Y'), '%m'):

                    self.monthly_getter(year, month, i)

                else:
                    self.firstmonth = '00'
                    self.monthly_setter()
                    self.monthly_getter(year, month, i)
            else:
                year = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%Y')
                month = datetime.strftime(datetime.strptime(self.df['Date'][i], '%d/%m/%Y'), '%m')

                if month == self.firstmonth or month == datetime.strftime(
                        datetime.strptime(self.df['Date'][i - 1], '%d/%m/%Y'),
                        '%m'):
                    self.monthly_getter(year, month, i)
                else:
                    self.firstmonth = '00'
                    self.monthly_setter()
                    self.monthly_getter(year, month, i)
            if i == len(self.df) - 1:
                self.monthly_setter()

            print(str(i) + ' de ' + str(len(self.df)))
        self.monthlymeandf = pd.DataFrame(columns=['month', 'depth', 'mean'])
        monthlydict = {'month':0, 'depth':0, 'mean':0}
        self.mydf2.replace(0, np.nan, inplace=True)
        for month in self.mydf2['month'].unique():
            for depth in self.mydf2['depth(m)'].unique():
                monthlydict['month'] = month
                monthlydict['depth'] = depth
                monthlydict['mean'] = np.nanmean(self.mydf2.loc[(self.mydf2['month'] == month) & (self.mydf2['depth(m)'] == depth), 'mean'])
                self.monthlymeandf = self.monthlymeandf.append(monthlydict, ignore_index=True)

def big_merge(filename1, filename2, output):
    df1 = pd.read_csv(filename1, '\t')
    df2 = pd.read_csv(filename2, sep="\s+", skiprows=6)
    df2.index.set_names(["Date", "Time"], level=[0, 1], inplace=True)
    df2.reset_index(inplace=True)

    for i in range(len(df2["Date"])):
        df2.at[i, "Date"] = datetime.strftime(datetime.strptime(df2["Date"][i], "%Y-%m-%d"), "%d/%m/%Y")

    dfconc = pd.concat([df1, df2])
    dfconc.replace(np.nan, '', regex=True, inplace=True)

    dfconc.to_csv('../src/output_files/'+ output + '.txt', sep='\t', index=False)

# prova = Excel("../src/output_files/mergo.txt", 'example2.xlsx')

