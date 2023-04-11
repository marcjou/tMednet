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
import user_interaction as ui
from geojson import Point, Feature, dump
from datetime import datetime, timedelta
from scipy.ndimage.filters import uniform_filter1d
import progressbar as pb


class DataManager:

    def __init__(self, console, reportlogger):
        self.path = ""
        self.files = []
        self.mdata = []
        self.index = []
        self.newfiles = 0
        self.recoverindex = None
        self.recoverindexpos = None
        self.reportlogger = []
        self.tempdataold = []
        self.controlevent = False
        self.console_writer = console
        self.reportlogger = reportlogger
        print('hello')

    def openfile(self, files, textBox, lister):
        """
        Method: openfile(self, files, consolescreen)
        Purpose: Opens the files to be used with the GUI
        Require:
            self: The mdata
            files: The filenames to be opened
            consolescreen: In order to write to the console
        Version: 01/2021, EGL: Documentation
        """

        filesname = []
        self.newfiles = 0
        nf = len(files)
        try:
            if nf > 0:
                self.path = "/".join(files[0].split("/")[:-1]) + "/"
                for ifile in files:
                    _, file_extension = os.path.splitext(ifile)
                    if file_extension != '.txt' and file_extension != '.csv':
                        raise ValueError('Error, file not loadable')
                    filesname.append(ifile.split("/")[-1])

                print(self.path, "files: ", filesname)

                # Escric els fitxers a la pantalla principal
                textBox.insert("end", 'Hem carregat: ' + str(nf) + ' files \n')
                textBox.insert("end", '\n'.join(filesname))
                if lister.size() != 0:  # Checks if the list is empty. If it isn't puts the item at the end of the list
                    n = lister.size()
                    for i in range(len(filesname)):
                        lister.insert(i + n, filesname[i])
                        self.newfiles = self.newfiles + 1
                else:
                    for i in range(len(filesname)):
                        lister.insert(i, filesname[i])
                        self.newfiles = self.newfiles + 1

            return filesname
        except (ValueError, TypeError) as err:
            self.console_writer(repr(err), 'warning')

    def load_data(self):
        """
        Method: load_data(self, consolescreen)
        Purpose: read tmednet *.txt data files
        Require:
            self: For the mdata dictionary
            consolescreen: In order to write to the consolescreen
        Version: 05/2021, MJB: Documentation
        """
        try:
            # Iterates based on the last entry on self.files to not overwrite
            for ifile in self.files[len(self.files) - self.newfiles:]:
                filein = self.path + ifile

                lat, lon, site_name = self.load_coordinates(int(ifile.split('_')[0]))
                # Extraemos campos del nombre del fichero
                datos = {"df": [], "S/N": "", "GMT": "",
                         "depth": int(ifile.split("_")[3].split(".")[0]), "region": int(ifile.split("_")[0]),
                         'region_name': site_name, "latitude": lat, "longitude": lon,
                         "datainici": datetime.strptime(ifile.split("_")[1], '%Y%m%d-%H'),
                         "datafin": datetime.strptime(ifile.split("_")[2], '%Y%m%d-%H'), 'images': []}

                # Loads the data on a dataframe
                df = pd.read_csv(filein, sep='\t', skiprows=1, header=None, index_col=0)
                col = df.columns
                df.drop(col[3:], axis=1, inplace=True)
                df.columns = ['Date', 'Time', 'Temp']
                df.dropna(inplace=True)
                print("file", filein)
                self.console_writer(filein, 'action')

                f = open(filein, "r", encoding='iso-8859-15')
                meta = f.readline()
                meta = re.sub('\t+', ' ', meta.strip()).split(' ')
                f.close()
                df.index = [datetime.strptime(df['Date'][i] + ' ' + df['Time'][i], "%d/%m/%y %H:%M:%S") for i
                            in
                            range(1, len(df) + 1)]
                df.drop(['Date', 'Time'], axis=1, inplace=True)
                datos['df'] = df
                igm = '_'.join(meta).find("GMT")
                gmtout = '_'.join(meta)[igm + 3:igm + 6]
                datos['GMT'] = gmtout
                try:
                    datos['S/N'] = int(re.sub('\D', '', meta[meta.index('S/N:') + 1]))
                except:
                    datos['S/N'] = 'XXXXXXXX'
                self.mdata.append(datos)
                self.tempdataold.append(datos.copy())
            self.mdata = sorted(self.mdata, key=lambda k: k['depth'])
            self.tempdataold = sorted(self.tempdataold, key=lambda k: k['depth'])
            self.to_utc()
            self.check_start()
            self.interpolate_hours()  # Interpolates the temperature between different not round hours

        except ValueError:
            self.console_writer("Error, file extension not supported, load a txt",'warning')

    def load_coordinates(self, region):
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

    def check_start(self):
        """
            Method: check_start(data)
            Purpose: Checks that the start time is correct
            Require:
                data: The mdata
            Version: 11/2021, MJB: Documentation
        """
        for dat in self.mdata:
            titlestart = dat['datainici'].timestamp()
            filestart = dat['df'].index[0].timestamp()
            if titlestart < filestart:
                self.console_writer("Error, start date on the title of the file set before the start date of the "
                                     "file in depth " + str(dat['depth']), 'warning')

    def interpolate_hours(self):
        """
        Method: interpolate_hours(data)
        Purpose: Interpolates the values of temp in case the hours are not round
        Require:
            data: The mdata
        Version: 05/2021, MJB: Documentation
        """
        for dat in self.mdata:
            for i in range(len(dat['df'].index)):
                if dat['df'].index[i].timestamp() % 3600 == 0:  # Check if the difference between timestamps is an hour
                    pass
                else:
                    # If it isn't, interpolates
                    dfraw = dat['df'].copy()
                    daterange = pd.date_range(dat['datainici'], dat['datafin'], freq='H')
                    dfcontrol = pd.DataFrame(np.arange(len(daterange)), index=daterange)
                    dfmerge = dfraw.merge(dfcontrol, how='outer', left_index=True,
                                          right_index=True).interpolate(method='index', limit_direction='both')
                    dfmerge = dfmerge[dfmerge.index.astype('int64') // 10 ** 9 % 3600 == 0]
                    dfinter = dfmerge.drop(columns='0')
                    sinter = dfinter['Temp'].round(3)
                    dat['df'] = sinter
                    break

    def to_utc(self):
        """
        Method: to_utc(data)
        Purpose: Shift temporal axis
        Require:
        Version: 01/2021, EGL: Documentation
        """
        for i in range(len(self.mdata)):
            gmthshift = int(self.mdata[i]["GMT"][1:])
            # Mirar timedelta
            self.mdata[i]['df'].index = [self.mdata[i]['df'].index[n] - timedelta(hours=gmthshift) for n in
                               range(len(self.mdata[i]['df'].index))]
            self.mdata[i]['datainici'] = self.mdata[i]['datainici'] - timedelta(hours=gmthshift)
            self.mdata[i]['datafin'] = self.mdata[i]['datafin'] - timedelta(hours=gmthshift)

    def report(self, textbox):
        """
        Method: report(self)
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
        PDF_DATA = {'Date Data Upload': 0,
                    'Date data ingestion report': datetime.strftime(datetime.today(), '%Y-%m-%d'),
                    'Site code': self.mdata[0]['region'], 'Site name': self.mdata[0]['region_name'],
                    'Sampling depth (m)': [], 'Sampling interval (hh:mm:ss)': '1:00:00',
                    'Parameter': 'Seawater Temperature in ºC',
                    'Recording Start Date': datetime.strftime(self.mdata[0]["df"].index[0], '%Y-%m-%d %H:%M:%S'),
                    'Recording End Date': datetime.strftime(self.mdata[0]["df"].index[-1], '%Y-%m-%d %H:%M:%S'),
                    'Underwater Start Date': datetime.strftime(self.mdata[0]["datainici"], '%Y-%m-%d %H:%M:%S'),
                    'Underwater End Date': datetime.strftime(self.mdata[0]['datafin'], '%Y-%m-%d %H:%M:%S'),
                    'GMT': self.mdata[0]["GMT"], 'Sensors': [],
                    'NData': []}
        # ATTENTION THIS HAS BEEN MODIFIED CHECK
        textbox, PDF_DATA = self.metadata_string_creator(textbox, PDF_DATA)
        textbox.insert("end", "=========\n")
        for text in self.reportlogger:
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
        if self.mdata[0]['images'] != []:
            pdf.titles('Images results')
            pdf.text('Invisible', color='White')
            n = 0
            for images in self.mdata[0]['images']:
                if n == 0:
                    pdf.imagex(images, True)
                    n = 1
                else:
                    pdf.imagex(images)
        pdf.titles('Other info')
        n = 0
        for text in self.reportlogger:
            if n == 0:
                pdf.text(text, afterTitle=True)
            else:
                pdf.text(text)
        pdf.output('test2.pdf', 'F')

    def metadata_string_creator(self, textbox, PDF_DATA):
        for item in self.mdata:
            daysinsitu = (item['datainici'] - item['datafin']).total_seconds() / 86400
            cadena = "=========\n"
            cadena += "Depth: " + str(item["depth"]) + "\n"
            cadena += "Init: " + item["datainici"].isoformat() + "\n"
            cadena += "End: " + item["datafin"].isoformat() + "\n"
            cadena += "Ndays: " + str(daysinsitu) + "\n"
            cadena += "GMT: " + item["GMT"] + "\n"
            cadena += "DInit: " + item["df"].index[0].isoformat() + "\n"
            cadena += "DEnd: " + item["df"].index[-1].isoformat() + "\n"
            textbox.insert("end", cadena)
            PDF_DATA['Sampling depth (m)'].append(item['depth'])
            PDF_DATA['Sensors'].append(item['S/N'])
            PDF_DATA['NData'].append(sum(map(lambda x: x != 999, item['df']['Temp'])))

            return textbox, PDF_DATA

    def zoom_data(self, data):
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
        valid_start = np.where(np.array(data['df']['Temp']) != 999)[0][0]
        valid_end = np.where(np.array(data['df']['Temp']) != 999)[0][-1]
        time_series = [data['df'].index[valid_start:72 + valid_start], data['df'].index[valid_end - 72:valid_end]]
        temperatures = [data['df']['Temp'][valid_start:72 + valid_start], data['df']['Temp'][valid_end - 72:valid_end]]
        if np.argwhere(np.array(time_series[1]) == np.array(enddate)).size == 0:
            time_series[1] = data['df'].index[int(data['df'].index.get_indexer([enddate])) - 72:]
            temperatures[1] = data['df']['Temp'][int(data['df'].index.get_indexer([enddate])) - 72:]

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
            control = time_series[0] == np.array(startdate)
            if np.all(~control):
                idx = int(np.argwhere(data['df'].index == startdate))
                time_series[0] = data['df'].index[int(idx) - 72:int(idx) + 1]
                start_index = np.argwhere(time_series[0] == startdate)
            else:
                start_index = np.argwhere(time_series[0] == startdate)

            if indexes.size != 0:
                if enddate < data['df'].index[int(indexes[0]) - len(temperatures[1])]:
                    index = np.argwhere(time_series[1] == enddate)
                    indexes = np.array(range(int(index), len(temperatures[1])))
                else:
                    indexes = np.array(range(int(indexes[0]), len(temperatures[1])))
                # start_index = np.array(range(int(start_index), len(temperatures[0])))
                return time_series, temperatures, indexes, start_index, valid_start, valid_end
            # start_index = np.array(range(int(start_index), len(temperatures[0])))
            return time_series, temperatures, indexes, start_index, valid_start, valid_end
        except TypeError:
            self.console_writer("WARNING, day of end of operation "
                          + str((data['df'].index[-1] - enddate).days) + " days earlier than the last recorded data.",
                          'warning')
            indexes = np.array(range(0, len(temperatures[0])))
            start_index = np.argwhere(time_series[0] == startdate)
            # start_index = np.array(range(int(start_index), len(temperatures[0])))
            return time_series, temperatures, indexes, start_index, valid_start, valid_end
        
    def zoom_data_loop(self):
        for data in self.mdata:
            # self.tempdataold.append(data['df']['Temp'].copy())
            time_series, temperatures, indexes, start_index, valid_start, valid_end = self.zoom_data(data)
            for i in indexes:
                data['df']['Temp'][int(i) - len(np.array(temperatures[1]))] = 999
            for i in range(0, int(np.argwhere(np.array(data['df'].index) == time_series[0][int(start_index)]))):
                data['df']['Temp'][int(i)] = 999

    def merge(self):
        """
        Method: merge(data)
        Purpose: Merges all of the loaded files into a single one
        Require:
        Version:
        01/2021, EGL: Documentation
        """

        print('merging files')
        # Merges all the available files while making sure that the times match
        df1, depths, SN = self.list_to_df()
        if len(self.mdata) < 2:
            merging = False
        else:
            merging = True
        return df1, depths, SN, merging

    def list_to_df(self):
        """
        Method: list_to_df(data)
        Purpose: Converts the list mdata to a dataframe
        Require:
            data: List mdata
        Version: 05/2021, MJB: Documentation
        """
        df1 = pd.DataFrame(self.mdata[0]['df'].values, index=self.mdata[0]['df'].index, columns=[str(self.mdata[0]['depth'])])
        depths = [self.mdata[0]['depth']]
        SN = [self.mdata[0]['S/N']]
        for dat in self.mdata[1:]:
            dfi = pd.DataFrame(dat['df'].values, index=dat['df'].index, columns=[str(dat['depth'])])
            depths.append(dat['depth'])
            SN.append(dat['S/N'])
            df1 = pd.merge(df1, dfi, how='outer', left_index=True,
                           right_index=True)  # Merges by index which is the date

        masked_df = df1.mask((df1 < -50) | (df1 > 50))
        return masked_df, depths, SN

    def df_to_geojson(self, df, properties, SN):
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

        point = Point((self.mdata[0]['latitude'], self.mdata[0]['longitude']))
        feature = Feature(geometry=point, properties=props)

        output_filename = '../src/output_files/dataset.geojson'
        with open(output_filename, 'w') as output_file:  # Crashes when opened with text editor
            dump(feature, output_file)
        print('geojson written')

        print("--- %s seconds ---" % (time.time() - start_time))

    def df_to_txt(self, df, SN):
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
        output = '../src/output_files/' + str(self.mdata[0]['region']) + '_' + self.mdata[0]['datainici'].strftime('%Y-%m-%d') + '_' + \
                 self.mdata[0][
                     'datafin'].strftime('%Y-%m-%d') + '_merged.txt'
        with open(output, 'w') as f:
            f.write('#' * (len(self.mdata[0]['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16))
            f.write('\n# Site: ' + str(self.mdata[0]['region']))
            f.write('\n# Start time: ' + self.mdata[0]['datainici'].strftime('%Y-%m-%d, %H:%M:%S'))
            f.write('\n# End time: ' + self.mdata[0]['datafin'].strftime('%Y-%m-%d, %H:%M:%S'))
            f.write('\n# Serial Numbers: {}\n'.format(SN))
            f.write(('#' * (len(self.mdata[0]['datainici'].strftime('%Y-%m-%d, %H:%M:%S')) + 16) + '\n\n\n'))
            df.to_string(f, col_space=10)
        print('txt written')
        return output

    def convert_to_netCDF(self, filename, df):
        # TODO print on console when the netCDF has been create
        try:
            xarray.Dataset(df.to_xarray()).to_netcdf('../src/output_files/' + filename + '.nc4')
            self.console_writer("netCDF file created", 'action')
        except Exception as e:
            print(str(e))

    def temp_difference(self):
        """
        Method: temp_difference(data)
        Purpose: Gets the difference in temperature between levels
        Require:
            data: The mdata dictionary
        Version: 05/2021, MJB: Documentation
        """
        # to_utc(data)      Applying it only at the beggining interpolate_hours
        df, depths, _ = self.list_to_df()
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


