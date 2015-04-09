from msmbuilder.featurizer import DihedralFeaturizer
from msmbuilder.utils import verboseload,verbosedump
from msmbuilder.decomposition import tICA
import glob
import os
import mdtraj as mdt
def featurize_project(featurizer_object,dir):

     if featurizer_object is None:
          featurizer = DihedralFeaturizer(types=['phi', 'psi','chi1'])
     else:
          try:
               featurizer = verboseload(featurizer_object)
          except:
               sys.exit("Cant Load Featurizer using msmbuilder verboseload")

     feature_dict={}

     traj_list =  glob.glob(dir+"trajectories/*.hdf5")
     for traj in traj_list:
          feature_dict[os.path.basename(traj)] = featurizer.partial_transform(mdt.load(traj))

     verbosedump(feature_dict,dir+"featurized_traj.pkl")

     return feature_dict


def tica_wrapper(feature_dict):
     #100ps*100==10ns
     tica_mdl = tICA(lag_time=100)
     tica_mdl.fit([feature_dict[i] for i in feature_dict.keys()])
     tica_features={}
     for i in feature_dict.keys():
          tica_features[i] = tica_mdl.transform(feature_dict[i])

     verbosedump(tica_features,dir+"tica_features.pkl")
     return tica_features