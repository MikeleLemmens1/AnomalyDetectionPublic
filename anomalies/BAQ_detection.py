"""BAQ Detection

This script runs all preprocessing and outlier detection scripts for BAQ tests. 

This script requires that the `./decoderen/BAQ_csv_for_DWH.py` ran before it as it uses the generated csv-files. 

This script creates the `./decoded_data/BA51/DimTestAnomalies.csv` file. 
"""

import os
import sys
import pandas as pd

root = os.path.abspath(".")
sys.path.append(root)

from func.run_script import python_script, compare_anomaly_models, conclude_anomaly

current_dir = os.path.abspath("anomalies")
print(current_dir)

anomaly_scripts = [
    'preprocessing.py', 
    'anomalies_pyod.py',
    'anomalies_dbscan.py',
    'neighbours.py',
]

general_scripts = [
    'pyod_ensemble.py'
]

for script in anomaly_scripts: 
    script_path = os.path.join(current_dir, 'BAQ', 'scripts', script)
    python_script(script_path)

for script in general_scripts:
    script_path = os.path.join(current_dir, 'all', script)
    python_script(script_path, arguments="BAQ")

## TEST ANOMALIES 

df_copod = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'copod.csv'))
df_ecod = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'ecod.csv'))
df_i_forest = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'i_forest.csv'))
df_lof = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'lof.csv'))
df_abod = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'abod.csv'))
df_dbscan = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'dbscan_anomalies.csv'))
df_neighbours = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'neighbours.csv'))
df_pyod_ensemble = pd.read_csv(os.path.join(current_dir, 'BAQ', 'csv', 'pyod_ensemble.csv'))

df_test_anomalies = compare_anomaly_models(
    (df_copod, 'copod'), 
    (df_ecod, 'ecod'), 
    (df_i_forest, 'i_forest'),
    (df_lof, 'lof'),
    (df_abod, 'abod'),
    (df_neighbours, 'neighbours'),
    (df_dbscan, 'dbscan'),
    (df_pyod_ensemble, 'pyod_ensemble'),
    id_column='TestKey'
)

### is_anomaly 
df_test_anomalies, threshold, percentile = conclude_anomaly(df_test_anomalies)
print('Calculated threshold for BAQ:', threshold)
print(f"The threshold corresponds to the {percentile:.2f}th percentile")

df_test_anomalies.to_csv(os.path.join(root, 'decoded_data', 'BA51', 'DimTestAnomalies.csv'), index=False)
