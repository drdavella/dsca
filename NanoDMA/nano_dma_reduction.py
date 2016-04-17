#!/usr/bin/env python3
"""
Created on Thu Apr 14 20:18:13 2016

@author: jgairjr
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import style
from collections import defaultdict
import sys, os, codecs, glob, statistics
from argparse import ArgumentParser

# If using Spyder instead of command line, set these variables appropriately
USING_SPYDER = False # set to True if using Spyder
SPYDER_DATA_PATH = None # set to path of directory where files live
SPYDER_OUTPUT_NAME = None # base name of output file

# Any files in the given directory that should NOT be processed should
# be added to this list. There is no need to specify the entire path; just
# the base filename will work
EXCLUDES = ['example.csv']

# Reading the input files fails unless this encoding is used. The encoding
# seems to correspond to a codepage from Windows called Latin 1, but it is not
# compatible with ASCII or UTF-8
ENCODING = 'ISO-8859-1'


class FreqData:
    '''
    Class representing the fields we care about from a single line of a data
    file.
    '''
    def __init__(self,freq,stor,loss,comp,tand,damp):
        '''
        Constructor for a FreqData object 

        @param freq     Frequency associated with this sample
        @param stor     Storage value for this sample (GPa)
        @param loss     Loss value for this sample (GPa)
        @param comp     Complex value for this sample (GPa)
        @param tand     Tan Delta value for this sample
        @param damp     Damping value for this sample (kg/s)

        @return     New FreqData object
        '''
        self.freq = freq
        self.stor = stor
        self.loss = loss
        self.comp = comp
        self.tand = tand
        self.damp = damp

    def __repr__(self):
        '''
        Defines text representation of this object.
        '''
        s = "FreqData({},{},{},{},{},{})".format(self.freq,self.stor,
                self.loss,self.comp,self.tand,self.damp)
        return s


def exitmsg(msg):
    '''
    Prints the given message to <stderr> and exits

    @param  msg     Error message to print to <stderr>
    '''
    print("error: {}\n".format(msg),file=sys.stderr)
    sys.exit(1)


def process_input_file(filename,freqdata):
    '''
    Processes the given input file. Adds fields from each data line,
    organized by frequency, to the given frequency data dictionary.

    @param filename     Name of the input file to be processed
    @param freqdata     defaultdict where keys are frequencies and
                        values are lists of FreqData objects
    '''
    data = list()
    with codecs.open(filename,'r',ENCODING) as infile:
        # iterate through every line of the file
        for i,line in enumerate(infile):
            # skip the first three lines
            if i in [0,1,2]: continue
            fields = line.split()
            try:
                freq = float(fields[7])
                stor = float(fields[14])
                loss = float(fields[15])
                comp = float(fields[17])
                tand = float(fields[18])
                damp = float(fields[22])
                # at each frequency, I append the values associated
                # with that frequency to the list of FreqData objects
                freqdata[freq].append(FreqData(freq,stor,loss,comp,tand,damp))
            except ValueError as e:
                exitmsg('error in {} at line {}: {}'.format(filename,i+1,e))


def compute_stats(data):
    '''
    Computes mean and standard deviation of input data list.

    @param data     List of input data samples

    @return mean(data), stdev(data)
    '''
    return statistics.mean(data), statistics.stdev(data)


def write_summary_header(outfile,sep='\t'):
    '''
    Writes header line to the output summary file.

    @param outfile  Open file handle corresponding to output file
    @param sep      Separator to use for output file. Defaults to tab,
                    but could also be comma
    '''
    header  = "Frequency (Hz){}".format(sep)
    header += "Mean Storage (GPa){}Sigma Storage (GPa){}".format(sep,sep)
    header += "Mean Loss (GPa){}Sigma Loss (GPa){}".format(sep,sep)
    header += "Mean Complex (GPa){}Sigma Complex (GPa){}".format(sep,sep)
    header += "Mean Tan Delta{}Sigma Tan Delta{}".format(sep,sep)
    header += "Mean Damping (kg/s){}Sigma Damping (kg/s){}".format(sep,sep)
    outfile.write(header + '\n')


def write_summary_file(filename,stats,sep='\t'):
    '''
    Writes the given stats, assumed to be collated by frequency, to
    the given output file. Assumes that the order of fields corresponding
    to each frequency is in the same order as the header line above.
    
    @param filename     Name of the output file to be created
    @param stats        Dictionary of statistics, where keys are frequencies
                        and values are tuples of statistics corresponding to
                        the fields we acare about
    @param sep      Separator to use for output file. Defaults to tab,
                    but could also be comma
    '''
    with open(filename,'w') as f:
        write_summary_header(f,sep)
        frequencies = sorted(stats.keys())
        for freq in frequencies:
            outline = ""
            for mean,sdev in stats[freq]:
                outline += "{}\t{}\t".format(mean,sdev)
            # replace the last tab with a newline
            outline[-1] = '\n'
            f.write(outline)


def process_arguments():
    '''
    Processes program arguments, taking into account whether it has been
    specified that the program is being run from a Spyder session. Returns
    paths that correspond to the input source directory, to the full path
    of the output file to be written, and a flag indicating whether to 
    operate in verbose mode.

    @return source_dir, outfile, verbose
    '''
    # this value should be set above if using SPYDER. I don't know if
    # there's a way to automatically detect if the program is being run
    # within SPYDER.
    if USING_SPYDER:
        if SPYDER_DATA_PATH is None:
            exitmsg("If using Spyder, SPYDER_DATA_PATH must be set appropriately!")
        if SPYDER_OUTPUT_NAME is None:
            exitmsg("If using Spyder, SPYDER_OUTPUT_NAME must be set appropriately!")
        source_dir = SPYDER_DATA_PATH
        outfile = "{}/{}".format(SPYDER_DATA_PATH,SPYDER_OUTPUT_NAME)
        # this will always be false, unless otherwise specified
        verbose = False
    else:
        p = ArgumentParser()
        p.add_argument('source_dir',type=str,nargs=1)
        p.add_argument('-v','--verbose',action='store_true',dest='verbose',
                       help="Verbose terminal output")
        args = p.parse_args()
        source_dir = args.source_dir[0]
        outfile = "{}/freq_summary.csv".format(source_dir)
        verbose = args.verbose

    if not os.path.isdir(source_dir):
        exitmsg("given source directory '{}' does not exist or is not a directory" \
                .format(source_dir))
    # create the output summary file in the source directory
    return source_dir, outfile, verbose


def main():
    '''
    Actually runs the program
    '''
    source_dir, outfile, verbose = process_arguments()
    # also want to exclude our output file
    excludes = EXCLUDES + [os.path.basename(outfile)]

    # frequencies is a dictionary where each key is
    # a single frequency and each value is a list
    frequencies = defaultdict(list)
    infiles = glob.glob("{}/*.csv".format(source_dir))
    if len(infiles) == 0:
        exitmsg("No input files found in given input directory {}".format(source_dir))
    for filename in infiles:
        # skip files that should not be processed
        if os.path.basename(filename) in excludes: continue
        if verbose: print("processing {}".format(filename))
        process_input_file(filename,frequencies)
    if len(frequencies) == 0:
        exitmsg("No input files were processed")

    stats = dict()
    # now analyze data at each frequency
    for freq in frequencies:
        # this is the list of all the stats at this frequency
        data = frequencies[freq]
        # sorry, this is not that efficient :(
        stor_stats = compute_stats([x.stor for x in data])
        loss_stats = compute_stats([x.loss for x in data])
        comp_stats = compute_stats([x.comp for x in data])
        tand_stats = compute_stats([x.tand for x in data])
        damp_stats = compute_stats([x.damp for x in data])
        # collect all of the statistics at this frequency
        # each statistic is a pair representing (mean,sdev)
        # NOTE: the order of these fields should be the same as the order
        # in the header so that the fields are aligned properly
        stats[freq] = (stor_stats, loss_stats, comp_stats, tand_stats, damp_stats)

    if verbose: print("writing summary file: {}".format(outfile))
    write_summary_file(outfile,stats)

    # This program doesn't do any graphing yet.
    # The summarized statistics, organized by frequency, are in the
    # data structure named 'stats'. Here's how you might go about
    # graphing something like mean loss against frequency:
    #
    #   # collect all the frequencies and sort them
    #   x_data = sorted(stats.keys())
    #   # collects all of the mean loss values corresponding to each frequency
    #   y_data = [stats[freq][1][0] for freq in x_data]
    #   # do graphing here

if __name__ == "__main__":
    main()
