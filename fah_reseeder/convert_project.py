#!/bin/env python
from __future__ import print_function, division
import os
import glob
import sys
import tarfile
import mdtraj as md
from mdtraj.utils.contextmanagers import enter_temp_directory
import sqlite3

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

def concatenate_core17(job_tuple):
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

    proj_folder, top_folder, db_name, run, clone = job_tuple

    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    try:
        cur.execute("create table dcd_%d_%d (processed STRING UNIQUE)"%(run,clone))
    except:
        pass

    path = os.path.join(proj_folder,"RUN%d/CLONE%d/"%(run,clone))
    top = md.load(os.path.join(top_folder,"%d.pdb"%run))
    output_filename =  os.path.join(proj_folder,"trajectories/%d_%d.dcd"%(run,clone))

    already_processed_filename =  os.path.join(proj_folder,"trajectories/processed_trajectories/%d_%d.txt"\
                                                                                            %(run,clone))
    print(path,top,output_filename)
    glob_input = os.path.join(path, "results-*.tar.bz2")
    filenames = glob.glob(glob_input)
    filenames = sorted(filenames, key=keynat)

    if len(filenames) <= 0:
        return

    trj_file = None
    trj = None
    if os.path.exists(output_filename):
        trj_file = md.load(output_filename,top=top)


    for filename in filenames:
        #check if the file has been processed
        cmd = "select * from dcd_%d_%d where processed=(\'%s\')"%(run,clone,os.path.basename(filename))
        # if row doesn't exist in the dcd table.
        if  cur.execute(cmd).fetchall() == []:
            with enter_temp_directory():
                    archive = tarfile.open(filename, mode='r:bz2')
                    archive.extract("positions.xtc")
                    trj = md.load("positions.xtc", top=top)
                    if trj_file is None:
                        trj_file =  trj
                    else:
                        trj_file += trj
            #add to processed
            while True:
                try:
                    with conn:
                        cmd = "insert into dcd_%d_%d values (\'%s\')"%(run,clone,os.path.basename(filename))
                        cur.execute(cmd)
                        break
                except:
                    pass

        #otherwise chill here.
        else:
            print("Already Processed %s"%filename)
            continue
    #if we processed at least one new trajectory object.do a test.
    if trj is not None:
        try:
            assert(trj_file.n_frames==trj.n_frames*len(filenames))
        except:
            sys.exit("Total trajectory size doesn't match single gen*len(files).\n\
            Recommend deleting trajectories folder all *.pkl to start over.")
    #now save the new dcd file.

    trj_file.save_dcd(output_filename)
    cur.close()
    conn.close()

    return


def sanity_test(proj_folder,top_folder):
    if not os.path.isdir(top_folder):
        #print("Toplogies Folder Doesnt exist")
        sys.exit("Toplogies Folder Doesnt exist.Exiting!")


    if not os.path.isdir(os.path.join(proj_folder,"trajectories")):
        print("Trajectories folder doesnt exist.Creating")
        os.makedirs(os.path.join(proj_folder,"trajectories"))

    return

def extract_project_wrapper(proj_folder,top_folder,view):

    sanity_test(proj_folder,top_folder)
    db_name = os.path.join(proj_folder,"trajectories","processed.db")

    runs=len(glob.glob(proj_folder+"/RUN*"))
    clones=len(glob.glob(proj_folder+"/RUN0/CLONE*"))
    print("Found %d runs and %d clones in %s"%(runs,clones,proj_folder))
    print("Using %d cores to parallelize"%len(view))
    jobs = [(proj_folder,top_folder,db_name,run,clone) for run in range(runs) for clone in range(clones)]
    result = view.map_sync(concatenate_core17,jobs)
    return result

