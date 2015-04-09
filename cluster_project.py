from msmbuilder.cluster import MiniBatchKMeans

def cluster_project_wrapper(dir,feature_dict,n_states):
     kmeans_mdl = MiniBatchKMeans(n_clusters = n_states)

     kmeans_mdl.fit([feature_dict[i] for i in feature_dict.key()])

     assignments={}
     for i in feature_dict.keys():
          assignments[i] = kmeans_mdl.transform(feature_dict[i])

     verbosedump(assignments,dir+"assignments.pkl")
     return assignments