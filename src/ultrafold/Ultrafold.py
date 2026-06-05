#!/usr/bin/env python
#  Primary script to run the SuperFold analysis pipeline (in other words RUN THIS SCRIPT)
#
#  - Requires a .map file as an argument (see README for details)
#  - Requires the following programs be executable from any location (i.e. in the PATH):
#        python, Fold, partition, ProbabilityPlot
#  - Take a look at the README for other required modules, installation, and execution help.
#  - Public release 1.2
#  - Copyright Greggory M Rice 2014
#           Copyright for Shapemapper 2.2 DMS compatibility David Mitchell III 2023

#  - Update: Sep 30, 2020: Addressed issues with SHAPE reactivity not displaying on Shannon entropy plot.
#			Altered the Shannon Entropy plot to display Shannon and SHAPE on separate y axes.
#			Fixed np.nan issue with SHAPE plotting.
#			-999 values no longer counted as low SHAPE when determining low SHAPE/low Shannon regions
#			Fixed issue with beginning of sequence being incorrectly included in low SHAPE/low Shannon region
#
#  - Update: Jul 25, 2023: Added compatibility with DMS functionality in Shapemapper 2.2
##################################################################################
# GPL statement:
# This file is part of Shapemapper.
#
# SuperFold is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SuperFold is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SuperFold.  If not, see <http://www.gnu.org/licenses/>.

# 25 July 2023
# all rights reserved
# 1.2 build
##################################################################################
import batchSubmit as batch
import argparse, sys, shlex, os, subprocess, hashlib, time
from RNAtools import dotPlot, CT, padCT, writeSHAPE
import pandas as pd
import os
import shlex
import subprocess
import math

# set the plotting environment to be non-interactive
import matplotlib as mtl
mtl.use("Agg")
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

# import arc drawing functions
from drawArcRibbons_simple import writeManyPlot as arcplot
import numpy as np
from PyCircleCompareSF import makeCircle

class shapeMAP:
    def __init__(self,fIN):
        self.seq    = []
        self.ntNum  = []
        self.shape  = []
        self.stdErr = []
        self.zfactor = []
        
        if fIN:
            parsed = self.readFile(fIN)
            
            self.ntNum = map(int,parsed[0])
            self.shape = map(float,parsed[1])
            self.stdErr= map(float,parsed[2])
            self.seq = parsed[3]
            
            if len(parsed.keys()) == 5:
                try:
                    self.zfactor = map(float,parsed[4])
                except:
                    print "formatting error: {0}\nNon float in zfactor column".format(fIN)
                    sys.exit()
            # replace T's with U's
            for i in range(len(self.seq)):
                if self.seq[i] == "T": self.seq[i] = "U"
            
    
    def readFile(self,fIN):
        data = {}
        lineNum = 0
        for line in open(fIN, "rU").readlines():
            x = line.rstrip().split()
            
            # initialize an array obj for the first line
            if lineNum == 0:
                for i in range(len(x)):
                    data[i] = [x[i]]
            
            # populate the array obj
            else:
                for i in range(len(x)):
                    data[i].append(x[i])
            
            lineNum += 1
        
        
        return data


