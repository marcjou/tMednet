import numpy as np
import pandas as pd
from scipy.ndimage.filters import uniform_filter1d

#Class used to access the log file and modify it
class LogWriter:
    LOG_PATH = '../src/tmednet_log.txt'

    def __init__(self):
        self._data = []
        self.open_file()

    def __str__(self):
        return "<LogWriter object>"

    def modify_log(self, site, new_log_line):
        self.insert_data(site, new_log_line)
        self.write_file()

    def open_file(self):
        with open(LogWriter.LOG_PATH, 'r') as file:
            self._data = file.readlines()


    def insert_data(self, site, new_log_line):
        #TODO make that if the -0.2 check already exists for a given site and depth just
        # append to the line the new occurences instead of creating a new line
        if type(new_log_line) == str:
            new_log_line = [new_log_line]
        lookfor = '****Site code: {}****\n'.format(site)
        separator = self._data[0]
        # Find the last line of the site on the log to write new information
        insert_index = self._data.index(lookfor) + self._data[self._data.index(lookfor):].index(separator) - 2
        count = 0
        for line in new_log_line:
            self._data.insert(insert_index + count, '-' + line + '\n')
            count = count + 1

    def write_file(self):
        with open(LogWriter.LOG_PATH, 'w') as file:
            file.writelines(self._data)

    def difference_and_filter(self, filename):
        df = pd.read_csv(filename, sep='\t')
        site = filename.split('/')[-1].split('_')[2]
        depths = df.columns[2:]
        df_filter = self._calculate_filter(self._calculate_difference(df, depths), depths)
        incident_dict = {x: [] for x in df_filter.columns}
        line = []
        for depth in df_filter.columns:
            index_list = df.iloc[df_filter['5-10'].loc[df_filter['5-10'] < -0.2].index]
            if len(index_list) > 0:
                incident_dict[depth] = (index_list['Date'] + ' ' + index_list['Time']).values
                line.append('Difference lower than -0.2 '
                            'between {} meters {} instances '
                            'at [{}]'.format(depth, len(incident_dict[depth]), ', '.join(incident_dict[depth])))
        if len(line) > 0:
            self.modify_log(site, line)
        print('Hi there')

    def _calculate_difference(self, df, depths):
        i = 1
        for depth in depths[:-1]:
            series1 = df[str(depth)] - df[
                str(depths[i])]  # If fails, raises Key error (depth doesn't exist)
            series1 = series1.rename(str(depth) + "-" + str(depths[i]))
            i += 1
            if 'dfdelta' in locals():
                dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
            else:
                dfdelta = pd.DataFrame(series1)
        return dfdelta

    def _calculate_filter(self, df, depths):
        i = 1
        for depth in depths[:-1]:
            series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])].dropna(), size=240),
                                   index=df[str(depth) + "-" + str(depths[i])].dropna().index,
                                   columns=[str(depth) + "-" + str(depths[i])]).reindex(df.index)
            # series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])], size=240),
            #                       index=data[indi]['time'], columns=[str(depth) + "-" + str(depths[i])])
            i += 1
            if 'dfdelta' in locals():
                dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
            else:
                dfdelta = pd.DataFrame(series1)

        return dfdelta

    @property
    def data(self):
        return self._data

    @classmethod
    def get_path(cls):
        return cls.LOG_PATH
