"""BAQ csv for DWH

This script prepares raw decoded BAQ data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the BAQ data is decoded and that the raw data is stored in `./decoderen/raw_data/decoded_baq.csv`. 
"""
import pandas as pd
import itertools
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

channel_crh = dep2connection("CRH")
channel_dwh = dep2connection("CRH_DWH")
cursor = channel_dwh.cursor()

print("Collecting the data")
baq_path = os.path.abspath("decoderen/raw_data/decoded_baq.csv")
df_baq = pd.read_csv(baq_path)

df_baq.rename(columns={
    'itemId_norm': 'NormItemID',
    'itemId_ips': 'IpsItemID',
    'norm_1': 'Norm1',
    'norm_2': 'Norm2',
    'norm_3': 'Norm3',
    'norm_4': 'Norm4',
    'norm_5': 'Norm5',
    'ips_1': 'Ips1',
    'ips_2': 'Ips2',
    'ips_3': 'Ips3',
    'ips_4': 'Ips4',
    'ips_5': 'Ips5',
    }, inplace=True)
df_baq['Test'] = 'BAQ'

# Cleaning
columns = ['Ips1', 'Ips2', 'Ips3', 'Ips4', 'Ips5', 'Norm1', 'Norm2', 'Norm3', 'Norm4', 'Norm5']

for col in columns:
    in_range = df_baq[col].isin([1, 2, 3, 4, 5]).all()
    if not in_range: 
        print(f"Some values in the {col} column do not fall in the permitted range.")
        df_baq = df_baq[df_baq[col].isin([1, 2, 3, 4, 5])]
    else: 
        print(f"All values in the {col} column fall in the permitted range.")

numbers = [1, 2, 3, 4, 5]
permutations = list(itertools.permutations(numbers))
permutations_list = [list(perm) for perm in permutations]
permutations_list[0], permutations_list[-1]

df_baq['combined_list'] = df_baq[['Norm1', 'Norm2', 'Norm3', 'Norm4', 'Norm5']].values.tolist()

df_baq = df_baq[df_baq['combined_list'].isin(permutations_list)]

df_baq.drop(columns=['combined_list'], inplace=True)

print("All values are now in the permitted range")

# Candidates
df_candidates_before_key = pd.read_sql("SELECT ID, CandidateID, InstanceID, CreatedDate, ModifiedDate, VersionNumber FROM CandidateResultBA51", channel_crh)

df_baq = pd.merge(df_baq, df_candidates_before_key, on=["CandidateID", "InstanceID"], how="left")

dim_candidate = pd.read_sql("SELECT CandidateKey, ID, InstanceID FROM DimCandidate", channel_dwh)

df_baq = pd.merge(df_baq, dim_candidate, left_on=["CandidateID", "InstanceID"], right_on=["ID", "InstanceID"], how="left")

df_baq.drop(columns=["ID_y", "CandidateID"], inplace=True)
df_baq.rename(columns={"ID_x": "TestID"}, inplace=True)

# Dates
df_dates = pd.read_sql("SELECT DateKey, Date FROM DimDate", channel_dwh)

df_baq["CreatedDate"] = pd.to_datetime(df_baq["CreatedDate"]).dt.date
df_baq = pd.merge(df_baq, df_dates, left_on="CreatedDate", right_on="Date", how="left")
df_baq.drop(columns=["Date", "CreatedDate"], inplace=True)
df_baq.rename(columns={"DateKey": "CreatedDateKey"}, inplace=True)

df_baq["ModifiedDate"] = pd.to_datetime(df_baq["ModifiedDate"]).dt.date
df_baq = pd.merge(df_baq, df_dates, left_on="ModifiedDate", right_on="Date", how="left")
df_baq.drop(columns=["Date", "ModifiedDate"], inplace=True)
df_baq.rename(columns={"DateKey": "ModifiedDateKey"}, inplace=True)

print("Create dataframes for correct files")
# Test
paq_path = os.path.abspath("decoded_data/PAQ/FactTest.csv")
df_test_paq = pd.read_csv(paq_path)

max_key = df_test_paq.TestKey.max()

df_test = df_baq[["TestID", "Test", "CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"]]

df_test.drop_duplicates(inplace=True)
df_test.reset_index(inplace=True, drop=True)
df_test["TestKey"] = df_test.index + max_key + 1

# Question
df_question = df_baq.drop(columns=["CandidateKey", "CreatedDateKey", "ModifiedDateKey", "VersionNumber"])
df_question["QuestionKey"] = df_question.index + 1

chunk_size = 100_000
chunks = []
c = 0
for chunk_start in range(0, len(df_question), chunk_size):
    c += 1
    chunk_end = chunk_start + chunk_size
    chunk = df_question.iloc[chunk_start:chunk_end]
    chunk_result = pd.merge(chunk, df_test[["TestKey", "TestID"]], on="TestID", how="left")
    chunks.append(chunk_result)
    if c % 10 == 0: print(f"chuck {c} complete")

df_question = pd.concat(chunks)
df_question.drop(columns=['TestID', 'InstanceID'], inplace=True)
df_test.drop(columns=["TestID"], inplace=True)

print("Creating the CSVs")
# To csv
test_path = os.path.abspath("decoded_data/BA51/FactTest.csv")
question_path = os.path.abspath("decoded_data/BA51/FactQuestionBAQ.csv")

df_test.to_csv(test_path, index=False)
df_question.to_csv(question_path, index=False)