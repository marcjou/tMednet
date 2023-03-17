import math
import numpy as np
import pandas as pd
import progressbar as pb
from statistics import stdev
from datetime import datetime
from pandas import ExcelWriter
import marineHeatWaves as mhw
import time


class Excel:

    def __init__(self, input_path, output_path='', write_excel=True, seasonal=True, lastyear=False, console=False):
        self.df = pd.read_csv(input_path, sep='\t', dayfirst=True)
        self.mhwdf = self.df.copy()
        self.n = 0
        self.total = {}
        self.total2 = {}
        self.total3 = {}
        self.firstdate = self.df['Date'][0]
        self.lastdate = self.df['Date'][len(self.df) - 1]
        self.console = console
        self.start_data_frames()
        self.appendict = {}
        self.appendict2 = {}
        self.appendict3 = {}
        self.df = self.df.fillna(0)
        self.dailymeans = {}
        self.seasonalmeans = {}
        self.fill_dictionaries()
        self.firstmonth = datetime.strftime(datetime.strptime(self.df['Date'][0], '%d/%m/%Y'), '%m')
        self.firstyear = datetime.strftime(datetime.strptime(self.df['Date'][0], '%d/%m/%Y'), '%Y')
        if write_excel:
            self.excel_writer(output_path)
        elif seasonal:
            self.only_seasonal()
        elif lastyear:
            self.calculate_lastyear()
        else:
            self.multiyear_mean_calculator()

    def start_data_frames(self):
        self.mydf = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])

        self.mydf2 = pd.DataFrame(
            columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                     'Ndays>=26'])
        self.mydf3 = pd.DataFrame(
            columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                     'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])

    def fill_dictionaries(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.dailymeans[column] = []
                self.seasonalmeans[column] = []
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

    def excel_setter(self, month):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                self.appendict[column]['depth(m)'] = column
                if self.appendict[column]['N'] == 0:
                    self.appendict[column]['mean'] = ''
                    self.appendict[column]['std'] = ''
                    self.appendict[column]['max'] = ''
                    self.appendict[column]['min'] = ''
                else:
                    self.total[column] = [np.nan if tot == 0 else tot for tot in self.total[column]]
                    self.appendict[column]['mean'] = round(np.nanmean(self.total[column]), 3)
                    self.appendict[column]['std'] = round(stdev(self.total[column]), 3) if len(self.total[column]) >=2 else 0
                    self.appendict[column]['max'] = round(max(self.total[column]), 3)
                    self.appendict[column]['min'] = round(min(self.total[column]), 3)

                    self.dailymeans[column].append(round(np.nanmean(self.total[column]), 3))
                    if month == '07' or month == '08' or month == '09':
                        self.seasonalmeans[column].append(round(np.nanmean(self.total[column]), 3))

                #self.mydf = self.mydf.append(self.appendict[column], ignore_index=True)
                self.mydf = pd.concat([self.mydf, pd.DataFrame.from_dict([self.appendict[column]])], axis=0,
                                       join='outer', ignore_index=True)
                self.appendict[column]['N'] = 0
                self.total[column] = []

    def excel_setter2(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict2 part
                self.appendict2[column]['depth(m)'] = column
                if self.appendict2[column]['N'] == 0:
                    self.appendict2[column]['mean'] = ''
                    self.appendict2[column]['std'] = ''
                    self.appendict2[column]['max'] = ''
                    self.appendict2[column]['min'] = ''
                else:
                    self.total2[column] = [np.nan if tot == 0 else tot for tot in self.total2[column]]
                    self.appendict2[column]['mean'] = round(np.nanmean(self.total2[column]), 3)
                    self.appendict2[column]['std'] = round(stdev(self.total2[column]), 3) if len(self.total2[column]) >=2 else 0
                    self.appendict2[column]['max'] = round(np.nanmax(self.total2[column]), 3)
                    self.appendict2[column]['min'] = round(np.nanmin(self.total2[column]), 3)
                    self.appendict2[column]['Ndays>=24'] = round(
                        len([days for days in self.total2[column] if days >= 24]) / 24)
                    self.appendict2[column]['Ndays>=25'] = round(
                        len([days for days in self.total2[column] if days >= 25]) / 24)
                    self.appendict2[column]['Ndays>=26'] = round(
                        len([days for days in self.total2[column] if days >= 26]) / 24)
                #self.mydf2 = self.mydf2.append(self.appendict2[column], ignore_index=True)
                self.mydf2 = pd.concat([self.mydf2, pd.DataFrame.from_dict([self.appendict2[column]])], axis=0,
                                       join='outer', ignore_index=True)
                self.appendict2[column]['N'] = 0
                self.total2[column] = []
                self.dailymeans[column] = []

    def excel_setter3(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict3 part
                self.appendict3[column]['depth(m)'] = column
                if self.appendict3[column]['N'] == 0:
                    self.appendict3[column]['mean'] = ''
                    self.appendict3[column]['std'] = ''
                    self.appendict3[column]['max'] = ''
                    self.appendict3[column]['min'] = ''
                else:
                    self.total3[column] = [np.nan if tot == 0 else tot for tot in self.total3[column]]
                    self.appendict3[column]['mean'] = round(np.nanmean(self.total3[column]), 3)
                    self.appendict3[column]['std'] = round(stdev(self.total3[column]), 3) if len(self.total3[column]) >=2 else 0
                    self.appendict3[column]['max'] = round(np.nanmax(self.total3[column]), 3)
                    self.appendict3[column]['min'] = round(np.nanmin(self.total3[column]), 3)
                    self.appendict3[column]['Ndays>=23'] = round(
                        len([days for days in self.total3[column] if days >= 23]) / 24)
                    self.appendict3[column]['Ndays>=24'] = round(
                        len([days for days in self.total3[column] if days >= 24]) / 24)
                    self.appendict3[column]['Ndays>=25'] = round(
                        len([days for days in self.total3[column] if days >= 25]) / 24)
                    self.appendict3[column]['Ndays>=26'] = round(
                        len([days for days in self.total3[column] if days >= 26]) / 24)
                    self.appendict3[column]['Ndays>=27'] = round(
                        len([days for days in self.total3[column] if days >= 27]) / 24)
                    self.appendict3[column]['Ndays>=28'] = round(
                        len([days for days in self.total3[column] if days >= 28]) / 24)
                #self.mydf3 = self.mydf3.append(self.appendict3[column], ignore_index=True)
                self.mydf3 = pd.concat([self.mydf3, pd.DataFrame.from_dict([self.appendict3[column]])], axis=0,
                                       join='outer', ignore_index=True)
                self.appendict3[column]['N'] = 0
                self.total3[column] = []
                self.seasonalmeans[column] = []

    def main(self):
        progress_bar = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50)
        if self.console:
            console_progress = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50,
                                              console=self.console)
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
                            self.excel_setter(month)
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter(month)
                        self.excel_setter2()
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter(month)
                    self.excel_setter2()
                    self.excel_setter()
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
                            self.excel_setter(month)
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter(month)
                        self.excel_setter2()
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter(month)
                    self.excel_setter2()
                    self.excel_setter3()
                    self.txt_getter(year, month, i)
            if i == len(self.df) - 1:
                self.excel_setter(month)
                self.excel_setter2()
                self.excel_setter3()

            # print(str(i) + ' de ' + str(len(self.df)))
            progress_bar.print_progress_bar(i)
            if self.console:
                console_progress.print_progress_bar(i)


    def create_mhw(self):
        del self.mhwdf['Time']
        self.mhwdf['Date'] = pd.to_datetime(self.mhwdf['Date'], format='%d/%m/%Y')
        nufile = self.mhwdf.groupby('Date').mean()
        dates = [x.date() for x in nufile.index]
        t = [x.toordinal() for x in dates]
        t = np.array(t)
        depths = nufile.columns
        sst5 = nufile[depths[0]].values
        mhws, clim = mhw.detect(t, sst5)
        diff = pd.DataFrame(
            {'Date': mhws['date_start'], 'Depth (m)': depths[0], 'Duration (Days)': mhws['duration'], 'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
             'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']], 'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']]})
        for depth in depths:
            if depth == depths[0]:
                pass
            else:
                sst = nufile[depth].values
                mhws, clim = mhw.detect(t, sst)
                dfi = pd.DataFrame(
                    {'Date': mhws['date_start'], 'Depth (m)': depth, 'Duration (Days)': mhws['duration'], 'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
                     'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']], 'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']]})
                diff = diff.append(dfi, ignore_index=True)

        return diff

    def excel_writer(self, path):
        start = time.time()
        writer = ExcelWriter(path)
        self.main()
        mhwdf = self.create_mhw()
        self.mydf.to_excel(writer, 'Daily')
        self.mydf2.to_excel(writer, 'Monthly')
        self.mydf3.to_excel(writer, 'Seasonal')
        mhwdf.to_excel(writer, 'MHW', index=False)
        writer.save()
        end = time.time()
        print(end-start)

    def calculate_lastyear(self):
        #Here calculates only from May to December of the last Year of Data
        progress_bar = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50)
        if self.console:
            console_progress = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50,
                                              console=self.console)
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
                            self.excel_setter(month)
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter(month)
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter(month)
                    self.excel_setter()
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
                            self.excel_setter(month)
                            self.txt_getter(year, month, i)
                    else:
                        self.firstmonth = '00'
                        self.excel_setter(month)
                        self.txt_getter(year, month, i)
                else:
                    self.excel_setter(month)
                    self.txt_getter(year, month, i)
            if i == len(self.df) - 1:
                self.excel_setter(month)

            # print(str(i) + ' de ' + str(len(self.df)))
            progress_bar.print_progress_bar(i)
            if self.console:
                console_progress.print_progress_bar(i)

    def calculate_seasonal(self):
        for column in self.df:
            if column != 'Date' and column != 'Time':
                # Appendict3 part
                self.appendict3[column]['depth(m)'] = column
                if self.appendict3[column]['N'] == 0:
                    self.appendict3[column]['mean'] = ''
                    self.appendict3[column]['std'] = ''
                    self.appendict3[column]['max'] = ''
                    self.appendict3[column]['min'] = ''
                else:
                    self.total3[column] = [np.nan if tot == 0 else tot for tot in self.total3[column]]
                    self.appendict3[column]['mean'] = round(np.nanmean(self.total3[column]), 3)
                    self.appendict3[column]['std'] = round(stdev(self.total3[column]), 3) if len(self.total3[column]) >=2 else 0
                    self.appendict3[column]['max'] = round(np.nanmax(self.total3[column]), 3)
                    self.appendict3[column]['min'] = round(np.nanmin(self.total3[column]), 3)
                    self.appendict3[column]['Ndays>=23'] = round(
                        len([days for days in self.total3[column] if days >= 23]) / 24)
                    self.appendict3[column]['Ndays>=24'] = round(
                        len([days for days in self.total3[column] if days >= 24]) / 24)
                    self.appendict3[column]['Ndays>=25'] = round(
                        len([days for days in self.total3[column] if days >= 25]) / 24)
                    self.appendict3[column]['Ndays>=26'] = round(
                        len([days for days in self.total3[column] if days >= 26]) / 24)
                    self.appendict3[column]['Ndays>=27'] = round(
                        len([days for days in self.total3[column] if days >= 27]) / 24)
                    self.appendict3[column]['Ndays>=28'] = round(
                        len([days for days in self.total3[column] if days >= 28]) / 24)
                #self.mydf3 = self.mydf3.append(self.appendict3[column], ignore_index=True)
                self.mydf3 = pd.concat([self.mydf3, pd.DataFrame.from_dict([self.appendict3[column]])], axis=0,
                                       join='outer', ignore_index=True)
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
        progress_bar = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50)
        if self.console:
            console_progress = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50,
                                              console=self.console)
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

            # print(str(i) + ' de ' + str(len(self.df)))
            progress_bar.print_progress_bar(i)
            if self.console:
                console_progress.print_progress_bar(i)

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
                    self.appendict2[column]['mean'] = ''
                    self.appendict2[column]['std'] = ''
                    self.appendict2[column]['max'] = ''
                    self.appendict2[column]['min'] = ''
                else:
                    self.total2[column] = [np.nan if tot == 0 else tot for tot in self.total2[column]]
                    self.appendict2[column]['mean'] = round(np.nanmean(self.total2[column]), 3)
                    self.appendict2[column]['std'] = round(stdev(self.total2[column]), 3) if len(self.total2[column]) >=2 else 0
                    self.appendict2[column]['max'] = round(np.nanmax(self.total2[column]), 3)
                    self.appendict2[column]['min'] = round(np.nanmin(self.total2[column]), 3)
                    self.appendict2[column]['Ndays>=24'] = len([days for days in self.total2[column] if days >= 24])
                    self.appendict2[column]['Ndays>=25'] = len([days for days in self.total2[column] if days >= 25])
                    self.appendict2[column]['Ndays>=26'] = len([days for days in self.total2[column] if days >= 26])
                #self.mydf2 = self.mydf2.append(self.appendict2[column], ignore_index=True)
                self.mydf2 = pd.concat([self.mydf2, pd.DataFrame.from_dict([self.appendict2[column]])], axis=0, join='outer', ignore_index=True)
                self.appendict2[column]['N'] = 0
                self.total2[column] = []

    def multiyear_mean_calculator(self):
        progress_bar = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50)
        if self.console:
            console_progress = pb.progressBar(len(self.df), prefix='Progress:', suffix='Complete', length=50,
                                              console=self.console)
        # Calculates the multiyear mean for the annual t-cycles plot
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

            # print(str(i) + ' de ' + str(len(self.df)))
            progress_bar.print_progress_bar(i)
            if self.console:
                console_progress.print_progress_bar(i)

        self.monthlymeandf = pd.DataFrame(columns=['month', 'depth', 'mean'])
        monthlydict = {'month': 0, 'depth': 0, 'mean': 0}
        self.mydf2.replace(0, np.nan, inplace=True)
        for month in self.mydf2['month'].unique():
            for depth in self.mydf2['depth(m)'].unique():
                monthlydict['month'] = month
                monthlydict['depth'] = depth
                self.mydf2.replace('', np.NaN, inplace=True) # Replaces the empty values for NaN in order to calculate
                monthlydict['mean'] = np.nanmean(
                    self.mydf2.loc[(self.mydf2['month'] == month) & (self.mydf2['depth(m)'] == depth), 'mean'])
                #self.monthlymeandf = self.monthlymeandf.append(monthlydict, ignore_index=True)
                self.monthlymeandf = pd.concat([self.monthlymeandf, pd.DataFrame.from_dict([monthlydict])], axis=0,
                                       join='outer', ignore_index=True)


