'''
This module uses sklearn.neighbors NearestNeighbors to compare the nearest other test compared to itself.
The model uses a preprocessed dataframe, with all answers, provided by the specific dataframeBuilder for FCA
Each row represents a test instance.

Input:
  - ./decoded_data/{TESTNAME}/FactQuestion{TESTNAME}.csv
  - ./decoded_data/{TESTNAME}/FactTest.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/{TESTNAME}/csv/neighbours.csv
  - ./anomalies/{TESTNAME}/csv/neighbours_distance_0_same_candidateID.csv
  - ./anomalies/{TESTNAME}/csv/neighbours_distance_0_diff_candidateID.csv
  - ./anomalies/{TESTNAME}/csv/neighbours_dropable_keys_for_anomalies.csv
  '''


# Get the name of the operating system
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(".")


from func.df_builders.dataframeBuilderFCA import get_df_column_per_combination
from func.df_builders.dataframeBuilderFCA import get_distances_indices_sklearn_NearestNeighbors
from func.df_builders.dataframeBuilderFCA import neighbors_distances_indices_to_readable_df

NEIGBOURS=3

df, df_test, _, df_candidate = get_df_column_per_combination(join_candidate=False)

# Drop candidate column, but keep a copy
df_candidate_column = df["CandidateKey"]
df.drop(columns="CandidateKey", inplace=True)
df_candidate_column


# To readable dataframe
print("Getting the distances of my nearest neighbours (FCA)")
distances, indices = get_distances_indices_sklearn_NearestNeighbors(df, n_neighbors=NEIGBOURS)
print("Finetuning results")

df_close_neighbors = neighbors_distances_indices_to_readable_df(df, indices=indices, distances=distances)

# Add extra candidate information to the result to compare & check results
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

# Reverse the rows TestKey <-> neighbourKey
reversed_df = df_distance_null.copy()
reversed_df['TestKey'], reversed_df['neighbourKey'] = reversed_df['neighbourKey'], reversed_df['TestKey']
reversed_df['CandidateKeyTestKey'], reversed_df['CandidateKeyneighbourKey'] = reversed_df['CandidateKeyneighbourKey'], reversed_df['CandidateKeyTestKey']
reversed_df['CandidateID_left'], reversed_df['CandidateID_neighbour'] = reversed_df['CandidateID_neighbour'], reversed_df['CandidateID_left']

# Concatenate the original DataFrame with the reversed one
df_distance_null = pd.concat([df_distance_null, reversed_df], ignore_index=True)

df_distance_null.drop_duplicates(inplace=True)

# Distances being 0 as spiekers or other doubles, with the same candidateID
df_distance_null_same_candidates = df_distance_null[df_distance_null["CandidateID_left"] == df_distance_null["CandidateID_neighbour"]]
df_distance_null_same_candidates = df_distance_null_same_candidates.loc[df_distance_null_same_candidates.groupby("TestKey")["minFCAKey"].idxmin()]

# Distances being 0 as spiekers or other doubles, with a different candidateID
df_distance_null_diff_candidates = df_distance_null[df_distance_null["CandidateID_left"] != df_distance_null["CandidateID_neighbour"]]
df_distance_null_diff_candidates = df_distance_null_diff_candidates.loc[df_distance_null_diff_candidates.groupby("TestKey")["minFCAKey"].idxmin()]

# Shortest distance of those results with a different candidateID
df_distance_not_null = df_close_neighbors[df_close_neighbors["CandidateID_left"] != df_close_neighbors["CandidateID_neighbour"]]
df_distance_not_null = df_distance_not_null.groupby("TestKey").min("distance").reset_index()

TRESHOLD = 0.7
# To give a % of spiekchance
# squared_distance = distance^2
# relative_distance = 100 - squared_distance
# min(0, relative_distance) > TRESHHOLD
# df_distance_not_null["spiekkans"] = np.pow((100 - np.pow(df_distance_not_null.distance, 2)).where(lambda val : val > 0, 0) / 100, 2)
df_distance_not_null["spiekkans"] = ((100 - (df_distance_not_null.distance)**2).where(lambda val : val > 0, 0) / 100)**2
df_distance_not_null["is_anomaly"] = (df_distance_not_null["spiekkans"] > TRESHOLD).astype(int)

series_dropable_keys_for_anomalies = df_distance_null_same_candidates[df_distance_null_same_candidates["TestKey"] != df_distance_null_same_candidates["minFCAKey"]]["neighbourKey"]

# Write to csv's
anomalies_dir = os.path.abspath("anomalies")
df_distance_null_same_candidates.to_csv(os.path.join(anomalies_dir, 'FCA', 'csv', 'neighbours_distance_0_same_candidateID.csv'),index=False)
df_distance_null_diff_candidates.to_csv(os.path.join(anomalies_dir, 'FCA', 'csv', 'neighbours_distance_0_diff_candidateID.csv'),index=False)
df_distance_not_null.to_csv(os.path.join(anomalies_dir, 'FCA', 'csv', 'neighbours.csv'),index=False)
series_dropable_keys_for_anomalies.to_csv(os.path.join(anomalies_dir, 'FCA', 'csv', 'neighbours_dropable_keys_for_anomalies.csv'),index=False)
