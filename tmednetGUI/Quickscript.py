from scipy import io
import pandas as pd
import numpy as np

mat = io.loadmat('../src/SST_sta_viz.mat')
mdata = mat['mySST_sta']
mdtype = mdata.dtype
ndata = {n: mdata[n][0, 0] for n in mdtype.names}

my_struct = {'month_data': {'stations': {'anomalies': {}, 'sst': {}}, 'regions': {'anomalies': {}, 'sst': {}}}}

# Annotate data for each year of operation
for year in ndata['YEARS'][0,:]:
    if year not in my_struct['month_data']['stations']['anomalies']:
        my_struct['month_data']['stations']['anomalies'][year] = {}
        year_index = np.where(ndata['YEARS'][0,:] == year)[0][0]
    if year not in my_struct['month_data']['regions']['anomalies']:
        my_struct['month_data']['regions']['anomalies'][year] = {}
    # Annotate data for each month of a given year of operation
    for month in range(1, 13):
        if month not in my_struct['month_data']['stations']['anomalies'][year]:
            my_struct['month_data']['stations']['anomalies'][year][month] = {}
            month_index = year_index * 12 + month - 1
        if month not in my_struct['month_data']['regions']['anomalies'][year]:
            my_struct['month_data']['regions']['anomalies'][year][month] = {}
        # Annotate data for each site of a given month in a given year of operation
        for site_id in ndata['code'][:,0]:
            site_id_index = np.where(ndata['code'][:,0] == site_id)[0][0]
            region = metadata['stations'][str(site_id)]['eco_region']
            my_struct['month_data']['stations']['anomalies'][year][month][site_id] = ndata['month_ano'][month_index, site_id_index]

            # Now, annotate data into 'regions', appending into an array to calculate average
            if region not in my_struct['month_data']['regions']['anomalies'][year][month]:
                my_struct['month_data']['regions']['anomalies'][year][month][region] = []

            my_struct['month_data']['regions']['anomalies'][year][month][region].append(ndata['month_ano'][month_index, site_id_index])

'''
#################################
# PROCES DE EXCEL ANOMALIES_FILE
#################################
workbook    = xlrd.open_workbook(ANOMALIES_FILE)
sheet       = workbook.sheet_by_index(0)

col_to_id = {}

my_struct = {'month_data': {'stations': {'anomalies': {}, 'sst': {}}, 'regions': {'anomalies': {}, 'sst': {}}}}

# Annotate translation from column number to site_id

for col_number in range(2, sheet.ncols):
    col_to_id[col_number] = int(sheet.cell(1,col_number).value)

# Annotate data for each year-month-station_id-anomaly_value

for row_number in range(2, sheet.nrows):
    year = int(sheet.cell(row_number, 0).value)
    month = int(sheet.cell(row_number, 1).value)

    print("Excel Anomalias: " + str(year) + "   " + str(month))

    for col_number in range(2, sheet.ncols):

        value = sheet.cell(row_number, col_number).value
        site_id = col_to_id[col_number]

        region = metadata['stations'][str(site_id)]['eco_region']

        if year not in my_struct['month_data']['stations']['anomalies']:
            my_struct['month_data']['stations']['anomalies'][year] = {}

        if month not in my_struct['month_data']['stations']['anomalies'][year]:
            my_struct['month_data']['stations']['anomalies'][year][month] = {}

        my_struct['month_data']['stations']['anomalies'][year][month][site_id] = value

        # Now, annotate data into 'regions', appending into an array to calculate average

        if year not in my_struct['month_data']['regions']['anomalies']:
            my_struct['month_data']['regions']['anomalies'][year] = {}

        if month not in my_struct['month_data']['regions']['anomalies'][year]:
            my_struct['month_data']['regions']['anomalies'][year][month] = {}

        if region not in my_struct['month_data']['regions']['anomalies'][year][month]:
            my_struct['month_data']['regions']['anomalies'][year][month][region] = []

        my_struct['month_data']['regions']['anomalies'][year][month][region].append(value)
'''