# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 20:18:13 2016

@author: jgairjr
"""
import math as m
import numpy as np
import scipy as sp
import matplotlib as mpl
import matplotlib.pyplot as plt
import csv
from matplotlib import style
import pylab as pl
from collections import defaultdict
from statistics import mean, stdev
import codecs
import glob
import os


class FreqData:
    def __init__(self,freq,stor,loss,comp,tand,damp):
        self.freq = freq
        self.stor = stor
        self.loss = loss
        self.comp = comp
        self.tand = tand
        self.damp = damp

# frequencies is a dictionary where 
# each key is a single frequency and
# each value is a list
frequencies = defaultdict(list)

path='PUU211 Neat DMA/'
outname = path + 'compiled_PUU211_Neat_NanoDMA.csv'

# want avg and stddev for each column (except Time and Freq)
header = 'Frequency (Hz), Storage (GPa), Loss (GPa), Complex (GPa), Tan delta , Damping(kg/s)\n'

def main():
    for filename in glob.glob(path+'*.csv'):
      print(filename)
      if filename == outname: # Skip the file we're writing.
        continue
      with codecs.open(filename, 'r', 'ISO-8859-1') as infile:
        count = 0
        lineno = 0
        for line in infile:
          if lineno in [0,1,2]: continue
          fields = line.split()
          print(fields)
          try:
              freq = float(fields[7])
              stor = float(fields[14])
              loss = float(fields[15])
              comp = float(fields[17])
              tand = float(fields[18])
              damp = float(fields[22])
              # at each frequency, I append the values associated
              # with that frequency to the list
              frequencies[freq].append(FreqData(freq,stor,loss,comp,tand,damp))
          except ValueError as e:
              print('error in {} at line {}: {}'.format(filename, lineno,e))
              exit(1)
          outfile.write('%f , %f , %f, %f, %f, %f\n' % (freq, stor, loss, comp, tand, damp))
          count += 1
          lineno += 1

    with open(outname,'w') as f:
        f.write(header)
        # iterate over all the frequencies 
        for freq in frequencies:
            stor_data = [x.stor for x in frequencies[freq]]
            stor_mean = mean(stor_data)
            stor_sdev = stdev(stor_data)
            # each of the points, etc.
            line = "blah blah blah"
            f.write(line + '\n')


if __name__ == "__main__":
    main()
