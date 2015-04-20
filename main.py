#!/bin/env/ python

import numpy as np
import mdtraj as mdt
import glob
import sys
import os

from convert_project import *
from featurize_project import *
from cluster_project import *
from reseed_project import *


def main(args):
     #extract
     extract_project_wrapper(args.d)
     #featurize
     feature_dict = featurize_project(args.d,args.f,args.s)

     #ticafy
     if args.i==True:
          feature_dict = tica_wrapper(args.d,feature_dict,args.l)

     #assignment
     cluster_mdl,assignments = cluster_project_wrapper(args.d,feature_dict,args.n)

     #cluster and pull frames
     pull_new_seeds(args.d,cluster_mdl,assignments,args.r,args.c,args.s)

     return

def parse_commandline():

     import argparse
     parser = argparse.ArgumentParser()
     parser.add_argument('-d', '--dir', dest='d', default='./',\
     help='Folder where the project has been rsynced')
     parser.add_argument('-t', '--ref_top', dest='t',default=None,help='Reference PDB Folder.\
          Should map to Runs i.e. folder_name/0.pdb is used for Run0')


     parser.add_argument('-f', '--featurizer',dest='f',default=None, help='Featurizer to use.Defualts to \
          DihedralFeaturizer')

     parser.add_argument('-s','--stride',dest='s',default=10,type=int,help='Stride to use when featurizing.')
     parser.add_argument('-i', '--do_tica',dest='i',default=True, help='Whether or not to do tica')
     parser.add_argument('-l', '--lag_time',dest='l',default=10, help='TICA lag_time')
     parser.add_argument('-n','--n_states',dest='n',default=50,help='Number of States')


     parser.add_argument('-r','--runs',dest='r',default=2,help='Choose top r states to reseed from')

     parser.add_argument('-c','--clones',dest='c',default=2,help='Start c clones from each state')

     args = parser.parse_args()
     return args



if __name__ == '__main__':

     args = parse_commandline()
     #make sure we have full path to avoid annoying issues with path
     args.d = os.path.abspath(args.d)
     main(args)

