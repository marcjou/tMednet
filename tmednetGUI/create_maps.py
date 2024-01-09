import mhw_mapper as mp
import sys, getopt, os
from datetime import datetime, timedelta

def main(argv):
    # Gets the parameters from the command line to execute the publication script
    mode = ''
    MODES = ['intensity', 'duration', 'temperature']
    last_day = False
    try:
        opts, args = getopt.getopt(argv, 'hm:', ['mode='])
    except getopt.GetoptError:
        print('create_maps.py m <mode>')
        print('fallaste aqui')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('converter.py -m <mode>\n '
                  'Modes:\n'
                  'all: Map all the modes\n'
                  'intensity: Map the intensity\n'
                  'duration: Map the duration')
            sys.exit()
        elif opt in ('-m', '--mode'):
            mode = arg
        print(opts)
    print('Selected map is ', mode)
    start_date = datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%d')[:-2] + '01'
    #start_date = '2023-11-01'
    end_date = datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%d')
    #end_date = '2023-11-30'
    if datetime.today().day == 1:
        last_day = True
    df_map = mp.MHWMapper('/mnt/MHW/2024_MHW.nc', start_period=start_date, end_period=end_date)
    if mode == 'all':
        for i in MODES:
            if i == 'temperature':
                df_map = mp.MHWMapper('/mnt/MHW/lastTemp.nc', start_period=start_date, end_period=end_date)
            df_map.map_temperature(i)
    else:
        df_map.map_temperature(mode)
    print('Map of {} successfully created at src/output_images'.format(mode))

if __name__ == '__main__':
    main(sys.argv[1:])