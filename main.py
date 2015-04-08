#!/bin/env/ python

import numpy as np
import mdtraj as mdt
import glob
import sys
from convert_project import *
from msmbuilder.featurizer import DihedralFeaturizer
from msmbuilder.utils import verboseload
def extract_project(dir):
     #calling the wrapper function
     convert_project_wrapper_func(dir)
     return

def featurize_project(featurizer_object,dir):
     if featurizer_object is None:
          featurizer = DihedralFeaturizer(types=['phi', 'psi','chi1'])
     else:
          try:
               featurizer = verboseload(featurizer_object)
          except:
               sys.exit("Cant Load Featurizer using msmbuilder verboseload")
     print featurizer
     return

def cluster_project():
     return

def pull_frames():
     return


def main(options):
     extract_project(options.d)
     featurize_project(options.f,options.d)
     cluster_project()
     pull_frames()

     return

def parse_commandline():
     import os
     parser = optparse.OptionParser()
     parser.add_option('-d', '--dir', dest='d', default='./',\
     help='Folder where the project has been rsynced')

     parser.add_option('-f', '--featurizer',dest='f',default=None, help='Featurizer to use.Defualts to \
          DihedralFeaturizer')
     parser.add_option('-n','--n_states',dest='n',default=1000,help='Number of States')

     parser.add_option('-t', '--ref_top', dest='t',default=None,help='Reference PDB Folder.\
          Should map to Runs i.e. folder_name/0.pdb is used for Run0')

     #
     parser.add_option('-r','--runs',dest='r',default=40,help='Choose top r states to reseed from')

     parser.add_option('-c','--clones',dest='c',default=20,help='Choose top c clones from each state')

     (options, args) = parser.parse_args()
     return (options, args)



if __name__ == '__main__':
     import optparse
     (options, args) = parse_commandline()
     main(options)

