from msmbuilder.featurizer import DihedralFeaturizer
from msmbuilder.utils import verboseload,verbosedump
from msmbuilder.decomposition import tICA
import glob
import os
import mdtraj as mdt

def featurize_traj(job_tuple):
    proj_folder,top_folder,featurizer,traj,stride = job_tuple
    top = os.path.join(top_folder, "%s.pdb"%os.path.basename(traj).split("_")[0])
    return [os.path.basename(traj),featurizer.partial_transform(mdt.load(traj,top=top,stride=stride))]

def featurize_project(proj_folder,top_folder,featurizer_object,stride,view):

     #if already featurized dont bother(should add a warning about this)
     if os.path.exists(proj_folder+"/featurized_traj.pkl"):
          return verboseload(proj_folder+"/featurized_traj.pkl")

     if featurizer_object is None:
          featurizer = DihedralFeaturizer(types=['phi', 'psi','chi1'])
     else:
          try:
               featurizer = verboseload(featurizer_object)
          except:
               sys.exit("Cant Load Featurizer using msmbuilder verboseload")

     feature_dict={}

     traj_list =  glob.glob(proj_folder+"/trajectories/*.dcd")


     jobs = [(proj_folder,top_folder,featurizer,traj,stride) for traj in traj_list]
     results = view.map_sync(featurize_traj,jobs)

     for result in results:
          feature_dict[result[0]] = result[1]

     verbosedump(feature_dict,proj_folder+"/featurized_traj.pkl")

     return feature_dict


def tica_wrapper(proj_folder,feature_dict,lag_time=10):
     #100ps*100==10ns and 10 features
     if os.path.exists(proj_folder+"/tica_features.pkl"):
          return verboseload(proj_folder+"/tica_features.pkl")

     tica_mdl = tICA(lag_time=lag_time,n_components=10)
     tica_mdl.fit([feature_dict[i] for i in feature_dict.keys()])

     tica_features={}
     for i in feature_dict.keys():
          tica_features[i] = tica_mdl.transform([feature_dict[i]])[0]
     verbosedump(tica_features,proj_folder+"/tica_features.pkl")
     return tica_features
