#!/usr/bin/env python
# coding: utf-8

# In[ ]:


'''
This module uses multiple pyod models as an unsupervised machine learning algorithms. 
Using a majority vote of the 3 most different paramameterized models of the same type, e.g. 6 definitions of IForest, keep the 3 most different.
The models use a preprocessed dataframe, with all answers, provided by the specific dataframeBuilder for the test
Additionaly, the models are also fitted on a reduced dimension, using Principal Component Analysis.
Each row represents a test instance.

Input:
  - ./decoded_data/{TESTNAME}/FactQuestion{TESTNAME}.csv
  - ./decoded_data/{TESTNAME}/FactTest.csv
  - ./decoded_data/DimCandidate.csv

Output:
  - ./anomalies/{TESTNAME}/csv/pyod_ensemble.csv
'''


# # Notebook exploring outliers using pyod

# In[ ]:


import platform
import os
import sys
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

CONTAM = 0.05

if "all" in os.getcwd():
    sys.path.append("../..")
    TESTNAME = "SJT"
else:
    sys.path.append(".")
    if len(sys.argv) < 2:
        raise ValueError("Pyod ensemble needs test to run, implemented tests: BAQ, FCA, PAQ, SJT")
    TESTNAME = sys.argv[1].upper()

match TESTNAME:
    case "FCA":
        from func.df_builders.dataframeBuilderFCA import get_df_column_per_combination
    case "SJT":
        from func.df_builders.dataframeBuilderSJT import get_df_column_per_combination
    case "BAQ":
        from func.df_builders.dataframeBuilderBAQ import get_df_column_per_combination
    case "PAQ":
        from func.df_builders.dataframeBuilderPAQ import get_df_column_per_combination

pd.set_option("display.max_rows", 10)


# In[2]:


from pyod.models.copod import COPOD
from pyod.models.abod import ABOD
from pyod.models.lof import LOF
from pyod.models.iforest import IForest
# from pyod.models.ae1svm import AE1SVM
from pyod.models.knn import KNN
from pyod.models.iforest import IForest
from pyod.models.dif import DIF
from pyod.models.lunar import LUNAR

from pyod.models.pca import PCA as pyodPCA
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler


# In[3]:


LOTS_OF_TRAINING_TIME = False # Run all
RUN_OPTIONAL = False # Just skip a few


# In[ ]:


def get_normal_dataframe():
    '''
    This function uses the dataframeBuilder of {TESTNAME}, 
    sets the TestKey as index and shuffles the dataset.
    Checks whether CandidateKey is in the dataframe and drops it.
    
    Parameters: None

    Returns:
    a dataframe with the following columns:
        - An answer for each possible question asked
        - Candidate information
        - Amount of days ago
    '''
    df, _, _, _ = get_df_column_per_combination(join_candidate=True)
    df.index = df["TestKey"]
    df.drop(columns="TestKey", inplace=True)
    df = df.sample(frac=1.)

    if "CandidateKey" in df.columns:
        df.drop(columns="CandidateKey", inplace=True)
    return df


# In[5]:


df = get_normal_dataframe()
df


# In[ ]:


def data_generator(X, batch_size=1000):
    '''
    This function splits X in batches of size {batch_size}, default 1000, 
    yields a result to be used as an iterator.

    Returns:
        batch_size samples of the dataframe
    '''
    for i in range(0, len(X), batch_size):
        yield X[i:i + batch_size]

# Functie om een model te trainen in batches
def process_batches(model, X, batch_size=1000):
    '''
    Process the fit proces in batches of size {batch_size}, default 1000, 

    Returns:
        Anomaly scores of each test instance in the dataset
    '''
    anomaly_scores = []
    
    # Train op batches
    for batch in data_generator(X, batch_size):
        model.fit(batch)  # Train op de huidige batch
        batch_scores = model.decision_function(batch)  # Verkrijg anomalie scores voor de batch
        anomaly_scores.extend(batch_scores)  # Voeg scores toe aan de lijst
    
    return np.array(anomaly_scores)

