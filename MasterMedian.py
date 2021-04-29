#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Median.py
Created on Fri Nov 13 14:47:04 2020

This code searches through all subfolders to the CWD, and creates a median data
set for all .ssf files found. It then generates a .png plot of the Median SSF.

It is run as python MasterMedian.py [OutputTitle] [Display? Y/N]

which allows the user to name the outputted data-file and plot, and also choose
whether or not the plot of background subtracted is displayed when the code 
finishes running.


author: Tom Joshi-Cale
"""
import os
import numpy as np
from os.path import join
import sys
import matplotlib.pyplot as plt

try:
    filename = sys.argv[1]+"_submedian"
except IndexError:
    filename = input("Enter Title\n")+"_SubMedian"

# =============================================================================
# Step 1:   Run through all folders and find the longest .ssf file, so all 
#           other .ssf files can be expanded to the same length.
# =============================================================================
max_len = 0
total_files = 0
for root, dirs, files in os.walk(os.getcwd(), topdown=True):
    if "_to_" in root:
        for file in files:
            if ".ssf" in file:
                try:
                    time, reading = np.loadtxt(join(root, file), dtype=float, unpack=True, usecols=[0, 1])
                except ValueError:
                    print("Skipping empty file", join(file))
                    continue
                targ_len = reading.shape
                if targ_len == ():
                    targ_len = 1
                else:
                    targ_len = reading.shape[0]
                max_len = max(max_len, targ_len)
                if targ_len == max_len:
                    full_time = time
#write the time column (x-values) to the output
out_table = full_time
# =============================================================================
# Step 2:   Run through every .ssf file and fill it to max_len with None
#           variables. Data stored into out_table.
# =============================================================================
for root, dirs, files in os.walk(os.getcwd(), topdown=True):
    if "_to_" in root:
        # print(root)
        for file in files:
            if ".ssf" in file:
                ssf = np.loadtxt(join(root, file), dtype=float, unpack=True, usecols=[0, 1])
                # print(file)
                # print(ssf[0])
                total_files += 1
                try:
                    length = len(ssf[0])
                except TypeError:
                    length = 1    
                if length != len(full_time):
                    continue
                out_table = np.vstack((out_table, ssf[1]))
                
out_table = out_table.T

# =============================================================================
# Format the header column so the TITLE_SubMedian.dat file can be imported
# into TOPCAT or other spreadsheet software
# =============================================================================
output = open(filename+".dat", "w")


header = '#BJD\tMEDSF\n'
"""while n<len(out_table[0]):
    header = header + "SF_" + str(n) + "\t"
    n += 1
output.write(header)###"""
# =============================================================================
# Write output to file, and add the MedianSF column onto the end of each row
# =============================================================================
j=0

while j<len(out_table):
    data = out_table[j][1:]
    media = np.median(data)
    # print(media)
    output.write(" "+str(out_table[j][0])+"\t"+str(media)+"\n")
    #output.write(" ".join(map(str, out_table[j]))+"\t"+str(np.median(data[data != None]))+"\n")
    j+=1

output.close()

print("Number of files: ", total_files)
# =============================================================================
# Step 3:   Plot the TITLE_SubMedian.dat file as a .png file. 
# =============================================================================
try:
    disp = str(sys.argv[2]).lower()
except IndexError:
    disp = "n"
x,y = np.loadtxt(filename+'.dat', dtype=float, comments='#', usecols = [0, -1], unpack=True)
fig = plt.figure()
ax= fig.add_subplot(111)
ax.set_title(filename)
ax.plot(x, np.sqrt(y),                       #This section plots
        marker='o', mfc='none', mec='black', #the graph 
        linestyle='--', color='black')

#The below section formats axis and file output
plt.setp(ax, xlim=(1e-3, 1e5), ylim=(1e-3, 1e0),
     xscale='log', yscale='log', 
     xlabel=r'Time ($\tau$), days', ylabel=r'S F')
plt.savefig(fname=filename+'.png', format='png')
if disp == "y":
	plt.show()
