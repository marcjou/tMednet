import sys, getopt, os

from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import file_manipulation as fm
import user_interaction as ui
import numpy as np
import matplotlib.dates as mdates
from matplotlib.figure import Figure

#Gets the parameters from the command line to execute the publication script
#TODO it uses fm-load_data properly, keep working

class Arguments:

    def __init__(self):
        self.path = ""
        self.files = []
        self.mdata = []
        self.index = []
        self.newfiles = 0
        self.counter = []
        self.recoverindex = None
        self.recoverindexpos = None
        self.reportlogger = []
        self.tempdataold = []
        self.controlevent = False

def main(argv):
    inputdir = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, 'hi:o:', ['idir=', 'ofile='])
    except getopt.GetoptError:
        print('publication.py -i <inputdirectory> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt =='-h':
            print('publication.py -i <inputdirectory> -o <outputfile>')
            sys.exit()
        elif opt in ('-i', '--idir'):
            inputdir = arg
        elif opt in ('-o', '--ofile'):
            outputfile = arg
        print(opts)
    print('Input directory is ', inputdir)
    print('Output file is ', outputfile)
    filepath = []
    files = []
    with os.scandir(inputdir) as entries:
        for entry in entries:
            filepath.append(inputdir + '/' + entry.name)
            files.append(entry.name)
    files.sort()
    filepath.sort()
    print(files)

    args = Arguments()
    args.path = inputdir + '/'
    args.files = files
    args.newfiles = len(files)

    fm.load_data(args)
    cut_endings(args)
    plot_hovmoller(args)

def cut_endings(args):
    if args.mdata:
        # self.tempdataold = []
        for data in args.mdata:
            # self.tempdataold.append(data['temp'].copy())
            _, temperatures, indexes, start_index = fm.zoom_data(data)
            for i in indexes:
                data['temp'][int(i) - len(np.array(temperatures[1]))] = 999
            for i in range(0, int(start_index)):
                data['temp'][int(i)] = 999
        print('Endings of all the files cut')
    else:
        print('Error could not cut')

def plot_hovmoller(args):
    try:

        plt.rc('legend', fontsize='medium')
        fig = Figure(figsize=(5, 4), dpi=100, constrained_layout=True)
        plot = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig)
        fm.to_utc(args.mdata)
        global cb
        df, depths, _ = fm.list_to_df(args.mdata)
        depths = np.array(depths)


        levels = np.arange(np.floor(np.nanmin(df.values)), np.ceil(np.nanmax(df.values)), 1)
        # df.resample(##) if we want to filter the results in a direct way
        # Draws a contourn line. Right now looks messy
        # ct = self.plot.contour(df.index.to_pydatetime(), -depths, df.values.T, colors='black', linewidths=0.5)
        cf = plot.contourf(df.index.to_pydatetime(), -depths, df.values.T, 256, extend='both', cmap='RdYlBu_r')

        cb = plt.colorbar(cf, ax=plot, label='Temperature (ºC)', ticks=levels)

        plot.set(ylabel='Depth (m)',
                      title='Stratification Site: ' + args.mdata[0]['region_name'])

        # Sets the X axis as the initials of the months
        locator = mdates.MonthLocator()
        plot.xaxis.set_major_locator(locator)
        fmt = mdates.DateFormatter('%b')
        plot.xaxis.set_major_formatter(fmt)
        #Sets the x axis on the top
        plot.xaxis.tick_top()

        plot.figure.savefig('tsdp.png')
        print('Plotting the HOVMOLLER DIAGRAM at region: ' + str(args.mdata[0]['region']))
    except IndexError:
        print('Load several files before creating a diagram')
    except TypeError:
        print('Load more than a file for the Hovmoller Diagram')

if __name__ == '__main__':
    main(sys.argv[1:])