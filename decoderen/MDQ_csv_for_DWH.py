"""MDQ csv for DWH

This script prepares raw decoded MDQ data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the MDQ data is decoded and that the raw data is stored in `./decoderen/raw_data/decoded_mdq.csv`. 
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
mdq_path = os.path.abspath("decoderen/raw_data/decoded_mdq.csv")
mdq = pd.read_csv(mdq_path)

df_mdq = mdq[['CandidateID', 'InstanceID', 'itemId', 'first_val',
       'second_val', 'third_val', 'fourth_val', 'fifth_val', 'sixth_val']]
df_mdq.rename(columns={
    'first_val': 'FirstVal',
    'second_val': 'SecondVal',
    'third_val': 'ThirdVal',
    'fourth_val': 'FourthVal',
    'fifth_val': 'FifthVal',
    'sixth_val': 'SixthVal',
    }, inplace=True)
df_mdq['Test'] = 'MDQ'

# Cleaning
df_mdq['answer_sequence'] = df_mdq[['FirstVal', 'SecondVal', 'ThirdVal', 'FourthVal', 'FifthVal', 'SixthVal']].values.tolist()

df_mdq = df_mdq[df_mdq['answer_sequence'].apply(lambda x: any(x))]

df_mdq.drop(columns=['answer_sequence'], inplace=True)

# Candidate
df_candidates_before_key = pd.read_sql("SELECT ID, CandidateID, InstanceID, CreatedDate, ModifiedDate, VersionNumber FROM CandidateResultMotivation", channel_crh)

df_mdq = pd.merge(df_mdq, df_candidates_before_key, on=["CandidateID", "InstanceID"], how="left")

dim_candidate = pd.read_sql("SELECT CandidateKey, ID, InstanceID FROM DimCandidate", channel_dwh)

df_mdq = pd.merge(df_mdq, dim_candidate, left_on=["CandidateID", "InstanceID"], right_on=["ID", "InstanceID"], how="left")

df_mdq.drop(columns=["ID_y", "CandidateID"], inplace=True)
df_mdq.rename(columns={"ID_x": "TestID"}, inplace=True)

# Dates
df_dates = pd.read_sql("SELECT DateKey, Date FROM DimDate", channel_dwh)

df_mdq["CreatedDate"] = pd.to_datetime(df_mdq["CreatedDate"]).dt.date
df_mdq = pd.merge(df_mdq, df_dates, left_on="CreatedDate", right_on="Date", how="left")
df_mdq.drop(columns=["Date", "CreatedDate"], inplace=True)
df_mdq.rename(columns={"DateKey": "CreatedDateKey"}, inplace=True)

df_mdq["ModifiedDate"] = pd.to_datetime(df_mdq["ModifiedDate"]).dt.date
df_mdq = pd.merge(df_mdq, df_dates, left_on="ModifiedDate", right_on="Date", how="left")
df_mdq.drop(columns=["Date", "ModifiedDate"], inplace=True)
df_mdq.rename(columns={"DateKey": "ModifiedDateKey"}, inplace=True)

print("Create dataframes for correct files")
# Test
baq_path = os.path.abspath("decoded_data/BA51/FactTest.csv")
df_test_baq = pd.read_csv(baq_path)

max_key = df_test_baq.TestKey.max()

df_test = df_mdq[["TestID", "Test", "CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"]]

df_test.drop_duplicates(inplace=True)
df_test.reset_index(inplace=True, drop=True)
df_test["TestKey"] = df_test.index + max_key + 1

# Question
df_question = df_mdq.drop(columns=["CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"])
df_question["QuestionKey"] = df_question.index + 1

df_question = pd.merge(df_question, df_test[["TestKey", "TestID"]], on="TestID", how="left")

df_question.drop(columns=['TestID', 'InstanceID'], inplace=True)

df_test.drop(columns=["TestID"], inplace=True)

print("Creating the CSVs")
# To csv
test_path = os.path.abspath("decoded_data/MDQ/FactTest.csv")
question_path = os.path.abspath("decoded_data/MDQ/FactQuestionMDQ.csv")

df_test.to_csv(test_path, index=False)
df_question.to_csv(question_path, index=False)