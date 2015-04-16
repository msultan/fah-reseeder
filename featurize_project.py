from msmbuilder.featurizer import DihedralFeaturizer
from msmbuilder.utils import verboseload,verbosedump
from msmbuilder.decomposition import tICA
import glob
import os
import numpy as np
import mdtraj as mdt
from joblib import Parallel, delayed
import multiprocessing

def featurize_traj(featurizer,traj):
     return [os.path.basename(traj),featurizer.partial_transform(mdt.load(traj))]

def featurize_project(dir,featurizer_object):

     if featurizer_object is None:
          featurizer = DihedralFeaturizer(types=['phi', 'psi','chi1'])
     else:
          try:
               featurizer = verboseload(featurizer_object)
          except:
               sys.exit("Cant Load Featurizer using msmbuilder verboseload")

     feature_dict={}

     traj_list =  glob.glob(dir+"/trajectories/*.hdf5")

     num_cores = multiprocessing.cpu_count()
     result_list = Parallel(n_jobs=num_cores)(delayed(featurize_traj)(featurizer,traj) \
        for traj in traj_list)


     for result in result_list:
          feature_dict[result[0]] = result[1]

     verbosedump(feature_dict,dir+"/featurized_traj.pkl")

     return feature_dict


def tica_wrapper(dir,feature_dict):
     #100ps*100==10ns and 10 features

     tica_mdl = tICA(lag_time=100,n_components=10)
     for i in feature_dict.keys():
          try:
               tica_mdl.partial_fit(feature_dict[i])
          except:
               pass

     tica_features={}
     for i in feature_dict.keys():
          tica_features[i] = tica_mdl.transform([feature_dict[i]])
     verbosedump(tica_features,dir+"/tica_features.pkl")
     return tica_features