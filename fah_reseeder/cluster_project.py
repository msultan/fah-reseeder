from msmbuilder.cluster import MiniBatchKMeans
from msmbuilder.utils import verbosedump,verboseload
import numpy as np
import os
def cluster_project_wrapper(dir,feature_dict,n_states):

     if os.path.exists(dir+"/assignments.pkl"):
          return verboseload(dir+"/cluster_mdl.pkl"),verboseload(dir+"/assignments.pkl")
     elif os.path.exists(dir+"/cluster_mdl.pkl"):
          cluster_mdl = verboseload(dir+"/cluster_mdl.pkl")
     else:
          cluster_mdl = MiniBatchKMeans(n_clusters = n_states)
          cluster_mdl.fit([feature_dict[i] for i in feature_dict.keys()])

     assignments={}
     for i in feature_dict.keys():
          assignments[i] = cluster_mdl.transform([feature_dict[i]])

     verbosedump(cluster_mdl,dir+"/cluster_mdl.pkl")
     verbosedump(assignments,dir+"/assignments.pkl")
     return cluster_mdl,assignments