'''
This module uses DBSCAN as an unsupervised clustering algorithm. 
All instances that aren't part of a cluster are marked as an anomaly.
The model uses a preprocessed dataframe with a row for every test instance.

Input:
  - ./anomalies/SJT/csv/preprocessed_data.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/SJT/csv/dbscan_anomalies.csv
'''
import os
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Read data

cand_path = os.path.join(os.getcwd(), "decoded_data", "DimCandidate.csv")
PAQ_path = os.path.join(os.getcwd(), "anomalies", "SJT", "csv", "preprocessed_data.csv")
df_cand = pd.read_csv(cand_path)
df = pd.read_csv(PAQ_path)

# Basic preprocessing

df = df.set_index(['TestKey'])
df.drop(columns=['Year','Month','Day'],inplace=True)
sc = StandardScaler()
df_scaled = pd.DataFrame(sc.fit_transform(df),index=df.index,columns=df.columns)
df_scaled.fillna(0, inplace=True)
df_for_pca = df_scaled

best_dbscan = DBSCAN(min_samples=10,eps=5)
print("Fitting DBSCAN for SJT with eps=5 and min_samples=10")
best_dbscan.fit(df_scaled)
print("Model fitted successfully")

labels = pd.DataFrame(best_dbscan.labels_,index=df.index, columns=['label'])
labels['is_anomaly'] = labels[['label']].map(lambda label : 1 if label==-1 else 0)
labels.drop(columns=['label'],inplace=True)

target_csv_path = os.path.join(os.getcwd(), "anomalies", "SJT","csv","dbscan_anomalies.csv")
labels[['is_anomaly']].to_csv(target_csv_path)
print(f"{target_csv_path} created")
print("SJT DBSCAN Done")