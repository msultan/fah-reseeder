#!/bin/env python
from __future__ import print_function, division
import os
import glob
import sys
import tarfile
from mdtraj.formats.dcd import DCDTrajectoryFile
import mdtraj as md
import tables
from mdtraj.utils.contextmanagers import enter_temp_directory
from mdtraj.utils import six
from msmbuilder.utils import verbosedump,verboseload


##The concatenation code is directly from F@H Munge. Thanks to @kylebeauchamp.
def keynat(string):
    '''A natural sort helper function for sort() and sorted()
    without using regular expression.
    >>> items = ('Z', 'a', '10', '1', '9')
    >>> sorted(items)
    ['1', '10', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1', '9', '10', 'Z', 'a']
    '''
    r = []
    for c in string:
        try:
            c = int(c)
            try:
                r[-1] = r[-1] * 10 + c
            except:
                r.append(c)
        except:
            r.append(c)
    return r



def concatenate_core17(dir,run,clone):
    """Concatenate tar bzipped XTC files created by Folding@Home Core17.

    Parameters
    ----------
    path : str
        Path to directory containing "results-*.tar.bz2".  E.g. a single CLONE directory.
    top : mdtraj.Topology
        Topology for system
    output_filename : str
        Filename of output HDF5 file to generate.

    Notes
    -----
    We use HDF5 because it provides an easy way to store the metadata associated
    with which files have already been processed.
    """
    if dir is None:
        dir="/nobackup/msultan/research/kinase/her_kinase/fah_data/PROJ9104"

    path = os.path.abspath(dir)+"/RUN%d/CLONE%d/"%(run,clone)
    top = md.load( os.path.abspath(dir)+"/topologies/%d.pdb"%run)
    output_filename =  os.path.abspath(dir)+"/trajectories/%d_%d.dcd"%(run,clone)

    already_processed_filename =  os.path.abspath(dir)+"/trajectories/processed_trajectories/%d_%d.txt"\
                                                                                            %(run,clone)
    print(path,top,output_filename)
    glob_input = os.path.join(path, "results-*.tar.bz2")
    filenames = glob.glob(glob_input)
    filenames = sorted(filenames, key=keynat)

    if len(filenames) <= 0:
        return

    trj_file = None
    if os.path.exists(output_filename):
        trj_file = md.load(output_filename,top=top)

    with open(already_processed_filename, 'a') as infile:

        for filename in filenames:
            if not os.path.basename(filename) in open(already_processed_filename).read():
                with enter_temp_directory():
                    archive = tarfile.open(filename, mode='r:bz2')
                    archive.extract("positions.xtc")
                    trj = md.load("positions.xtc", top=top)
                    if trj_file is None:
                        trj_file =  trj
                    else:
                        trj_file += trj
                infile.writelines(os.path.basename(filename)+'\n')
            else:
                print("Already Processed %s"%filename)
                continue

    trj_file.save_dcd(output_filename)
    return




def sanity_test(dir):
    if not os.path.isdir(os.path.join(dir+"/topologies")):
        #print("Toplogies Folder Doesnt exist")
        sys.exit("Toplogies Folder Doesnt exist.Exiting!")


    if not os.path.isdir(os.path.join(dir+"/trajectories")):
        print("Trajectories folder doesnt exist.Creating")
        os.makedirs(os.path.join(dir+"/trajectories"))

    if not os.path.exists(os.path.join(dir+"/trajectories/processed_trajectories/")):
        print("Processed trajectories folder doesn't exist.Creating.")
        os.makedirs(os.path.join(dir+"/trajectories/processed_trajectories/"))
    return

def extract_project_wrapper(dir,view):

    sanity_test(dir)

    runs=len(glob.glob(dir+"/RUN*"))
    clones=len(glob.glob(dir+"/RUN0/CLONE*"))
    print("Found %d runs and %d clones in %s"%(runs,clones,dir))
    print("Using %d cores to parallelize"%len(view))

    jobs = [(dir,run,clone) for run in range(runs) for clone in range(clones)]
    result = view.map(concatenate_core17,*zip(*jobs))

    result.get()
    return
#    Parallel(n_jobs=num_cores)(delayed(concatenate_core17)(dir,run,clone) \
 #       for run in range(runs) for clone in range(clones))

