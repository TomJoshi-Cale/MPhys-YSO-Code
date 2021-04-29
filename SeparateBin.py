# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 11:56:54 2020
v1.0 completed Sat Oct 10 13:40 2020
v2.0 completed Mon Oct 12 13:36 2020 - Added Section 2.
v2.1 completed Mon Oct 12 14:41 2020 - Switched order of comments, and renamed bin folders
An OS non-specific code for taking a large data file in our standard format,
and separating out all its component stars into bins of a selectable (line 71)
size.
@author: tj294
"""
import operator
import os
import math as m

from timeit import default_timer as timer
from collections import OrderedDict
from shutil import move
from shutil import copyfile
from pathlib import Path
from tempfile import NamedTemporaryFile
import sys

try:
    filename = sys.argv[1]
except IndexError:
    filename = input("Which file would you like to separate?")

t = timer()
tot_t = timer()
# =============================================================================
# SECTION 1: Separate input and calculate each mean-magnitude
# First we cycle through all stars in the inputted data file, separate them
# into separate data files, and calculate each stars mean magnitude, which is
# saved into the mean_mag dictionary, with the starID as a key
# For ~1400 files, section takes ~25 seconds
# =============================================================================
nobs = 10 #<--Change this value to alter minimum number of observations to be
          #included. To include all observations, set to -1.
smallfiles = []
with open(filename) as bigFile:
    outfiles = {}         # mapping FULL_ID -> output file
    mean_mag = {}
    header = "#BJD MAG UNCER FLAG" # compute output header
    bigFile.readline() #skips past the header line
    n_rows = 0
    mag_total = 0
    #The First Time Through, things need to work differently:
    row = bigFile.readline().split()
    output = open(f'{row[0]}.dat', 'w')
    print(header, file=output)
    outfiles[row[0]] = output
    n_rows += 1
    mag_total += float(row[2])
    totalfiles = 1
    for line in bigFile:
        currentfile = row[0]
        row = line.split() #Turns each row into a list of data
        try:
            output = outfiles[row[0]] #Checks if the ID on current line is a key in outfiles
        except KeyError: #if that check says no:
            if n_rows < nobs and n_rows != 0:
                smallfiles.append(currentfile)
            mean_mag[currentfile] = mag_total / n_rows
            output = open(f'{row[0]}.dat', 'w') #opens a file named ID.dat
            print(header, file=output) #writes the header to the file
            outfiles[row[0]] = output #sets up ID:ID.dat within the outfiles dictionary
            totalfiles += 1
            n_rows = 0
            mag_total = 0
        n_rows += 1
        mag_total += float(row[2])
        print(' '.join(row[1:]), file=output) #writes all rows with current ID to ID.dat
    mean_mag[row[0]] = mag_total / n_rows
    if (n_rows < nobs and n_rows != 0):
            smallfiles.append(currentfile)
    for output in outfiles.values():               # close all files before exiting
        output.close()#"""
    
# sort the mean_mag dictionary into ascending order by magnitude
mean_mag = OrderedDict(sorted(mean_mag.items(), key=operator.itemgetter(1)))
time_elapsed = timer() - t

i=0
for file in smallfiles:
    i += 1
    os.remove(file+".dat")
    del mean_mag[file]
    print("Deleted", file)
print(totalfiles, "Read in")
print(i, "files deleted")
print(totalfiles - i, "files separated")

print("Section one Time: %f seconds.\n\n" % time_elapsed)

t = timer()
# =============================================================================
# SECION 2: Mean Mag into file
# This section is going to attempt to put the mean magnitude as a comment on
# the second line of each data file.
# =============================================================================
for key in mean_mag:
    sourcefile = Path("./"+str(key)+".dat").resolve()
    insert_lineno = 1
    insert_data = "# Mean magnitude = " + str(mean_mag[key])+"\n"
    with sourcefile.open(mode="r") as source:
        destination = NamedTemporaryFile(mode="w", dir=str(sourcefile.parent))
        lineno = 1
    
        while lineno < insert_lineno:
            destination.file.write(source.readline())
            lineno += 1
        
        destination.file.write(insert_data)
        
        while True:
            data = source.read(1024)
            if not data:
                break
            destination.file.write(data)
    
# Finish writing data.
    destination.flush()
# Overwrite the original file's contents with that of the temporary file.
# This uses a memory-optimised copy operation starting from Python 3.8.
    copyfile(destination.name, str(sourcefile))
# Delete the temporary file.
    destination.close()
elapsed_time = timer() - t
print("Section 2 time: %f seconds\n\n" % elapsed_time)

# =============================================================================
# SECTION 3: Calculate bins
# Calculate the floor of the lowest bin, and the ceiling of the highest bin.
# For ~1400 files, Time: 0.000219 seconds
# =============================================================================
t = timer()
bin_size = 0.5 #<-change this value to edit size of bin (default: 0.5, half-magnitude)
lowest_mag = list(mean_mag.values())[0]
highest_mag = list(mean_mag.values())[-1]
print("Lowest Magnitude: ", lowest_mag, "\t Highest Magnitude: ", highest_mag)
lowest_bin = m.floor(lowest_mag / bin_size) * bin_size
highest_bin = m.ceil(highest_mag / bin_size) * bin_size
n_bins = round((highest_bin - lowest_bin) / bin_size)
print("Lowest bin: ", lowest_bin, "\tHighest bin: ", highest_bin)
print("Number of bins: ", n_bins)

elapsed_time = timer() - t
print("Section 3 Time: %f seconds.\n\n" % elapsed_time)

# =============================================================================
# SECTION 4: Create a directory for each bin, and move all datafiles into their
#            respective bin directory
# For ~1400 files, Time: 6.61 seconds
# =============================================================================
t = timer()
bin_ceiling = lowest_bin + bin_size
bin_no = 1
while bin_no <= n_bins:
    for key in mean_mag:
        if mean_mag[key] < bin_ceiling and mean_mag[key] >= bin_ceiling - bin_size:
            try:
                os.mkdir("./"+str(bin_ceiling-bin_size)+"_to_"+str(bin_ceiling))
                move("./"+str(key)+".dat", "./"+str(bin_ceiling-bin_size)+"_to_"+str(bin_ceiling)+"/"+str(key)+".dat")
            except FileExistsError:
                move("./"+str(key)+".dat", "./"+str(bin_ceiling-bin_size)+"_to_"+str(bin_ceiling)+"/"+str(key)+".dat")

    bin_ceiling = bin_ceiling + bin_size
    bin_no += 1

elapsed_time = timer() - t

print("Section 4 Time: %f seconds.\n\n" % elapsed_time)

tot_elap = timer() - tot_t
print("Total Time elapsed: %f seconds" % tot_elap)
