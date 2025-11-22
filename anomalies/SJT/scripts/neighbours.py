'''
This module uses sklearn.neighbors NearestNeighbors to compare the nearest other test compared to itself.
The model uses a preprocessed dataframe, with all answers, provided by the specific dataframeBuilder for SJT
Each row represents a test instance.

Input:
  - ./decoded_data/SJT/FactQuestionSJT.csv
  - ./decoded_data/SJT/FactTest.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/SJT/csv/neighbours.csv
  - ./anomalies/SJT/csv/neighbours_distance_0_same_candidateID.csv
  - ./anomalies/SJT/csv/neighbours_distance_0_diff_candidateID.csv
  - ./anomalies/SJT/csv/neighbours_dropable_keys_for_anomalies.csv
'''

#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Get the name of the operating system
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(".")

pd.set_option("display.max_columns", None)

from func.df_builders.dataframeBuilderSJT import get_df_column_per_combination
from func.df_builders.dataframeBuilderSJT import get_distances_indices_sklearn_NearestNeighbors
# from helpers.dataframeBuilderSJT import neighbors_distances_indices_to_readable_df

NEIGBOURS=5


# In[2]:


df, df_test, _, df_candidate = get_df_column_per_combination(join_candidate=False, min_max_scale=False)
df["CandidateKey"] = df["CandidateKey"].astype(int)

# Keep a 'copy' of candidate column, to join later again to check the results
df_candidate_column = df["CandidateKey"]
df.drop(columns="CandidateKey", inplace=True)
df_candidate_column


print("Getting the distances of my nearest neighbours (SJT)")
distances, indices = get_distances_indices_sklearn_NearestNeighbors(df, n_neighbors=NEIGBOURS)
print("Finetuning results")

# Pretify distances and indices in a proper dataframe df_close_neighbours
df_close_neighbors = pd.DataFrame(columns=["TestKey", "neighbourKey", "distance", "minKey"])
for i in np.arange(NEIGBOURS):
    testkeys = indices[:, i].tolist()
    distance = distances[:, i].tolist()
    neighbours = df.iloc[testkeys].index.tolist()
    testkeys = df.iloc[np.arange(len(testkeys))].index.tolist()
    # print(testkeys)
    # print(distance)
    # print(neighbours)
    minima = np.minimum(testkeys, neighbours)
    df_neighbours_i = pd.DataFrame(data={
        "TestKey" : testkeys,
        "neighbourKey" : neighbours,
        "distance" : distance,
        "minKey" : minima
    })
    df_close_neighbors = pd.concat([df_close_neighbors,df_neighbours_i], ignore_index=True)
# Drop self references
df_close_neighbors = df_close_neighbors[df_close_neighbors["TestKey"] != df_close_neighbors["neighbourKey"]]

# Join additional candidate information of the test to compare potential doubles
df_test.index = df_test["TestKey"]
df_close_neighbors = df_close_neighbors.join(df_candidate_column, on="TestKey", how='left')
df_close_neighbors.rename(columns={"CandidateKey" : "CandidateKeyTestKey"}, inplace=True)
df_close_neighbors = df_close_neighbors.join(df_candidate_column, on="neighbourKey", how='left')
df_close_neighbors.rename(columns={"CandidateKey" : "CandidateKeyneighbourKey"}, inplace=True)
df_candidate.index = df_candidate["CandidateKey"]
df_close_neighbors = df_close_neighbors.join(df_candidate[["ID"]], on="CandidateKeyTestKey", how="left")
df_close_neighbors.rename(columns={"ID" : "CandidateID_left"}, inplace=True)
df_close_neighbors = df_close_neighbors.join(df_candidate[["ID"]], on="CandidateKeyneighbourKey", how="left")
df_close_neighbors.rename(columns={"ID" : "CandidateID_neighbour"}, inplace=True)

df_distance_null = df_close_neighbors[df_close_neighbors.distance == 0]

# Reverse the rows TestKey <-> neighbourKey (to keep the minimumgroups later)
reversed_df = df_distance_null.copy()
reversed_df['TestKey'], reversed_df['neighbourKey'] = reversed_df['neighbourKey'], reversed_df['TestKey']
reversed_df['CandidateKeyTestKey'], reversed_df['CandidateKeyneighbourKey'] = reversed_df['CandidateKeyneighbourKey'], reversed_df['CandidateKeyTestKey']
reversed_df['CandidateID_left'], reversed_df['CandidateID_neighbour'] = reversed_df['CandidateID_neighbour'], reversed_df['CandidateID_left']

# Concatenate the original DataFrame with the reversed one
df_distance_null = pd.concat([df_distance_null, reversed_df], ignore_index=True)

df_distance_null.drop_duplicates(inplace=True)

# Filter the same results, with a different or the same candidateID
df_distance_null_same_candidates = df_distance_null[df_distance_null["CandidateID_left"] == df_distance_null["CandidateID_neighbour"]]
df_distance_null_diff_candidates = df_distance_null[df_distance_null["CandidateID_left"] != df_distance_null["CandidateID_neighbour"]]

# Shortest distance of those with a differnt candidataID, 0 (different ID) or not 0 combined
df_shortest_distance = df_close_neighbors[df_close_neighbors["CandidateID_left"] != df_close_neighbors["CandidateID_neighbour"]]

# Keep the min distances
min_distances = df_close_neighbors.groupby('TestKey')["distance"].min()
df_close_neighbors = pd.merge(df_close_neighbors, min_distances, on='TestKey', suffixes=('', '_min'))
df_shortest_distance = df_close_neighbors[df_close_neighbors['distance'] == df_close_neighbors['distance_min']]
df_shortest_distance.drop(columns=['distance_min'], inplace=True)
df_shortest_distance.drop_duplicates(subset=["TestKey"], keep='first', inplace=True)

# Threshold for being an anomaly
# To give a % of spiekchance
# squared_distance = distance^2
# relative_distance = 100 - squared_distance
# min(0, relative_distance) > TRESHHOLD
# df_distance_not_null["spiekkans"] = np.pow((100 - np.pow(df_distance_not_null.distance, 2)).where(lambda val : val > 0, 0) / 100, 2)
TRESHOLD = 0.8
df_shortest_distance["spiekkans"] = np.pow((100 - np.pow(df_shortest_distance.distance, 2)).where(lambda val : val > 0, 0) / 100, 2)
df_shortest_distance["is_anomaly"] = (df_shortest_distance["spiekkans"] > TRESHOLD).astype(int)

# Write to csv's
anomalies_dir = os.path.abspath("anomalies")
TESTNAME = 'SJT'
df_distance_null_same_candidates.to_csv(os.path.join(anomalies_dir, TESTNAME, 'csv', 'neighbours_distance_0_same_candidateID.csv'),index=False)
df_distance_null_diff_candidates.to_csv(os.path.join(anomalies_dir, TESTNAME, 'csv', 'neighbours_distance_0_diff_candidateID.csv'),index=False)
df_shortest_distance.to_csv(os.path.join(anomalies_dir, TESTNAME, 'csv', 'neighbours.csv'),index=False)
