'''
This module uses sklearn.neighbors NearestNeighbors to compare the nearest other test compared to itself.
The model uses a preprocessed csv, with all answers
Afterwards it adds other information from candidates, using helperfunctions from the dataBuilderBAQ
Each row represents a test instance.

Input:
  - ./decoded_data/BAQ/FactQuestionBAQ.csv
  - ./decoded_data/BAQ/FactTest.csv
  - ./decoded_data/DimCandidate.csv
  - ./anomalies/BAQ/preprocessed_data.csv

Output:
  - ./anomalies/BAQ/csv/neighbours.csv
  - ./anomalies/BAQ/csv/neighbours_distance_0_same_candidateID.csv
  - ./anomalies/BAQ/csv/neighbours_distance_0_diff_candidateID.csv
  - ./anomalies/BAQ/csv/neighbours_dropable_keys_for_anomalies.csv
  '''


import os
import sys
import numpy as np
import pandas as pd
cwd = os.getcwd()

import matplotlib.pyplot as plt
sys.path.append(".")


from func.df_builders.dataframeBuilderBAQ import get_distances_indices_sklearn_NearestNeighbors
from func.df_builders.dataframeBuilderBAQ import neighbors_distances_indices_to_readable_df
from func.df_builders.dataframeBuilderBAQ import add_days_ago
from func.df_builders.dataframeBuilderBAQ import add_version
from func.df_builders.dataframeBuilderBAQ import add_candidate
from func.df_builders.dataframeBuilderBAQ import load_df_candidate


NEIGBOURS=5

current_dir = os.path.abspath("anomalies")

# getting data, starts from preprocessed_data instead of dataframebuilder
df = pd.read_csv(os.path.join(current_dir, 'BAQ','csv', 'preprocessed_data.csv'))
df_candidate = load_df_candidate()

# Add additional information
df.index = df["TestKey"]
df, df_test = add_days_ago(df)
df = add_candidate(df, df_test=df_test)
df = add_version(df, df_test=df_test, one_hot=True)

# Experimental idea:
# For neighbours, multiply versions by 10 to increase distance.
WEIGHT = 10
df["VersionNumber_v1.0"] = WEIGHT * df["VersionNumber_v1.0"]
df["VersionNumber_v1.1"] = WEIGHT * df["VersionNumber_v1.1"]
df["VersionNumber_v1.2"] = WEIGHT * df["VersionNumber_v1.2"]
df["VersionNumber_v2.0"] = WEIGHT * df["VersionNumber_v2.0"]
df["VersionNumber_v2.1"] = WEIGHT * df["VersionNumber_v2.1"]

df.drop(columns="TestKey", inplace=True)

# Keep a 'copy' of candidate column, to join later again to check the results
df_candidate_column = df["CandidateKey"]
df.drop(columns="CandidateKey", inplace=True)


# Getting the neigbours
# Get the closest N neighbours of each test and pretify the result
distances, indices = get_distances_indices_sklearn_NearestNeighbors(df, n_neighbors=NEIGBOURS)
df_close_neighbors = neighbors_distances_indices_to_readable_df(df, indices=indices, distances=distances, n_neighbours=NEIGBOURS)
df_close_neighbors

# Add additional columns, like candidateID
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

# Filter distances where its 0
df_distance_null = df_close_neighbors[df_close_neighbors.distance == 0]
df_distance_null

# Reverse the rows TestKey <-> neighbourKey (to keep the minimumgroups later)
reversed_df = df_distance_null.copy()
reversed_df['TestKey'], reversed_df['neighbourKey'] = reversed_df['neighbourKey'], reversed_df['TestKey']
reversed_df['CandidateKeyTestKey'], reversed_df['CandidateKeyneighbourKey'] = reversed_df['CandidateKeyneighbourKey'], reversed_df['CandidateKeyTestKey']
reversed_df['CandidateID_left'], reversed_df['CandidateID_neighbour'] = reversed_df['CandidateID_neighbour'], reversed_df['CandidateID_left']

# Concatenate the original DataFrame with the reversed one
df_distance_null = pd.concat([df_distance_null, reversed_df], ignore_index=True)

df_distance_null.drop_duplicates(inplace=True)
df_distance_null.sort_values(["TestKey"])

# Seem to be no duplicates
df_distance_null_same_candidates = df_distance_null[df_distance_null["CandidateID_left"] == df_distance_null["CandidateID_neighbour"]]

# Some of the results seem to be the same, on the same day, with a different candidateID
df_distance_null_diff_candidates = df_distance_null[df_distance_null["CandidateID_left"] != df_distance_null["CandidateID_neighbour"]]


# Keep the shortest of tests with a different candidateID
df_shortest_distance = df_close_neighbors[df_close_neighbors["CandidateID_left"] != df_close_neighbors["CandidateID_neighbour"]]
min_distances = df_shortest_distance.groupby('TestKey')["distance"].min()
df_shortest_distance = pd.merge(df_shortest_distance, min_distances, on='TestKey', suffixes=('', '_min'))
df_shortest_distance = df_shortest_distance[df_shortest_distance['distance'] == df_shortest_distance['distance_min']]
df_shortest_distance.drop(columns=['distance_min'], inplace=True)
df_shortest_distance.drop_duplicates(subset=["TestKey"], keep='first', inplace=True)


TRESHOLD = 0.7
# To give a % of spiekchance
# squared_distance = distance^2
# relative_distance = 100 - squared_distance
# min(0, relative_distance) > TRESHHOLD
# df_distance_not_null["spiekkans"] = np.pow((100 - np.pow(df_distance_not_null.distance, 2)).where(lambda val : val > 0, 0) / 100, 2)
df_shortest_distance["spiekkans"] = np.pow((100 - np.pow(df_shortest_distance.distance, 2)).where(lambda val : val > 0, 0) / 100, 2)
df_shortest_distance["is_anomaly"] = (df_shortest_distance["spiekkans"] > TRESHOLD).astype(int)
potential_spiekers = df_shortest_distance[df_shortest_distance.spiekkans > TRESHOLD].sort_values("spiekkans", ascending=False)
potential_spiekers.reset_index(drop=True, inplace=True)
potential_spiekers


# Write to csv's
df_distance_null_same_candidates.to_csv(os.path.join(current_dir, 'BAQ','csv', 'neighbours_afstand_0_same_candidateID.csv'), index=False)
df_distance_null_diff_candidates.to_csv(os.path.join(current_dir, 'BAQ','csv', 'neighbours_afstand_0_diff_candidateID.csv'), index=False)
df_shortest_distance.to_csv(os.path.join(current_dir, 'BAQ','csv', 'neighbours.csv'), index=False)