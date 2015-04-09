#!/bin/env python
from __future__ import print_function, division
import os
import glob
import sys
import tarfile
from mdtraj.formats.hdf5 import HDF5TrajectoryFile
import mdtraj as md
import tables
from mdtraj.utils.contextmanagers import enter_temp_directory
from mdtraj.utils import six
from joblib import Parallel, delayed
import multiprocessing

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

    path = dir+"RUN%d/CLONE%d/"%(run,clone)
    top = md.load(dir+"/topologies/%d.pdb"%run)
    output_filename = dir+"/trajectories/%d_%d.hdf5"%(run,clone)

    print(path,top,output_filename)
    glob_input = os.path.join(path, "results-*.tar.bz2")
    filenames = glob.glob(glob_input)
    filenames = sorted(filenames, key=keynat)

    if len(filenames) <= 0:
        return

    trj_file = HDF5TrajectoryFile(output_filename, mode='a')

    try:
        trj_file._create_earray(where='/', name='processed_filenames',\
            atom=trj_file.tables.StringAtom(1024), shape=(0,))
        trj_file.topology = top.topology
    except trj_file.tables.NodeError:
        pass

    for filename in filenames:
        if six.b(filename) in trj_file._handle.root.processed_filenames:  \
        # On Py3, the pytables list of filenames has type byte (e.g. b"hey"), so we need to deal with this via six.
            print("Already processed %s" % filename)
            continue
        with enter_temp_directory():
            print("Processing %s" % filename)
            archive = tarfile.open(filename, mode='r:bz2')
            archive.extract("positions.xtc")
            trj = md.load("positions.xtc", top=top)

            for frame in trj:
                trj_file.write(coordinates=frame.xyz, \
                    cell_lengths=frame.unitcell_lengths, cell_angles=frame.unitcell_angles)

            trj_file._handle.root.processed_filenames.append([filename])

def sanity_test(dir):
    if not os.path.exists(dir+"topologies"):
        #print("Toplogies Folder Doesnt exist")
        sys.exit("Toplogies Folder Doesnt exist.Exiting!")


    if not os.path.exists(dir+"trajectories"):
        print("Trajectories Folder Doesnt exist.Creating")
        os.makedirs(dir+"trajectories")


def convert_project_wrapper_func(dir):
    sanity_test(dir)
    num_cores = multiprocessing.cpu_count()
    runs=len(glob.glob(dir+"/RUN*"))
    clones=len(glob.glob(dir+"RUN0/CLONE*"))
    print("Found %d runs and %d clones in %s"%(runs,clones,dir))
    print("Using %d cores to parallelize"%num_cores)
    Parallel(n_jobs=num_cores)(delayed(concatenate_core17)(dir,run,clone) \
        for run in range(runs) for clone in range(clones))