def predict_model(model, name, prefix, X_train, contamination, df_is_anomaly):
    '''
    Predicts a certain percentage ({contamination}) of anomalies in the given dataset ({X_train})
    Uses the given model to predict.
    Adds the result in the received dataframe ({df_is_anomaly})

    When the model uses (batched) epochs, .fit and .predict will be called
    otherwise predict_batches

    Parameters:
        model: Pyod model to fit on
        name: used as partial columnname to add is_anomaly results in df_is_anomaly (e.g. lof_default, lof_neigbours10)
        prefix: type of dataframe it is fitted on. e.g. noraml/pca/feature-engineered
        X_train: dataset to fit & predict
        contamination: float in range [0.0, 1.0], percentual amount of outliers the model needs to see as anomaly.
        df_is_anomaly: dataframe containing all predicted results. 

    Returns:
        "Done" : str
    '''
    print(f"Training {name}!")
    
    if "deepforest" in name or "lunar" in name:
        model.fit(X_train)
        anomaly_scores = model.predict(X_train)
    else:
        anomaly_scores = process_batches(model, X_train)

    # Determine anomalies based on scores (e.g., top 5% as anomaly)
    threshold = np.percentile(anomaly_scores, 100 - 100*contamination)  # Drempelwaarde instellen
    is_anomaly = anomaly_scores > threshold
    
    full_name = f"{prefix}_{name}"
    df_is_anomaly[full_name] = is_anomaly.astype(int)


# In[ ]:


df_is_anomaly = pd.DataFrame(index=df.index)


# In[ ]:


def get_X_train_normal(df):
    '''
    Uses min_max_scales the given dataframe

    Parameters:
        df: X dataframe to make predictions on

    Returns:
        scaled dataframe X_train
    '''
    scaler = MinMaxScaler()
    scaler.fit(df)
    return scaler.transform(df)

def get_X_train_pca(df, n_components=10):
    '''
    Uses Principal Component Analysis on get_X_train_normal

    Parameters:
        df: X dataframe to make predictions on
        n_components (default 10): Amount of dimensions to reduce to when adapting PCA
 
    Returns:
        scaled & pca reduced dimensionality of the dataframe X_train
    '''
    X_train_scaled_normal = get_X_train_normal(df)
    pca = PCA(n_components=n_components)
    return pca.fit_transform(X_train_scaled_normal)


# In[9]:


get_X_train_normal(df).shape, get_X_train_pca(df).shape


# In[10]:


# This defines all types of dataframes for the pyod ensemble 
# TODO : add pca 95% variance
# PCA(n_components=n_components_95)
# X_pca_95 = pca_95.fit_transform(X_scaled)
dataframes = {
    "normal" : lambda: get_X_train_normal(df),
    "pca-10c" : lambda: get_X_train_pca(df),
}


# In[ ]:


