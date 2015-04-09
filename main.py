#!/bin/env/ python

import numpy as np
import mdtraj as mdt
import glob
import sys
from msmbuilder.msm import MarkovstateModel
from convert_project import *
from featurize_project import *
from cluster_project import *
from reseed_project import *
def extract_project(dir):
     #calling the wrapper function
     convert_project_wrapper_func(dir)
     return


def perform_tica(dir,feature_dict,n_states):
     return tica_wrapper(dir,feature_dict,n_states)

def cluster_project(feature_dict):
     return cluster_project_wrapper(feature_dict)

def build_msm(assignments):
     msm_mdl = MarkovstateModel(lag_time=100,ergodic_trimming=False)
     msm_mdl.fit([assignments[i] for i in assignments.keys()])
     return msm_mdl

def pull_frames():
     return reseed_project(dir,msm_mdl)


def main(options):
     extract_project(options.d)
     feature_dict = featurize_project(options.f,options.d)

     if options.i==True:
          feature_dict = tica_wrapper(feature_dict)

     assignments = cluster_project(dir,feature_dict,options.n)

     msm_mdl =  build_msm(assignments)

     pull_frames(dir,msm_mdl,options.r,options.c)

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
     parser.add_option('-n','--n_states',dest='n',default=1000,help='Number of States')

     parser.add_option('-r','--runs',dest='r',default=40,help='Choose top r states to reseed from')

     parser.add_option('-c','--clones',dest='c',default=20,help='Choose top c clones from each state')

     (options, args) = parser.parse_args()
     return (options, args)



if __name__ == '__main__':
     import optparse
     (options, args) = parse_commandline()
     main(options)

