from msmbuilder.cluster import MiniBatchKMeans
from msmbuilder.utils import verbosedump
import numpy as np
def cluster_project_wrapper(dir,feature_dict,n_states):
     cluster_mdl = MiniBatchKMeans(n_clusters = n_states)


     cluster_mdl.fit([feature_dict[i] for i in feature_dict.keys()])
     assignments={}
     for i in feature_dict.keys():
          assignments[i] = cluster_mdl.transform([feature_dict[i]])

     verbosedump(cluster_mdl,dir+"/cluster_mdl.pkl")
     verbosedump(assignments,dir+"/assignments.pkl")
     return cluster_mdl,assignments