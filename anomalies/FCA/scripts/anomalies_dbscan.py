'''
This module uses DBSCAN as an unsupervised clustering algorithm. 
All instances that aren't part of a cluster are marked as an anomaly.
Because there are many different ItemID's, aggregations on test level are used
to compare different instances. For every test, the following columns are calculated:

- The mean answer of the test instance
- The standard deviation of the answers
- The sum of all the answer values
- The lowest answer (usually 1, but 0 is possible when a question is skipped)
- The highest answer (usually 5)
- The ratio of every possible answer, ranging from 0 to 5 (included)
- The total time spent for the whole test

Input:
  - ./decoded_data/FCA/FactTest.csv
  - ./decoded_data/FCA/FactQuestionFCA.csv
  - ./decoded_data/FCA/FactQuestion.csv
  - ./decoded_data/DimCandidate.csv
  - ./decoded_data/Language_codes.csv
  - All DimTime fields from the DWH

Output:
  - ./anomalies/FCA/csv/dbscan_anomalies.csv
'''

import pandas as pd
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import os
import sys
sys.path.append(".")
from func.dep2pyodbc import dep2connection

# Prepare csv's for joining
## FactTest
path = os.path.join(os.getcwd(), "decoded_data", "FCA", "FactTest.csv")
df_fact_test = pd.read_csv(path)
df_fact_test.drop(columns=["CreatedDateKey","ModifiedDateKey","PostedDateKey","VersionNumber"],inplace=True)
## FactQuestion
path = os.path.join(os.getcwd(), "decoded_data", "FCA", "FactQuestionFCA.csv")
df_fact_question = pd.read_csv(path)
df_fact_question.drop(columns=["Competence1Key","Competence2Key","Competence3Key","Competence4Key"],inplace=True)
## Candidate
path = os.path.join(os.getcwd(), "decoded_data", "DimCandidate.csv")
df_DimCand = pd.read_csv(path)
df_DimCand.drop(columns=["ID","InstanceID"],inplace=True)
cols = ["CandidateKey", "Gender", "ChosenGender", "ChosenLanguage", "Qualification"]
df_DimCand = df_DimCand[cols]
## Languages
path = os.path.join(os.getcwd(), "decoded_data", "Language_codes.csv")
languages = pd.read_csv(path,delimiter=";")
## DimTime
con = dep2connection("CRH_DWH")
query = 'SELECT * FROM DimTime'
df_DimTime = pd.read_sql(query,con)

# Merge all necessary files
df_fact_test = df_fact_test.merge(df_DimTime,left_on='TestStartTimeKey', right_on='TimeKey', how='inner')
df_fact_test.drop(columns=["TestStartTimeKey","TimeKey","uren","minuten","seconden","uur_12_not","am_pm"],inplace=True)
df_fact_test.rename(columns={"tekst":"TestStartTime"},inplace=True)
df_fact_test = df_fact_test.merge(df_DimTime,left_on='TestFinishTimeKey', right_on='TimeKey', how='inner')
df_fact_test.drop(columns=["TestFinishTimeKey","TimeKey","uren","minuten","seconden","uur_12_not","am_pm"],inplace=True)
df_fact_test.rename(columns={"tekst":"TestFinishTime"},inplace=True)
df_fca = df_fact_test.merge(df_fact_question, on="TestKey", how="inner")
df_fca.rename(columns={"ItemId": "ItemID", "TimeSpent": "TimeSpentQuestion"},inplace=True)
df_fca = df_fca.merge(df_DimCand,on="CandidateKey", how='inner')
cols = ["QuestionKey","TestKey","ItemID","TimeSpentQuestion","TestStartTime","TestFinishTime","CandidateKey","Gender","ChosenGender","ChosenLanguage","Qualification","Answer1","Answer2","Answer3"]
df_fca = df_fca[cols]
del df_fact_test
del df_DimTime
del df_fact_question
del df_DimCand

