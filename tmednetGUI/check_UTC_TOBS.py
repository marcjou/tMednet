import os
import numpy as np
import pandas as pd
from datetime import datetime

FILEPATH = '../res/TOBS/'
site = []
date = []
time = []
filenames = os.listdir(FILEPATH)
for tobsfile in filenames:
    tobs_path = FILEPATH + tobsfile
    site.append(tobsfile.split('_')[1])
    file = pd.read_csv(tobs_path, sep='\t')
    file2 = file.rename(columns={'NaN': 'Date', 'NaN.1': 'Time'})
    file2.dropna(how='all', inplace=True)
    date.append(datetime.strftime(datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(file2['Date'].iloc[-1].astype(int)) - 2), '%d/%m/%Y'))
    time_df = file2['Time'].iloc[-1]
    if len(str(int(((float(time_df) * 24) % 1) * 60))) == 1:
        time_temp = str(int(float(time_df) * 24)) + ':0' + str(int(((float(time_df) * 24) % 1) * 60)) +\
               ':0' + str(int(((((float(time_df) * 24) % 1) * 60) % 1) * 60))
    else:
        time_temp = str(int(float(time_df) * 24) + 1) + ':00:00'
    if len(time_temp) == 7:
        time.append('0' + time_temp)
    else:
        time.append(time_temp)

df = pd.DataFrame([date, time]).T
df.columns = ['Date', 'Time']
df.index = site
df.index = df.index.astype(int)
df.sort_index(inplace=True)
with open("../src/tmednet_log.txt", "w") as file_object:
    for index, row in df.iterrows():
        site_line = '****Site code: {}****\n\n'.format(str(index))
        utc_jump_line = '-Last record in local time: {} at {}\n\n\n'.format(row['Date'], row['Time'])
        separator = '-' * len(utc_jump_line)
        jumpline = '\n\n'
        file_object.writelines([site_line, utc_jump_line, separator, jumpline])
print('Hi there')