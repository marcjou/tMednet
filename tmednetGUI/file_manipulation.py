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


def load_data(args, consolescreen):
    """
    Method: load_data(args)
    Purpose: read tmednet *.txt data files
    Require:
    Version: 01/2021, EGL: Documentation
    """
    try:
        for ifile in args.files[
                     len(args.files) - args.newfiles:]:  # Iterates based on the last entry on args.files to not overwrite
            filein = args.path + ifile

            # Extraemos campos del nombre del fichero
            datos = {"timegmt": [], "time": [], "temp": [], "S/N": "", "GMT": "",
                     "depth": int(ifile.split("_")[3].split(".")[0]), "region": int(ifile.split("_")[0]),
                     "datainici": datetime.strptime(ifile.split("_")[1], '%Y%m%d-%H'),
                     "datafin": datetime.strptime(ifile.split("_")[2], '%Y%m%d-%H')}

            print("file", filein)
            consolescreen.insert("end", "file ")
            consolescreen.insert("end", filein + "\n =============\n")

            f = open(filein, "r")
            a = f.readlines()
            f.close()
            # We clean and separate values that contain "Enregistré"
            a[:] = map(lambda item: re.sub('\t+', ' ', item.strip()).split(' '), a)
            bad = []
            for i in range(len(a)):
                if a[i][-1] == "Enregistré":
                    bad.append(i)
            nl = len(a) - len(bad) + 1
            datos["timegmt"] = [datetime.strptime(a[i][1] + ' ' + a[i][2], "%d/%m/%y %H:%M:%S") for i in
                                range(1, nl)]
            datos["temp"] = [float(a[i][3]) for i in range(1, nl)]
            igm = '_'.join(a[0]).find("GMT")
            gmtout = '_'.join(a[0])[igm + 3:igm + 6]
            datos['GMT'] = gmtout
            datos['S/N'] = a[0][a[0].index('S/N:') + 1]
            args.mdata.append(datos)
        check_hour_interval(args.mdata)
    except ValueError:
        consolescreen.insert("end", "Error, file extension not supported, load a txt\n", 'warning')
        consolescreen.insert("end", "=============\n")


def check_hour_interval(data):
    for dat in data:
        for i in range(len(dat['timegmt'])):
            if i + 1 == len(dat['timegmt']):
                break
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

    textbox.insert("end", "=========\n")


def openfile(args, files, consolescreen):
    """
    Method: onOpen(self)
    Purpose: Launches the askopen widget to set data filenames
    Require:
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
                if file_extension != '.txt':
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


def to_utc(args):
    """
    Method: to_utc(self)
    Purpose: Shift temporal axis
    Require:
    Version: 01/2021, EGL: Documentation
    """
    for i in range(len(args.mdata)):
        gmthshift = int(args.mdata[i]["GMT"][1:])
        # Mirar timedelta
        args.mdata[i]["time"] = [args.mdata[i]["timegmt"][n] - timedelta(hours=gmthshift) for n in
                                 range(len(args.mdata[i]["timegmt"]))]
        print(args.mdata[i]["time"][10], args.mdata[i]["timegmt"][10])


def merge(args):
    """
            Method: merge(self)
            Purpose: Merges all of the loaded files into a single one
            Require:
            Version:
            01/2021, EGL: Documentation
    """

    print('merging files')
    # Merges all the available files while making sure that the times match
    df1, depths, SN = list_to_df(args)
    if len(args.mdata) < 2:
        merging = False
    else:
        merging = True
    return df1, depths, SN, merging


def list_to_df(args):
    df1 = pd.DataFrame(args.mdata[0]['temp'], index=args.mdata[0]['time'], columns=[str(args.mdata[0]['depth']) +
                                                                                    'm temp'])
    depths = [args.mdata[0]['depth']]
    SN = [args.mdata[0]['S/N']]
    for data in args.mdata[1:]:
        dfi = pd.DataFrame(data['temp'], index=data['time'], columns=[str(data['depth']) + 'm temp'])
        depths.append(data['depth'])
        SN.append(data['S/N'])
        df1 = pd.merge(df1, dfi, how='outer', left_index=True, right_index=True)  # Merges by index which is the date

    masked_df = df1.mask((df1 < -50) | (df1 > 50))
    return masked_df, depths, SN


def df_to_txt(df):
    print('writing txt')  # TODO Create progress bar
    with open('out.txt', 'w') as f:
        df.to_string(f, col_space=10)
    print('txt written')


def df_to_geojson(df, properties, SN, lat,
                  lon):  # Iterates through the DF in order to create the properties for the Geojson file
    start_time = time.time()
    df = df.fillna(999)
    print('writing geojson')
    props = {'depth': [], 'SN': SN, 'time': df.index.map(str).to_list(), 'temp': []}
    for prop in properties:
        props['depth'].append(prop)
        temp = []
        for _, row in df.iterrows():
            temp.append(row[str(prop) + 'm temp'])
        props['temp'].append(temp)

    point = Point((lat, lon))
    feature = Feature(geometry=point, properties=props)

    output_filename = '../src/output_files/dataset.geojson'
    with open(output_filename, 'w') as output_file:  # Crashes when opened with text editor
        dump(feature, output_file)
    print('geojson written')

    print("--- %s seconds ---" % (time.time() - start_time))


def zoom_data(data):
    # Gets the first and last day of operation to look for the possible errors.
    # TODO Possibility of making it more than a day
    time_series = [data['timegmt'][:24], data['timegmt'][-24:]]
    temperatures = [data['temp'][:24], data['temp'][-24:]]
    ftimestamp = [item.timestamp() for item in time_series[1]]
    finaldydx = diff(temperatures[1]) / diff(ftimestamp)
    indexes = np.argwhere(finaldydx > 0.0002) + 1  # Gets the indexes in which the variation is too big (removing)
    indexes = np.array(range(int(indexes[0]), len(temperatures[0])))
    return time_series, temperatures, indexes


def temp_difference(data):
    to_utc(data)
    df, depths, _ = list_to_df(data)
    i = 1
    for depth in depths[:-1]:
        series1 = df[str(depth) + 'm temp'] - df[
            str(depths[i]) + 'm temp']  # If fails, raises Key error (depth doesn't exist)
        series1 = series1.rename(str(depth) + "-" + str(depths[i]))
        i += 1
        if 'dfdelta' in locals():
            dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
        else:
            dfdelta = pd.DataFrame(series1)

    return dfdelta, depths


def apply_uniform_filter(data):
    df, depths = temp_difference(data)
    i = 1
    for depth in depths[:-1]:
        series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])], size=240),
                               index=data.mdata[0]['time'], columns=[str(depth) + "-" + str(depths[i])])
        i += 1
        if 'dfdelta' in locals():
            dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
        else:
            dfdelta = pd.DataFrame(series1)

    return dfdelta
