"""PAQ csv for DWH

This script prepares raw decoded PAQ data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the PAQ data is decoded and that the raw data is stored in `./decoderen/raw_data/decoded_paq.csv`. 
"""

import pandas as pd
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

channel_crh = dep2connection("CRH")
channel_dwh_lisa = dep2connection("CRH_DWH")
cursor = channel_dwh_lisa.cursor()

print("Collecting the data")
paq_path = os.path.abspath("decoderen/raw_data/decoded_paq.csv")
paq = pd.read_csv(paq_path)

df_paq = paq[['CandidateID', 'InstanceID', 'left_statement', 'right_statement', 'anwser_val']]
df_paq.rename(columns={
    'left_statement': 'LeftStatement',
    'right_statement': 'RightStatement',
    'anwser_val': 'AnswerVal'
    }, inplace=True)
df_paq['Test'] = 'PAQ'

# Candidates
df_candidates_before_key = pd.read_sql("SELECT ID, CandidateID, InstanceID, CreatedDate, ModifiedDate, VersionNumber FROM CandidateResultPAQ", channel_crh)
df_paq = pd.merge(df_paq, df_candidates_before_key, on=["CandidateID", "InstanceID"], how="left")

dim_candidate = pd.read_sql("SELECT CandidateKey, ID, InstanceID FROM DimCandidate", channel_dwh_lisa)
df_paq = pd.merge(df_paq, dim_candidate, left_on=["CandidateID", "InstanceID"], right_on=["ID", "InstanceID"], how="left")

df_paq.drop(columns=["ID_y", "CandidateID"], inplace=True)
df_paq.rename(columns={"ID_x": "TestID"}, inplace=True)

# Dates
df_dates = pd.read_sql("SELECT DateKey, Date FROM DimDate", channel_dwh_lisa)

df_paq["CreatedDate"] = pd.to_datetime(df_paq["CreatedDate"]).dt.date
df_paq = pd.merge(df_paq, df_dates, left_on="CreatedDate", right_on="Date", how="left")
df_paq.drop(columns=["Date", "CreatedDate"], inplace=True)
df_paq.rename(columns={"DateKey": "CreatedDateKey"}, inplace=True)

df_paq["ModifiedDate"] = pd.to_datetime(df_paq["ModifiedDate"]).dt.date
df_paq = pd.merge(df_paq, df_dates, left_on="ModifiedDate", right_on="Date", how="left")
df_paq.drop(columns=["Date", "ModifiedDate"], inplace=True)
df_paq.rename(columns={"DateKey": "ModifiedDateKey"}, inplace=True)

# Cleaning
df_paq.dropna(inplace=True)
only_int = df_paq.AnswerVal.apply(lambda x: x % 1 == 0).all()

if only_int:
    df_paq['AnswerVal'] = df_paq['AnswerVal'].astype(int)

is_valid = df_paq['AnswerVal'].isin([1, 2, 3, 4, 5]).all()
if not is_valid: 
    df_paq = df_paq[df_paq['AnswerVal'].isin([1, 2, 3, 4, 5])]

print("Create dataframes for correct files")
# Test
sjt_path = os.path.abspath("decoded_data/SJT/FactTest.csv")
df_test_sjt = pd.read_csv(sjt_path)

max_key = df_test_sjt.TestKey.max()

df_test = df_paq[["TestID", "Test", "CandidateKey", "CreatedDateKey", "VersionNumber"]]

df_test.drop_duplicates(inplace=True)
df_test.reset_index(inplace=True, drop=True)
df_test["TestKey"] = df_test.index + max_key + 1

# Question
df_question = df_paq.drop(columns=["CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"])
df_question["QuestionKey"] = df_question.index + 1

df_question = pd.merge(df_question, df_test[["TestKey", "TestID"]], on="TestID", how="left")
df_question.set_index('QuestionKey', inplace=True)

df_test.drop(columns=["TestID"], inplace=True)
df_question.drop(columns=["TestID"], inplace=True)

print("Creating the CSVs")
# To csv
test_path = os.path.abspath("decoded_data/PAQ/FactTest.csv")
question_path = os.path.abspath("decoded_data/PAQ/FactQuestionPAQ.csv")

df_test.to_csv(test_path, index=False)
df_question.to_csv(question_path)