# Define models for pyod ensemble
# Some are not worth it to train for FCA
is_fca = True if TESTNAME == "FCA" else False
drop_for_fca = [
    "IForest_2048est_.3sample_.8features",
    "IForest_128est",
    "abod_n_neighors_30",
    "lunar_default",
    "lof_manhattan",
    "lof_32neighbours_leaf64",
]
models = {
    "lof_default" : lambda: LOF(contamination=CONTAM, n_jobs=-1),
    "lof_5neighbours_brute" : lambda: LOF(n_neighbors=5, algorithm='brute', leaf_size=50, metric='minkowski', p=1, metric_params=None, contamination=CONTAM, n_jobs=-1),
    "lof_cosine" : lambda: LOF(n_neighbors=8 if is_fca else 16, algorithm='brute', leaf_size=16, metric='cosine', p=1, metric_params=None, contamination=CONTAM, n_jobs=-1),
    "lof_32neighbours_leaf64" : lambda: LOF(n_neighbors=32, contamination=CONTAM, leaf_size=32 if is_fca else 64, n_jobs=-1),
    "lof_manhattan" : lambda: LOF(metric='manhattan', contamination=CONTAM, n_jobs=-1),

    "IForest_default" : lambda: IForest(contamination=CONTAM, n_jobs=-1),
    "IForest_128est" : lambda: IForest(contamination=CONTAM, n_jobs=-1, n_estimators=128),
    "IForest_256est_bootstrap" : lambda: IForest(contamination=CONTAM, n_jobs=-1, n_estimators=256, bootstrap=True),
    "IForest_256est_.7features" : lambda: IForest(contamination=CONTAM, n_jobs=-1, n_estimators=256, max_features=0.7),
    "IForest_512est_.77samp" : lambda: IForest(contamination=CONTAM, n_estimators=555, max_samples=0.77, max_features=0.55, bootstrap=True, n_jobs=-1),
    "IForest_1024est_.44sample" : lambda: IForest(contamination=CONTAM, n_jobs=-1, n_estimators=1024, max_samples=0.44),
    "IForest_2048est_.3sample_.8features" : lambda: IForest(contamination=CONTAM, n_jobs=-1, n_estimators=2024, max_samples=0.3, max_features=0.8),

    "knn_default" : lambda: KNN(contamination=CONTAM, n_jobs=-1),
    "knn_mean" : lambda: KNN(contamination=CONTAM, method="mean", n_jobs=-1),
    "knn_16neighbours" : lambda: KNN(contamination=CONTAM, n_neighbors=8 if is_fca else 16, method="mean", n_jobs=-1),

    "deepforest_default" : lambda: DIF(contamination=CONTAM),
    "deepforest_params" :lambda: DIF(batch_size=1024, hidden_neurons=[64,64,32], hidden_activation='relu', skip_connection=True, n_ensemble=32, n_estimators=8, max_samples=128, contamination=0.1, random_state=None, device=None),
    
    "lunar_default" : lambda: LUNAR(contamination=CONTAM),
    "lunar_params": lambda: LUNAR(n_neighbours=4, val_size=0.1, proportion=0.8, n_epochs=150, lr=0.0011, contamination=CONTAM),

    "abod_default" : lambda: ABOD(contamination=CONTAM),
    "abod_n_neighors_10" : lambda: ABOD(contamination=CONTAM, n_neighbors=10),
    "abod_n_neighors_30" : lambda: ABOD(contamination=CONTAM, n_neighbors=30),

    "pca_1" : lambda: pyodPCA(n_components=0.95, svd_solver="full", contamination=CONTAM),
    "pca_max_components" : lambda: pyodPCA(n_components=min(len(df.columns), 128), svd_solver="full", contamination=CONTAM),
}
if TESTNAME == "FCA":
    for m in drop_for_fca:
        if m in models.keys():
            del models[m]
models


# In[ ]:


# Iterate one type of dataframe at a time, to preserve memory usage
# Then fit all the defined models above
for prefix, df_function in dataframes.items():
    X_train = df_function()
    print(f"Fitting {prefix} dataframe with shape: {X_train.shape}")
    # Iterate all models
    for modelname, modelfunction in models.items():
        model = modelfunction()
        start = time.time()
        try:
            predict_model(
                modelfunction(),
                name=f"{modelname}",
                prefix=prefix,
                X_train=X_train, 
                contamination=CONTAM, 
                df_is_anomaly=df_is_anomaly,
            )
        except Exception as e:
            print(f"An error occurred while executing the prediction of {modelname}: {str(e)}")
        end = time.time()
        seconds = end-start
        print(f"{modelname} took {seconds:.0f}s")
    print("="*70)

# In[13]:


df_is_anomaly


# In[ ]:


def compare_models_individual(df, threshold=97):
    '''
    Calculate the similarity between each model result in df.columns.
    Prints similar model results > {threshold}

    Parameters:
        df: dataframe with anomaly results
        threshold: default 97, when to print if a model predicts an equal result
    '''
    columns = df.columns.to_list()
    columns_copy = columns.copy()
    for col in columns:
        columns_copy.remove(col)
        for other in columns_copy:
            similarity = (df[col] == df[other]).sum() / len(df) * 100
            # if similarity >= threshold:
            #     print(f"{similarity:.2f}% = similarity between {col} & {other} ")

