"""SJT csv for DWH

This script prepares raw decoded SJT data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the SJT data is decoded and that the raw data is stored in `./decoderen/raw_data/decoded_sjt.csv`. 
"""

import pandas as pd
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

channel_crh = dep2connection("CRH")
channel_dwh = dep2connection("CRH_DWH")
cursor = channel_dwh.cursor()

print("Collecting the data")
sjt_path = os.path.abspath("decoderen/raw_data/decoded_sjt.csv")
sjt = pd.read_csv(sjt_path)

df_sjt = sjt[['CandidateID', 'InstanceID', 'itemId', 'answer1', 'answer2', 'answer3', 'timeSpent']]
df_sjt.rename(columns={
    'itemId':'ItemID', 
    'answer1': 'AnswerSequence1',
    'answer2': 'AnswerSequence2',
    'answer3': 'AnswerSequence3',
    'timeSpent': 'TimeSpent'
    }, inplace=True)
df_sjt['Test'] = 'SJT'

# Candidates
df_candidates_before_key = pd.read_sql("SELECT ID, CandidateID, InstanceID, CreatedDate, ModifiedDate, VersionNumber FROM CandidateResultSJT",
                                       channel_crh)

df_sjt = pd.merge(df_sjt, df_candidates_before_key, on=["CandidateID", "InstanceID"], how="left")

dim_candidate = pd.read_sql("SELECT CandidateKey, ID, InstanceID FROM DimCandidate", channel_dwh)

df_sjt = pd.merge(df_sjt, dim_candidate, left_on=["CandidateID", "InstanceID"],
                  right_on=["ID", "InstanceID"], how="left")

df_sjt.drop(columns=["ID_y", "CandidateID"], inplace=True)
df_sjt.rename(columns={"ID_x": "TestID"}, inplace=True)

# Dates
df_dates = pd.read_sql("SELECT DateKey, Date FROM DimDate", channel_dwh)

df_sjt["CreatedDate"] = pd.to_datetime(df_sjt["CreatedDate"]).dt.date
df_sjt = pd.merge(df_sjt, df_dates, left_on="CreatedDate", right_on="Date", how="left")
df_sjt.drop(columns=["Date", "CreatedDate"], inplace=True)
df_sjt.rename(columns={"DateKey": "CreatedDateKey"}, inplace=True)

df_sjt["ModifiedDate"] = pd.to_datetime(df_sjt["ModifiedDate"]).dt.date
df_sjt = pd.merge(df_sjt, df_dates, left_on="ModifiedDate", right_on="Date", how="left")
df_sjt.drop(columns=["Date", "ModifiedDate"], inplace=True)
df_sjt.rename(columns={"DateKey": "ModifiedDateKey"}, inplace=True)

print("Create dataframes for correct files")
# Test
fca_path = os.path.abspath("decoded_data/FCA/FactTest.csv")
df_test_fca = pd.read_csv(fca_path)
max_key = df_test_fca.TestKey.max()
df_test = df_sjt[["TestID", "Test", "CandidateKey", "CreatedDateKey", "VersionNumber"]]

df_test.drop_duplicates(inplace=True)
df_test.reset_index(inplace=True, drop=True)
df_test["TestKey"] = df_test.index + max_key + 1

# Question
df_question = df_sjt.drop(columns=["CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"])
df_question["QuestionKey"] = df_question.index + 1

df_question = pd.merge(df_question, df_test[["TestKey", "TestID"]], on="TestID", how="left")
df_question.set_index('QuestionKey', inplace=True)

df_test.drop(columns=["TestID"], inplace=True)
df_question.drop(columns=["TestID"], inplace=True)

# TimeSpent Test
df = df_question[["TestKey", "TimeSpent"]]

df_timespent = df.groupby('TestKey')['TimeSpent'].sum().reset_index()

df_test = df_test.merge(df_timespent, on='TestKey')

print("Creating the CSVs")
# To csv
test_path = os.path.abspath("decoded_data/SJT/FactTest.csv")
question_path = os.path.abspath("decoded_data/SJT/FactQuestionSJT.csv")

df_test.to_csv(test_path, index=False)
df_question.to_csv(question_path)