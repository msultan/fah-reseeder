#!/bin/env/ python
import os
from fah_reseeder.convert_project import *
from fah_reseeder.featurize_project import *
from fah_reseeder.cluster_project import *
from fah_reseeder.reseed_project import *
from IPython import parallel


def reseed_project():
     #
     args = parse_commandline()
     #make sure we have full path to avoid annoying issues with path
     args.d = os.path.abspath(args.d)

     client_list = parallel.Client(profile=args.p)
     client_list[:].execute("from fah_reseeder import *")
     print("Running on:",len(client_list.ids))
     view = client_list.load_balanced_view()
     view.block = True
     #extract
     extract_project_wrapper(args.d,view)
     #featurize
     feature_dict = featurize_project(args.d,args.f,args.s,view)

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
     help='Folder where the project has been rsynced', required=True)
     parser.add_argument('-t', '--ref_top', dest='t',help='Reference PDB Folder.\
          Should map to Runs i.e. folder_name/0.pdb is used for Run0', required=True)

     parser.add_argument('-p', '--prf', dest='p',default="mpi",help='What ipython cluster\
      profile to use')
     parser.add_argument('-f', '--featurizer',dest='f',default=None, help='Featurizer to use.Defualts to \
          DihedralFeaturizer')

     parser.add_argument('-s','--stride',dest='s',default=10,type=int,help='Stride to use when featurizing.')
     parser.add_argument('-i', '--do_tica',dest='i',default=True, help='Whether or not to do tica')
     parser.add_argument('-l', '--lag_time',dest='l',default=10, type=int,help='TICA lag_time')
     parser.add_argument('-n','--n_states',dest='n',default=50,type=int,help='Number of States')


     parser.add_argument('-r','--runs',dest='r',default=2,type=int,help='Choose top r states to reseed from')

     parser.add_argument('-c','--clones',dest='c',default=2,type=int,help='Start c clones from each state')

     args = parser.parse_args()
     return args



if __name__ == '__main__':
     reseed_project()

