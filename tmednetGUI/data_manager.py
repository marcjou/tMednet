import os
import re
import time
import json
import xarray
import numpy as np
import pdf_creator
import pandas as pd
from numpy import diff
from geojson import Point, Feature, dump
from datetime import datetime, timedelta
from scipy.ndimage.filters import uniform_filter1d
import progressbar as pb


class DataManager:
    """
        Creates an object containing all the data that is being loaded into the GUI.
        It also allows to load and manipulate said data.

        ...

        Attributes
        ----------
        path : str
            Path to the files being loaded
        files : list
            List containing the names of the files loaded
        mdata : list of dict
            List of dictionaries containing all the important data of each loaded file
        index : list
            List containing the indexes of the loaded files
        newfiles: int
            Number of new files loaded into the GUI
        tempdataold : list of dict
            Copy of the original mdata for recovery purposes

        Methods
        -------
        openfile(self, files, textBox, lister)
            Opens the files to be used with the GUI
        load_data(self)
            Reads the txt files and stores them on mdata dictionaries
        report(self, textBox)
            Creates a report in txt and pdf format
        zoom_data(self, data)
            Gets the first and lasts days of operation for a given depth
        zoom_data_loop(self)
            Gets the first and lasts days of operation for all the depths
        merge(self)
            Merges all of the loaded files into a single one
        list_to_df(self)
            Converts the mdata attribute into a single dataframe
        df_to_geojson(self, df, properties, SN)
            Iterates through the DF in order to create the properties for the Geojson file
        df_to_txt(self, df, SN)
            Converts the dataframe containing the data of all the files loaded into a txt file
        convert_to_netCDF(self, filename, df)
            Converts the dataframe containing the data of all the files loaded into a netCDF file
        temp_difference(self)
            Gets the difference in temperature between levels
        apply_uniform_filter(self)
            Applies the 10 running day filter to the data
        historic_to_df(historic, year, start_month='05', end_month='12')
            Converts the loaded historic txt file into a dataframe
        running_average_special(year_df, running=240)
            Applies the 10 running day filter to the data
        thresholds_df(historical)
            Creates a DataFrame containing the information needed to plot the thresholds

        Version: 04/2023 MJB: Documentation
        """
    def __init__(self, console, reportlogger):
        self.path = ""
        self.files = []
        self.mdata = []
        self.index = []
        self.newfiles = 0
        self.reportlogger = []
        self.tempdataold = []
        self.console_writer = console
        self.reportlogger = reportlogger
        print('hello')

    def openfile(self, files, textBox, lister):
        """
        Opens the files to be used with the GUI

        ...

        Parameters
        ----------
        files : list
            The filenames to be opened
        textBox : tK Text
            Writes on console
        lister : list
            List of all the previously loaded files
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
        Reads the txt files and stores them on mdata dictionaries
        """
        try:
            # Iterates based on the last entry on self.files to not overwrite
            for ifile in self.files[len(self.files) - self.newfiles:]:
                filein = self.path + ifile

                lat, lon, site_name = self.__load_coordinates(int(ifile.split('_')[0]))
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
                df.index = [datetime.strptime(df['Date'].iloc[i] + ' ' + df['Time'].iloc[i], "%d/%m/%y %H:%M:%S") for i
                            in
                            range(0, len(df))]
                df = df.drop_duplicates()
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
                self.tempdataold.append({'df':datos['df'].copy(), 'depth':datos['depth']})
            self.mdata = sorted(self.mdata, key=lambda k: k['depth'])
            self.tempdataold = sorted(self.tempdataold, key=lambda k: k['depth'])
            self.__to_utc()
            self.__check_start()
            self.__interpolate_hours()  # Interpolates the temperature between different not round hours

        except ValueError:
            self.console_writer("Error, file extension not supported, load a txt",'warning')

    def __load_coordinates(self, region):
        # Loads the coordinates of the file from the 'metadata.json' auxiliary file
        with open('../src/metadata.json') as f:
            data = json.load(f)
        lat = float(data['stations'][str(region)]['lat'])
        lon = float(data['stations'][str(region)]['long'])
        name = data['stations'][str(region)]['site_name']
        return lat, lon, name

    def __check_start(self):
        # Checks that the start time is correct
        for dat in self.mdata:
            titlestart = dat['datainici'].timestamp()
            filestart = dat['df'].index[0].timestamp()
            if titlestart < filestart:
                self.console_writer("Error, start date on the title of the file set before the start date of the "
                                     "file in depth " + str(dat['depth']), 'warning')

    def __interpolate_hours(self):
        # Interpolates the values of temp in case the hours are not round
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
                    dfinter = dfmerge.drop(columns=0)

                    dfinter['Temp'] = dfinter['Temp'].round(3)
                    dat['df'] = dfinter
                    break

    def __to_utc(self):
        # Change from local time to utc
        for i in range(len(self.mdata)):
            gmthshift = int(self.mdata[i]["GMT"][1:])
            # Mirar timedelta
            self.mdata[i]['df'].index = [self.mdata[i]['df'].index[n] - timedelta(hours=gmthshift) for n in
                               range(len(self.mdata[i]['df'].index))]
            self.mdata[i]['datainici'] = self.mdata[i]['datainici'] - timedelta(hours=gmthshift)
            self.mdata[i]['datafin'] = self.mdata[i]['datafin'] - timedelta(hours=gmthshift)

    def report(self, textbox):
        """
        List main file characteristics and prints it on the report screen and on a PDF

        ...

        Parameters
        ----------
        textbox : tK Text
            The textbox object for the report screen on the GUI
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
        textbox, PDF_DATA = self.__metadata_string_creator(textbox, PDF_DATA)
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

    def __metadata_string_creator(self, textbox, PDF_DATA):
        # Generates the metadata of the files on a string to implement on the report
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
        Gets the first and last day of operation for a given depth

        ...

        Parameters
        ----------
        data : dict
            An mdata dict of a given depth

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
        """
        Gets the first and last days of operation for all the depths
        """
        for data in self.mdata:
            time_series, temperatures, indexes, start_index, valid_start, valid_end = self.zoom_data(data)
            for i in indexes:
                data['df']['Temp'][int(i) - len(np.array(temperatures[1]))] = 999
            for i in range(0, int(np.argwhere(np.array(data['df'].index) == time_series[0][int(start_index)]))):
                data['df']['Temp'][int(i)] = 999

    def merge(self):
        """
        Merges all of the loaded files into a single one
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
        Converts the mdata attribute into a single dataframe
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
        Iterates through the DF in order to create the properties for the Geojson file

        ...

        Parameters
        ----------
        df : DataFrame
            The Dataframe to be read
        properties : list
            The depths of the geojson
        SN : list
            List of serial numbers
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
        Converts the dataframe containing the data of all the files loaded into a txt file

        ...

        Parameters
        ----------
        df : DataFrame
            The Dataframe to be read
        SN : list
            List of serial numbers
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
        """
        Converts the dataframe containing the data of all the files loaded into a netCDF file

        ...

        Parameters
        ----------
        filename : str
            Name of the resulting file
        df : DataFrame
            Dataframe to be stored as a NetCDF
        """
        # TODO print on console when the netCDF has been create
        try:
            xarray.Dataset(df.to_xarray()).to_netcdf('../src/output_files/' + filename + '.nc4')
            self.console_writer("netCDF file created", 'action')
        except Exception as e:
            print(str(e))

    def temp_difference(self):
        """
        Gets the difference in temperature between levels
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

    def apply_uniform_filter(self):
        """
        Applies the 10 running day filter to the data
        """
        df, depths = self.temp_difference()
        i = 1
        longest = 0
        indi = 0  # Checks the longest time series of all to use it as the base for the plots
        for u in range(0, len(self.mdata)):
            if len(self.mdata[u]['df'].index) > longest:
                longest = len(self.mdata[u]['df'].index)
                indi = u
        for depth in depths[:-1]:
            series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])].dropna(), size=240),
                                   index=df[str(depth) + "-" + str(depths[i])].dropna().index,
                                   columns=[str(depth) + "-" + str(depths[i])]).reindex(self.mdata[indi]['df'].index)
            # series1 = pd.DataFrame(uniform_filter1d(df[str(depth) + "-" + str(depths[i])], size=240),
            #                       index=data[indi]['time'], columns=[str(depth) + "-" + str(depths[i])])
            i += 1
            if 'dfdelta' in locals():
                dfdelta = pd.merge(dfdelta, series1, right_index=True, left_index=True)
            else:
                dfdelta = pd.DataFrame(series1)

        return dfdelta

    @staticmethod
    def historic_to_df(historic, year, start_month='05', end_month='12'):
        """
        Converts the loaded historic txt file into a dataframe

        ...

        Parameters
        ----------
        historic : str
            Filepath of the data that will be loaded and converted into a DataFrame
        year : str
            Year of operation that we want to extract
        start_month : str, optional
            First month that we want to extract
            (default is May, month '05')
        end_month : str, optional
            Last month that we want to extract
            (default is December, month '12')
        """
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
            end_time = datetime.strftime(
                min(n, key=lambda x: abs(x - datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'))),
                '%Y-%m-%d %H:%M:%S')
            filtered_df = df[start_time: end_time]
        else:
            filtered_df = df[start_time: end_time]
        if filtered_df.columns[0] == '5':
            filtered_df.insert(0, '0', filtered_df['5'], allow_duplicates=True)
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
            final_df = filtered_df.interpolate(axis=1, limit_area='inside')

        minyear = pd.to_datetime(df.index).year.min()
        return final_df, histmin, histmax, minyear

    @staticmethod
    def running_average_special(year_df, running=240):
        """
        Applies the 10 running day filter to the data

        ...

        Parameters
        ----------
        year_df : DataFrame
            Dataframe which will be applied the filter
        running : int, optional
            Number of instances for which the filter will be applied in hours
            (default is 240, which corresponds to 10 days)
        """
        i = 1
        longest = 0
        indi = len(year_df)
        depths = list(year_df.columns)
        arr = []
        df_empty = pd.DataFrame({str(depths[0]): []})
        for depth in depths:
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

        return dfdelta

    @staticmethod
    def thresholds_df(historical):
        """
        Creates a DataFrame containing the information needed to plot the thresholds

        ...

        Parameters
        ----------
        historical : str
            Path to the data file to be read

        Returns
        -------
        df_recreated : DataFrame
            Dataframe containing the information related to how many days over a certain temperature have
            been on a summer season each year
        """
        df_read = pd.read_csv(historical, sep='\t')
        depths = list(df_read)[2:]
        df_read['month'] = pd.DatetimeIndex(df_read['Date'], dayfirst=True).month
        df_read = df_read.loc[(df_read['month'] >= 7) & (df_read['month'] <= 9)]
        df_read['year'] = pd.DatetimeIndex(df_read['Date'], dayfirst=True).year
        df_recreated = pd.DataFrame(df_read['year'].unique(), columns=['year'])
        df_recreated = pd.DataFrame(np.repeat(df_recreated.values, len(depths), axis=0), columns=['year'])
        df_recreated['season'] = np.repeat(3, len(df_recreated))
        df_recreated['depth(m)'] = depths * int(len(df_recreated) / len(depths))
        df_recreated['depth(m)'] = df_recreated['depth(m)'].astype(int)
        df_inter = df_read.melt(id_vars=['year'], value_vars=depths,
                         var_name="depth(m)",
                         value_name="Value", ignore_index=False)
        df_inter['depth(m)'] = df_inter['depth(m)'].astype(int)
        df_inter_count = df_inter.groupby(['year', 'depth(m)']).count()
        df_recreated['N'] = df_inter_count['Value'].values
        for i in range(23, 29):
            df_recreated['Ndays>=' + str(i)] = round(
                df_inter.groupby(['year', 'depth(m)'])['Value'].apply(lambda x: (x >= i).sum()) / 24).values
        return df_recreated


