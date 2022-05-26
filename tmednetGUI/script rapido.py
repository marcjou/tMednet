import math
import pandas as pd
import numpy as np
from datetime import datetime
import progressbar as pb
import time
start = time.time()
file = pd.read_csv('../src/Tobs_05_Cap de Creus-S_200705-202110.txt', sep='\t')
file2 = file.rename(columns={'NaN': 'Date', 'NaN.1': 'Time'})
datime = []
nanline = []
i = 0

#progress_bar = pb.progressBar(len(file2['Date']), prefix='Progress:', suffix='Complete', length=50)

# TESTS
file2.dropna(how='all', inplace=True) #Drops all the lines that are pure NaN
file2['Date'] = file2['Date'].astype(int)
file2['Date'] = file2['Date'].map(lambda x: datetime.strftime(datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(x) - 2), '%d/%m/%Y'))
file2['Time'] = file2['Time'].map(lambda x: str(int(float(x) * 24)) + ':0' + str(int(((float(x) * 24) % 1) * 60)) + ':0' + str(int(((((float(x) * 24) % 1) * 60) % 1)* 60)) if len(str(int(((float(x) * 24) % 1) * 60))) == 1 else str(int(float(x) * 24) + 1) + ':00:00')
file2['Time'] = file2['Time'].map(lambda x: '0' + x if len(x) == 7 else x)

'''
# Not necessary with what we have above much faster
for x in file2['Date']:
    if math.isnan(x) == False:
        file2['Date'][i] = datetime.strftime(datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(x) - 2), '%d/%m/%Y')
    else:
        nanline.append(i)
    #progress_bar.print_progress_bar(i)
    i = i + 1
for n in nanline:
    file2.drop(index=n, inplace=True)
i = 0
#progress_bar = pb.progressBar(len(file2['Time']), prefix='Progress:', suffix='Complete', length=50)


for x in file2['Time']:
    try:
        hour = str(int(float(x) * 24))
        min = str(int(((float(x) * 24) % 1) * 60))
        sec = str(int(((((float(x) * 24) % 1) * 60) % 1)* 60))
        if len(hour) == 1:
            hour = '0' + hour
        if len(min) == 1:
            min = '0' + min
        elif min == '59':
            hour = str(int(hour) + 1)
            if len(hour) == 1:
                hour = '0' + hour
            min = '00'
            sec = '00'
        if len(sec) == 1:
            sec = '0' + sec
        time = hour + ':' + min + ':' + sec
        file2['Time'][i] = time
    except ValueError:
        file2.drop(index=i, inplace=True)
    #progress_bar.print_progress_bar(i)
    i = i + 1

file2['added'] = file2['Date'].astype(str) + ' ' + file2['Time'].astype(str)

end = time.time()
print(end-start)

file2.set_index('added', inplace=True)
file2.index.name = None
del file2['Date']
del file2['Time']
end = time.time()
print(end-start)
'''

file2.to_csv('../src/output_files/CPS_Try_Old.txt', sep='\t', index=False)

end = time.time()
print(end-start)
