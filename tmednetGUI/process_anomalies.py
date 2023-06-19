import sys, getopt, os
import pandas as pd
import numpy as np
from datetime import datetime
import surface_temperature as st


def main(argv):
    # Gets the parameters from the command line to execute the publication script
    path = ''
    year = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:y:', ['path=', 'year='])
    except getopt.GetoptError:
        print('converter.py -i <path> -y <year>')
        print('fallaste aqui')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('converter.py -i <path> -y <year>')
            sys.exit()
        elif opt in ('-i', '--path'):
            path = arg
        elif opt in ('-y', '--year'):
            year = arg
        print(opts)
    print('Path file is ', path)

    file_list = os.listdir(path)

    for filename in file_list:
        # Calls the multidepht_anomaly_plotter method under HistoricData object
        print(filename)
        historic = st.HistoricData(path + '/'  + filename)
        depths = ['10', '25', '40']
        for i in range(int(year), historic.last_year):
            historic.multidepth_anomaly_plotter(i, depths)
        print('Plots saved at output_images', 'action')


if __name__ == '__main__':
    main(sys.argv[1:])
