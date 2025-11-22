'''
This module uses DBSCAN as an unsupervised clustering algorithm. 
All instances that aren't part of a cluster are marked as an anomaly.
The model uses a preprocessed dataframe with a row for every test instance.
No aggregations are made but the categorical data is used to train the model.

Input:
  - ./anomalies/MDQ/csv/preprocessed_data.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/MDQ/csv/dbscan_anomalies.csv
'''
import os
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Read data

cand_path = os.path.join(os.getcwd(), "decoded_data", "DimCandidate.csv")
PAQ_path = os.path.join(os.getcwd(), "anomalies", "MDQ", "csv", "preprocessed_data.csv")
df_cand = pd.read_csv(cand_path)
df = pd.read_csv(PAQ_path)

df = df.set_index(['TestKey'])

# Merge both dataframes

df_cand = df_cand[['CandidateKey','Gender','Qualification']]
df_merged = df.merge(df_cand,on=['CandidateKey']).drop(columns=['CandidateKey'])
df_merged = df_merged.set_index(df.index)

# One hot encode the categorical columns

cat_feat = df_merged[['Gender','Qualification']]
enc = OneHotEncoder(handle_unknown='ignore',sparse_output=False)
enc.fit(cat_feat)
cat_feat = enc.transform(cat_feat)
cat_feat = pd.DataFrame(cat_feat,columns=enc.get_feature_names_out(), dtype='int',index=df_merged.index)
df_merged.drop(columns=['Gender','Qualification'],inplace=True)
df_merged_with_cat = df_merged.merge(cat_feat,left_index=True,right_index=True)

# Compress the features down to 10 and scale them

sc = StandardScaler()
pca10 = PCA(n_components=10)
df_pca10 = pd.DataFrame(pca10.fit_transform(df_merged_with_cat),index=df.index)
df_pca10_scaled = pd.DataFrame(sc.fit_transform(df_pca10),index=df.index,columns=df_pca10.columns)
best_dbscan = DBSCAN(min_samples=3,eps=0.5, n_jobs=-1)
print("Fitting DBSCAN for PAQ with eps=10 and min_samples=50")
print("This might take very long :'(")
best_dbscan.fit(df_pca10_scaled)
print("Model fitted successfully")

labels = pd.DataFrame(best_dbscan.labels_,index=df_merged_with_cat.index, columns=['label'])
labels['is_anomaly'] = labels[['label']].map(lambda label : 1 if label==-1 else 0)
labels.drop(columns=['label'],inplace=True)

target_csv_path = os.path.join(os.getcwd(), "anomalies", "MDQ","csv","dbscan_anomalies.csv")
labels[['is_anomaly']].to_csv(target_csv_path)
print(f"{target_csv_path} created")
print("MDQ DBSCAN Done")
