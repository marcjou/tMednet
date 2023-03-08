import sys, getopt, os
import pandas as pd
import numpy as np
from datetime import datetime


def main(argv):
    # Gets the parameters from the command line to execute the publication script
    tobsfile = ''
    outfile = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['tobsfile=', 'ofile='])
    except getopt.GetoptError:
        print('converter.py -i <tobsfilepath> -o <outputfilename>')
        print('fallaste aqui')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('converter.py -i <tobsfilepath> -o <outputfilename>')
            sys.exit()
        elif opt in ('-i', '--tobsfile'):
            tobsfile = arg
        elif opt in ('-o', '--ofile'):
            outfile = arg
        print(opts)
    print('Tobs file is ', tobsfile)
    print('Output file will be ', outfile)

    file2 = convert_time(tobsfile)
    file2.to_csv('../src/output_files/' + outfile + '.txt', sep='\t', index=False)
    print(outfile + ' successfully created at src/output_files')

def convert_time(tobsfile):
    file = pd.read_csv(tobsfile, sep='\t')
    file2 = file.rename(columns={'NaN': 'Date', 'NaN.1': 'Time'})

    # TODO Should I conserve nan lines between time periods? YES!!!!
    # TODO mirar que pasa con las horas que no salen correctas
    file2.dropna(how='all', inplace=True)  # Drops all the lines that are pure NaN
    file2['Date'] = file2['Date'].astype(int)
    file2['Date'] = file2['Date'].map(lambda x: datetime.strftime(datetime.fromordinal(datetime(1900, 1, 1).toordinal()
                                                                                       + int(x) - 2), '%d/%m/%Y'))
    file2['Time'] = file2['Time'].map(
        lambda x: str(int(float(x) * 24)) + ':0' + str(int(((float(x) * 24) % 1) * 60)) + ':0'
                  + str(int(((((float(x) * 24) % 1) * 60) % 1) * 60)) if len(
            str(int(((float(x) * 24) % 1) * 60))) == 1 else str(int(float(x) * 24) + 1) + ':00:00')
    file2['Time'] = file2['Time'].map(lambda x: '0' + x if len(x) == 7 else x)

    for key in file2:
        if key != 'Date' and key != 'Time':
            file2[key] = file2[key].round(decimals=3)

    file2.replace('', np.nan, regex=True, inplace=True)
    return file2

if __name__ == '__main__':
    main(sys.argv[1:])
