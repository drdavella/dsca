#!/usr/bin/env python3
import sys, os, codecs, math
from argparse import ArgumentParser
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib import style

# Reading the summary file fails unless this encoding is used. The encoding
# seems to correspond to a codepage from Windows called Latin 1, but it is not
# compatible with ASCII or UTF-8
ENCODING = 'ISO-8859-1'
DEFAULT_Z_THRESH = 3    # standard deviations


class DataLine():
    '''
    Class representing the fields we care about from a single entry
    from a summary file.
    '''
    def __init__(self,fname,depth,stiff,hard,line):
        '''
        Constructor for a DataLine object

        @param fname    Name of the data point file associated with this data
        @param depth    Max depth for this data point (nm)
        @param stiff    Overall stiffness for this data point (GPa)
        @param hard     Overall hardness for this data point (GPa)
        @param line     Verbatim line from summary file representing this point

        @return     New DataLine object
        '''
        self.fname = fname
        self.depth = depth
        self.stiff = stiff
        self.hard = hard
        self.line = line


    def __repr__(self):
        '''
        Defines the text representation of this object.
        '''
        s = "DataLine(\"{}\",{},{},{})".format(self.fname,self.depth,
                self.stiff,self.hard)
        return s


class DataSample():
    '''
    Class representing a single sample from a data point file.
    '''
    def __init__(self,time,depth,load):
        '''
        Constructor for a DataSample object

        @param time     Time (in seconds)
        @param depth    Depth (in nanometers)
        @param load     Load (in micro Newtons)
        '''
        self.time = time
        self.depth = depth
        self.load = load


    def __repr__(self):
        '''
        Defines the text representation of this object.
        '''
        s = "DataSample({},{},{})".format(self.time,self.depth,self.load)
        return s


def exitmsg(msg):
    '''
    Prints the given message to <stderr> and exits

    @param  msg     Error message to print to <stderr>
    '''
    print("error: {}".format(msg),file=sys.stderr)
    sys.exit(1)


def read_summary_file(filename):
    '''
    Reads and parses given summary file into a list of DataLines.
    Returns the header line and the list of DataLine objects

    @param filename     Path to the summary file to be parsed

    @return     (header,DataLines)
    '''
    data = list()
    # check if the file exists
    if not os.path.exists(filename):
        exitmsg("given file '{}' does not exist".format(filename))
    # we can't just use the default encoding of ASCII/UTF-8
    with codecs.open(filename,'r',ENCODING) as f:
        for i,line in enumerate(f):
            # skip the first line and third line
            if i == 0: continue
            # capture the header line
            if i == 2:
                header = line.strip()
                continue
            # skip the empty lines
            if line == '' or line == '\n': continue
            # CURSE THEE WINDOWS!!!! (line feed and carriage return)
            if line == "\x0d\x0a" or line == "\x0d": continue
            # split each data line into individual fields
            fields = line.split()
            if len(fields) == 0: continue
            # build the name of the data file
            try:
                filename = "{} {} LC.txt".format(fields[0],fields[1])
                # these numbers represent indices that correspond to
                # whitespace-separated columns that we care about
                # in the summary file
                depth = float(fields[7])
                stiffness = float(fields[9])
                hardness = float(fields[10])
            # assume that a parsing error means we got a bad line
            except ValueError:
                continue
            data.append(DataLine(filename,depth,stiffness,hardness,line.strip()))
    return (header,data)


def write_summary_file(path,points,header):
    '''
    Creates a summary file at the given path and writes out
    the given set of DataPoint objects.

    @param  path    Path of the summary file to be created and written
    @param  points  List of DataPoint objects to be written to file
    @param  header  Line of text representing summary file header  
    '''
    # for the sake of consistency write the file with the same encoding
    with codecs.open(path,'w',ENCODING) as f:
        # duplicate the first line
        f.write("Number of Data Points = {}\n\n".format(len(points)))
        # duplicate the header line
        f.write(header + '\n')
        for p in points:
            f.write(p.line + '\n')


def read_datapoint_file(filename):
    '''
    Reads and parses data point file with the given filename.
    Returns a list of DataSample objects representing the samples
    in this file.

    @param filename     Path to the data point file to be parsed 

    @return     List of DataSample objects
    '''
    samples = list()
    # check if the file exists
    if not os.path.exists(filename):
        exitmsg("given file '{}' does not exist".format(filename))
    # we can't just use the default encoding of ASCII/UTF-8
    with codecs.open(filename,'r',ENCODING) as f:
        for i,line in enumerate(f):
            # skip the first four lines
            if i < 4: continue
            # skip the empty lines
            if line == "" or line == '\n': continue
            # CURSE THEE WINDOWS!!!! (line feed and carriage return)
            if line == "\x0d\x0a" or line == "\x0d": continue
            fields = line.split()
            try:
                depth = float(fields[0])
                load = float(fields[1])
                time = float(fields[2])
            # assume that a parsing error means we have a bad line
            except ValueError:
                continue
            ds = DataSample(time,depth,load)
            samples.append(ds)
    return samples


