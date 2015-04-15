#!/bin/env/ python

import numpy as np
import mdtraj as mdt
import glob
import sys

from convert_project import *
from featurize_project import *
from cluster_project import *
from reseed_project import *


def main(options):
     #extract
     extract_project_wrapper(options.d)
     #featurize
     feature_dict = featurize_project(options.d,options.f)

     #ticafy
     if options.i==True:
          feature_dict = tica_wrapper(options.d,feature_dict)

     #assignment
     cluster_mdl,assignments = cluster_project_wrapper(options.d,feature_dict,options.n)

     #cluster and pull frames
     pull_new_seeds(options.d,cluster_mdl,assignments,options.r,options.c)

     return

def parse_commandline():
     import os
     parser = optparse.OptionParser()
     parser.add_option('-d', '--dir', dest='d', default='./',\
     help='Folder where the project has been rsynced')
     parser.add_option('-t', '--ref_top', dest='t',default=None,help='Reference PDB Folder.\
          Should map to Runs i.e. folder_name/0.pdb is used for Run0')


     parser.add_option('-f', '--featurizer',dest='f',default=None, help='Featurizer to use.Defualts to \
          DihedralFeaturizer')

     parser.add_option('-i', '--do_tica',dest='i',default=True, help='Whether or not to do tica')
     parser.add_option('-n','--n_states',dest='n',default=50,help='Number of States')

     parser.add_option('-r','--runs',dest='r',default=2,help='Choose top r states to reseed from')

     parser.add_option('-c','--clones',dest='c',default=2,help='Start c clones from each state')

     (options, args) = parser.parse_args()
     return (options, args)



if __name__ == '__main__':
     import optparse
     (options, args) = parse_commandline()
     #make sure we have full path to avoid annoying issues with path
     options.d = os.path.abspath(options.d)
     main(options)

