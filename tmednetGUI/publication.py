import sys, getopt, os

from datetime import datetime
import pandas as pd
from matplotlib import pyplot as plt

import file_manipulation as fm
import file_writer as fw
import numpy as np
import matplotlib.dates as mdates
from matplotlib.figure import Figure

import arguments_class as arguments


# Gets the parameters from the command line to execute the publication script

def main(argv):
    inputdir = ''
    historical = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:x:', ['idir=', 'hfile='])
    except getopt.GetoptError:
        print('publication.py -i <inputdirectory> -x <historicalfilepath>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('publication.py -i <inputdirectory> -x <historicalfilepath>')
            sys.exit()
        elif opt in ('-i', '--idir'):
            inputdir = arg
        elif opt in ('-x', '--hfile'):
            historical = arg
        print(opts)
    print('Input directory is ', inputdir)
    print('Historical file is ', historical)
    filepath = []
    files = []
    with os.scandir(inputdir) as entries:
        for entry in entries:
            filepath.append(inputdir + '/' + entry.name)
            files.append(entry.name)
    files.sort()
    filepath.sort()
    print(files)

    args = arguments.Arguments(inputdir + '/', files, len(files))
    args.plot_hovmoller()
    print('Stratification Plot Done')

    args.plot_annualTCycle(historical)
    print('TCycles Plot Done')

    args.plot_thresholds(historical)
    print('Thresholds Plot Done')

    fw.big_merge(historical, merge(args), 'historical_updated')
    print('Historical merge created')
    fw.Excel('../src/output_files/historical_updated.txt', '../src/output_files/outs.xlsx')




def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd='',
                     console=False):
    percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    # TODO it freezes the console and it only updates after the loop which isn't useful at all, maybe raise a label?
    if console:
        console.delete('insert linestart', 'insert lineend')
        consolelen = int(length / 2)
        consolefillen = int(consolelen * iteration // total)
        consolebar = fill * consolefillen + '-' * (consolelen - consolefillen)
        console.insert("end", f'\r{prefix} |{consolebar}| {percent}% {suffix}')
        if iteration == total:
            console.insert("end", '\n')
    else:
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        if iteration == total:
            print()


def merge(args):
    try:
        if not args.mdata[0]['time']:
            print('First select \'To UTC\' option')
        else:

            df, depths, SN, merging = fm.merge(args)
            if merging is False:
                print('Load more than a file for merging, creating an output of only a file instead')

            fm.df_to_geojson(df, depths, SN, args.mdata[0]['latitude'], args.mdata[0]['longitude'])
            output = fm.df_to_txt(df, args.mdata[0], SN)
            print('File merged')
            return output
    except IndexError:
        print('Please, load a file first', )


if __name__ == '__main__':
    main(sys.argv[1:])
