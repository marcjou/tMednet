import os
import re
import time
import json
import xarray
import numpy as np
import pdf_creator
import pandas as pd
from numpy import diff
from netCDF4 import Dataset
from geojson import Point, Feature, dump
from datetime import datetime, timedelta
from scipy.ndimage.filters import uniform_filter1d
import progressbar as pb


# TODO REWORK WHOLE CODE TO WORK WITH DATAFRAMES FROM THE START
def load_coordinates(region):
    """
    Method: load_coordinates(region)
    Purpose: Loads the coordinates of the file from the 'metadata.json' auxiliary file
    Require:
        region: The number of the site where the data is taken from
    Version: 05/2021, MJB: Documentation
    """
    with open('../src/metadata.json') as f:
        data = json.load(f)
    lat = float(data['stations'][str(region)]['lat'])
    lon = float(data['stations'][str(region)]['long'])
    name = data['stations'][str(region)]['site_name']
    return lat, lon, name


def load_data(args, consolescreen=False):
    """
    Method: load_data(args, consolescreen)
    Purpose: read tmednet *.txt data files
    Require:
        args: For the mdata dictionary
        consolescreen: In order to write to the consolescreen
    Version: 05/2021, MJB: Documentation
    """
    try:
        # Iterates based on the last entry on args.files to not overwrite
        for ifile in args.files[len(args.files) - args.newfiles:]:
            filein = args.path + ifile

            lat, lon, site_name = load_coordinates(int(ifile.split('_')[0]))
            # Extraemos campos del nombre del fichero
            datos = {"timegmt": [], "time": [], "temp": [], "S/N": "", "GMT": "",
                     "depth": int(ifile.split("_")[3].split(".")[0]), "region": int(ifile.split("_")[0]),
                     'region_name': site_name, "latitude": lat, "longitude": lon,
                     "datainici": datetime.strptime(ifile.split("_")[1], '%Y%m%d-%H'),
                     "datafin": datetime.strptime(ifile.split("_")[2], '%Y%m%d-%H'), 'images': []}

            print("file", filein)
            if not consolescreen:
                print(filein + '\n')
            else:
                consolescreen.insert("end", "file ")
                consolescreen.insert("end", filein + "\n =============\n")

            f = open(filein, "r", encoding='iso-8859-15')
            a = f.readlines()
            f.close()
            # We clean and separate values that contain "Enregistré"
            a[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), a)
            bad = []
            good = []
            for i in range(len(a)):
                if len(a[i]) >= 5:
                    if a[i][4] == "Enregistré" or a[i][4] == "Registrado":
                        bad.append(i)
                    else:
                        good.append(a[i])
                elif len(a[i]) >= 4:
                    if a[i][3] == 'Enregistré' or a[i][3] == 'Registrado':
                        bad.append(i)
                    else:
                        good.append(a[i])
                else:
                    good.append(a[i])  # Only uses the data without the "Enregistré" string to avoid errors
            if len(good[1]) == 4:
                # Check if the format year is in two digits or four (8 digits mean 2 for day, 2 for month 2 for year and 2 slash)
                if len(good[1][1]) == 8:
                    datos["timegmt"] = [datetime.strptime(good[i][1] + ' ' + good[i][2], "%d/%m/%y %H:%M:%S") for i in
                                        range(1, len(good))]
                elif len(good[1][1]) == 10:
                    datos["timegmt"] = [datetime.strptime(good[i][1] + ' ' + good[i][2], "%d/%m/%Y %H:%M:%S") for i in
                                        range(1, len(good))]
                datos["temp"] = [float(good[i][3]) for i in range(1, len(good))]
            else:
                datos["timegmt"] = [datetime.strptime(str(good[i][0]) + ' ' + str(good[i][1]), "%d/%m/%Y %H:%M:%S") for
                                    i in
                                    range(1, len(good))]
                datos["temp"] = [float(good[i][2]) for i in range(1, len(good))]
            igm = '_'.join(good[0]).find("GMT")
            gmtout = '_'.join(good[0])[igm + 3:igm + 6]
            datos['GMT'] = gmtout
            try:
                datos['S/N'] = int(re.sub('\D', '', good[0][good[0].index('S/N:') + 1]))
            except:
                datos['S/N'] = 'XXXXXXXX'
            args.mdata.append(datos)
            args.tempdataold.append(datos.copy())
        args.mdata = sorted(args.mdata, key=lambda k: k['depth'])
        args.tempdataold = sorted(args.tempdataold, key=lambda k: k['depth'])
        check_start(args.mdata, consolescreen)
        interpolate_hours(args.mdata)  # Interpolates the temperature between different not round hours

    except ValueError as e:
        if consolescreen == False:
            print('Error, file extension not suported, load a txt ' + e)
        else:
            consolescreen.insert("end", "Error, file extension not supported, load a txt " + e +"\n", 'warning')
            consolescreen.insert("end", "=============\n")


