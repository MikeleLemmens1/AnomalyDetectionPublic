"""FCA Fill

This script fills all tables in the DWH with all FCA related data.  

This script requires that the `./anomalies/FCA_detection.py` ran before it as it uses the generated csv-files. It also requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""

import pandas as pd
import numpy as np
import sys 
import os

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert

# Add anomalies to test
print("Preparing Test data")
path_test_anomalies = os.path.abspath("decoded_data/FCA/DimTestAnomalies.csv")
df_test_anomalies = pd.read_csv(path_test_anomalies)
df_test_anomalies["AnomaliesKey"] = df_test_anomalies.index + 1

path_test = os.path.abspath("decoded_data/FCA/FactTest.csv")
df_test = pd.read_csv(path_test)

df_test_anomalies['TestKey'] = df_test_anomalies.TestKey.astype(int)

df_test = pd.merge(df_test, df_test_anomalies[["TestKey", "AnomaliesKey"]],
                   on="TestKey", how="left")

df_test_anomalies.rename(columns={
    'SameAnswers': 'SameAnswer',

    "abod_anomaly": "Abod",
    'copod_anomaly':'Copod', 
    'ecod_anomaly':'Ecod', 
    'i_forest_anomaly':'iForest',
    'lof_anomaly':'Lof', 
    'pyod_ensemble_anomaly':'PyodEnsemble',

    'dbscan_anomaly':'DBSCAN', 
    'neighbours_anomaly':'Neighbours', 

    'anomaly_score':'AnomalyScore',
    'is_anomaly':'IsAnomaly',
}, 
inplace=True)

# Add anomalies to question
print("Preparing Question data")
path_question_anomalies = os.path.abspath("decoded_data/FCA/DimQuestionAnomalies.csv")
df_question_anomalies = pd.read_csv(path_question_anomalies)
df_question_anomalies["AnomaliesKey"] = df_question_anomalies.index + 1

path_question = os.path.abspath("decoded_data/FCA/FactQuestionFCA.csv")
df_question = pd.read_csv(path_question)

df_question = pd.merge(df_question, df_question_anomalies[["QuestionKey", "ItemId", "AnomaliesKey"]],
                       on=["QuestionKey", "ItemId"], how="left")

df_question = df_question[["QuestionKey", "TestKey", "Competence1Key",
                           "Competence2Key", "Competence3Key", "Competence4Key",
                           "AnomaliesKey", "ItemId", "Answer1", "Answer2",
                           "Answer3", "TimeSpent"]]

df_question = df_question.rename(columns={
    "Answer1": "AnswerSequence1",
    "Answer2": "AnswerSequence2",
    "Answer3": "AnswerSequence3"

})

df_question_anomalies = df_question_anomalies[["AnomaliesKey", "SameAnswers",
                                               "TooFast", "TooSlow"]]
df_question_anomalies = df_question_anomalies.rename(columns={'SameAnswers': 'SameAnswer'})

# TestAnomalies to DWH
zeros = {'AnomaliesKey': 0, 
         'SameAnswer': 0, 
         'TooFast': 0, 
         'TooSlow': 0, 
         'DBSCAN': 0,
         'Neighbours': 0, 
         'Copod': 0, 
         'Ecod': 0, 
         'iForest': 0, 
         'Lof': 0, 
         'PyodEnsemble': 0,
         'AnomalyScore': 0,
         'IsAnomaly':0,
        }

df_test_anomalies = df_test_anomalies._append(zeros, ignore_index=True)

df_test = df_test.replace(np.nan, 0)
df_test["AnomaliesKey"] = df_test["AnomaliesKey"].astype(int)

dim_test_anomalies = df_test_anomalies[[
    'AnomaliesKey',
    'SameAnswer', 
    'TooFast', 
    'TooSlow', 
    'DBSCAN',
    'Neighbours', 
    'Copod', 
    'Ecod', 
    'iForest', 
    'Lof',
    'PyodEnsemble',
    'AnomalyScore',
    'IsAnomaly',
]]

insert(
    df=dim_test_anomalies,
    table='DimTestAnomalies'
    )

# QuestionAnomalies to DWH
zeros = {"AnomaliesKey": 0, "SameAnswer": 0, "TooSlow": 0, "TooFast": 0}
df_question_anomalies = df_question_anomalies._append(zeros, ignore_index=True)

df_question = df_question.replace(np.nan, 0)
df_question["AnomaliesKey"] = df_question["AnomaliesKey"].astype(int)

insert(
    df=df_question_anomalies,
    table='DimQuestionAnomalies'
)

# Competences to DWH
path_competence = os.path.abspath("decoded_data/FCA/DimCompetence.csv")
df_competence = pd.read_csv(path_competence)
df_competence = df_competence[["CompetenceKey", "CompetenceCode", "ItemId",
                               "IdealAnswerSequence1", "IdealAnswerSequence2",
                               "IdealAnswerSequence3"]]

insert(
    df=df_competence,
    table='DimCompetence'
)

# Test to DWH
insert(
    df=df_test,
    table='FactTest'
)

# Question to DWH
insert(
    df=df_question,
    table='FactQuestionFCA'
)

# print("All done! <3")