# compare_models_individual(df_is_anomaly)


# In[ ]:

def compare_models_total(df):
    '''
    Calculate the similarity between each model result in df.columns.
        ! Watch out ! df.columns * df.columns results!
        Also compares with itself --> 100% similarity.
        Similarity between 0-100%

    Parameters:
        df: dataframe with anomaly results

    Returns:
        A dataframe with each comparison, with columns:
            - df: df type1 (e.g. normal/pca/feature-engineered)
            - other_df: df_type2 (compared to)
            - model: pyod model (e.g. LOF, IForest, ABOD...)
            - other_model: pyod model which is compared to
            - variant: parameter description
            - other variant: parameter description of the other model
    '''
    columns = df.columns.to_list()
    columns_copy = columns.copy()
    individual_simularities = {
        "df" : [],
        "model" : [],
        "variant": [],
        "other_var" : [],
        "other_model" : [],
        "other_df" : [],
        "similarity": [],
    }
    total_similarity = {col:0 for col in columns_copy}
    for col in columns:
        for other in columns_copy:
            # if other != col:
            # Yes compare with itself, but because everyone is compared with itself, 
            # later functions add +100 for every, still keeping the lowest similirity between the same models
            similarity = (df[col] == df[other]).sum() / len(df) * 100
            total_similarity[col] += similarity
            splitted_col = col.split("_")
            splitted_other = other.split("_")
            individual_simularities["df"].append(splitted_col[0])
            individual_simularities["model"].append(splitted_col[1])
            individual_simularities["variant"].append("_".join(splitted_col[2:]))
            individual_simularities["other_df"].append(splitted_other[0])
            individual_simularities["other_model"].append(splitted_other[1])
            individual_simularities["other_var"].append("_".join(splitted_other[2:]))
            individual_simularities["similarity"].append(similarity)

    return pd.DataFrame(individual_simularities)

df_compared = compare_models_total(df_is_anomaly)
df_compared


# In[ ]:

# Compare models of the same type, e.g. IForest, LOF to keep those 3 who are less similar with each other.
# Splitted in two notebook cells to show an inbetween result
tmp = df_compared[(df_compared["model"] == df_compared["other_model"]) & (df_compared["df"] == df_compared["other_df"])]
tmp = tmp.groupby(["df", "model", "variant"]).sum("similarity").sort_values("similarity", ascending=False).reset_index()
tmp


# In[ ]:


tmp = tmp.groupby(["df", "model"]).tail(3)

filtered_columns = (tmp["df"] + "_" + tmp["model"] + "_" + tmp["variant"])
filtered_columns


# In[ ]:


# Filter anomaly datframe to keep only the wanted models
df_is_anomaly = df_is_anomaly[filtered_columns].copy()
df_is_anomaly


# In[ ]:


# Print/show the amount of kept variations for each model
# Divide by the amount of dataframes, to as otherwise its counted N times for each dataframe type
tmp.groupby(["model"]).count() / len(dataframes)


# In[ ]:


# Calculate the percentage of models that predicted a given test as anomaly
# Use count as inbetween result
columns = df_is_anomaly.columns.to_list()
df_is_anomaly.loc[:, 'count'] =  df_is_anomaly[columns].sum(axis=1)
df_is_anomaly.loc[:, 'percentage'] = df_is_anomaly['count'] / len(columns)
df_is_anomaly


# In[21]:


df_is_anomaly['count'].value_counts()


# In[ ]:

# Based on THRESHOLD, decide which test is considered an anomaly
TRESHOLD = 0.5
df_is_anomaly["is_anomaly"] = np.where(df_is_anomaly['percentage'] >= TRESHOLD, 1, 0)
df_is_anomaly


# In[23]:


df_is_anomaly["is_anomaly"].sum()


# In[ ]:


# Write result as csv
anomalies_path = os.path.abspath("anomalies")
csv_path = os.path.join(anomalies_path, TESTNAME, "csv", "pyod_ensemble.csv")
df_is_anomaly.to_csv(csv_path, index=True)

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