def check_start(data, consolescreen):
    """
        Method: check_start(data)
        Purpose: Checks that the start time is correct
        Require:
            data: The mdata
        Version: 11/2021, MJB: Documentation
    """
    for dat in data:
        titlestart = dat['datainici'].timestamp()
        filestart = dat['timegmt'][0].timestamp()
        if titlestart < filestart:
            consolescreen.insert("end", "Error, start date on the title of the file set before the start date of the "
                                        "file in depth " + str(dat['depth']) + "\n", 'warning')
            consolescreen.insert("end", "=============\n")


def interpolate_hours(data):
    """
    Method: interpolate_hours(data)
    Purpose: Interpolates the values of temp in case the hours are not round
    Require:
        data: The mdata
    Version: 05/2021, MJB: Documentation
    """
    to_utc(data)
    for dat in data:
        for i in range(len(dat['time'])):
            if dat['time'][i].timestamp() % 3600 == 0:  # Check if the difference between timestamps is an hour
                pass
            else:
                # If it isn't, interpolates
                dfraw = pd.DataFrame(dat['temp'], index=dat['time'])
                daterange = pd.date_range(dat['datainici'], dat['datafin'], freq='H')
                dfcontrol = pd.DataFrame(np.arange(len(daterange)), index=daterange)
                dfmerge = dfraw.merge(dfcontrol, how='outer', left_index=True,
                                      right_index=True).interpolate(method='index', limit_direction='both')
                dfmerge = dfmerge[dfmerge.index.astype('int64') // 10 ** 9 % 3600 == 0]
                dfinter = dfmerge.drop(columns='0_y')
                sinter = dfinter['0_x'].round(3)
                dat['temp'] = sinter[daterange].values.tolist()
                dat['time'] = daterange.to_pydatetime().tolist()
                break

# TODO DEPRECATED
def convert_round_hour(data):
    """
    Method: convert_round_hour(data)
    Purpose: Currently deprecated
    Require:
    Version: 05/2021, MJB: Documentation
    """
    # If there is a time desviation from the usual round hours, it corrects it
    for dat in data:
        for i in range(len(dat['timegmt'])):
            if dat['timegmt'][i].timestamp() % 3600 == 0:
                pass
            else:
                # Round the hour
                dt_start_of_hour = dat['timegmt'][i].replace(minute=0, second=0, microsecond=0)
                dt_half_hour = dat['timegmt'][i].replace(minute=30, second=0, microsecond=0)

                if dat['timegmt'][i] >= dt_half_hour:
                    # round up
                    dat['timegmt'][i] = dt_start_of_hour + timedelta(hours=1)
                else:
                    # round down
                    dat['timegmt'][i] = dt_start_of_hour

# TODO DEPRECATED
def check_hour_interval(data):
    """
    Method: check_hour_interval(data)
    Purpose: Currently deprecated
    Require:
    Version: 05/2021, MJB: Documentation
    """
    to_utc(data)
    df, depths, _ = list_to_df(data)
    for dat in data:
        for i in range(len(dat['timegmt'])):
            if i + 1 == len(dat['timegmt']):
                break
            # Ancillary code
            if (dat['timegmt'][i + 1] - dat['timegmt'][i]).seconds > 3600:
                print("Difference of an hour in depth " + str(dat['depth']) + " line" + str(i))
        print("Finished depth" + str(dat['depth']))


def report(args, textbox):
    """
    Method: report(args)
    Purpose: List main file characteristics
    Require:
        textBox: text object
    Version: 01/2021, EGL: Documentation
    """
    textbox.delete(1.0, "end")
    # TODO format the PDF file to make it more "elegant"
    # Creating the same report as a PDF
    pdf = pdf_creator.pdf_starter()
    # Dict to store the PDF metadata
    PDF_DATA = {'Date Data Upload': 0, 'Date data ingestion report': datetime.strftime(datetime.today(), '%Y-%m-%d'),
                'Site code': args.mdata[0]['region'], 'Site name': args.mdata[0]['region_name'],
                'Sampling depth (m)': [], 'Sampling interval (hh:mm:ss)': '1:00:00',
                'Parameter': 'Seawater Temperature in ºC',
                'Recording Start Date': datetime.strftime(args.mdata[0]["timegmt"][0], '%Y-%m-%d %H:%M:%S'),
                'Recording End Date': datetime.strftime(args.mdata[0]["timegmt"][-1], '%Y-%m-%d %H:%M:%S'),
                'Underwater Start Date': datetime.strftime(args.mdata[0]["datainici"], '%Y-%m-%d %H:%M:%S'),
                'Underwater End Date': datetime.strftime(args.mdata[0]['datafin'], '%Y-%m-%d %H:%M:%S'),
                'GMT': args.mdata[0]["GMT"], 'Sensors': [],
                'NData': []}
    # ATTENTION THIS HAS BEEN MODIFIED CHECK
    textbox, args, PDF_DATA = metadata_string_creator()
    textbox.insert("end", "=========\n")
    for text in args.reportlogger:
        textbox.insert("end", text + "\n")
        textbox.insert("end", "=========\n")
    with open('../src/output_files/report.txt', 'w') as fr:
        text = textbox.get('1.0', 'end').splitlines()
        for line in text:
            fr.write(line + "\n")
    n = 0
    pdf.titles('Metadata')
    for key in PDF_DATA:
        if n == 0:
            pdf.text(key + ': ' + str(PDF_DATA[key]) + '\n', True)
            n = 1
        else:
            pdf.text(key + ': ' + str(PDF_DATA[key]) + '\n')
    if args.mdata[0]['images'] != []:
        pdf.titles('Images results')
        pdf.text('Invisible', color='White')
        n = 0
        for images in args.mdata[0]['images']:
            if n == 0:
                pdf.imagex(images, True)
                n = 1
            else:
                pdf.imagex(images)
    pdf.titles('Other info')
    n = 0
    for text in args.reportlogger:
        if n == 0:
            pdf.text(text, afterTitle=True)
        else:
            pdf.text(text)
    pdf.output('test2.pdf', 'F')


def metadata_string_creator(textbox, args, PDF_DATA):
    for item in args.mdata:
        daysinsitu = (item['datainici'] - item['datafin']).total_seconds() / 86400
        cadena = "=========\n"
        cadena += "Depth: " + str(item["depth"]) + "\n"
        cadena += "Init: " + item["datainici"].isoformat() + "\n"
        cadena += "End: " + item["datafin"].isoformat() + "\n"
        cadena += "Ndays: " + str(daysinsitu) + "\n"
        cadena += "GMT: " + item["GMT"] + "\n"
        cadena += "DInit: " + item["timegmt"][0].isoformat() + "\n"
        cadena += "DEnd: " + item["timegmt"][-1].isoformat() + "\n"
        textbox.insert("end", cadena)
        PDF_DATA['Sampling depth (m)'].append(item['depth'])
        PDF_DATA['Sensors'].append(item['S/N'])
        PDF_DATA['NData'].append(sum(map(lambda x: x != 999, item['temp'])))

        return textbox, args, PDF_DATA


def openfile(args, files, consolescreen):
    """
    Method: openfile(args, files, consolescreen)
    Purpose: Opens the files to be used with the GUI
    Require:
        args: The mdata
        files: The filenames to be opened
        consolescreen: In order to write to the console
    Version: 01/2021, EGL: Documentation
    """

    filesname = []
    args.newfiles = 0
    nf = len(files)
    try:
        if nf > 0:
            path = "/".join(files[0].split("/")[:-1]) + "/"
            for ifile in files:
                _, file_extension = os.path.splitext(ifile)
                if file_extension != '.txt' and file_extension != '.csv':
                    raise ValueError('Error, file not loadable')
                filesname.append(ifile.split("/")[-1])
                # consolescreen.insert("end", "files: " + ifile + "\n") # Redundant
            print(path, "files: ", filesname)

            # Escric els fitxers a la pantalla principal
            args.textBox.insert("end", 'Hem carregat: ' + str(nf) + ' files \n')
            args.textBox.insert("end", '\n'.join(filesname))
            if args.list.size() != 0:  # Checks if the list is empty. If it isn't puts the item at the end of the list
                n = args.list.size()
                for i in range(len(filesname)):
                    args.list.insert(i + n, filesname[i])
                    args.newfiles = args.newfiles + 1
            else:
                for i in range(len(filesname)):
                    args.list.insert(i, filesname[i])
                    args.newfiles = args.newfiles + 1

        return filesname, path
    except (ValueError, TypeError) as err:
        consolescreen.insert("end", repr(err) + "\n", 'warning')
        consolescreen.insert("end", "=============\n")


def to_utc(data):
    """
    Method: to_utc(data)
    Purpose: Shift temporal axis
    Require:
    Version: 01/2021, EGL: Documentation
    """
    for i in range(len(data)):
        gmthshift = int(data[i]["GMT"][1:])
        # Mirar timedelta
        data[i]["time"] = [data[i]["timegmt"][n] - timedelta(hours=gmthshift) for n in
                           range(len(data[i]["timegmt"]))]
        data[i]['datainici'] = data[i]['datainici'] - timedelta(hours=gmthshift)
        data[i]['datafin'] = data[i]['datafin'] - timedelta(hours=gmthshift)
        print(data[i]["time"][10], data[i]["timegmt"][10])


def merge(args):
    """
    Method: merge(data)
    Purpose: Merges all of the loaded files into a single one
    Require:
    Version:
    01/2021, EGL: Documentation
    """

    print('merging files')
    # Merges all the available files while making sure that the times match
    df1, depths, SN = list_to_df(args.mdata)
    if len(args.mdata) < 2:
        merging = False
    else:
        merging = True
    return df1, depths, SN, merging


def list_to_df(data):
    """
    Method: list_to_df(data)
    Purpose: Converts the list mdata to a dataframe
    Require:
        data: List mdata
    Version: 05/2021, MJB: Documentation
    """
    df1 = pd.DataFrame(data[0]['temp'], index=data[0]['time'], columns=[str(data[0]['depth'])])
    depths = [data[0]['depth']]
    SN = [data[0]['S/N']]
    for dat in data[1:]:
        dfi = pd.DataFrame(dat['temp'], index=dat['time'], columns=[str(dat['depth'])])
        depths.append(dat['depth'])
        SN.append(dat['S/N'])
        df1 = pd.merge(df1, dfi, how='outer', left_index=True, right_index=True)  # Merges by index which is the date

    masked_df = df1.mask((df1 < -50) | (df1 > 50))
    return masked_df, depths, SN


def historic_to_df(historic, year, start_month='05', end_month='12'):
    start_time = year + '-' + start_month + '-01 00:00:00'
    if end_month == '01':
        end_time = str(int(year) + 1) + '-' + end_month + '-01 00:00:00'
    else:
        end_time = year + '-' + end_month + '-01 00:00:00'

    df = pd.read_csv(historic, sep='\t')
    print('Historic to df:\n')
    progress_bar = pb.progressBar(len(df['Date']), prefix='Progress:', suffix='Complete', length=50)
    df['added'] = df['Date'] + ' ' + df['Time']
    for i in range(0, len(df['Date'])):
        if str(df['added'][i]) == 'nan':
            pass
        else:
            try:
                df.at[i, 'added'] = datetime.strftime(datetime.strptime(str(df['added'][i]), '%d/%m/%Y %H:%M:%S'),
                                                      '%Y-%m-%d %H:%M:%S')
            except ValueError:
                splt = df['added'][i].split(':')
                splt[-1] = '00'
                jn = ':'.join(splt)
                df.at[i, 'added'] = datetime.strftime(datetime.strptime(str(jn), '%d/%m/%Y %H:%M:%S'),
                                                      '%Y-%m-%d %H:%M:%S')

        progress_bar.print_progress_bar(i)
    df.set_index('added', inplace=True)
    df.index.name = None
    del df['Date']
    del df['Time']
    if start_time not in df.index:
        n = [datetime.strptime(str(i), '%Y-%m-%d %H:%M:%S') for i in df.index if str(i) != 'nan']
        # Makes sure to only browse the values that are after the desired month
        nn = [x for x in n if x >= datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')]
        start_time = datetime.strftime(
            min(nn, key=lambda x: abs(x - datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'))), '%Y-%m-%d %H:%M:%S')
    if end_time not in df.index:
        n = [datetime.strptime(str(i), '%Y-%m-%d %H:%M:%S') for i in df.index if str(i) != 'nan']
        end_time = datetime.strftime(min(n, key=lambda x: abs(x - datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'))),
                                     '%Y-%m-%d %H:%M:%S')
        filtered_df = df[start_time: end_time]
    else:
        filtered_df = df[start_time: end_time]
    if filtered_df.columns[0] == '5':
        filtered_df.insert(0, '0', filtered_df['5'], allow_duplicates=True)
        # TODO check this histmax assumption, if the planet goes heating it may be deprecated
    '''
    if np.nanmax(df.values) > 30:
        histmax = 30
    else:
        histmax = np.nanmax(df.values)
    '''
    # TODO add this line of code to the creation of the historical merge
    # Merges the rows that have the same index
    filtered_df = filtered_df.groupby(level=0).mean()
    # Gets the historic min and max values only for the months from May through November
    dfcopy = df.copy()
    dfcopy.index = pd.to_datetime(dfcopy.index)
    dfcopy = dfcopy.loc[(dfcopy.index.month >= 5) & (dfcopy.index.month < 12)]
    histmin = round(np.nanmin(dfcopy.quantile(0.01))) - 1
    histmax = round(np.nanmax(dfcopy.quantile(0.99))) + 1
    # limit_area='inside' parameter makes that only NaN values inside valid values will be filled
    # Checks if it has been called by stratification or annual to decide wether interpolate between columns or not
    # Does not interpolate if there is a gap bigger than 1 days (24h)
    if start_month == '01':
        filtered_df.index = pd.to_datetime(filtered_df.index)
        final_df = filtered_df.interpolate(method='time', axis=0, limit_area='inside', limit=24,
                                           limit_direction='forward')
    elif start_month == '05':
        # Deletes the depths that are all null
        depths = filtered_df.columns
        for depth in depths:
            if filtered_df[depth].isnull().all():
                del filtered_df[depth]
        depths = filtered_df.columns
        int_depths = [eval(i) for i in depths]
        depth_diff = [t - s for s, t in zip(int_depths, int_depths[1:])]
        for i in range(0, len(depth_diff)):
            if depth_diff[i] > 13:
                filtered_df.insert(filtered_df.columns.get_loc(depths[i + 1]) + 1, str(int(depths[i + 1]) + 2.5),
                                   filtered_df[depths[i + 1]])
                filtered_df.insert(filtered_df.columns.get_loc(depths[i + 1]), str(int(depths[i + 1]) - 2.5),
                                   filtered_df[depths[i + 1]])
        '''
        bad_depths = []
        for i in range(0,len(depths)):
            if i != len(depths) - 1:
                if filtered_df[depths[i + 1]].isnull().all() == True and filtered_df[depths[i]].isnull().all() == False:
                    filtered_df.insert(filtered_df.columns.get_loc(depths[i]) + 1, str(int(depths[i]) + 2.5), filtered_df[depths[i]])
                    bad_depths.append(depths[i + 1])
            if i>0:
                if filtered_df[depths[i - 1]].isnull().all() == True and filtered_df[depths[i]].isnull().all() == False:
                    filtered_df.insert(filtered_df.columns.get_loc(depths[i]), str(int(depths[i]) - 2.5),
                                                                               filtered_df[depths[i]])
                    bad_depths.append(depths[i - 1])
        for depth in bad_depths:
            if depth in filtered_df.columns:
                del filtered_df[depth]
        '''
        final_df = filtered_df.interpolate(axis=1, limit_area='inside')

    minyear = pd.to_datetime(df.index).year.min()
    return final_df, histmin, histmax, minyear


def check_for_interpolation(df):
    """
    Method: check_for_interpolation(df)
    Purpose: Checks for data gaps in order to interpolate them
    Requires:
        df: The Dataframe to be read
        data: List mdata
        SN: The serial number list
    Version: 05/2021, MJB: Documentation
    """
    # Not necessary???


def df_to_txt(df, data, SN):
    """
    Method: df_to_txt(df, data, SN)
    Purpose: Writes a txt with the Dataframe values
    Requires:
        df: The Dataframe to be read
        data: List mdata
        SN: The serial number list
    Version: 05/2021, MJB: Documentation
    """
    print('writing txt')
    output = '../src/output_files/' + str(data['region']) + '_' + data['datainici'].strftime('%Y-%m-%d') + '_' + data[
        'datafin'].strftime('%Y-%m-%d') + '_merged.txt'
    with open(output, 'w') as f:
        f.write('#' * (len(data['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16))
        f.write('\n# Site: ' + str(data['region']))
        f.write('\n# Start time: ' + data['datainici'].strftime('%Y-%m-%d, %H:%M:%S'))
        f.write('\n# End time: ' + data['datafin'].strftime('%Y-%m-%d, %H:%M:%S'))
        f.write('\n# Serial Numbers: ' + '.join(SN)' + '\n')
        f.write(('#' * (len(data['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16) + '\n\n\n'))
        df.to_string(f, col_space=10)
    print('txt written')
    return output


def df_to_geojson(df, properties, SN, lat, lon):
    """
    Method: df_to_geojson(df, properties, SN, lat, lon)
    Purpose: Iterates through the DF in order to create the properties for the Geojson file
    Require:
        df: The Dataframe to be read
        properties: The properties of the geojson
        SN: List of serial numbers
        lat: The latitude coordinate
        lon: The longitude coordinate
    Version: 05/2021, MJB: Documentation
    """
    start_time = time.time()
    df = df.fillna(999)
    print('writing geojson')
    props = {'depth': [], 'SN': SN, 'time': df.index.map(str).to_list(), 'temp': []}
    for prop in properties:
        props['depth'].append(prop)
        temp = []
        for _, row in df.iterrows():
            temp.append(row[str(prop)])
        props['temp'].append(temp)

    point = Point((lat, lon))
    feature = Feature(geometry=point, properties=props)

    output_filename = '../src/output_files/dataset.geojson'
    with open(output_filename, 'w') as output_file:  # Crashes when opened with text editor
        dump(feature, output_file)
    print('geojson written')

    print("--- %s seconds ---" % (time.time() - start_time))


def zoom_data(data, consolescreen):
    """
    Method: zoom_data(data)
    Purpose: Gets the first and last day of operation data
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """

    enddate = data["datafin"]  # - timedelta(hours=int(data["GMT"][1:])) converted to utc in new to_utc method
    startdate = data["datainici"]  # - timedelta(hours=int(data["GMT"][1:]))

    # Gets the first and last 72h of operation to look for the possible errors.
    # TODO maybe choose if we want to see 24h of operation or 72h depending on the case. Automatically
    valid_start = np.where(np.array(data['temp']) != 999)[0][0]
    valid_end = np.where(np.array(data['temp']) != 999)[0][-1]
    time_series = [data['time'][valid_start:72 + valid_start], data['time'][valid_end-72:valid_end]]
    temperatures = [data['temp'][valid_start:72 + valid_start], data['temp'][valid_end-72:valid_end]]
    if np.argwhere(np.array(time_series[1]) == np.array(enddate)).size == 0:
        time_series[1] = data['time'][data['time'].index(enddate) - 72:]
        temperatures[1] = data['temp'][data['time'].index(enddate) - 72:]

    ftimestamp = [item.timestamp() for item in time_series[1]]
    finaldydx = diff(temperatures[1]) / diff(ftimestamp)
    indexes = np.argwhere(finaldydx > 0.0006) + 1  # Gets the indexes in which the variation is too big (removing)
    # Checks whether if the error values begin before the declarated time of removal or later.
    # If later, the time of removal is the marked time to be removed

    # Checks if the declared date is earlier than the real date, if so, uses the real date as start date
    # Old chunk and (time_series[0][0] - startdate).total_seconds() < 7200
    if (time_series[0][0] - startdate).total_seconds() > 0:
        startdate = time_series[0][0]
    # If the removal time is way earlier than 72h from the last registered data, a warning is raised
    try:
        control = np.array(time_series[0]) == np.array(startdate)
        if np.all(~control):
            idx = np.argwhere(np.array(data['time']) == np.array(startdate))
            time_series[0] = data['time'][int(idx) - 72:int(idx) + 1]
            start_index = np.argwhere(np.array(time_series[0]) == np.array(startdate))
        else:
            start_index = np.argwhere(np.array(time_series[0]) == np.array(startdate))

        if indexes.size != 0:
            if enddate < data['time'][int(indexes[0]) - len(temperatures[1])]:
                index = np.argwhere(np.array(time_series[1]) == np.array(enddate))
                indexes = np.array(range(int(index), len(temperatures[1])))
            else:
                indexes = np.array(range(int(indexes[0]), len(temperatures[1])))
            # start_index = np.array(range(int(start_index), len(temperatures[0])))
            return time_series, temperatures, indexes, start_index, valid_start, valid_end
        # start_index = np.array(range(int(start_index), len(temperatures[0])))
        return time_series, temperatures, indexes, start_index, valid_start, valid_end
    except TypeError:
        consolescreen("WARNING, day of end of operation "
                      + str((data['time'][-1] - enddate).days) + " days earlier than the last recorded data.",
                      'warning')
        indexes = np.array(range(0, len(temperatures[0])))
        start_index = np.argwhere(np.array(time_series[0]) == np.array(startdate))
        # start_index = np.array(range(int(start_index), len(temperatures[0])))
        return time_series, temperatures, indexes, start_index, valid_start, valid_end


def temp_difference(data):
    """
    Method: temp_difference(data)
    Purpose: Gets the difference in temperature between levels
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """
    # to_utc(data)      Applying it only at the beggining interpolate_hours
    df, depths, _ = list_to_df(data)
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

    return dfdelta, depths


def apply_uniform_filter(data):
    """
    Method: apply_uniform_filter(data)
    Purpose: Applies the 10 running day filter to the data
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """
    df, depths = temp_difference(data)
    i = 1
    longest = 0
    indi = 0  # Checks the longest time series of all to use it as the base for the plots
    for u in range(0, len(data)):
        if len(data[u]['time']) > longest:
            longest = len(data[u]['time'])
            indi = u
    for depth in depths[:-1]:
        series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])].dropna(), size=240),
                               index=df[str(depth) + "-" + str(depths[i])].dropna().index,
                               columns=[str(depth) + "-" + str(depths[i])]).reindex(data[indi]['time'])
        # series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])], size=240),
        #                       index=data[indi]['time'], columns=[str(depth) + "-" + str(depths[i])])
        i += 1
        if 'dfdelta' in locals():
            dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
        else:
            dfdelta = pd.DataFrame(series1)

    return dfdelta


def running_average(data, running=240):
    """
    Method: apply_uniform_filter(data)
    Purpose: Applies the 10 running day filter to the data
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """
    df, depths, _ = list_to_df(data)
    i = 1
    longest = 0
    indi = 0  # Checks the longest time series of all to use it as the base for the plots
    for u in range(0, len(data)):
        if len(data[u]['time']) > longest:
            longest = len(data[u]['time'])
            indi = u
    for depth in depths:
        # Cambiado entre otros index del data al dropna
        series1 = pd.DataFrame(uniform_filter1d(df[str(depth)].dropna(), size=running),
                               index=df[str(depth)].dropna().index, columns=[str(depth)]).reindex(data[indi]['time'])
        i += 1
        if 'dfdelta' in locals():
            dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
        else:
            dfdelta = pd.DataFrame(series1)

    return dfdelta


def running_average_special(year_df, running=240):
    """
    Method: running_average_special(data)
    Purpose: Applies the 10 running day filter to the data
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """
    i = 1
    longest = 0
    indi = len(year_df)
    depths = list(year_df.columns)
    arr = []
    df_empty = pd.DataFrame({str(depths[0]): []})
    for depth in depths:
        # TODO se ha realizado un pequeño cambio aquí revisar si es incompatible con lo anteriormente creado
        '''
        first_nonnan = year_df[depth].first_valid_index()
        # TODO si hay un hueco muy grande en la serie deberia ignorar ese hueco y no hacer el filtro en el y retomar la serie más adelante
        if first_nonnan:
            empty = np.empty(year_df.index.get_loc(first_nonnan))
            empty.fill(np.nan)
            incomplete = uniform_filter1d(year_df[str(depth)].dropna(), size=running)
            arr.append(np.insert(incomplete,0,empty))
        else:
            nonna_df = year_df[str(depth)].dropna()
            nan_df = year_df[year_df[str(depth)].isnull()]
            complete = uniform_filter1d(nonna_df, size=running)
            complete_df = pd.DataFrame(complete, columns=[str(depth)], index=nonna_df.index)
            complete_df = pd.concat([complete_df, nan_df[str(depth)]], sort=False).sort_index()
            arr.append(complete)
            '''
        nonna_df = year_df[str(depth)].dropna()
        nonna_df.index = pd.to_datetime(nonna_df.index)
        time_diff = nonna_df.index[1:] - nonna_df.index[:-1]
        day_diff = time_diff.components.days * 24
        hour_diff = time_diff.components.days
        total_time_diff = day_diff + hour_diff
        index_shifts = total_time_diff.loc[total_time_diff > running].index
        nan_df = year_df[year_df[str(depth)].isnull()]
        nan_df.index = pd.to_datetime(nan_df.index)
        if len(index_shifts) > 0:
            complete = np.empty(0)
            old_index = 0
            for i in index_shifts:
                complete = np.append(complete, uniform_filter1d(nonna_df[old_index:i], size=running))
                old_index = i
            complete = np.append(complete, uniform_filter1d(nonna_df[old_index:], size=running))
        else:
            complete = uniform_filter1d(nonna_df, size=running)
        # nonna_df.index = nonna_df.index.strftime('%Y-%m-%d %H:%M:%S')
        complete_df = pd.DataFrame(complete, columns=[str(depth)], index=nonna_df.index)
        complete_df = pd.concat([complete_df, nan_df[str(depth)]], sort=False).sort_index()
        df_empty[str(depth)] = complete_df[str(depth)]
    # maxlen = max(len(i) for i in arr)

    dfdelta = df_empty.copy()

    '''
    for i in range(0, len(arr)):
        if len(arr[i]) < maxlen:
            remainder = [np.NaN] * (maxlen - len(arr[i]))
            arr[i] = np.concatenate((arr[i], remainder))
    if maxlen < len(year_df):
        remainder = [np.NaN] * (len(year_df) - maxlen)
        for i in range(0, len(arr)):
            arr[i] = np.concatenate((arr[i], remainder))
    dfdelta = pd.DataFrame(np.column_stack(arr), columns=depths, index=year_df.index)
    
    for depth in depths:
        # Cambiado entre otros index del data al dropna
        series1 = pd.DataFrame(uniform_filter1d(year_df[str(depth)].dropna(), size=running),
                               index=year_df[str(depth)].dropna().index, columns=[str(depth)]).reindex(year_df.index)
        i += 1
        if 'dfdelta' in locals():
            dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
        else:
            dfdelta = pd.DataFrame(series1)
    '''

    return dfdelta


def convert_to_netCDF(filename, df, consolescreen):
    # TODO print on console when the netCDF has been create
    try:
        xarray.Dataset(df.to_xarray()).to_netcdf('../src/output_files/' + filename + '.nc4')
        consolescreen.insert("end", "netCDF file created \n")
        consolescreen.insert("end", "=============\n")
    except Exception as e:
        print(str(e))