def big_merge(filename1, filename2, output):

    df2 = pd.read_csv(filename2, sep="\s+", skiprows=6)
    df2.index.set_names(["Date", "Time"], level=[0, 1], inplace=True)
    df2.reset_index(inplace=True)

    for i in range(len(df2["Date"])):
        df2.at[i, "Date"] = datetime.strftime(datetime.strptime(df2["Date"][i], "%Y-%m-%d"), "%d/%m/%Y")
    if filename1 == '':
        df2.replace(np.nan, '', regex=True, inplace=True)
        df2.to_csv('../src/output_files/' + output + '.txt', sep='\t', index=False)
    else:
        df1 = pd.read_csv(filename1, sep='\t')
        # Add white space between datasets
        df1 = pd.concat([df1, pd.Series([None]*len(df1.columns),index=df1.columns).to_frame().T],
                        axis=0, join='outer', ignore_index=True)
        dfconc = pd.concat([df1, df2])
        # Check if there is duplicity
        df1['dates'] = df1['Date'] + ' ' + df1['Time']
        df2['dates'] = df2['Date'] + ' ' + df2['Time']
        # Drop old duplicated rows that could come from older Datasets
        df1.drop(df1.loc[df1.duplicated(['dates'])].index, inplace=True)
        df2.drop(df2.loc[df2.duplicated(['dates'])].index, inplace=True)
        df1_in = df1.set_index('dates')
        df2_in = df2.set_index('dates')
        df = pd.concat([df1_in, df2_in], axis=1, keys=['df1', 'df2'], join='inner')
        duplicity = []
        if len(df) > 0:
            duplicity = df.index
        dfconc.replace(np.nan, '', regex=True, inplace=True)



        dfconc.to_csv('../src/output_files/' + output + '.txt', sep='\t', index=False)
        return duplicity