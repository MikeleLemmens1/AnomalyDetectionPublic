"""Anomaly Detection for SJT Data

This script is designed to detect anomalies in the SJT dataset using various anomaly detection models 
from the `pyod` library. It includes data preprocessing, model training, and saving the anomaly detection 
results to CSV files for further analysis.

Usage:
- Ensure the required dataset (`preprocessed_data.csv`) is located in the `SJT/csv/` directory.
- Run the script to generate anomaly detection results for all models.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
import os

from pyod.models.ecod import ECOD
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.copod import COPOD
from pyod.models.abod import ABOD

# getting data
current_dir = os.path.abspath("anomalies")
df = pd.read_csv(os.path.join(current_dir, 'SJT', 'csv', 'preprocessed_data.csv'))

# preprocessing
X = df.select_dtypes(include=[np.number]).values
imputer = SimpleImputer(strategy='median')
X = imputer.fit_transform(X)
X = X.astype(np.float64)

# MODELLEN TRAINEN

# voor elke model dezelfde contamination
contamination= 0.01

def predict_model(model, name):
    """ Predict anomalies using a machine learning model.

    This function fits the provided model on a feature set (X), calculates anomaly scores, 
    and predicts whether each instance is an anomaly. It then saves the results to a CSV 
    file and returns the processed DataFrame.

    Args:
        model (object): a machine learning model from the pyod library.
        name (str): The name used to save the output CSV file.

    Returns:
        pandas.DataFrame: A DataFrame containing the test key, anomaly scores, 
                          and binary anomaly predictions (1 for anomaly, 0 for normal).
    
    Notes:
        - The `X` variable must be defined and contain the feature set for model training.
        - The results are saved in the directory `<current_dir>/SJT/csv/` with the provided name.
    """
    df_answers=df
    
    model.fit(X)
    
    df_answers['anomaly_score'] = model.decision_scores_
    df_answers['is_anomaly'] = model.predict(X)

    df_answers = df_answers.reset_index()
    df_answers = df_answers[['TestKey','anomaly_score', 'is_anomaly']]
    
    print(f"Detected anomalies: {df_answers['is_anomaly'].sum()}")

    df_answers.set_index('TestKey', inplace=True)
    df_answers.to_csv(os.path.join(current_dir, 'SJT', 'csv', f'{name}.csv'))
    df_answers.reset_index(inplace=True)
    
    return df_answers

# ECOD
ecod = ECOD(contamination=contamination)
df_ecod = predict_model(ecod, "ecod")

# Isolation forest
i_forest = IForest(contamination=contamination, n_estimators=100, max_samples='auto')
df_iForest = predict_model(i_forest, 'i_forest')

# LOF
lof = LOF(contamination=contamination)
df_lof = predict_model(lof, 'lof')

# COPOD 
copod = COPOD(contamination=contamination)
df_copod = predict_model(copod, 'copod')

# ABOD
abod = ABOD(contamination=contamination, method='fast', n_neighbors=10)
df_abod = predict_model(abod, 'abod')