def clean_dataset(df_fca):
    '''
    This function takes a dataframe of FCA questions and prettifies the values of each column
    Most of the columns stay present, TimeSpentTest is added as the total amount of seconds between start and finish
    
    Parameters:
    df_fca: a dataframe with the following columns:
      ["QuestionKey","TestKey","ItemID","TimeSpentQuestion","TestStartTime","TestFinishTime","CandidateKey","Gender","ChosenGender","ChosenLanguage","Qualification","Answer1","Answer2","Answer3"]
    
    Returns:
    a dataframe with the following columns:
      ['QuestionKey', 'TestKey', 'ItemID', 'TimeSpentQuestion',
       'TestStartTime', 'TestFinishTime', 'CandidateKey', 'Gender',
       'ChosenGender', 'ChosenLanguage', 'Qualification', 'Answer1', 'Answer2',
       'Answer3', 'TimeSpentTest']
    '''
    # Prettify languages
    languages.columns = ["ChosenLanguage","HudsonID"]
    df_fca = df_fca.merge(languages, how='left', on="ChosenLanguage")
    df_fca['ChosenLanguage'] = df_fca['HudsonID']
    df_fca.drop(columns=['HudsonID'],inplace=True)

    # Prettify Qualification and Genders
    df_fca['Qualification'] = df_fca['Qualification'].str.split(pat='_').str[1]
    df_fca['Gender'] = df_fca['Gender'].str.split(pat='_').str[1]
    df_fca['ChosenGender'] = df_fca['ChosenGender'].str.split(pat='_').str[1]

    # Add TimeDelta (TestFinish - TestStart) and clean negative values
    # Also convert the values to integers
    df_fca['TestStartTime'] = pd.to_datetime(df_fca['TestStartTime'], format='%H:%M:%S').dt.time
    df_fca['TestFinishTime'] = pd.to_datetime(df_fca['TestFinishTime'], format='%H:%M:%S').dt.time
    df_fca["TimeSpentTest"] = df_fca.apply(lambda row: 
        (datetime.combine(datetime.today(), row['TestFinishTime']) + timedelta(days=1) if row['TestFinishTime'] < row['TestStartTime'] else datetime.combine(datetime.today(), row['TestFinishTime'])) 
        - datetime.combine(datetime.today(), row['TestStartTime']), axis=1)
    df_fca.TimeSpentTest = df_fca.TimeSpentTest.dt.total_seconds().astype(int)

    # Fill missing values in Chosen Gender
    df_fca['ChosenGender'] = df_fca.ChosenGender.fillna(df_fca.Gender)

    return df_fca

df_fca = clean_dataset(df_fca)

# Transform the dataframe so that each item has 3 rows, an AnswerSequenceID column is created and the Answers for the item are in separate rows

df_melted = df_fca.melt(
    id_vars=['QuestionKey', 'TestKey','CandidateKey', 'ItemID', 'Gender', 'ChosenGender', 
             'ChosenLanguage', 'Qualification', 'TimeSpentTest'],
    value_vars=['Answer1', 'Answer2', 'Answer3'],
    var_name='AnswerID', value_name='Answer'
)
# Rename the AnswerSequenceID so that it contains the itemID

df_melted['AnswerID'] = df_melted['AnswerID'] + '_' + df_melted['ItemID'].astype(str)
df_pivot = df_melted.pivot_table(
    index=['TestKey', 'Gender', 'ChosenGender', 'ChosenLanguage', 'Qualification', 'TimeSpentTest'],
    columns='AnswerID', values='Answer', aggfunc='first'
).reset_index()

del df_melted

# All tests have NaN because not every item is included in the test
# To make a difference between a blank answer (0), fill NaN with -1
# df_pivot = df_pivot.fillna(-1.0)

df_pivot.columns.name = None
df_fca_transformed = df_pivot.set_index('TestKey')
del df_pivot

df_fca_transformed['mean'] = df_fca_transformed.iloc[:,5:].mean(axis=1)
df_fca_transformed['std'] = df_fca_transformed.iloc[:,5:-1].std(axis=1)
df_fca_transformed['sum'] = df_fca_transformed.iloc[:,5:-2].sum(axis=1)
df_fca_transformed['min'] = df_fca_transformed.iloc[:,5:-3].min(axis=1)
df_fca_transformed['max'] = df_fca_transformed.iloc[:,5:-5].max(axis=1)

# Copy df_fca_transformed and proceed with aggregated columns

df_answers_per_test = df_fca_transformed.drop(columns=['Gender','ChosenGender','ChosenLanguage','Qualification','TimeSpentTest','mean','std','sum','min','max'])
df_ratios = pd.DataFrame(index=df_fca_transformed.index)
for i in range(0,6):
  df_ratios[f"ratio_{i}'s"] = df_answers_per_test[df_answers_per_test==i].count(axis=1)/df_answers_per_test.count(axis=1)

df_agg = pd.concat([df_fca_transformed.TimeSpentTest,df_fca_transformed[['mean','std','sum','min','max']],df_ratios],axis=1)
del df_fca_transformed
# Scale and impute the aggregations
# Remove duplicates

sc_agg = StandardScaler()
df_agg_scaled = pd.DataFrame(sc_agg.fit_transform(df_agg),index=df_agg.index,columns=df_agg.columns)
df_agg_dedup_sc = df_agg_scaled.drop_duplicates()
df_agg_dedup_sc.columns = df_agg_scaled.columns
df_dbscan = df_agg_dedup_sc
del df_agg
# Deploy DBSCAN

dbscan = DBSCAN(eps=0.9, min_samples=50, n_jobs=-1)
print("Fitting DBSCAN for FCA with eps=2 and min_samples=50")
dbscan.fit(df_dbscan)
print("Model fitted successfully")

labels = pd.DataFrame(dbscan.labels_,index=df_agg_dedup_sc.index, columns=['label'])
dbscan_anom = pd.concat([df_dbscan,labels],axis=1)
dbscan_anom['is_anomaly'] = dbscan_anom[['label']].map(lambda label : 1 if label==-1 else 0)

target_csv_path = os.path.join(os.getcwd(), "anomalies", "FCA","csv","dbscan_anomalies.csv")
dbscan_anom[['is_anomaly']].to_csv(target_csv_path)
print(f"{target_csv_path} created")
print("FCA DBSCAN Done")
