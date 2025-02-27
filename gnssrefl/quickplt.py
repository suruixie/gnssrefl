# -*- coding: utf-8 -*-
import argparse
from astropy.time import Time
import datetime
import numpy as np
import matplotlib.pyplot as plt
import os
import sys


import gnssrefl.quicklib as q


def main():
    """
    quick file plotting using matplotlib

    A png file is saved as temp.png or to your preferred
    filename if outfile is given. In either case, it goes to REFL_CODE/Files

    Allows you to set x and y-axis limits with a title and various axes labels

    a different symbol can also be set
    
    Someone could easily update this to include different filetypes (e.g. jpeg)

    Examples
    --------

    quickplt txtfile 1 16
        would plot column 1 on the x-axis and column 16 on the y-axis

    quickplt txtfile 1 16 -xlabel Time
        would plot column 1 on the x-axis and column 16 on the y-axis
        and add Time on the x-axis label

    quickplt txtfile 1 16 -xlabel "Time (sec)"
        would plot column 1 on the x-axis and column 16 on the y-axis
        and add Time (sec) on the x-axis label, but need quote marks since you 
        have spaces in the x-axis labe.

    quickplt txtfile 1 16 -reverse T
        would plot column 1 on the x-axis and column 16 on the y-axis
        it would reverse the y-axis parameter as you might want if 
        you are ploting RH but want it to have the same sense as a tide gauge.

    quickplt txtfile 1 16 -ylimits 0 2
        would restrict y-axis to be between 0 and 2

    quickplt txtfile 1 16 -outfile myfile.png
        would save png file to $REFL_CODE/Files/myfile.png


    Parameters
    ----------
    filename : str
        name of file to be plotted 
    xcol : str
        column number in the file for the x-axis parameter
    ycol : str
        column number in the file for the y-axis parameter
    mjd : str
        T or True, code will convert MJD to datetime, optional
    xlabel : str, optional
        label for x-axis 
    ylabel : str
        label for y-axis 
    symbol : str, optional
        prescibe the marker used in the plot 
    reverse : str, optional
        T or True, to reverse y-axis limits
    title : str, optional
        title for plot 
    outfile : str, optional
        name of png file to store plot 
    ylimits: float, optional
        pair of yaxis limits  
    xlimits: float, optional
        pair of xaxis limits  

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="filename", type=str)
    parser.add_argument("xcol", help="x-column", type=str)
    parser.add_argument("ycol",   help="y-column", type=str)
    parser.add_argument("-mjd", help="set to True/T if x-values are MJD (should add MM/SS?", type=str,default=None)
    parser.add_argument("-reverse", help="set to True/T to reverse the y-axis", type=str,default=None)
    parser.add_argument("-ymdhm", help="if True/T, columns 1-4 are year mon day hour minute", type=str,default=None)
    parser.add_argument("-xlabel", type=str, help="optional x-axis label", default=None)
    parser.add_argument("-ylabel", type=str, help="optional y-axis label", default=None)
    parser.add_argument("-symbol", help="plot symbol ", type=str,default=None)
    parser.add_argument("-title", help="optional title", type=str,default=None)
    parser.add_argument("-outfile", help="optional filename for plot. Must end in png", type=str,default=None)
    parser.add_argument("-ylimits", nargs="*",type=float, help="optional ylimits", default=None)
    parser.add_argument("-xlimits", nargs="*",type=float, help="optional xlimits", default=None)
    parser.add_argument("-ydoy", help="if True/T, columns 1-2 are year and doy", type=str,default=None)
    parser.add_argument("-filename2", help="second filename", type=str, default=None)

    args = parser.parse_args()

    filename = args.filename
    # change column numbers to pythonese
    xcol = int(args.xcol) - 1
    ycol = int(args.ycol) - 1


    if args.ylabel is None:
        ylabel = 'Unknown'
    else:
        ylabel = args.ylabel

    secondFile = False

    reverse_sign = False
    if (args.reverse == 'True') or (args.reverse == 'T'):
        reverse_sign = True

    # was previously ymdh
    ymd = False
    if (args.ymdhm == 'True') or (args.ymdhm == 'T'):
        ymd = True

    ydoy = False
    if (args.ydoy == 'True') or (args.ydoy == 'T'):
        ydoy = True

    convert_mjd = False
    if (args.mjd== 'True') or (args.mjd == 'T'):
        convert_mjd = True

    commentsign = '%'

    if os.path.isfile(filename):
        tvd = np.loadtxt(filename,comments=commentsign)
        if len(tvd) == 0:
            print('empty input file number 1')
            return
        tval = []
        yval = []
    else:
        print('input file does not exist')
        sys.exit()

    tvd2=[]
    secondFile = False
    if args.filename2 is not None:
        filename2 = args.filename2
        if os.path.isfile(filename2):
            tvd2 = np.loadtxt(filename2,comments=commentsign)
            if len(tvd2) == 0:
                print('empty input for filenumber 2')
                return
            else:
                secondFile = True
        else:
            print('second filename does not exist')


    tval,yval = q.trans_time(tvd, ymd, convert_mjd, ydoy,xcol,ycol)
    if secondFile:
        tval2,yval2 = q.trans_time(tvd2, ymd, convert_mjd, ydoy,xcol,ycol)



    fig,ax=plt.subplots()
    if args.symbol is None:
        ax.plot(tval, yval, 'b.')
    else:
        ax.plot(tval, yval, args.symbol)

    # second file is not currently supported
    if secondFile:
        ax.plot(tval2, yval2, 'r.')

    fig.autofmt_xdate()

    plt.ylabel(ylabel)

    if args.xlabel is not None:
        plt.xlabel(str(args.xlabel))

    if reverse_sign:
        ax.invert_yaxis()

    if args.title is None:
        ax.set_title(os.path.basename(filename) )
    else:
        ax.set_title(args.title )

    plt.grid()


    if args.ylimits is not None:
        print('found y-axis limits')
        ylimits = args.ylimits
        plt.ylim((ylimits))
    if args.xlimits is not None:
        print('found x-axis limits')
        xlimits = args.xlimits
        if convert_mjd:
            t1 = Time(xlimits[0],format='mjd')
            t1_utc = t1.utc # change to UTC
            tval1 =  t1_utc.datetime # change to datetime
            t2 = Time(xlimits[1],format='mjd')
            t2_utc = t2.utc # change to UTC
            tval2 =  t2_utc.datetime # change to datetime
            plt.xlim((tval1,tval2))

        else:
            plt.xlim((xlimits))

    out = args.outfile

    # make sure output directory exists.
    xdir = os.environ['REFL_CODE']  + '/Files/' 
    if not os.path.exists(xdir) :
        subprocess.call(['mkdir', xdir])

    if out is None:
        out = 'temp.png'
        print('Plotfile saved to: ', xdir + out)
        plt.savefig(xdir + out ,dpi=300)
    else:
        if out[-3:] == 'png':
            print('Plotfile saved to: ', xdir  + out)
            plt.savefig(xdir + out,dpi=300)
        else:
            print('Output filename must end in png.')

    plt.show()


if __name__ == "__main__":
    main()
