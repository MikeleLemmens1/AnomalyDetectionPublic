"""PAQ Fill

This script fills all tables in the DWH with all PAQ related data.  

This script requires that the `./anomalies/PAQ_detection.py` ran before it as it uses the generated csv-files. It also requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""

import pandas as pd
import sys 
import os

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert, get_max_anomaly_key

print('Preparing data')

test_path = os.path.abspath("decoded_data/PAQ/FactTest.csv")
question_path = os.path.abspath("decoded_data/PAQ/FactQuestionPAQ.csv")

df_test_PAQ = pd.read_csv(test_path)
df_question = pd.read_csv(question_path)

# Test anomalies
max_test_key = get_max_anomaly_key(table="DimTestAnomalies")

test_anomalies_path = os.path.abspath("decoded_data/PAQ/DimTestAnomalies.csv")
df_test_anomalies = pd.read_csv(test_anomalies_path)
df_test_anomalies["AnomaliesKey"] = df_test_anomalies.index + 1 + max_test_key

df_test_anomalies.rename(columns={
        "copod_anomaly": "Copod",
        "ecod_anomaly": "Ecod",
        "i_forest_anomaly": "iForest",
        "lof_anomaly": "Lof",
        "abod_anomaly": "Abod",
        'pyod_ensemble_anomaly':'PyodEnsemble',
        
        'dbscan_anomaly':'DBSCAN', 
        'neighbours_anomaly':'Neighbours', 

        "anomaly_score": "AnomalyScore",
        'is_anomaly':'IsAnomaly',
    }, inplace=True)

dim_test_anomalies = df_test_anomalies[[
    'AnomaliesKey', 

    'Copod', 
    'Ecod', 
    'iForest', 
    'Lof', 
    'Abod', 
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
df_test_PAQ = pd.merge(
    df_test_PAQ, 
    df_test_anomalies[["TestKey", "AnomaliesKey"]], 
    on="TestKey", how="left")

fact_test = df_test_PAQ[['Test', 'CandidateKey', 'CreatedDateKey', 'VersionNumber', 'TestKey', 'AnomaliesKey']]

insert(
    df=fact_test,
    table='FactTest'
)

# Question
df_question = df_question[['QuestionKey', 'TestKey', 'LeftStatement', 'RightStatement',  'AnswerVal']]
insert(
    df=df_question,
    table='FactQuestionPAQ'
)