def calculate_stats(samples,samplevar=True):
    '''
    Calculates the mean and standard deviation of a given list of samples.

    @param samples      List of samples
    @param samplevar    Flag indicating whether samples represent full
                        population or set of samples (defaults to set of
                        samples)

    @return     tuple(mean, standard deviation)
    '''
    mean = sum(samples) / len(samples)
    variance = sum([(x - mean) ** 2 for x in samples])
    # how we calculate variance depends on whether this is an
    # entire population or just a set of samples
    size = len(samples) - 1 if samplevar else len(samples)
    variance = variance / size
    sdev = math.sqrt(variance)
    return (mean,sdev)


def main():
    # argument parsing and processing
    p = ArgumentParser()
    p.add_argument('summary_file',type=str,nargs=1)
    p.add_argument('-d','--data-dir',action='store',dest='datadir',type=str,
            help='directory containing data points ' \
                 '(defaults to same directory as summary file)')
    p.add_argument('-p','--pval',action='store',dest='pval',type=float,
            help='p-value threshold for outlier data points')
    p.add_argument('-s','--sdev',action='store',dest='sdev',type=float,
            help='standard deviation threshold for outlier data points')
    args = p.parse_args()
    if args.pval and args.sdev:
        exitmsg("--pval and --sdev are not compatible")

    sumfile = args.summary_file[0]
    # where do the data point files live?
    if args.datadir:
        datadir = args.datadir
        if not os.path.exists(datadir):
            exitmsg("given data point path '{}' does not exist".format(datadir))
    # if not given on the command line, assume that the data
    # points live in the same directory as the summary file
    else:
        datadir = os.path.dirname(os.path.abspath(sumfile))
    # use Z threshold from the command line, if provided
    if args.sdev:
        if args.sdev < 0:
            exitmsg("invalid Z score: {}".format(args.sdev))
        zthresh = args.sdev
    elif args.pval:
        if args.pval < 0 or args.pval > 1:
            exitmsg("invalid p value: {}".format(args.pval))
        # we're doing a two-tailed test here
        tails = 1 - args.pval
        zthresh = stats.norm.ppf(args.pval + tails/2)
        print("zthresh={}".format(zthresh))
    else:
        zthresh = DEFAULT_Z_THRESH

    # we'll use the header line when we write out the new files
    print("parsing summary file")
    header,data = read_summary_file(sumfile)
    # do these data points represent full populations or sample sets?
    (depth_mean, depth_sdev) = calculate_stats([x.depth for x in data])
    (stiff_mean, stiff_sdev) = calculate_stats([x.stiff for x in data])
    (hard_mean, hard_sdev) = calculate_stats([x.hard for x in data])

    # weed out the outliers
    valid_points = list()
    outliers = list()
    for x in data:
        # NOTE: The statistics for this might not be exactly right. 
        # I'm trying to do a Z-test here, but according to Wikipedia,
        # to properly do a Z test it is necessary to have a population
        # mean and standard deviation, and it seems like we only have
        # a sample mean and standard deviation. I really don't know
        # enough to say how badly this fudges the stats though.
        depth_score = (x.depth - depth_mean) / depth_sdev
        stiff_score = (x.stiff - stiff_mean) / stiff_sdev
        hard_score = (x.hard - hard_mean) / hard_sdev
        # reject data points if any of these scores exceeds the threshold
        if abs(depth_score) >= zthresh:
            outliers.append(x)
            continue
        if abs(stiff_score) >= zthresh:
            outliers.append(x)
            continue
        if abs(hard_score) >= zthresh:
            outliers.append(x)
            continue
        valid_points.append(x)

    # use the same output directory as where the summary file lives
    outdir,basename = os.path.split(os.path.abspath(sumfile))
    # how standard is the summary file name? this might have to change
    data_name = basename.split()[0]
    # write the processed (clean) summary file
    clean_name = "{}/{}_clean.txt".format(outdir,data_name)
    print("writing processed data to {}".format(clean_name))
    write_summary_file(clean_name,valid_points,header)
    # write the outlier summary file (is this necessary?)
    outlier_name = "{}/{}_outliers.txt".format(outdir,data_name)
    print("writing outliers to {}".format(outlier_name))
    write_summary_file(outlier_name,outliers,header)

    # find the most representative point
    best_score = float('inf')
    best_point = None
    best_samples = list()
    print("finding best representative data point file")
    for p in valid_points:
        # NOTE: This is an extremely naive way to compute a similarity
        # score. Once a better way has been determined, this will need
        # to be updated.
        datapath = "{}/{}".format(datadir,p.fname)
        samples = read_datapoint_file(datapath)
        mean,_ = calculate_stats([x.depth for x in samples])
        score = abs(mean - depth_mean)
        if score < best_score:
            best_score = score
            best_point = p
            best_samples = samples

    print("graphing the most representative data point file")
    style.use('bmh')
    t = [x.time for x in best_samples]
    d = [x.depth for x in best_samples]
    l = [x.load for x in best_samples]
    dplot = plt.subplot(211)
    plt.title('Best Point: {}'.format(p.fname))
    plt.plot(t,d, color='#170323') # depth against time
    plt.ylabel('Depth (nm)')
    lplot = plt.subplot(212, sharex=dplot)
    plt.plot(t,l) # load against time
    # it should be possible to print a mu, but I don't have the
    # patience to figure out how right now (tried using tex)
    plt.ylabel('Load (micro Newtons)')
    plt.xlabel('Time (s)')
    plt.show()


if __name__ == "__main__":
    main()
