"""SJT Fill

This script fills all tables in the DWH with all SJT related data.  

This script requires that the `./anomalies/SJT_detection.py` ran before it as it uses the generated csv-files. It also requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""

import pandas as pd
import numpy as np
import sys 
import os

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert, get_max_anomaly_key

print("Preparing data")
test_path = os.path.abspath("decoded_data/SJT/FactTest.csv")
question_path = os.path.abspath("decoded_data/SJT/FactQuestionSJT.csv")

df_test_SJT = pd.read_csv(test_path)
df_question = pd.read_csv(question_path)

# Question anomalies
fca_quest_anom_path = os.path.abspath("decoded_data/FCA/DimQuestionAnomalies.csv")

max_question_key = get_max_anomaly_key(table='DimQuestionAnomalies')

question_anomalies_path = os.path.abspath("decoded_data/SJT/DimQuestionAnomalies.csv")
df_question_anomalies = pd.read_csv(question_anomalies_path)
df_question_anomalies["AnomaliesKey"] = df_question_anomalies.index + 1 + max_question_key
df_question_anomalies = df_question_anomalies.rename(columns={'SameAnswers': 'SameAnswer'})
dim_question_anomalies = df_question_anomalies[['AnomaliesKey', 'TooSlow', 'TooFast', 'SameAnswer']]

insert(
    df=dim_question_anomalies,
    table='DimQuestionAnomalies'
)

# Test anomalies
max_test_key = get_max_anomaly_key(table='DimTestAnomalies')

test_anomalies_path = os.path.abspath("decoded_data/SJT/DimTestAnomalies.csv")
df_test_anomalies = pd.read_csv(test_anomalies_path)
df_test_anomalies["AnomaliesKey"] = df_test_anomalies.index + 1 + max_test_key

df_test_anomalies.rename(columns={
    'SameAnswerPercentage':'SameAnswer',

    'copod_anomaly':'Copod', 
    'ecod_anomaly':'Ecod', 
    'i_forest_anomaly':'iForest',
    'lof_anomaly':'Lof', 
    "abod_anomaly": "Abod",
    'pyod_ensemble_anomaly':'PyodEnsemble',

    'dbscan_anomaly':'DBSCAN', 
    'neighbours_anomaly':'Neighbours', 

    'anomaly_score':'AnomalyScore',
    'is_anomaly':'IsAnomaly',
}, 
inplace=True)

dim_test_anomalies = df_test_anomalies[[
    'AnomaliesKey', 

    'SameAnswer', 
    'TooFast', 
    'TooSlow',

    'Copod', 
    'Ecod', 
    'iForest', 
    'Lof', 
    'PyodEnsemble',

    'DBSCAN',
    'Neighbours', 

    'AnomalyScore',
    'IsAnomaly',
    ]]

insert(
    df=dim_test_anomalies,
    table='DimTestAnomalies'
)

# Test
df_test_SJT = pd.merge(
    df_test_SJT, 
    df_test_anomalies[["TestKey", "AnomaliesKey"]], 
    on="TestKey", how="left")

insert(
    df=df_test_SJT,
    table='FactTest'
)

# Question
df_question = pd.merge(df_question, 
                       df_question_anomalies[["QuestionKey", "AnomaliesKey"]],
                       on="QuestionKey", how="left")

df_question.drop(columns=['Test', 'InstanceID'], inplace=True)

df_question = df_question.replace(np.nan, 0)
df_question["AnomaliesKey"] = df_question["AnomaliesKey"].astype(int)

insert(
    df=df_question,
    table='FactQuestionSJT'
)

# print("All done! <3")