"""MDQ Detection

This script runs all preprocessing and outlier detection scripts for MDQ tests. 

This script requires that the `./decoderen/MDQ_csv_for_DWH.py` ran before it as it uses the generated csv-files. 

This script creates the `./decoded_data/MDQ/DimTestAnomalies.csv` file. 
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
]

for script in anomaly_scripts: 
    script_path = os.path.join(current_dir, 'MDQ', 'scripts', script)
    python_script(script_path)

## TEST ANOMALIES 

df_copod = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'copod.csv'))
df_ecod = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'ecod.csv'))
df_i_forest = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'i_forest.csv'))
df_lof = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'lof.csv'))
df_abod = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'abod.csv'))
df_dbscan = pd.read_csv(os.path.join(current_dir, 'MDQ', 'csv', 'dbscan_anomalies.csv'))

df_test_anomalies = compare_anomaly_models(
    (df_copod, 'copod'), 
    (df_ecod, 'ecod'), 
    (df_i_forest, 'i_forest'),
    (df_lof, 'lof'),
    (df_abod, 'abod'),
    (df_dbscan, 'dbscan'),
    id_column='TestKey'
)

### is_anomaly 
df_test_anomalies, threshold, percentile = conclude_anomaly(df_test_anomalies)
print('Calculated threshold for MDQ:', threshold)
print(f"The threshold corresponds to the {percentile:.2f}th percentile")

df_test_anomalies.to_csv(os.path.join(root, 'decoded_data', 'MDQ', 'DimTestAnomalies.csv'), index=False)
