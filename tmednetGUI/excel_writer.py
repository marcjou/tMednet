import numpy as np
import pandas as pd
import time
from pandas import ExcelWriter
import marineHeatWaves as mhw

def create_mhw(mhwdf):
    del mhwdf['Time']
    mhwdf['Date'] = pd.to_datetime(mhwdf['Date'], format='%d/%m/%Y')
    nufile = mhwdf.groupby('Date').mean()
    dates = [x.date() for x in nufile.index]
    t = [x.toordinal() for x in dates]
    t = np.array(t)
    depths = nufile.columns
    sst5 = nufile[depths[0]].values
    mhws, clim = mhw.detect(t, sst5)
    diff = pd.DataFrame(
        {'Date': mhws['date_start'], 'Depth (m)': depths[0], 'Duration (Days)': mhws['duration'],
         'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
         'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']],
         'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']]})
    for depth in depths:
        if depth == depths[0]:
            pass
        else:
            sst = nufile[depth].values
            mhws, clim = mhw.detect(t, sst)
            dfi = pd.DataFrame(
                {'Date': mhws['date_start'], 'Depth (m)': depth, 'Duration (Days)': mhws['duration'],
                 'Max Intensity (ºC)': [round(num, 2) for num in mhws['intensity_max']],
                 'Cumulative Intensity (ºC day)': [round(num, 2) for num in mhws['intensity_cumulative']],
                 'Mean Intensity (ºC)': [round(num, 2) for num in mhws['intensity_mean']]})
            diff = diff.append(dfi, ignore_index=True)

    return diff


def excel_writer(filein, fileout):
    start = time.time()

    df = pd.read_csv(filein, sep='\t')
    mhwdf = df.copy()
    depths = df.columns.tolist()
    del depths[0]
    del depths[0]


    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')
    df['year'] = df['Date'].dt.year
    df['month'] = df['Date'].dt.month

    dfinter = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])

    dfexcel = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])
    dfmonthly = pd.DataFrame(
                columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                         'Ndays>=26'])
    dfintermonth = pd.DataFrame(
                columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                         'Ndays>=26'])
    dfseasonal = pd.DataFrame(
                columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                         'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])
    dfinterseason = pd.DataFrame(
                columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                         'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])


    for depth in depths:
        # Setting up
        dfinter = pd.DataFrame(columns=['date', 'depth(m)', 'N', 'mean', 'std', 'max', 'min'])
        dfintermonth = pd.DataFrame(
            columns=['year', 'month', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=24', 'Ndays>=25',
                     'Ndays>=26'])
        dfinterseason = pd.DataFrame(
            columns=['year', 'season', 'depth(m)', 'N', 'mean', 'std', 'max', 'min', 'Ndays>=23', 'Ndays>=24',
                     'Ndays>=25', 'Ndays>=26', 'Ndays>=27', 'Ndays>=28'])
        temp = df.groupby('Date')[str(depth)]
        tempmonth = df.groupby(['year', 'month'])[str(depth)]
        tempseason = df.loc[(df['month']>=7) & (df['month']<=9)].groupby(['year'])[str(depth)]
        depto = np.repeat(depth, len(temp)).tolist()
        deptomonth = np.repeat(depth, len(tempmonth)).tolist()
        deptoseason = np.repeat(depth, len(tempseason)).tolist()

        # Daily Calculations
        dfinter['date'] = temp.count().index.tolist()
        dfinter['N'] = temp.count().values
        dfinter['mean'] = temp.mean().values.round(3)
        dfinter['std'] = temp.std().values.round(3)
        dfinter['max'] = temp.max().values.round(3)
        dfinter['min'] = temp.min().values.round(3)
        dfinter['depth(m)'] = depto

        # Monthly Calculations
        dfintermonth['year'] = tempmonth.count().index.get_level_values(0).to_list()
        dfintermonth['month'] = tempmonth.count().index.get_level_values(1).to_list()
        dfintermonth['depth(m)'] = deptomonth
        dfintermonth['N'] = tempmonth.count().values
        dfintermonth['mean'] = tempmonth.mean().values.round(3)
        dfintermonth['std'] = tempmonth.std().values.round(3)
        dfintermonth['min'] = tempmonth.min().values.round(3)
        dfintermonth['max'] = tempmonth.max().values.round(3)
        dfintermonth['Ndays>=24'] = tempmonth.apply(lambda x: x[x >= 24].count()).values
        dfintermonth['Ndays>=25'] = tempmonth.apply(lambda x: x[x >= 25].count()).values
        dfintermonth['Ndays>=26'] = tempmonth.apply(lambda x: x[x >= 26].count()).values

        # Seasonal Calculations
        dfinterseason['year'] = tempseason.count().index.to_list()
        dfinterseason['season'] = np.repeat(3, len(tempseason)).tolist()
        dfinterseason['depth(m)'] = deptoseason
        dfinterseason['N'] = tempseason.count().values
        dfinterseason['mean'] = tempseason.mean().values.round(3)
        dfinterseason['std'] = tempseason.std().values.round(3)
        dfinterseason['min'] = tempseason.min().values.round(3)
        dfinterseason['max'] = tempseason.max().values.round(3)
        dfinterseason['Ndays>=24'] = tempseason.apply(lambda x: x[x >= 24].count()).values
        dfinterseason['Ndays>=25'] = tempseason.apply(lambda x: x[x >= 25].count()).values
        dfinterseason['Ndays>=26'] = tempseason.apply(lambda x: x[x >= 26].count()).values
        dfinterseason['Ndays>=27'] = tempseason.apply(lambda x: x[x >= 27].count()).values
        dfinterseason['Ndays>=28'] = tempseason.apply(lambda x: x[x >= 28].count()).values

        dfexcel = dfexcel.append(dfinter, ignore_index=True)
        dfmonthly = dfmonthly.append(dfintermonth, ignore_index=True)
        dfseasonal = dfseasonal.append(dfinterseason, ignore_index=True)

    dfexcel['depth(m)'] = dfexcel['depth(m)'].astype(int)
    dfmonthly['depth(m)'] = dfmonthly['depth(m)'].astype(int)
    dfexcel = dfexcel.sort_values(by=['date', 'depth(m)'])
    dfmonthly = dfmonthly.sort_values(by=['year', 'month', 'depth(m)'])
    dfseasonal['depth(m)'] = dfseasonal['depth(m)'].astype(int)
    dfseasonal = dfseasonal.sort_values(by=['year', 'depth(m)'])
    dfexcel['date'] = dfexcel['date'].dt.date



    writer = ExcelWriter('../src/output_files/' + fileout + '.xlsx')
    mhwdf = create_mhw(mhwdf)
    dfexcel.to_excel(writer, 'Daily', index=False)
    dfmonthly.to_excel(writer, 'Monthly', index=False)
    dfseasonal.to_excel(writer, 'Seasonal', index=False)
    mhwdf.to_excel(writer, 'MHW', index=False)
    writer.save()


    end = time.time()
    print(end-start)
