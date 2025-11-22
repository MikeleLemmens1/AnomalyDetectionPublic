"""BAQ Fill

This script fills all tables in the DWH with all BAQ related data.  

This script requires that the `./anomalies/BAQ_detection.py` ran before it as it uses the generated csv-files. It also requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""

import pandas as pd
import numpy as np
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert, get_max_anomaly_key

print('Preparing data')

test_path = os.path.abspath("decoded_data/BA51/FactTest.csv")
test_anomalies_path = os.path.abspath("decoded_data/BA51/DimTestAnomalies.csv")
df_test = pd.read_csv(test_path)
df_test_anomalies = pd.read_csv(test_anomalies_path)

# DimTestAnomalies
max_test_key = get_max_anomaly_key(table='DimTestAnomalies')
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

# Test to DWH
df_test = pd.merge(
    df_test,
    df_test_anomalies[["TestKey", "AnomaliesKey"]],
    on="TestKey", how="left"
)

df_test = df_test.replace(np.nan, 0)
df_test["AnomaliesKey"] = df_test["AnomaliesKey"].astype(int)

fact_test = df_test[['TestKey', 'Test', 'CandidateKey', 'CreatedDateKey','ModifiedDateKey', "AnomaliesKey"]]
fact_test[['VersionNumber']] = None

insert(
    df=fact_test,
    table='FactTest'
)

# Question
question_path = os.path.abspath("decoded_data/BA51/FactQuestionBAQ.csv")
df_question = pd.read_csv(question_path)

fact_question = df_question[[
    'QuestionKey', 'TestKey',
    'NormItemID', 'Norm1', 'Norm2', 'Norm3', 'Norm4', 'Norm5', 
    'IpsItemID', 'Ips1', 'Ips2', 'Ips3', 'Ips4', 'Ips5',]]

insert(
    df=fact_question,
    table='FactQuestionBAQ'
)
