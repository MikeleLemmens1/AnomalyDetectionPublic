'''
This module uses sklearn.neighbors NearestNeighbors to compare the nearest other test compared to itself.
The model uses a preprocessed dataframe, with all answers, provided by the specific dataframeBuilder for PAQ
Each row represents a test instance.

Input:
  - ./decoded_data/PAQ/FactQuestionPAQ.csv
  - ./decoded_data/PAQ/FactTest.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/PAQ/csv/neighbours.csv
  - ./anomalies/PAQ/csv/neighbours_distance_0_same_candidateID.csv
  - ./anomalies/PAQ/csv/neighbours_distance_0_diff_candidateID.csv
  - ./anomalies/PAQ/csv/neighbours_dropable_keys_for_anomalies.csv
  '''


import platform
import os
import sys
import numpy as np
import pandas as pd
cwd = os.getcwd()
import matplotlib.pyplot as plt
system_name = platform.system()

pd.set_option("display.max_columns", None)
sys.path.append(".")

from func.df_builders.dataframeBuilderPAQ import get_df_column_per_combination
from func.df_builders.dataframeBuilderPAQ import get_distances_indices_sklearn_NearestNeighbors
from func.df_builders.dataframeBuilderPAQ import neighbors_distances_indices_to_readable_df

NEIGBOURS=5

df, _, _, df_candidate = get_df_column_per_combination(join_candidate=False)
df["CandidateKey"] = df["CandidateKey"].astype(int)

# Keep a 'copy' of candidate column, to join later again to check the results
df_candidate_column = df["CandidateKey"]
df.drop(columns="CandidateKey", inplace=True)

# Get the closest N neighbours of each test and pretify the result
distances, indices = get_distances_indices_sklearn_NearestNeighbors(df, n_neighbors=NEIGBOURS)
df_close_neighbors = neighbors_distances_indices_to_readable_df(df, indices=indices, distances=distances, n_neighbours=NEIGBOURS)
df_close_neighbors

# Add additional columns, like candidateID
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

# Almost all seem to be duplicates
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
df_shortest_distance["spiekkans"] = ((100 - (df_shortest_distance.distance ** 2)).where(lambda val: val > 0, 0) / 100) ** 2
df_shortest_distance["is_anomaly"] = (df_shortest_distance["spiekkans"] > TRESHOLD).astype(int)
potential_spiekers = df_shortest_distance[df_shortest_distance.spiekkans > TRESHOLD].sort_values("spiekkans", ascending=False)
potential_spiekers.reset_index(drop=True, inplace=True)


# Write to csv's
current_dir = os.path.abspath("anomalies")
df_distance_null_same_candidates.to_csv(os.path.join(current_dir, 'PAQ','csv', 'neighbours_afstand_0_same_candidateID.csv'), index=False)
df_distance_null_diff_candidates.to_csv(os.path.join(current_dir, 'PAQ','csv', 'neighbours_afstand_0_diff_candidateID.csv'), index=False)
df_shortest_distance.to_csv(os.path.join(current_dir, 'PAQ','csv', 'neighbours.csv'), index=False)