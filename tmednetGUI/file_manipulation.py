from datetime import datetime, timedelta
import re
import user_interaction as ui
import pandas as pd
from geojson import Point, Feature, dump
import time
import os
from numpy import diff
import numpy as np
from scipy.ndimage.filters import uniform_filter1d
import json
import user_interaction
from fpdf import FPDF
import pdf_creator


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
    return lat, lon


def load_data(args, consolescreen):
    """
    Method: load_data(args, consolescreen)
    Purpose: read tmednet *.txt data files
    Require:
        args: For the mdata dictionary
        consolescreen: In order to write to the consolescreen
    Version: 05/2021, MJB: Documentation
    """
    try:
        for ifile in args.files[
                     len(args.files) - args.newfiles:]:  # Iterates based on the last entry on args.files to not overwrite
            filein = args.path + ifile

            lat, lon = load_coordinates(int(ifile.split('_')[0]))
            # Extraemos campos del nombre del fichero
            datos = {"timegmt": [], "time": [], "temp": [], "S/N": "", "GMT": "",
                     "depth": int(ifile.split("_")[3].split(".")[0]), "region": int(ifile.split("_")[0]),
                     "latitude": lat, "longitude": lon,
                     "datainici": datetime.strptime(ifile.split("_")[1], '%Y%m%d-%H'),
                     "datafin": datetime.strptime(ifile.split("_")[2], '%Y%m%d-%H'), 'images': []}

            print("file", filein)
            consolescreen.insert("end", "file ")
            consolescreen.insert("end", filein + "\n =============\n")

            f = open(filein, "r")
            a = f.readlines()
            f.close()
            # We clean and separate values that contain "Enregistré"
            a[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), a)
            bad = []
            good = []
            for i in range(len(a)):
                if a[i][3] == "Enregistré" or a[i][3] == "Registrado":
                    bad.append(i)
                else:
                    good.append(a[i])  # Only uses the data without the "Enregistré" string to avoid errors
            # Deprecated nl = len(a) - len(bad) + 1
            # Deprecated datos["timegmt"] = [datetime.strptime(a[i][1] + ' ' + a[i][2], "%d/%m/%y %H:%M:%S") for i in
            #                    range(1, nl)]
            datos["timegmt"] = [datetime.strptime(good[i][1] + ' ' + good[i][2], "%d/%m/%y %H:%M:%S") for i in
                                range(1, len(good))]
            # Deprecated datos["temp"] = [float(a[i][3]) for i in range(1, nl)]
            datos["temp"] = [float(good[i][3]) for i in range(1, len(good))]
            # UPDATE: Changed all a[] to good[]
            igm = '_'.join(good[0]).find("GMT")
            gmtout = '_'.join(good[0])[igm + 3:igm + 6]
            datos['GMT'] = gmtout
            datos['S/N'] = good[0][good[0].index('S/N:') + 1]
            args.mdata.append(datos)
            args.tempdataold.append(datos.copy())
        # check_hour_interval(args.mdata)
        # convert_round_hour(args.mdata)
        args.mdata = sorted(args.mdata, key=lambda k: k['depth'])
        args.tempdataold = sorted(args.tempdataold, key=lambda k: k['depth'])
        check_start(args.mdata, consolescreen)
        interpolate_hours(args.mdata)  # Interpolates the temperature between different not round hours

    except ValueError:
        consolescreen.insert("end", "Error, file extension not supported, load a txt\n", 'warning')
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
        filestart= dat['timegmt'][0].timestamp()
        if titlestart < filestart:
            consolescreen.insert("end", "Error, start date on the title of the file set before the start date of the file in depth " + str(dat['depth']) + "\n", 'warning')
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
                dfinter = dfmerge.drop(columns='0_y')
                sinter = dfinter['0_x'].round(3)
                dat['temp'] = sinter[daterange].values.tolist()
                break


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
    #TODO format the PDF file to make it more "elegant"
    #Creating the same report as a PDF
    pdf = pdf_creator.pdf_starter()
    #Dict to store the PDF metadata
    PDF_DATA = {'Date Data Upload': 0, 'Date data ingestion report': datetime.strftime(datetime.today(), '%Y-%m-%d'),
                'Site': args.mdata[0]['region'], 'Sampling depth (m)': [], 'Sampling interval': '1:00:00',
                'Parameter': 'Seawater Temperature in ºC', 'Recording Start Date': args.mdata[0]["datainici"].isoformat(),
                'Recording End Date': args.mdata[0]["datafin"].isoformat(), 'GMT': args.mdata[0]["GMT"], 'Sensors': [],
                'Data': []}

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
        PDF_DATA['Data'].append(sum(map(lambda x : x != 999, item['temp'])))
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
    pdf.output('test2.pdf', 'F')





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
    with open('../src/output_files/' + str(data['region']) + '_' + data['datainici'].strftime('%Y-%m-%d') + '_' + data['datafin'].strftime('%Y-%m-%d')+'_merged.txt', 'w') as f:
        f.write('#' * (len(data['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16))
        f.write('\n# Site: ' + str(data['region']))
        f.write('\n# Start time: ' + data['datainici'].strftime('%Y-%m-%d, %H:%M:%S'))
        f.write('\n# End time: ' + data['datafin'].strftime('%Y-%m-%d, %H:%M:%S'))
        f.write('\n# Serial Numbers: ' + ''.join(SN) + '\n')
        f.write(('#' * (len(data['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16) + '\n\n\n'))
        df.to_string(f, col_space=10)
    print('txt written')


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
    # Gets the first and last 72h of operation to look for the possible errors.
    # TODO maybe choose if we want to see 24h of operation or 72h depending on the case. Automatically
    time_series = [data['time'][:72], data['time'][-72:]]
    temperatures = [data['temp'][:72], data['temp'][-72:]]
    ftimestamp = [item.timestamp() for item in time_series[1]]
    finaldydx = diff(temperatures[1]) / diff(ftimestamp)
    indexes = np.argwhere(finaldydx > 0.0002) + 1  # Gets the indexes in which the variation is too big (removing)
    # Checks whether if the error values begin before the declarated time of removal or later.
    # If later, the time of removal is the marked time to be removed

    enddate = data["datafin"] - timedelta(hours=int(data["GMT"][1:]))
    startdate = data["datainici"] - timedelta(hours=int(data["GMT"][1:]))
    # If the removal time is way earlier than 72h from the last registered data, a warning is raised
    try:

        if indexes.size != 0:
            if enddate < data['time'][int(indexes[0]) - 72]:
                index = np.argwhere(np.array(time_series[1]) == np.array(enddate))
                indexes = np.array(range(int(index), len(temperatures[0])))
            else:
                indexes = np.array(range(int(indexes[0]), len(temperatures[0])))
            start_index = np.argwhere(np.array(time_series[0]) == np.array(startdate))
            # start_index = np.array(range(int(start_index), len(temperatures[0])))
            return time_series, temperatures, indexes, start_index
    except TypeError:
        consolescreen.insert("end", "WARNING, day of end of operation "
                             + str((data['time'][-1] - enddate).days) + " days earlier than the last recorded data.\n",
                             'warning')
        consolescreen.insert("end", "=============\n")
        indexes = np.array(range(0, len(temperatures[0])))
        start_index = np.argwhere(np.array(time_series[0]) == np.array(startdate))
        # start_index = np.array(range(int(start_index), len(temperatures[0])))
        return time_series, temperatures, indexes, start_index


def temp_difference(data):
    """
    Method: temp_difference(data)
    Purpose: Gets the difference in temperature between levels
    Require:
        data: The mdata dictionary
    Version: 05/2021, MJB: Documentation
    """
    to_utc(data)
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
                               index=df[str(depth) + "-" + str(depths[i])].dropna().index, columns=[str(depth) + "-" + str(depths[i])]).reindex(data[indi]['time'])
        #series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])], size=240),
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