def main():
    
    debug = False
    
    # Start the stopwatch
    startTime = time.time()
    
    # Check to see if cmd line programs are available
    runCheck()
    
    # Parse the input arguments
    args = parseArgs()
    
    # Prepare a temporary sequence file
    temp_seq_file = "temp_seq_file.seq"
    with open(temp_seq_file, 'w') as seq_file:
        seq_data = args.mapObj.seq  # Assuming seq attribute holds sequence data
        seq_file.write(";\n\n" + "RNA_sequence" + "\n\n")
        for i, nuc in enumerate(seq_data):
            seq_file.write(nuc)
            if (i + 1) % 50 == 0:
                seq_file.write("\n")
            elif (i + 1) % 10 == 0:
                seq_file.write(" ")
        seq_file.write("\n1\n")

    # Prepare bpp2seq file
    bpp2seq_file = "profile_data.bpp2seq"
    create_bpp2seq(args.mapObj, 1, len(args.mapObj.seq), bpp2seq_file)
    
    # Set the results directory paths
    currDir = os.getcwd()
    resultsFile = 'results_' + args.safeName
    resultsDir = os.path.join(currDir, 'results')

    print 'Current Directory:', currDir
    print 'Results Directory:', resultsDir
    print 'Results Log File:', resultsFile

    try:
        os.mkdir(resultsDir)
    except:
        pass

    try:
        os.mkdir(os.path.join(resultsDir, "regions"))
    except:
        pass

    # Set location of the logfile
    logFile = open("{0}/log_{1}.txt".format(resultsDir,resultsFile), "a")
    sys.stdout = logFile
    print >> sys.stderr, "log file location: {0}/log_{1}.txt".format(resultsDir, resultsFile)
    banner_width = 63  # Change this value to adjust the width as needed
    print("\n" * 3 + "#" * banner_width)
    print """
#          (           (              (        )   (    (      #
#          )\ )  *   ) )\ )    (      )\ )  ( /(   )\ ) )\ )   #
#      (  (()/(` )  /((()/(    )\    (()/(  )\()) (()/((()/(   #
#      )\  /(_))( )(_))/(_))((((_)(   /(_))((_)\   /(_))/(_))  #
#   _ ((_)(_)) (_(_())(_))   )\ _ )\ (_))_|  ((_) (_)) (_))_   #
#  | | | || |  |_   _|| _ \  (_)_\(_)| |_   / _ \ | |   |   \  #
#  | |_| || |__  | |  |   /   / _ \  | __| | (_) || |__ | |) | #
#   \___/ |____| |_|  |_|_\  /_/ \_\ |_|    \___/ |____||___/  #
#                                                              #
"""                             
    print("#" * banner_width)
    print("#{0:^{1}}#".format("", banner_width - 2))
    print("#{0:^{1}}#".format("Ultrafold ver. 1.0.1 - 5 June 2026", banner_width - 2))
    print("#{0:^{1}}#".format("Adaptation of Superfold ver. 1.2 - 21 July 2023", banner_width - 2))
    print("#{0:^{1}}#".format("Developed by George Stephenson", banner_width - 2))
    print("#{0:^{1}}#".format("", banner_width - 2)) 
    print("#{0:^{1}}#".format("starting job: " + args.safeName, banner_width - 2))
    print("#{0:^{1}}#".format(time.strftime("%c"), banner_width - 2))
    print("#{0:^{1}}#".format("", banner_width - 2))
    print("#" * banner_width + "\n\n# Job Submitted with following attributes:")
    print(args, "\n")
    
    # Run the partition function
    print >> sys.stderr, "\nstarting Partition function calculation..."
    partitionPairing = dotPlot()
    
    if not debug:
        partitionPairing = generateAndRunPartition(args.mapObj, args.DMS, args.allConstraints,
                                                    args.partitionWindowSize, args.partitionStepSize, 
                                                    args.safeName, args.SHAPEslope, 
                                                    args.SHAPEintercept, args.np, 
                                                    args.maxPairingDist)
    
    # Write the partition function file
    partitionFileName = "{0}/merged_{1}.dp".format(resultsDir, args.safeName)
    
    if not debug:
        partitionPairing.writeDP(partitionFileName)
    
    # Debug line
    if debug:
        partitionPairing = dotPlot(partitionFileName)
    
    # Get the 99% most probable pairs to use as constraints in folding
    probablePairs99 = partitionPairing.requireProb(0.004364805402450088).pairList()
    dsConstraint = {0: [], 1: []}
    for i, j in probablePairs99:
        dsConstraint[0].append(i)
        dsConstraint[1].append(j)
    
    print "Checking partitionPairing attributes..."
    print "Partition Pairing object type:", type(partitionPairing)
    print "Self length value:", getattr(partitionPairing, 'length', 'length not defined')

    # Calculate Shannon entropy
    bpShannonEntropy = partitionPairing.calcShannon()
    
    # Write the Shannon entropy in .shape format
    shannonEntropyName = "{0}/shannon_{1}.txt".format(resultsDir, args.safeName)
    writeSHAPE(bpShannonEntropy, shannonEntropyName)
    
    # Generate the folded structure model
    print >> sys.stderr, "starting Fold..."
    
    initialStructure = CT()
    if not debug:
        initialStructure = generateAndRunFold(args.mapObj, args.DMS, args.allConstraints, dsConstraint, args.foldWindowSize, 
                                              args.foldStepSize, args.safeName, args.SHAPEslope, args.SHAPEintercept, args.np, 
                                              args.maxPairingDist)
    
    # Write the folded structure
    initialStructureFileName = "{0}/merged_{1}.ct".format(resultsDir, args.safeName)
    if not debug:
        initialStructure.writeCT(initialStructureFileName)
    
    # Debug
    if debug:
        initialStructure.readCT(initialStructureFileName)
    
    # Write final files and figures
    print >> sys.stderr, "drawing figures..."
    
    # Add in former pk constraints
    pkPair = []
    for i, j in zip(args.dsConstraints[0], args.dsConstraints[1]):
        pkPair.append((i, j))
    nonPKpairs = initialStructure.pairList()
    finalStructure = CT()
    finalStructure.pair2CT(nonPKpairs + pkPair, seq=initialStructure.seq, name='finalStructure wPKs')
    finalStructureName = "{0}/merged_wPK_{1}.ct".format(resultsDir, args.safeName)
    
    # If there are pk pairs in the file, then write a second ct file with pk's included
    if pkPair:
        finalStructure.writeCT(finalStructureName)
    
    # Calculate low Shannon/SHAPE regions with expansions based on structure
    shannonShapeName = "{0}/shannonShape_{1}.pdf".format(resultsDir, args.safeName)
    
    lowSHAPEregions = mainShannonFunc(args.mapObj.origSHAPE, bpShannonEntropy, shannonShapeName, finalStructure)
    
    # Plot the arcs along with the Shannon/SHAPE reactivities
    arcFileName = "{0}/arcPlot_{1}.pdf".format(resultsDir, args.safeName)
    ensembleRNA_splitPlot(partitionPairing, initialStructure, pk=pkPair, outFile=arcFileName)
    
    # Export the structures of the low Shannon/SHAPE regions
    maxChar = len(str(lowSHAPEregions[-1][1]))
    
    # File for containing all regions
    ps_comb = "{0}/regions_{1}.ps".format(resultsDir, args.safeName)
    ps_write = open(ps_comb, "w")
    
    if args.noPVclient:
        try:
            import pvclient
        except:
            print "PVclient failed to load"
            args.drawPVclient = False
    
    for i, j in lowSHAPEregions:
        # Define file names
        print >> sys.stderr, i, j
        ct_name = "{2}/regions/region_{3}_{0:0>{maxChar}}_{1:0>{maxChar}}.ct".format(i, j, resultsDir, args.safeName, maxChar=maxChar)
        ps_name = "{2}/regions/region_{3}_{0:0>{maxChar}}_{1:0>{maxChar}}.ps".format(i, j, resultsDir, args.safeName, maxChar=maxChar)
        pvclient_name = "{2}/regions/region_{3}_{0:0>{maxChar}}_{1:0>{maxChar}}".format(i, j, resultsDir, args.safeName, maxChar=maxChar)
        
        # Write new ct file
        x = finalStructure.cutCT(i, j)
        x.name = "region {0}-{1}, ".format(i, j) + args.safeName
        x.writeCT(ct_name)
        
        # Print diagnostic information for debugging
        print "CT region name:", x.name
        print "Writing CT File:", ct_name
        print "Structure Length:", len(x.seq)
        
        # Circle plotting functions
        tmpSHAPE = args.mapObj.origSHAPE[i-1:j]
        tmpZeros = np.zeros_like(tmpSHAPE)
        
        # Debugging: Sanity check before makeCircle
        print("Debugging before makeCircle call:")
        print("- Length of structure for region:", len(x.pairList()))
        print("- Start index:", i, "End index:", j)
        
        # File lines
        lines = makeCircle(x, x, tmpZeros, tmpSHAPE, {'i': [], 'j': [], 'correl': []}, [], offset=i)
        
        w = open(ps_name, "w")
        w.write(lines)
        ps_write.write(lines)
        w.close()
        
        if args.noPVclient:
            try:
                pvclient.python_client(x, tmpSHAPE, i, pvclient_name)
            except:
                print "Structure drawing failed Region {0}-{1}".format(i, j)
    ps_write.close()
    
    runtime = "{0:.2f}".format(time.time() - startTime)
    print "\n", "#" * 51
    print "#{0:^49}#".format("job finished: " + args.safeName)
    print "#{0:^49}#".format(time.strftime("%c"))
    print "#{0:^49}#".format("Total Runtime: " + runtime + " sec.")
    print "#" * 51

def debug_print(message, **kwargs):
    print("[DEBUG]:", message)
    for key, value in kwargs.items():
        print("  - {}: {}".format(key, value))

def create_bpp2seq(mapObj, start, end, output_file):
    print("Creating .bpp2seq file:", output_file)
    try:
        # Indices for the window, always starting from 1
        indices = list(range(1, end - start + 2))  # Since range is inclusive of start, make sure it starts at 1
        sequence_data = list(zip(indices, mapObj.seq[start-1:end], mapObj.shape[start-1:end]))

        with open(output_file, 'w') as f:
            for i, nucleotide, evidence in sequence_data:
                line = "{0}\t{1}\te1\t{2:.6f}\n".format(i, nucleotide, evidence)
                f.write(line)
    except Exception as e:
        print("Error in bpp2seq creation:", str(e))

    print("bpp2seq conversion completed:", output_file)

