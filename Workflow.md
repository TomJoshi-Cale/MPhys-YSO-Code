# WorkFlow - From big datafile to Median Subtracted Structure Function

## Create Folder for Sample

```bash
$ mkdir SAMPLE_FOLDER/
```

## Use TOPCAT to save all star file to folder

## Separate the stars into individual .dat lightcurves, and bin them

```bash
/SAMPLE_FOLDER: $ python ~/Python/SeparateBin.py FILENAME.txt
```

## Create .sf files for every magnitude bin

```bash
/SAMPLE_FOLDER: $ MasterSF
```

which is an alias command for

```bash
/SAMPLE_FOLDER: $ for d in *_to_*
do
    echo $d
    (cd $d && ls *.dat > files.txt && sf_text && rm files.txt)
done```

## Copy in LPS median for each magnitude bin
Navigate to the folder containing LPS bins:
​```bash
LPS_FOLDER: $ for d in *_to_*
do
    echo $d
    (cd $d && cp *Median.dat [PATH/TO/SAMPLE_FOLDER/"$d"/)
done
```

## Create .ssf files for every star 

Navigate back to SAMPLE_FOLDER/:

```bash
SAMPLE_FOLDER: $ LPSSub
```

which is an alias command for

```bash
SAMPLE_FOLDER: $ for d in *_to_*
do
    echo $d
    (cd $d && python ~/Python/LPSSubtract.py *Median.dat)
done```

## Create the Master Median
​```bash
SAMPLE_FOLDER: $ python ~/Python/MasterMedian.py [TITLE]
```

