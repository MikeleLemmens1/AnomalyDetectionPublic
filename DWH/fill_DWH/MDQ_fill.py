"""MDQ Fill

This script fills all tables in the DWH with all MDQ related data.  

This script requires that the `./anomalies/MDQ_detection.py` ran before it as it uses the generated csv-files. It also requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""

import pandas as pd
import os
import sys

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert, get_max_anomaly_key

print('Preparing data')

test_path = os.path.abspath("decoded_data/MDQ/FactTest.csv")
test_anomalies_path = os.path.abspath("decoded_data/MDQ/DimTestAnomalies.csv")
df_test = pd.read_csv(test_path)
df_test_anomalies = pd.read_csv(test_anomalies_path)

# Test Anomalies
max_test_key = get_max_anomaly_key(table='DimTestAnomalies')

df_test_anomalies["AnomaliesKey"] = df_test_anomalies.index + 1 + max_test_key

df_test_anomalies.rename(columns={
        "copod_anomaly": "Copod",
        "ecod_anomaly": "Ecod",
        "i_forest_anomaly": "iForest",
        "lof_anomaly": "Lof",
        "abod_anomaly": "Abod",
        
        'dbscan_anomaly':'DBSCAN', 

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
    
    'DBSCAN',

    'AnomalyScore',
    'IsAnomaly',
    ]]

insert(
    df=dim_test_anomalies,
    table='DimTestAnomalies'
)

# Test to DWH
df_test = df_test.merge(df_test_anomalies, on='TestKey')
df_test[['VersionNumber']] = None

fact_test = df_test[['TestKey', 'Test', 'CandidateKey', 'CreatedDateKey','ModifiedDateKey',
                     'VersionNumber', 'AnomaliesKey']]

insert(
    df=fact_test,
    table='FactTest'
)

# Question to DWH
question_path = os.path.abspath("decoded_data/MDQ/FactQuestionMDQ.csv")
df_question = pd.read_csv(question_path)
df_question.rename(columns={'itemId':'ItemID'}, inplace=True)

fact_question = df_question[[
    'QuestionKey', 'TestKey', 'ItemID', 
    'FirstVal', 'SecondVal', 'ThirdVal', 
    'FourthVal', 'FifthVal', 'SixthVal'
    ]].copy()

# print('Deze gaat nen eroor gooien, enyoy!')
insert(
    df=fact_question,
    table='FactQuestionMDQ'
)

# print('All done!')