def convert_bpp2seq_to_pairprob(bps_file, pairprob_file):
    def find_max_position(bps_file):
        max_position = 0
        with open(bps_file, 'r') as infile:
            for line in infile:
                # Only check the first column for each line
                position = int(line.strip().split()[0])
                max_position = max(max_position, position)
        return max_position

    max_position = find_max_position(bps_file)
    
    with open(bps_file, 'r') as infile, open(pairprob_file, 'w') as outfile:
        # Write the header with the max position number
        outfile.write("{}\n".format(max_position))
        outfile.write("i\tj\t-log10(Probability)\n")
        
        # Read the entire bpp2seq file line by line
        for line in infile:
            # Split the line into components
            parts = line.strip().split()
            position = parts[0]
            nucleotide = parts[1]
            bindings = parts[2:]
            
            # Process each binding information
            for binding in bindings:
                # Extract the position and probability
                bound_pos, prob_str = binding.split(':')
                prob = float(prob_str)
                
                # Calculate -log10(probability)
                if prob > 0:
                    log_prob = -math.log10(prob)
                    # Write to the output file in the format: i\tj\t-log10(Probability)
                    outfile.write("{}\t{}\t{:.5f}\n".format(position, bound_pos, log_prob))

def clean_db_file(db_file):
    """Removes the first line from the .db file."""
    try:
        # Read the contents of the .db file
        with open(db_file, 'r') as infile:
            lines = infile.readlines()

        # Always remove the first line
        lines = lines[1:]

        # Write the cleaned data back to the .db file
        with open(db_file, 'w') as outfile:
            outfile.writelines(lines)
        
        print "Cleaned the first line from {0}".format(db_file)

    except Exception as e:
        print "Error cleaning {0}: {1}".format(db_file, str(e))

def convert_db_to_ct(db_file, ct_file):
    """Converts a cleaned dot-bracket file to CT format."""
    clean_db_file(db_file)  # Clean the .db file by removing the first line before conversion
    try:
        # Use subprocess.call for Python 2.7 compatibility
        subprocess.call(['dot2ct', db_file, ct_file])
        print "Converted {0} to {1}".format(db_file, ct_file)
    except subprocess.CalledProcessError as e:
        print "Error converting {0} to CT format: {1}".format(db_file, str(e))

def ensembleRNA_splitPlot(dpObj, ctObj, pk=None, outFile="arcs.pdf"):
    
    def rgb_int2pct(rgbArr):
        out = []
        for rgb in rgbArr:
            out.append((rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0))
        return out
        
    x = dpObj
    y = ctObj
    
    # binning is in log10 scale
    #binning = [0.0,0.09691,0.5228,1.0,2.0]
    binning = [1.5228, 1.0, 0.5228, 0.09691, 0.0]
    # 3% 10% 30% 80% 100%
    
    alphaList = [0.7, 0.7, 0.7, 0.3]
    alphaList = [0.3, 0.7, 0.7, 0.7]
    #alphaList = [1.0, 1.0, 1.0, 1.0]
    #colorList  = ["red", "orange", "yellow", "green","blue", "violet"]
    
    # nat methods palett
    #colorList  = [(215, 25, 28), (253, 174, 97), (171, 221, 164), (43, 131, 186)]
    colorList  = [ (150,150,150), (255,204,0),  (72,143,205) ,(81, 184, 72)  ]
    
    # colorbrewer palett
    #colorList  = [ (43, 131, 186), (171, 221, 164), (253, 174, 97), (215, 25, 28)]
    colorList = rgb_int2pct(colorList)
    
    nucArr = []
    colors = []
    alpha  = []
    
    # bin the pairs by cutoff
    for i in range(0, len(binning)-1):
        
        probPairs = x.requireProb(binning[i],binning[i+1]).pairList()
        
        for pair in probPairs:
            
            temp = np.zeros_like(y.ct)
            temp[pair[0]-1] = pair[1]
            
            #tempCT = RNA.CT()
            #tempCT.pair2CT([pair],y.seq)
        
            #nucArr.append(tempCT.stripCT())
            nucArr.append(temp)
        
            #add a color from the choice list
            colors.append(colorList[i])
            alpha.append(alphaList[i])
    
    if pk:
        for pair in pk:
            temp = np.zeros_like(y.ct)
            temp[pair[0]-1] = pair[1]
            nucArr.append(temp)
            colors.append((0,0,0))
            alpha.append(0.8)
    #nucArr.append(y.stripCT())
    #colors.append("gray")
    
    arcplot(outPath=outFile, pairedNucArr=nucArr, arcColors=colors,seq=y.seq, alpha=alpha, maxDistance=None)


import os
import subprocess
from multiprocessing import Pool


def _runShellCommand(cmd):
    """Run a single shell command to completion.

    Module-level (and therefore picklable) so it can be dispatched by a
    multiprocessing.Pool worker. Returns (cmd, returncode, stderr).
    """
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    return (cmd, process.returncode, err)


def _dispatchCommands(commands, nprocs):
    """Run independent shell commands concurrently across up to ``nprocs`` workers.

    The per-window fold/partition jobs are independent, so they are fanned out
    instead of being run one-at-a-time. Falls back to serial execution when
    ``nprocs`` <= 1 or there is a single command. The returned list of
    (cmd, returncode, stderr) tuples is in the same order as ``commands``, so
    callers can zip it back against their job queue. See issue #2.
    """
    if not commands:
        return []
    if nprocs and int(nprocs) > 1 and len(commands) > 1:
        pool = Pool(processes=min(int(nprocs), len(commands)))
        try:
            results = pool.map(_runShellCommand, commands)
        finally:
            pool.close()
            pool.join()
        return results
    return [_runShellCommand(c) for c in commands]


