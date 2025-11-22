"""FCA csv for DWH

This script prepares raw decoded FCA data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the FCA data is decoded and that the raw data is stored in `./decoderen/raw_data/decoded_fca.csv`. 
"""

import pandas as pd
import numpy as np
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

# connection with the database
channel_crh = dep2connection("CRH")
channel_dwh = dep2connection("CRH_DWH")
cursor = channel_dwh.cursor()

print("Collecting the data")

# FCA decoded data
decoded_path = os.path.abspath("decoderen/raw_data/decoded_fca.csv")
df_decoded = pd.read_csv(decoded_path)
df_decoded.drop(columns=["Sequence1", "Sequence2", "Sequence3", "InstrumentClassId"],
                inplace=True)

# Other data for FCA tests
df_not_coded = pd.read_sql(
    "SELECT ID, CandidateID, InstanceID, TestStartTime, TestFinishTime, Data, CreatedDate, ModifiedDate, VersionNumber, PostedDate FROM CandidateResultFCA",
    channel_crh)

# Combine both
df_fca = pd.merge(df_decoded, df_not_coded, left_on=["CandidateId", "InstanceId"],
                  right_on=["CandidateID", "InstanceID"], how="left")

# Get necessary candidate data
df_candidate = pd.read_sql("SELECT CandidateKey, ID, InstanceID FROM DimCandidate",
                           channel_dwh)

df_fca = pd.merge(df_fca, df_candidate, left_on=["CandidateId", "InstanceId"],
                  right_on=["ID", "InstanceID"], how="left")

df_fca.drop(columns=["CandidateId", "ID_y", "CandidateID", "InstanceId", "InstanceID_x", "InstanceID_y"],
            inplace=True)
df_fca.rename(columns={"ID_x": "TestID"}, inplace=True)

# Get necessary data from DimDate
df_dates = pd.read_sql("SELECT DateKey, Date FROM DimDate", channel_dwh)

df_fca["CreatedDate"] = pd.to_datetime(df_fca["CreatedDate"]).dt.date
df_fca = pd.merge(df_fca, df_dates, left_on="CreatedDate", right_on="Date", how="left")
df_fca.drop(columns=["Date", "CreatedDate"], inplace=True)
df_fca.rename(columns={"DateKey": "CreatedDateKey"}, inplace=True)

df_fca["ModifiedDate"] = pd.to_datetime(df_fca["ModifiedDate"]).dt.date
df_fca = pd.merge(df_fca, df_dates, left_on="ModifiedDate", right_on="Date", how="left")
df_fca.drop(columns=["Date", "ModifiedDate"], inplace=True)
df_fca.rename(columns={"DateKey": "ModifiedDateKey"}, inplace=True)

df_fca["PostedDate"] = pd.to_datetime(df_fca["PostedDate"]).dt.date
df_fca = pd.merge(df_fca, df_dates, left_on="PostedDate", right_on="Date", how="left")
df_fca.drop(columns=["Date", "PostedDate"], inplace=True)
df_fca.rename(columns={"DateKey": "PostedDateKey"}, inplace=True)

# Get necessary data from DimTime
df_time = pd.read_sql("SELECT TimeKey, tekst FROM DimTime", channel_dwh)
df_time["tekst"] = pd.to_datetime(df_time["tekst"], format='%H:%M:%S').dt.time

df_fca["TestStartTime"] = pd.to_datetime(df_fca["TestStartTime"]).dt.round('s').dt.time
df_fca = pd.merge(df_fca, df_time, left_on="TestStartTime", right_on="tekst", how="left")
df_fca.drop(columns=["tekst", "TestStartTime"], inplace=True)
df_fca.rename(columns={"TimeKey": "TestStartTimeKey"}, inplace=True)

df_fca["TestFinishTime"] = pd.to_datetime(df_fca["TestFinishTime"]).dt.round('s').dt.time
df_fca = pd.merge(df_fca, df_time, left_on="TestFinishTime", right_on="tekst", how="left")
df_fca.drop(columns=["tekst", "TestFinishTime"], inplace=True)
df_fca.rename(columns={"TimeKey": "TestFinishTimeKey"}, inplace=True)

# duplicate check 
columns_test = df_fca.columns
columns_test = columns_test.drop("TestID")
columns_test = columns_test.drop("TestStartTimeKey")
df_fca.drop_duplicates(inplace=True, subset=columns_test)

print("Create dataframes for correct files")

# Split df_fca into test, question and competence df
df_test = df_fca[["TestID", "CandidateKey", "CreatedDateKey",
                   "ModifiedDateKey", "PostedDateKey", "TestStartTimeKey",
                   "TestFinishTimeKey", "VersionNumber"]].copy()

df_test.drop_duplicates(inplace=True)

df_test.reset_index(inplace=True, drop=True)
df_test["TestKey"] = df_test.index + 1

df_competence1 = df_fca[["Competency_1", "ItemId", "Correct_answer_comp1_seq1", "Correct_answer_comp1_seq2", "Correct_answer_comp1_seq3"]].copy()
df_competence2 = df_fca[["Competency_2", "ItemId", "Correct_answer_comp2_seq1", "Correct_answer_comp2_seq2", "Correct_answer_comp2_seq3"]].copy()
df_competence3 = df_fca[["Competency_3", "ItemId", "Correct_answer_comp3_seq1", "Correct_answer_comp3_seq2", "Correct_answer_comp3_seq3"]].copy()
df_competence4 = df_fca[["Competency_4", "ItemId", "Correct_answer_comp4_seq1", "Correct_answer_comp4_seq2", "Correct_answer_comp4_seq3"]].copy()
df_competence1.rename(columns={"Competency_1": "CompetenceCode", "Correct_answer_comp1_seq1":"IdealAnswerSequence1",
                               "Correct_answer_comp1_seq2":"IdealAnswerSequence2", "Correct_answer_comp1_seq3":"IdealAnswerSequence3"},
                                inplace=True)
