import mhw_mapper as mp
import sys, getopt, os
from datetime import datetime, timedelta


mode = ''
MODES = ['intensity', 'duration']
mode = 'all'
last_day = False

print('Selected map is ', mode)
start_date = '2023-01-01'
#start_date = '2024-04-01'
end_date = '2023-12-31'
#end_date = '2024-04-08'
df_map = mp.MHWMapper('/mnt/MHW/2023_MHW.nc', start_period=start_date, end_period=end_date)
if mode == 'all':
    for i in MODES:
        df_map.map_temperature(i, whole_year=True)
else:
    df_map.map_temperature(mode, whole_year=True)
print('Map of {} successfully created at src/output_images'.format(mode))