def generateAndRunFold(mapObj, usedms, constraints, dsConstraints, windowSize, stepSize, prefix, shapeSlope, shapeIntercept, nprocs, maxDist):
    """
    Generates folded RNA structures for various segments, resolving conflicts to build a consensus structure.
    """
    print 'Using EternaFold for structure prediction\n'

    dirname = "fold_" + prefix
    if not os.path.exists(dirname):
        os.makedirs(dirname)

    jobQueue1 = []
    rnaLength = len(mapObj.seq)

    debug_print("Initial RNA sequence processing", rna_length=rnaLength, window_size=windowSize, step_size=stepSize)

    if rnaLength - windowSize < 200:
        cut_i, cut_j = 1, rnaLength
        fname = "{0}/{1}_{2}_{3}".format(dirname, prefix, cut_i, cut_j)
        genFiles(mapObj, constraints, dsConstraints, cut_i, cut_j, fname)

        foldCMD = "contrafold predict {0}.bpp2seq --evidence --numdatasources 1 --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 > {0}.db".format(fname)
        jobQueue1.append((foldCMD, "{0}.db".format(fname), "{0}.ct".format(fname)))
    else:
        for i in range(1, rnaLength - windowSize, stepSize):
            cut_i, cut_j = i, i + windowSize - 1
            fname = "{0}/{1}_{2}_{3}".format(dirname, prefix, cut_i, cut_j)
            genFiles(mapObj, constraints, dsConstraints, cut_i, cut_j, fname)

            foldCMD = "contrafold predict {0}.bpp2seq --evidence --numdatasources 1 --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 > {0}.db".format(fname)
            jobQueue1.append((foldCMD, "{0}.db".format(fname), "{0}.ct".format(fname)))
            debug_print("Queued job for fold generation", file_name=fname, cut_range=(cut_i, cut_j))

        for i in [-100, -50, 50, 100]:
            cut5prime_j = windowSize + i
            fname = "{0}/{1}_{2}_{3}".format(dirname, prefix, 1, cut5prime_j)
            genFiles(mapObj, constraints, dsConstraints, 1, cut5prime_j, fname)

            foldCMD = "contrafold predict {0}.bpp2seq --evidence --numdatasources 1 --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 > {0}.db".format(fname)
            jobQueue1.append((foldCMD, "{0}.db".format(fname), "{0}.ct".format(fname)))
            debug_print("Queued 5' end job for fold generation", file_name=fname, cut_range=(1, cut5prime_j))

            cut3prime_i = rnaLength - windowSize + i
            fname = "{0}/{1}_{2}_{3}".format(dirname, prefix, cut3prime_i, rnaLength)
            genFiles(mapObj, constraints, dsConstraints, cut3prime_i, rnaLength, fname)

            foldCMD = "contrafold predict {0}.bpp2seq --evidence --numdatasources 1 --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 > {0}.db".format(fname)
            jobQueue1.append((foldCMD, "{0}.db".format(fname), "{0}.ct".format(fname)))
            debug_print("Queued 3' end job for fold generation", file_name=fname, cut_range=(cut3prime_i, rnaLength))

    # run the fold commands concurrently (each window is independent); honors --np
    foldResults = _dispatchCommands([job[0] for job in jobQueue1], nprocs)

    # convert successful windows to CT only after the pool has fully drained
    for (foldCMD, returncode, err), (_cmd, db_filename, ct_filename) in zip(foldResults, jobQueue1):
        if returncode != 0:
            print "Error executing command: ", foldCMD
            print "Error details: ", err
        else:
            print "Successfully executed command: ", foldCMD
            convert_db_to_ct(db_filename, ct_filename)

    targetRNA = CT()
    targetRNA.pair2CT([], "".join(mapObj.seq))

    debug_print("Assembling target RNA from CT files", directory=dirname, prefix=prefix)

    targetFolderRNAs, baseCount = MasterModel_readAndRenumberAll(targetRNA, dirname, prefix)
    pairs = MasterModel_findOverlapPairs(targetFolderRNAs, baseCount)

    debug_print("Constructing master model structure", pair_count=len(pairs))

    masterModelStructure = CT()
    masterModelStructure.pair2CT(pairs, targetRNA.seq, 'ConsensusModel')

    return masterModelStructure
    
def generateAndRunPartition(mapObj, usedms, constraints, windowSize, stepSize, prefix, shapeSlope, shapeIntercept, nprocs, maxDist):
    print 'Using EternaFold for the partition function\n'

    dirname = "partition_" + prefix
    if not os.path.exists(dirname):
        os.makedirs(dirname)
        print "Created directory:", dirname
    else:
        print "Using existing directory:", dirname

    rnaLength = len(mapObj.seq)
    print "Initializing partition function calculation"
    print "Expected length of the sequence:", len(mapObj.seq)

    jobQueue1 = []

    def addJobToQueue(cut_i, cut_j, fname):
        print "Processing segment from {} to {}".format(cut_i, cut_j)
        create_bpp2seq(mapObj, cut_i, cut_j, "{0}.bpp2seq".format(fname))
        print "Generated files for:", fname

        output_bps_file = "{0}/{1}.bps".format(dirname, fname)
        cutoff_value = "0.000001"

        # --evidence makes contrafold actually use the SHAPE/DMS reactivity column of the
        # .bpp2seq file. Without it the partition posteriors (and therefore the merged dot
        # plot, the 99% constraint pairs, and the Shannon-entropy/region analysis) are
        # computed sequence-only. See issue #1.
        foldCMD = "contrafold predict {0}.bpp2seq --evidence --numdatasources 1 --params /opt/EternaFold/parameters/EternaFoldParams_PLUS_POTENTIALS.v1 --posteriors {1} {2}".format(fname, cutoff_value, output_bps_file)
        jobQueue1.append(foldCMD)

    if rnaLength - windowSize < 200:
        cut_i, cut_j = 1, rnaLength
        fname = "{0}_{1}_{2}".format(prefix, cut_i, cut_j)
        addJobToQueue(cut_i, cut_j, fname)
    else:
        for i in range(0, rnaLength - windowSize + 1, stepSize):
            cut_i = i + 1
            cut_j = min(i + windowSize, rnaLength)
            fname = "{0}_{1}_{2}".format(prefix, cut_i, cut_j)
            addJobToQueue(cut_i, cut_j, fname)

    # run the partition commands concurrently (each window is independent); honors --np
    for cmd, returncode, err in _dispatchCommands(jobQueue1, nprocs):
        if returncode != 0:
            print "Error executing command: ", cmd
            print "Error details: ", err
        else:
            print "Successfully executed command: ", cmd

    bps_files = [f for f in os.listdir(dirname) if f.endswith('.bps')]
    if not bps_files:
        print "No .bps files were generated. Something might have gone wrong during execution."
        return None

    print "Generated .bps files:", bps_files

    for bps_file in bps_files:
        bps_filepath = os.path.join(dirname, bps_file)
        dp_filepath = bps_filepath.replace('.bps', '.dp')
        convert_bpp2seq_to_pairprob(bps_filepath, dp_filepath)
        print "Converted {} to {}".format(bps_file, dp_filepath)

    dpObject = mainAssemble(dirname, trim=300)
    print "dpObject length initialized to:", getattr(dpObject, 'length', "No length attribute found")
    assert dpObject.length is not None, "dpObject length should not be None"

    return dpObject

def mainAssemble(folderPath, trim=300):
    print("Checking files in {0}".format(folderPath))
    
    dp_files = sorted([f for f in os.listdir(folderPath) if f.endswith('.bps')])
    for dpFile in dp_files:
        print("Reading file: {0}".format(dpFile))

    if not dp_files:
        print("No .bps files found in directory: {0}".format(folderPath))
        return dotPlot()  # or raise an error if this should not happen

    # Initialize handling of .bps files into dp objects
    print("Begin assembly of files into dotPlot objects")
    targetDP = {}
    
    for num, dpFileName in enumerate(dp_files, start=1):
        dp = dotPlot(os.path.join(folderPath, dpFileName))
        
        # Debug print basic info from dp object or raise error if invalid
        print("Processed: {0} with initial length: {1}".format(dpFileName, getattr(dp, 'length', 'N/A')))
        
        start = int(dpFileName.split("_")[-2])
        end = int(dpFileName.split("_")[-1].split(".")[0])
        targetDP[(start, end)] = dp

        # Debugging Detail
        if len(dp.dp['i']) == 0 or len(dp.dp['j']) == 0:
            print("Warning: Empty dp for {0}".format(dpFileName))
        if dp.length is None:
            print("Error: Missing length attribute in {0}".format(dpFileName))

    if not targetDP:
        raise RuntimeError("Failed to load any valid dp files!")
    
    firstDP = min(targetDP.keys(), key=lambda x: x[0])[0]
    lastDP = max(targetDP.keys(), key=lambda x: x[1])[1]
    print("First DP start: {0}".format(firstDP))
    print("Last DP end: {0}".format(lastDP))

    # Create and fill finalDP object
    finalDP = dotPlot(name="assembled dotPlot", length=lastDP)
    
    print("Initialized finalDP with length: {0}".format(lastDP))

    for dpKey in targetDP.keys():
        dp = targetDP[dpKey]
        print("Trimming window: {0}".format(dpKey))

        if dpKey[0] == firstDP:
            dp = dp.trimEnds(trim, which='3prime')
        elif dpKey[1] == lastDP:
            dp = dp.trimEnds(trim, which='5prime')
        else:
            dp = dp.trimEnds(trim)

        dp.dp['i'] += dpKey[0] - 1
        dp.dp['j'] += dpKey[0] - 1

        finalDP.dp['i'] = np.append(finalDP.dp['i'], dp.dp['i'])
        finalDP.dp['j'] = np.append(finalDP.dp['j'], dp.dp['j'])
        finalDP.dp['logBP'] = np.append(finalDP.dp['logBP'], dp.dp['logBP'])

    print("File assembly complete. Final coverage being computed.")
    finalDP = concatonateDP(finalDP, [(k[0], k[1]) for k in targetDP.keys()])
    print("Concatenation completed. Verified FinalDP with length: {0}".format(finalDP.length))

    return finalDP
    
    
