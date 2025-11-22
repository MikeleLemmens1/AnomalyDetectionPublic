'''
This module uses DBSCAN as an unsupervised clustering algorithm. 
All instances that aren't part of a cluster are marked as an anomaly.
The model uses a preprocessed dataframe with a row for every question.
Further preprocessing involves aggregating the total score for each statement per test instance.

Input:
  - ./anomalies/PAQ/csv/preprocessed_data.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/PAQ/csv/dbscan_anomalies.csv
'''
import os
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN

# Read data

cand_path = os.path.join(os.getcwd(), "decoded_data", "DimCandidate.csv")
PAQ_path = os.path.join(os.getcwd(), "anomalies", "PAQ", "csv", "preprocessed_data.csv")
df_cand = pd.read_csv(cand_path)
df = pd.read_csv(PAQ_path)

# Perform extra preprocessing steps to correctly compare test instances
# For each test instance, the total score of every "statement" is calculated

df = df.set_index(['TestKey'])
df['AnswerValLeft'] = 5 - df['AnswerVal']
df['AnswerValRight'] = df['AnswerVal']
df.drop(columns=['Year','Month','Day','AnswerVal'],inplace=True)
df.AnswerValLeft.sum()+df.AnswerValRight.sum()
# df[['LeftStatement','RightStatement']] = df[['LeftStatement','RightStatement']].applymap(lambda str: str[:3])
df[['LeftStatement', 'RightStatement']] = df[['LeftStatement', 'RightStatement']].astype(str).applymap(lambda s: s[:3])
df_sand = df
df_sand_left = pd.DataFrame(df_sand.groupby([df_sand.index,'LeftStatement'])['AnswerValLeft'].sum().reset_index())
df_sand_right = pd.DataFrame(df_sand.groupby([df_sand.index,'RightStatement'])['AnswerValRight'].sum().reset_index())
df_merged = df_sand_left.merge(df_sand_right,left_on=[df_sand_left.TestKey,df_sand_left.LeftStatement],right_on=[df_sand_right.TestKey,df_sand_right.RightStatement],how='outer')
df_merged = df_merged[['key_0','LeftStatement','AnswerValLeft','RightStatement','AnswerValRight']]
df_merged.LeftStatement.fillna(df_merged.RightStatement,inplace=True)
df_merged.RightStatement.fillna(df_merged.LeftStatement,inplace=True)
df_merged.fillna(0,inplace=True)
df_merged['Total'] = df_merged['AnswerValLeft'] + df_merged['AnswerValRight']
df_merged.rename(columns={'key_0':'TestKey','LeftStatement':'Statement'},inplace=True)
df_merged.drop(columns=['AnswerValLeft','AnswerValRight','RightStatement'],inplace=True)
df_merged.set_index('TestKey',inplace=True)

# Prepare a dataframe with candidate info

df_merged_w_cand = df_merged.merge(df[['CandidateKey']],left_index=True,right_index=True)
df_merged_w_cand.drop_duplicates(inplace=True)
df_cand = df_cand[['CandidateKey','Gender','Qualification']]
df_merged_w_cand = df_merged_w_cand.merge(df_cand,on=['CandidateKey']).drop(columns=['CandidateKey'])
df_merged_w_cand = df_merged_w_cand.set_index(df_merged.index)

# Encode the categorical features

cat_feat = df_merged_w_cand[['Gender','Qualification']]
enc = OneHotEncoder(handle_unknown='ignore',sparse_output=False)
enc.fit(cat_feat)
cat_feat = enc.transform(cat_feat)
cat_feat = pd.DataFrame(cat_feat,columns=enc.get_feature_names_out(), dtype='int',index=df_merged_w_cand.index)
cat_feat = cat_feat.loc[~cat_feat.index.duplicated(keep='first')]

# Drop the statements in the former dataframe that have nearly no entries

df_tran = df_merged_w_cand.pivot(columns='Statement', values='Total')
drop_cols = df_tran.columns[np.where(df_tran.count()<16000)]
df_tran.drop(columns=drop_cols, inplace=True)

# Perform the final merge

df_merged = df_tran.merge(cat_feat,left_index=True,right_index=True)

# Scale the features. Use the first 30 columns (which are the statements) for model training

sc = StandardScaler()
df_scaled = pd.DataFrame(sc.fit_transform(df_merged),index=df_merged.index,columns=df_merged.columns)
df_scaled.fillna(0, inplace=True)
best_dbscan = DBSCAN(min_samples=50,eps=10)
print("Fitting DBSCAN for PAQ with eps=10 and min_samples=50")
best_dbscan.fit(df_scaled)
print("Model fitted successfully")

# Use the labels to mark instances as anomalies and export the result

labels = pd.DataFrame(best_dbscan.labels_,index=df_scaled.index, columns=['label'])
labels['is_anomaly'] = labels[['label']].map(lambda label : 1 if label==-1 else 0)
labels.drop(columns=['label'],inplace=True)

target_csv_path = os.path.join(os.getcwd(), "anomalies", "PAQ","csv","dbscan_anomalies.csv")
labels[['is_anomaly']].to_csv(target_csv_path)
print(f"{target_csv_path} created")
print("PAQ DBSCAN Done")