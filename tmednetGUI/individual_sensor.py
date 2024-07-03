import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import matplotlib.dates as mdates
from matplotlib.figure import Figure


class SensorData():

    def __init__(self, filename):
        # For test "/home/marc/Projects/Mednet/tMednet/src/input_files/prueba_seascale.csv"
        # Load csv as DataFrame directly with its header
        self.data = pd.read_csv(filename, sep=',', header=9)
        # Reads the file and stores the metadata
        with open(filename) as f:
            content = f.readlines()
            self.utc = content[7][-8:-2]
            self.sensor = content[4][7:-1]
            self.dive = content[6][5:-1]
            self.duration = datetime.strptime(content[10][10:-4], '%H:%M:%S').time()
            self.duration_seconds = (self.duration.hour*60 + self.duration.minute)*60 + self.duration.second
        self.__convert_to_utc()

    def __convert_to_utc(self):
        #TODO se deberia mostrar todo siempre en UTC 0??

        # Converts date column to datetime object and transforms it to UTC 00:00
        if self.utc[0] == '+':
            self.data['date'] = pd.to_datetime(self.data['date'],
                                               format="%Y-%m-%d %H:%M:%S") - timedelta(hours=float(self.utc[1:3]),
                                                                                       minutes=float(self.utc[4:6]))
        else:
            self.data['date'] = pd.to_datetime(self.data['date'],
                                               format="%Y-%m-%d %H:%M:%S") + timedelta(hours=float(self.utc[1:3]),
                                                                                       minutes=float(self.utc[4:6]))

    def plot_temperature_depth(self):

        # Create ticks and labels for x axis
        start_round_time = self.data['date'][0].floor('15min')
        end_round_time = self.data['date'][len(self.data) - 1].ceil('15min')
        ticks = pd.date_range(start_round_time, end_round_time, freq='15min')

        # Starts the figures and axes
        fig, ax1 = plt.subplots()
        ax1.set_ylabel('Temperature (ºC)', color='tab:blue')
        ax2 = ax1.twinx()
        ax2.set_ylabel('Depth (m)', color='tab:red')

        # Plots the temperature and depth
        self.data.plot(x='date', y='temperature(ºC)', ax=ax1)
        self.data.plot(x='date', y='depth(m.)', color='tab:red', ax=ax2)
        ax1.xaxis.set_ticks(ticks)
        plt.xticks(ticks)
        plt.xlabel('Time')
        ax1.set_xlabel('Time')

        # Sets a grid showing the depths levels
        plt.grid(color='gray', linestyle='--', linewidth=0.3)

        self.__class__.__save_image('../src/output_images/Temperature+Depth_' + self.dive + '_' +
                                    self.data['date'][0].strftime('%d-%m-%Y') + '.png')

    @staticmethod
    def __save_image(savefile):
        plt.savefig(savefile)

    @staticmethod
    def __custom_round(x, base=0.25):
        return base * round(float(x) / base)

    def __transform_to_columns(self):
        data_copy = self.data.copy()
        data_copy['depth(m.)'] = data_copy['depth(m.)'].apply(lambda x: self.__class__.__custom_round(x))

    def stratification_plot(self):
        # Open all the files to use on the stratification plot
