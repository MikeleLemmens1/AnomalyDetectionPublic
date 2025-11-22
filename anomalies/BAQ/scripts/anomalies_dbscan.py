'''
This module uses DBSCAN as an unsupervised clustering algorithm. 
All instances that aren't part of a cluster are marked as an anomaly.
The model uses a preprocessed dataframe with all answers (both normative and ipsative values) spread over the columns.
Each row represents a test instance.

Input:
  - ./anomalies/BAQ/csv/preprocessed_data.csv

Output:
  - ./anomalies/BAQ/csv/dbscan_anomalies.csv
'''

import os
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Read data

path = os.path.join(os.getcwd(), "anomalies", "BAQ", "csv", "preprocessed_data.csv")
df = pd.read_csv(path)
df = df.set_index(['TestKey'])

# Lower number of columns (>500) to 10 using PCA, then scale these 10 features

df_for_pca = df
pca10 = PCA(n_components=10)
df_pca10 = pd.DataFrame(pca10.fit_transform(df_for_pca),index=df.index)
sc = StandardScaler()
df_pca10_scaled = pd.DataFrame(sc.fit_transform(df_pca10),index=df.index,columns=df_pca10.columns)

# Fit a DBSCAN model on the scaled data

dbscan = DBSCAN(eps=2, min_samples=10)
print("Fitting DBSCAN for BAQ with eps=2 and min_samples=10")
dbscan.fit(df_pca10_scaled)
print("Model fitted successfully")

# Use the labels to mark instances as anomalies and export the result

labels = pd.DataFrame(dbscan.labels_,index=df.index, columns=['label'])
labels['is_anomaly'] = labels[['label']].map(lambda label : 1 if label==-1 else 0)
labels.drop(columns=['label'],inplace=True)

target_csv_path = os.path.join(os.getcwd(), "anomalies", "BAQ","csv","dbscan_anomalies.csv")
labels[['is_anomaly']].to_csv(target_csv_path)
print(f"{target_csv_path} created")
print("BAQ DBSCAN Done")