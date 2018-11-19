from sklearn.cluster import AgglomerativeClustering
# from sklearn.cluster import MeanShift
import numpy as np
import csv
import json

team_names = json.load(open('team_name.json'))

scoring_scv = open('scoring_20181117.csv', 'r')
team_score = []
for row in csv.reader(scoring_scv):
	for index in range(len(row)):
		row[index] = float(row[index])
	
	team_score.append(row)


n_clusters = 5
X = np.array(team_score)
clustering = AgglomerativeClustering(n_clusters=n_clusters).fit(X)
# clustering = MeanShift().fit(X)

cluster = []
for gp_idx in range(n_clusters):
	cluster.append([])

rst = clustering.labels_
for team_idx in range(len(rst)):
	label = rst[team_idx]
	cluster[label].append(team_names[team_idx])

print json.dumps(cluster, indent=2)
