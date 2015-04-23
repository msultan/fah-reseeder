from msmbuilder.cluster import KMeans
from msmbuilder.utils import verbosedump,verboseload
import os
def cluster_project_wrapper(proj_folder,feature_dict,n_states):

     if os.path.exists(proj_folder+"/assignments.pkl"):
          return verboseload(proj_folder+"/cluster_mdl.pkl"),verboseload(proj_folder+"/assignments.pkl")
     elif os.path.exists(proj_folder+"/cluster_mdl.pkl"):
          cluster_mdl = verboseload(proj_folder+"/cluster_mdl.pkl")
     else:
          cluster_mdl = KMeans(n_clusters = n_states)
          cluster_mdl.fit([feature_dict[i] for i in feature_dict.keys()])

     assignments={}
     for i in feature_dict.keys():
          assignments[i] = cluster_mdl.transform([feature_dict[i]])

     verbosedump(cluster_mdl,proj_folder+"/cluster_mdl.pkl")
     verbosedump(assignments,proj_folder+"/assignments.pkl")
     return cluster_mdl,assignments