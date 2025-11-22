"""
This script performs anomaly detection on a dataset using multiple pyod models (ECOD, IForest, LOF, COPOD, ABOD). 

It processes data in chunks, imputes missing values using the median strategy, and applies anomaly detection models. 
Results, including anomaly scores and labels, are saved incrementally to a CSV file.

Configuration:
    - CHUNK_SIZE: Batch size for data processing (default 20,000).
    - contamination: Expected proportion of outliers (default 0.01).
    - MAIN_FOLDER: Project directory.
    - ANOMALIES: Directory for saving results.
    - TEST_TYPE: Test type for anomaly detection.

Functions:
    - data_generator(df, chunk_size): Generates batches of data with imputation.
    - predict_model(df, model, name): Applies anomaly detection and saves results.
"""
import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
import os
import sys
from pyod.models.ecod import ECOD
from pyod.models.iforest import IForest
from pyod.models.lof import LOF
from pyod.models.copod import COPOD
from pyod.models.abod import ABOD

sys.path.append('.')
from func.df_builders.dataframeBuilderFCA import get_df_column_per_combination

# Configuration
CHUNK_SIZE = 20000
contamination = 0.01
MAIN_FOLDER = os.getenv("PROJECT_FOLDER")
ANOMALIES = "anomalies"
TEST_TYPE = "FCA"
dirpath = os.path.join(MAIN_FOLDER, ANOMALIES, TEST_TYPE, "csv")
os.makedirs(dirpath, exist_ok=True)
os.chdir(dirpath)

def data_generator(df, chunk_size=CHUNK_SIZE):
    """
    Generator that yields batches of numerical data from a DataFrame, with missing values imputed.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        chunk_size (int): The size of each batch. Default is `CHUNK_SIZE`.

    Yields:
        tuple: A tuple of:
            - A NumPy array with imputed numerical data.
            - The corresponding rows from the original DataFrame.

    Notes:
        - Imputation is done using the median strategy.
        - Data is converted to `np.float32` for memory efficiency.
    """
    
    for i in range(0, len(df), chunk_size):
        print(f"Processing batch {i // chunk_size + 1}")
        chunk = df.iloc[i:i+chunk_size].copy()  # Make explicit copy
        X = chunk.select_dtypes(include=[np.number]).values
        imputer = SimpleImputer(strategy='median')
        X = imputer.fit_transform(X)
        X = X.astype(np.float32)  # Using float32 for memory efficiency
        yield X, chunk

def predict_model(df, model, name):
    """
    Predicts anomaly scores and labels for data chunks using the specified model. 
    Results are appended to a CSV file, and the total number of anomalies is tracked.

    Parameters:
    - df (pandas.DataFrame): Input data for prediction.
    - model: Anomaly detection model with `fit`, `partial_fit`, `decision_function`, and `predict` methods.
    - name (str): Name for the output CSV file.

    Returns:
    - None: Results are written to a CSV file.
    """
    print(f"Training {name}")
    csv_file = os.path.join(dirpath, f'{name}.csv')
    total_anomalies = 0
    
    # Write header to CSV
    pd.DataFrame(columns=['TestKey', 'anomaly_score', 'is_anomaly']).to_csv(csv_file, index=False)
    
    for i, (X, chunk) in enumerate(data_generator(df)):
        
        try:
            # Make explicit copy of chunk
            chunk = chunk.copy()
            
            # Fit or partial_fit the model
            if i == 0 or not hasattr(model, 'partial_fit'):
                model.fit(X)
            elif hasattr(model, 'partial_fit'):
                model.partial_fit(X)
            
            # Calculate scores and predictions
            chunk['anomaly_score'] = model.decision_function(X)
            
            chunk['is_anomaly'] = model.predict(X)

            # Add TestKey using range instead of index
            if 'TestKey' not in chunk.columns:
                chunk['TestKey'] = chunk.index
            
            # Save results
            results = chunk[['TestKey', 'anomaly_score', 'is_anomaly']]
            results.to_csv(csv_file, mode='a', header=False, index=False)
            
            # Track anomalies
            batch_anomalies = chunk['is_anomaly'].sum()
            total_anomalies += batch_anomalies
            
            # Explicitly clear memory
            del X
            del chunk
            del results
            
        except Exception as e:
            print(f"Error in batch {i+1}:")
            print(f"Error type: {type(e)}")
            print(f"Error message: {str(e)}")
            raise
    
    print(f"Finished {name}. Total anomalies found: {total_anomalies}")

# Define models
models = [
    (ECOD(contamination=contamination), "ecod"),
    (IForest(contamination=contamination, n_estimators=100, max_samples='auto'), "i_forest"),
    (LOF(contamination=contamination), "lof"),
    (COPOD(contamination=contamination), "copod"),
    (ABOD(contamination=contamination, method='fast', n_neighbors=10), "abod")
]

df, _, _, _ = get_df_column_per_combination()

# Train models and make predictions
for model, name in models:
    predict_model(df, model, name)

print("All models are trained and the predictions are saved.")