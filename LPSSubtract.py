#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This code takes every .sf file in a folder, and subtracts a given file from them
v2: added lines 48-49 [if (len(YSO) == 0): etc..] to exclude empty files that
    slip through SeparateBin.py
Created on Fri Nov 13 09:26:12 2020

@author: Tom Joshi-Cale
"""
import sys
import os
import platform
import numpy as np

try:
    LPSFile = sys.argv[1]
except IndexError:
    print("Please provide the names of the LPS file (e.g. *Median.dat)\n")
    exit(1)

if platform.system() == 'Windows':
    os.system('dir /b *.sf > files.txt')
else:
    os.system('ls *.sf > files.txt')
    
files = []
files = np.loadtxt('files.txt', dtype=str, unpack=True)

# =============================================================================
# Read in the Median LPS data into an array
# =============================================================================
MedianLPS = np.loadtxt(LPSFile, usecols=(0, -1), unpack=False)

# =============================================================================
# For each .sf file in files.txt, open, subtract relevant LPS column
# =============================================================================
try:
    for file in files:
        SSF = []
        YSO = np.loadtxt(file, dtype=float, usecols=(0, 1), unpack=False, ndmin=2)
        if (len(YSO) == 0):
            continue
        for YSOline in YSO:
            for LPSline in MedianLPS:
                #print("LPS: ", LPSline[0])
                #print("YSO: ", YSOline[0])
                if YSOline[0] != LPSline[0]:
                    continue
                else:
                    sub_value = YSOline[1] - LPSline[1]
                    SSF.append((YSOline[0],sub_value))
        with open(file[:-3]+".ssf", 'w') as output:
            header = '#BJD\tSF\n'
            output.write(header)
            for items in SSF:
                line = str(items[0])+'\t'+str(items[1])+'\n'
                output.write(line)
except TypeError:
    SSF = []
    file = str(files)
    YSO = np.loadtxt(file, usecols=(0, 1), unpack=False)
    for YSOline in YSO:
        for LPSline in MedianLPS:
            if YSOline[0] != LPSline[0]:
                continue
            else:
                sub_value = YSOline[1] - LPSline[1]
                SSF.append((YSOline[0], sub_value))
    with open(file[:-3]+".ssf", 'w') as output:
        header = '#BJD\tSF\n'
        output.write(header)
        for items in SSF:
            line = str(items[0])+'\t'+str(items[1])+'\n'
            output.write(line)