df_competence2.rename(columns={"Competency_2": "CompetenceCode", "Correct_answer_comp2_seq1":"IdealAnswerSequence1",
                               "Correct_answer_comp2_seq2":"IdealAnswerSequence2", "Correct_answer_comp2_seq3":"IdealAnswerSequence3"},
                               inplace=True)
df_competence3.rename(columns={"Competency_3": "CompetenceCode", "Correct_answer_comp3_seq1":"IdealAnswerSequence1",
                               "Correct_answer_comp3_seq2":"IdealAnswerSequence2", "Correct_answer_comp3_seq3":"IdealAnswerSequence3"},
                               inplace=True)
df_competence4.rename(columns={"Competency_4": "CompetenceCode", "Correct_answer_comp4_seq1":"IdealAnswerSequence1",
                               "Correct_answer_comp4_seq2":"IdealAnswerSequence2", "Correct_answer_comp4_seq3":"IdealAnswerSequence3"},
                               inplace=True)

df_competence = pd.concat([df_competence1, df_competence2, df_competence3, df_competence4])
df_competence.drop_duplicates(inplace=True)
df_competence.reset_index(inplace=True, drop=True)

df_competence = df_competence[df_competence["CompetenceCode"] != 0]
df_competence["CompetenceKey"] = df_competence.index + 1


df_question = df_fca.drop(
    columns=["CandidateKey", "CreatedDateKey", "ModifiedDateKey", "PostedDateKey", 
             "TestStartTimeKey", "TestFinishTimeKey", "VersionNumber", "Data"
             ])

# change: merge op TestID terugzetten 
df_question = pd.merge(df_question, df_test[["TestKey", "TestID"]], on="TestID", how="left")
df_test.drop(columns=["TestID"], inplace=True)
df_question.drop(columns=["TestID"], inplace=True)
# einde change 

for i in [1,2,3,4]:
    df_question = pd.merge(left=df_question, right=df_competence, how='left',
                        left_on=["ItemId", f"Competency_{i}", f"Correct_answer_comp{i}_seq1", f"Correct_answer_comp{i}_seq2", f"Correct_answer_comp{i}_seq3"],
                        right_on=["ItemId", "CompetenceCode", "IdealAnswerSequence1", "IdealAnswerSequence2", "IdealAnswerSequence3"])
    df_question.drop(columns=[f"Competency_{i}", "CompetenceCode", "IdealAnswerSequence1", "IdealAnswerSequence2", "IdealAnswerSequence3"], inplace=True)
    df_question.rename(columns={"CompetenceKey": f"Competence{i}Key"}, inplace=True)

df_question.rename(columns={
    "Answer1" : "AnswerSequence1",
    "Answer2" : "AnswerSequence2",
    "Answer3" : "AnswerSequence3",
})
df_question = df_question.drop(columns=["Correct_answer_comp1_seq1",
                                   "Correct_answer_comp1_seq2",
                                   "Correct_answer_comp1_seq3",
                                   "Correct_answer_comp2_seq1",
                                   "Correct_answer_comp2_seq2",
                                   "Correct_answer_comp2_seq3",
                                   "Correct_answer_comp3_seq1",
                                   "Correct_answer_comp3_seq2",
                                   "Correct_answer_comp3_seq3",
                                   "Correct_answer_comp4_seq1",
                                   "Correct_answer_comp4_seq2",
                                   "Correct_answer_comp4_seq3",])
df_question["QuestionKey"] = df_question.index + 1

df_question = df_question.replace(np.nan, 0)
df_question["Competence2Key"] = df_question["Competence2Key"].astype(int)
df_question["Competence3Key"] = df_question["Competence3Key"].astype(int)
df_question["Competence4Key"] = df_question["Competence4Key"].astype(int)

df_question = df_question[[
    "QuestionKey", "TestKey", 
    "Competence1Key", "Competence2Key", "Competence3Key", "Competence4Key", 
    "ItemId", "Answer1", "Answer2", "Answer3", "TimeSpent"
    ]]

print("Creating the CSVs")

# Make the CSVs
df_competence = df_competence[["CompetenceKey", "CompetenceCode", "ItemId",
                               "IdealAnswerSequence1", "IdealAnswerSequence2",
                               "IdealAnswerSequence3"]]
zeros = {"CompetenceKey": 0, "CompetenceCode": 0, "ItemId": 0,
         "IdealAnswerSequence1": 0, "IdealAnswerSequence2": 0,
         "IdealAnswerSequence3": 0}
df_competence = df_competence._append(zeros, ignore_index=True)

competence_path = os.path.abspath("decoded_data/FCA/DimCompetence.csv")
df_competence.to_csv(competence_path, index=False)


df_test.loc[:, 'Test'] = 'FCA'
test_path = os.path.abspath("decoded_data/FCA/FactTest.csv")
df_test.to_csv(test_path, index=False)

question_path = os.path.abspath("decoded_data/FCA/FactQuestionFCA.csv")
df_question.to_csv(question_path, index=False)