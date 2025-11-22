"""FCA Detection

This script runs all preprocessing and outlier detection scripts for FCA tests. 

This script requires that the `./decoderen/FCA_csv_for_DWH.py` ran before it as it uses the generated csv-files. 

This script creates the `./decoded_data/FCA/DimTestAnomalies.csv` and `./decoded_data/FCA/DimQuestionAnomalies.csv` files. 
"""

import os
import sys
import pandas as pd

root = os.path.abspath(".")
sys.path.append(root)

from func.run_script import python_script, compare_anomaly_models, conclude_anomaly

current_dir = os.path.abspath("anomalies")

anomaly_scripts = [
    'same_answers_question.py',
    'same_answers_test.py',
    'time_spent_question.py',
    'time_spent_test.py',
    'anomalies_pyod.py',
    'anomalies_dbscan.py',
    'neighbours.py',
]

general_scripts = [
    'pyod_ensemble.py'
]

for script in anomaly_scripts: 
    script_path = os.path.join(current_dir, 'FCA', 'scripts', script)
    python_script(script_path)

for script in general_scripts:
    script_path = os.path.join(current_dir, 'all', script)
    python_script(script_path, arguments="FCA")


## TEST ANOMALIES 

df_copod = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'copod.csv'))
df_ecod = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'ecod.csv'))
df_i_forest = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'i_forest.csv'))
df_lof = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'lof.csv'))
df_abod = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'abod.csv'))
df_neighbours = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'neighbours.csv'))
df_dbscan = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'dbscan_anomalies.csv'))
df_test_same_ans = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'same_answers_test_checked.csv'))
df_test_time_spent = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'time_spent_test_checked.csv'))
df_pyod_ensemble = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'pyod_ensemble.csv'))

df_test_anomalies = compare_anomaly_models(
    (df_copod, 'copod'), 
    (df_ecod, 'ecod'), 
    (df_i_forest, 'i_forest'),
    (df_lof, 'lof'),
    (df_test_same_ans, 'same_ans'),
    (df_test_time_spent, 'timespent'),
    (df_dbscan, 'dbscan'),
    (df_neighbours, 'neighbours'),
    (df_pyod_ensemble, 'pyod_ensemble'),
    id_column='TestKey'
)

### is_anomaly 
df_test_anomalies, threshold, percentile = conclude_anomaly(df_test_anomalies)
print('Calculated for FCA:', threshold)
print(f"The threshold corresponds to the {percentile:.2f}th percentile")

## same answer and timespent data
df_test_anomalies = df_test_anomalies.merge(df_test_same_ans[['TestKey','SameAnswerPercentage']], on='TestKey')
df_test_anomalies = df_test_anomalies.merge(df_test_time_spent[['TestKey', 'TooSlow','TooFast']], on='TestKey')
df_test_anomalies.rename(columns={'SameAnswerPercentage':'SameAnswer'}, inplace=True)
df_test_anomalies.drop(columns=['timespent_anomaly', 'same_ans_anomaly'], inplace=True)

df_test_anomalies.to_csv(os.path.join(root, 'decoded_data', 'FCA', 'DimTestAnomalies.csv'), index=False)

## QUESTION ANOMALIES 

df_question_same_ans = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'same_answers_question_checked.csv'))
df_question_time_spent = pd.read_csv(os.path.join(current_dir, 'FCA', 'csv', 'time_spent_question_checked.csv'))

df_question_anomalies = df_question_time_spent.merge(df_question_same_ans)

df_question_anomalies.to_csv(os.path.join(root, 'decoded_data', 'FCA', 'DimQuestionAnomalies.csv'), index=False)