def runCheck():
    """
    check to see if necessary commands are available to call
    """
    neededCmds = ["Fold", "partition", "ProbabilityPlot"]
    count = 0
    
    for each in neededCmds:
        try:
            out, err = "", ""
            subprocess.call([each], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            count += 1
        except OSError:
            print "Program {0} not found in the path".format(each)
    
    if len(neededCmds) != count:
        print "...exiting"
        sys.exit()
    
    try:
        # get the data path and test to see if it is real
        datapath = os.environ.get("DATAPATH")
        os.listdir(datapath)
    except:
        print "DATAPATH is not set. RNAstructure will not run"
        print "...exiting"
        sys.exit()


def parseArgs():
    
    def parseTXT(fIN):
        data = {}
        lineNum = 0
        for line in open(fIN, "rU").readlines():
            x = line.rstrip().split()
            
            try:
                x = map(int,x)
            except:
                print "Unexpected character in {0}...exiting".format(fIN)
                return 0
            
            # initialize an array obj for the first line
            if lineNum == 0:
                for i in range(len(x)):
                    data[i] = [x[i]]
            
            # populate the array obj
            else:
                for i in range(len(x)):
                    data[i].append(x[i])
            
            lineNum += 1
        
        
        return data
    
    def shapeEnergy(x,slope,intercept):
        out = []
        for i in x:
            if i<-500:
                out.append(-999)
                continue
            if -500<i<0:i=0.0
            g = slope*np.log(i+1)+intercept
            out.append(g)
        return np.array(out)
    
    def differentialEnergy(x,a,b,zfactor):
        zfactor = np.array(zfactor)
        
        # set -inf and nan to non significant zfactors
        zfactor[np.isinf(zfactor)] = -999
        zfactor[np.isnan(zfactor)] = -999
        
        out = []
        for i in x:
            if i<-500:
                out.append(-999)
                continue
            #slow fit; linear so easy
            if i >= 0:
                g = a*i+b
            #slow case
            if i < 0:
                g = -999#c*i+d
                #c = abs(i)
                #if c > 0.2:
                #    g = -0.620*np.log(func(c,f1[0],f1[1],f1[2])/func(c,f2[0],f2[1],f2[2]))
                #else:
                #    g = 2.57275425027 * c + 0.0239
            out.append(g)
        return np.array(out)*(zfactor>0)
    
    def fakeSHAPE(shape,diff,slope,intercept):
        #shape_f,diff_fmap=(float(shape)),map(float(diff))
        #print shape
        out = []
        for i,j in zip(shape,diff):
            if i < -500 and j<-500:
                out.append(-999)
                continue
            if i < -500:
                g = j
            if j < -500:
                g = i
            if i >-500 and j>-500:
                g = i + j
            #out.append(g)
            out.append(np.exp( (g-intercept) / slope ) -1.0)
        return out

    arg = argparse.ArgumentParser(description="SuperFold takes a windowing approach to break up the folding of large RNAs. Dividing the folding of a large RNA into smaller segments allows modern multi-core workstations to model RNA structures in a modest amount of clock-time. See README file for further details and file descriptions", epilog="SuperFold v1.0 by Gregg Rice ( gmr@unc.edu )")
    arg.add_argument('profileFile', type=str, help='Input profile.txt file for conversion to .bpp2seq')
    arg.add_argument('--DMS', action='store_true', default=False, help='Using DMS probing data generated by ShapeMapper 2.2 with --dms flag')
    arg.add_argument('--ssRegion', type=str, help='file containing forced single stranded regions')
    arg.add_argument('--pkRegion', type=str, help='text file containing pseudoknotted basepairs:\npaired nucleotides on each line seperated by whitespace. e.g.\n\n1 50(newline)2 49(newline)...')
    arg.add_argument('--np', type=int, default=2, help='number of processors to use, default:2')
    arg.add_argument('--SHAPEslope',type=float,default=1.8, help='SHAPE pseudofreeenergy slope, default:1.8')
    arg.add_argument('--SHAPEintercept',type=float,default=-0.6,help='SHAPE pseudofreeenergy intercept, default:-0.6')
    arg.add_argument('--differentialFile',type=str, help='.mapd file containing NMIA-1M6 calculated values')
    arg.add_argument('--differentialSlope',type=float,default=2.1,help='differential SHAPE slope, default:2.1')
    arg.add_argument('--trimInterior',type=int,default=300, help='number of nucleotides to trim to improve negative end effects during windowed folding, default:300')
    arg.add_argument('--partitionWindowSize',type=int,default=1200, help='length of the partition window size, default:1200')
    arg.add_argument('--partitionStepSize',type=int,default=100, help='spacing between partition windows, default:100')
    arg.add_argument('--foldWindowSize',type=int,default=3000, help='length of the Fold window size, default:3000')
    arg.add_argument('--foldStepSize',type=int,default=300, help='spacing between Fold windows, default:300')
    arg.add_argument('--maxPairingDist', type=int, default=600, help='Maximum pairing distance for partition and Fold, default:600')
    arg.add_argument('--noPVclient', action='store_false', help="Don't draw secondary structures using PVclient")
    
    o = arg.parse_args()
    
    # Convert profile file to map object
    mapfile = convertProfileToShapeMap(o.profileFile)
    o.mapObj = mapfile
    
    # Keep original logic for SHAPE handling
    o.mapObj.origSHAPE = np.array(o.mapObj.shape)

    if o.differentialFile:
        o.diffMapFile = shapeMAP(o.differentialFile)
        
        calcSHAPEenergy = shapeEnergy(mapfile.shape,o.SHAPEslope,o.SHAPEintercept)
        calcDiffEnergy  = differentialEnergy(o.diffMapFile.shape,o.differentialSlope,0,o.diffMapFile.zfactor)
        
        calcFakeShape   = fakeSHAPE(calcSHAPEenergy,calcDiffEnergy,o.SHAPEslope,o.SHAPEintercept)
        
        o.mapObj.shape = calcFakeShape
        
        #print o.diffMapFile.zfactor
    
    # read the constraint files
    
    # first the ss constraints
    try:
        ss = parseTXT(o.ssRegion)
        if ss == 0:
            sys.exit()
    except:
        if o.ssRegion is None: ss = {0:[]}
        else: sys.exit()

    o.ssConstraints = ss

    try:
        ds = parseTXT(o.pkRegion)
        if ds == 0:
            sys.exit()
        if len(ds[0]) != len(ds[1]):
            print "pkRegion file incorrectly formatted...exiting"
            sys.exit()
    except:
        if o.pkRegion is None: ds = {0:[], 1:[]}
        else: sys.exit()

    o.dsConstraints = ds
    
    # Concatenate constraints
    allConst = ss[0] + ds[0] + ds[1]
    o.allConstraints = allConst
    
    # Use the correct attribute ('profileFile') instead of 'mapFile'
    m = hashlib.md5()
    m.update(str(o.profileFile))
    m.update(str(o.DMS))
    m.update(str(o.ssRegion))
    m.update(str(o.pkRegion))
    m.update(str(o.differentialFile))
    m.update(str(o.foldWindowSize))
    m.update(str(o.partitionWindowSize))
    m.update(str(o.maxPairingDist))
    m.update(str(o.partitionStepSize))
    
    o.safeName = o.profileFile.split('.')[0] + "_" + m.hexdigest()[:4]

    return o


def convertProfileToShapeMap(profileFile):
    # Load the map file considering no headers, so just plain reading
    profileData = pd.read_csv(profileFile, sep='\s+', header=None, names=['Position', 'Norm_profile', 'Std_err', 'Sequence'])

    # Debugging: Print the column names to verify they are read correctly
    print("Columns available in profile data: ", profileData.columns.tolist())

    mapObj = shapeMAP(None)
    mapObj.ntNum = map(int, profileData['Position'].tolist())
    mapObj.seq = list(profileData['Sequence'].apply(lambda x: x.upper().replace('T', 'U')))
    mapObj.shape = map(float, profileData['Norm_profile'].tolist())
    mapObj.stdErr = map(float, profileData['Std_err'].tolist())

    return mapObj


def genFiles(mapObj, ssConstraints, dsConstraints, ntStart, ntEnd, fName):
    def shapeFile(SHAPEdata, fOUT):
        """
        Writes a .SHAPE file compatible with RNAstructure
        """
        with open(fOUT, "w") as w:
            for i, shape_value in enumerate(SHAPEdata):
                w.write("{0}\t{1}\n".format(i + 1, shape_value))
        return fOUT
        
    def seqFile(sequence, fOUT, name=None):
        """
        Write a seq file compatible with RNAstructure format
        """
        if not name:
            name = str(fOUT)
        with open(fOUT, "w") as w:
            w.write(";\n\n{0}\n\n".format(name))
            for i, nucleotide in enumerate(sequence):
                w.write(nucleotide)
                if (i + 1) % 50 == 0:
                    w.write("\n")
                elif (i + 1) % 10 == 0:
                    w.write(" ")
            w.write("1\n")
        return fOUT
    
    def constraintFile(ssConstraint, dsConstraint, fOUT):
        """
        Writes a constraint file compatible with RNAstructure
        """
        with open(fOUT, "w") as w:
            w.write("DS:\n-1\nSS:\n")
            for const in ssConstraint:
                w.write("{0}\n".format(const))
            w.write("-1\nMod:\n-1\nPairs:\n")
            for i, j in zip(dsConstraint[0], dsConstraint[1]):
                w.write("{0} {1}\n".format(i, j))
            w.write("-1 -1\nFMN:\n-1\nForbids:\n-1 -1\nMicroarray Constraints:\n0\n")
        return fOUT
    
    # Renumber constraints
    renumSS = [i - (ntStart - 1) for i in ssConstraints if ntStart <= i <= ntEnd]
    renumDS = {0: [], 1: []}

    for i, j in zip(dsConstraints[0], dsConstraints[1]):
        if ntStart <= i <= ntEnd and ntStart <= j <= ntEnd:
            renumDS[0].append(i - (ntStart - 1))
            renumDS[1].append(j - (ntStart - 1))
        elif ntStart <= j <= ntEnd:
            renumSS.append(j - (ntStart - 1))
        elif ntStart <= i <= ntEnd:
            renumSS.append(i - (ntStart - 1))
    
    renumSS.sort()

    # Generate necessary files
    shapeFile(mapObj.shape[ntStart - 1:ntEnd], fName + ".shape")
    seqFile(mapObj.seq[ntStart - 1:ntEnd], fName + ".seq", name=fName)
    constraintFile(renumSS, renumDS, fName + ".const")

    # Create the .bpp2seq file for EternaFold
    create_bpp2seq(mapObj, ntStart, ntEnd, fName + ".bpp2seq")
    

def mainAssemble(folderPath, trim=300):
    print "Assembling dotPlot objects from folder:", folderPath

    targetDP = {}
    dp_files = sorted([f for f in os.listdir(folderPath) if f.endswith('.dp')])

    if not dp_files:
        print "No .dp files found in directory:", folderPath
        return dotPlot()  # Assuming the dotPlot can be initialized without arguments

    numFiles = len(dp_files)
    print "Number of .dp files found:", numFiles

    for num, dpFileName in enumerate(dp_files, start=1):
        print "Reading file {}/{}: {}".format(num, numFiles, dpFileName)
        dp = dotPlot(os.path.join(folderPath, dpFileName))

        start = int(dpFileName.split("_")[-2])
        end = int(dpFileName.split("_")[-1].split(".")[0])
        targetDP[(start, end)] = dp

    if not targetDP:
        print "Error: No valid dp files were loaded."
        return dotPlot()  # Assuming the dotPlot can be initialized without arguments
    
    firstDP = min(targetDP.keys(), key=lambda x: x[0])[0]
    lastDP = max(targetDP.keys(), key=lambda x: x[1])[1]
    print "First DP start:", firstDP
    print "Last DP end:", lastDP

    # Initialize the dotPlot without any unspecified arguments
    finalDP = dotPlot()  # Assume simple initialization, check class definition if different

    # If necessary, manually set 'length'
    if hasattr(finalDP, 'length'):
        finalDP.length = lastDP
    else:
        print "Warning: finalDP object does not have a 'length' attribute."

    print "Initialized finalDP with expected length:", lastDP
    
    coverage = []

    print "Trimming and resorting..."
    
    for dpKey in targetDP.keys():
        print "Processing window from {} to {}".format(*dpKey)
        dp = targetDP[dpKey]
        
        if dpKey[0] == firstDP:
            dp = dp.trimEnds(trim, which='3prime')
            coverage.append((dpKey[0], dpKey[1] - (trim - 1)))
        elif dpKey[1] == lastDP:
            dp = dp.trimEnds(trim, which='5prime')
            coverage.append((dpKey[0] + (trim - 1), dpKey[1]))
        else:
            dp = dp.trimEnds(trim)
            coverage.append((dpKey[0] + (trim - 1), dpKey[1] - (trim - 1)))

        dp.dp['i'] += dpKey[0] - 1
        dp.dp['j'] += dpKey[0] - 1

        finalDP.dp['i'] = np.append(finalDP.dp['i'], dp.dp['i'])
        finalDP.dp['j'] = np.append(finalDP.dp['j'], dp.dp['j'])
        finalDP.dp['logBP'] = np.append(finalDP.dp['logBP'], dp.dp['logBP'])

    print "Coverage details:", coverage
    
    finalDP = concatonateDP(finalDP, coverage)
    print "Assembly complete. Final coverage reported."
    return finalDP


def concatonateDP(dpObj, coverage):
    """
    merges duplicate entries in a dp file by averaging
    """
    def calcCoverage(i, j, coverage):
        n = 0
        if j-i >= 600: return 500
        for a,b in coverage:
            if a <= i <= b and a<= j <= b:
                n+=1
        return n
        
    #print dpObj
    #print coverage
    dpObj = dpObj.requireProb(2)
    
    # make a shortcut
    dp = dpObj.dp
    
    # maxDist is the max search space
    maxDist = 600
    
    # construct the return object
    outObj        = dotPlot()
    outObj.length = dpObj.length
    outObj.name   = dpObj.name
    
    # grab the potential pairs to limit looping space
    pairs = set(dpObj.pairList())
    
    fullSize = len(pairs)
    outObj.dp['i'] = np.zeros(fullSize)
    outObj.dp['j'] = np.zeros(fullSize)
    outObj.dp['logBP'] = np.zeros(fullSize)
    outObj.dp['coverage'] = np.zeros(fullSize)
    
    n = 0
    
    oldFilter = np.zeros_like(dp['logBP'])
    dp['logBP'] = 10**( -dp['logBP'])
    
    print "merging dotplots..."
    for i,j in pairs:
        i = int(i)
        j = int(j)
        
            
        # remove any long distance base pairs
        #if j-i > maxDist: continue
        dpFilter = ( dp['i']== i ) * ( dp['j'] == j )
        
        
        oldFilter += dpFilter
        # skip nonexisting pairs
        entries = np.sum(dpFilter)
        outObj.dp['i'][n] = i
        outObj.dp['j'][n] = j
        outObj.dp['logBP'][n] = 0.0
        outObj.dp['coverage'][n] = calcCoverage(i, j, coverage)
        if entries == 0: continue
        #elif entries == 1:
            #outObj.dp['i'] = np.append(outObj.dp['i'], i )
            #outObj.dp['j'] = np.append(outObj.dp['j'], j )
            #outObj.dp['logBP'] = np.append(outObj.dp['logBP'], dp['logBP'][dpFilter] )
        else:
            #outObj.dp['i'] = np.append(outObj.dp['i'], i )
            #outObj.dp['j'] = np.append(outObj.dp['j'], j )
            #outObj.dp['logBP'] = np.append(outObj.dp['logBP'], np.average(dp['logBP'][dpFilter]) )
            #outObj.dp['logBP'][n] = np.average(dp['logBP'][dpFilter])
            outObj.dp['logBP'][n] = np.sum(dp['logBP'][dpFilter])/outObj.dp['coverage'][n]
            #print np.average(dp['logBP'][dpFilter]), dp['logBP'][dpFilter]
        
        #remove already searched from full list
        #debugging
        n+=1
        progress(n, fullSize)
        if n%1000 == 0:
            dp['i'] = np.delete(dp['i'],np.nonzero(oldFilter))
            dp['j'] = np.delete(dp['j'],np.nonzero(oldFilter))
            dp['logBP'] = np.delete(dp['logBP'],np.nonzero(oldFilter))
            oldFilter = np.zeros_like(dp['logBP'])
            #print n, len(dp['logBP'])
    
    print "DONE!"
    
    
    outObj.dp['logBP'] = -np.log10(outObj.dp['logBP'])
    #print np.sum(outObj.dp['coverage'] ==2)
    
    return outObj
    

def progress(num,outof):
    num = float(num)
    outof = float(outof)
    width = 30
    line = '['
    
    meter =  ''.join(['=']*int(num/outof*width)) + ''.join([' ']*int((outof-num)/outof*width))
    line += meter[:width-4]
    line += ']'
    
    line += ' %s / %s' % (int(num),int(outof))
    if num == 1:
        sys.stdout.write(line)
    elif num==outof:
        sys.stdout.write('\r'+line)
        sys.stdout.flush()
        sys.stdout.write("\n")
    else:
        sys.stdout.write('\r'+line)
        sys.stdout.flush()


def MasterModel_readAndRenumberAll(targetCT,folder, prefix):
    """go through the folder of ct files
       read and renumber them in the context
       of the big sequence"""
    targetCTfiles = []
    
    #initialize bp overlap object
    #stores how many times particular base is possible
    bpoverlap = np.zeros(len(targetCT.ct))
    
    for i in os.listdir(folder):
        # skip non-ct files
        if i[-2:] != 'ct': continue
        
        # check file prefix
        checkLen = len(prefix)
        if i[:checkLen] != prefix: continue
        
        #load the fold
        loadedCT = CT(folder+"/"+i)
        #renumber it in context of the target genome
        paddedFold,pos = padCT(loadedCT,targetCT,giveAlignment=True)
        
        #add one to each position if it is contained in
        #the aligned ct
        for i in range(pos,pos+len(loadedCT.ct)):
            bpoverlap[i]+=1
        
        #add it to the array
        targetCTfiles.append(paddedFold)
    
    return targetCTfiles, bpoverlap

def MasterModel_findOverlapPairs(ctObjectList, baseCount):
    """
    Analyze CT objects to find consensus base pairs, emphasizing pairs appearing in overlapping windows.
    :param ctObjectList: List of CT objects containing folding information.
    :param baseCount: Expected base count for each nucleotide.
    :return: List of consensus base pairs (i, j).
    """
    bpairs = {}
    debug_print("Starting overlap pair analysis")

    for rna in ctObjectList:
        for nuc in range(len(rna.ct)):
            if rna.ct[nuc] == 0:
                continue
            i, j = nuc + 1, rna.ct[nuc]
            if j < i:
                continue
            if (i, j) not in bpairs:
                bpairs[(i, j)] = 0
            bpairs[(i, j)] += 1

    overlap_threshold = 0.5
    outpairs = {}

    for key in bpairs.keys():
        i, j = key
        min_base_count = min(baseCount[i - 1], baseCount[j - 1])
        if min_base_count > 0 and (bpairs[key] / float(min_base_count)) > overlap_threshold:
            outpairs[key] = bpairs[key]

    debug_print("Completed overlap pair analysis", outpairs_found=len(outpairs))
    return outpairs.keys()

############################
# SHANNON SHAPE SEARCH FUNCTIONS
############################

def mainShannonFunc(shapeReact, shannonEntropy, saveName, ctStruct):
    
    def findTransitions(react, cutoff):
        transitions = []
        prev = 1
        for i in range(0, len(react)):
            curr = (react[i] > cutoff)
            if np.isnan(react[i]):
                curr = True
            if curr != prev:
                transitions.append((i, curr))
                prev = curr
        print("[DEBUG] Transitions found:", transitions)
        return transitions

    def cullTransitions(transitions, minLength):
        dist = []
        culled = []
        skip = False
        for i in range(len(transitions) - 1):
            dist.append(transitions[i + 1][0] - transitions[i][0])
        for i, distance in enumerate(dist):
            if skip:
                skip = False
                continue
            if distance < minLength:
                skip = True
                print("[DEBUG] Culling transition at index", i, 
                      "due to minimum length requirement. Distance:", distance)
                continue
            culled.append(transitions[i])
        culled.append(transitions[-1])
        print("[DEBUG] Culled Transitions:", culled)
        return culled

    def selectCutsites(trans1, trans2, seqLength, minlength=40):
        def genStretch(shortlist, seqLength, high=True):
            addnums = 1 - abs(shortlist[0][1])
            if not high:
                addnums = abs(addnums - 1)
            addList = []
            for i in range(0, seqLength + 1):
                if addnums:
                    addList.append(i)
                else:
                    addList.append(0)
                for j in shortlist:
                    if j[0] == i:
                        addnums = abs(j[1])
                        if not high:
                            addnums = abs(1 - j[1])
            print("[DEBUG] Generated stretch list for high={}: {}".format(high, addList))
            return addList
        
        t1 = np.array(genStretch(trans1, seqLength, high=False))
        t2 = np.array(genStretch(trans2, seqLength, high=False))
        
        combined = (t1 * t2) > 0
        transitions = cullTransitions(findTransitions(combined, 0.5), minlength)
        culled_combined = genStretch(transitions, seqLength)
        print("[DEBUG] Final combined cutsites derived:", culled_combined)
        
        return culled_combined

    def movingWindow(dataIn, degree):
        out = np.zeros(len(dataIn))
        dataIn = np.array(dataIn)
        dataIn[dataIn < -500] = np.nan
        for i in range(degree, len(dataIn) - degree):
            sele = dataIn[i - degree:i + degree + 1]
            mask = np.isfinite(sele)
            if np.any(mask):
                out[i] = np.median(sele[mask])
        for i in range(degree):
            out[i] = float(out[degree])
        for i in range(len(dataIn) - degree, len(dataIn)):
            out[i] = float(out[len(dataIn) - degree - 1])
        print("[DEBUG] Moving window results:", out)
        return out

    print("[INIT] Starting mainShannonFunc")
    shannonUnscaled = shannonEntropy
    shapeUnscaled = shapeReact

    shape = movingWindow(shapeUnscaled, 25)
    shannon = movingWindow(shannonUnscaled, 25)

    mask2 = np.isfinite(shape)
    shapeTrans = findTransitions(shape, np.median(shape[mask2]) / 1)
    shannonTrans = findTransitions(shannon, np.median(shannon))

    shape_culled = cullTransitions(shapeTrans, 10)
    shannon_culled = cullTransitions(shannonTrans, 10)

    a = np.array(selectCutsites(shape_culled, shannon_culled, len(shape)))
    b = a > 0

    print "####### shannonShapeTransitions #######"
    regions = findTransitions(b, 0.5)

    x = np.linspace(0, len(shape), len(shape))
    fig = plt.gcf()
    fig.set_size_inches(24, 7)
    pdf = PdfPages(saveName)
    plt.subplots_adjust(left=0.05, right=0.95, bottom=0.06, top=0.98)
    ax = plt.subplot(111)

    az = fig.add_axes()
    plt.xlabel('Nucleotide', fontsize=10)
    plt.ylabel('Shannon entropy', fontsize=10)
    plt.setp(ax.get_xticklabels(), fontsize=8)
    plt.setp(ax.get_yticklabels(), fontsize=8)

    majLoc = MultipleLocator(500)
    minorLoc = MultipleLocator(100)
    yMajLoc = MultipleLocator(0.1)
    YminorLoc = MultipleLocator(0.05)
    yMajLoc2 = MultipleLocator(0.1)
    YminorLoc2 = MultipleLocator(0.05)
    ax.xaxis.set_major_locator(majLoc)
    ax.xaxis.set_minor_locator(minorLoc)
    ax.yaxis.set_major_locator(yMajLoc)
    ax.yaxis.set_minor_locator(YminorLoc)

    ax.spines['right'].set_color('none')
    ax.spines['top'].set_color('none')
    ax.spines['left'].set_color('none')

    plt.ylim(0, 2)
    plt.xlim(0, 5000)

    lowShannonLowSHAPE = plt.fill_between(range(len(b)), b * 3.0, 0, alpha=0.2, color='blue', label="Low Shannon low SHAPE")
    
    plt.plot(x, np.median(shannon) * np.ones(len(x)), color='y')
    shannonPlot = plt.fill_between(x, shannon, np.zeros_like(shannon), facecolor='brown', interpolate=True, label="Shannon")

    ax2 = ax.twinx()
    shape_med = np.median(shape[mask2])
    shapeForPlotting = shape[:]
    for i in range(len(shapeForPlotting)):
        if np.isnan(shapeForPlotting[i]):
            shapeForPlotting[i] = shape_med

    shapePlot = ax2.fill_between(x, shapeForPlotting, shape_med, facecolor='black', interpolate=True, label="SHAPE")
    
    plt.ylabel('SHAPE reactivity')
    plt.ylim(-1, 1)
    plt.legend([lowShannonLowSHAPE, shapePlot, shannonPlot], ["Low SHAPE low Shannon", "SHAPE", "Shannon"], loc=2)
    ax2.yaxis.set_major_locator(yMajLoc2)
    ax2.yaxis.set_minor_locator(YminorLoc2)
    
    pdf.savefig(dpi=300, transparent=True)
    plt.xlim(5000, len(x))
    pdf.savefig(dpi=300, transparent=True)
    plt.xlim(0, len(x))
    pdf.close()
    plt.savefig(saveName, dpi=300, transparent=True)

    n = 0
    regionPair = []

    try:
        if len(regions) > 0 and regions[0][1] == False:
            if regions[0][0] != 0:
                regionPair.append([1, regions[0][0]])
            n = 1

        for i in range(n, len(regions) - n, 2):
            regionPair.append([regions[i][0], regions[i + 1][0]])

        if len(regions) > 0 and regions[-1][1] == True:
            regionPair.append([regions[-1][0], len(shape)])

    except Exception as e:
        print "[ERROR] An exception occurred while defining regions:", str(e)
        regionPair.append([1, len(shape)])

    print "Unexpanded regions:"
    for i, j in regionPair:
        print i, "-", j

    allPair = ctStruct.pairList()
    expandedRegion = []

    for i, j in regionPair:
        new_i, new_j = i, j
        print "[EXPAND] Expanding region:", i, "-", j

        for k, l in allPair:
            if k < i and l > i:
                if k < new_i:
                    new_i = k
                if l > new_j:
                    new_j = l
            if k < j and l > j:
                if k < new_i:
                    new_i = k
                if l > new_j:
                    new_j = l
            print "[DEBUG] Checked pair ({}, {}). Updated range: {}-{}".format(k, l, new_i, new_j)

        expandedRegion.append((new_i, new_j))

    print "Expanded regions:"
    for i, j in expandedRegion:
        print i, "-", j

    return expandedRegion
    


if __name__ == '__main__':
    main()
