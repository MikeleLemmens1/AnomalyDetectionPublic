"""
This script explores outlier detection using the pyod library. Various algorithms
like LOF, COPOD, IForest, and PCA are used to detect anomalies in a dataset.
Metrics EM and MV are calculated to evaluate the effectiveness of the models.

functions:
    - `func.df_builders.dataframeBuilderFCA`: this function is used for getting preprocessed data.
"""

import platform
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys

sys.path.append("..")

pd.set_option("display.max_columns", None)

from func.df_builders.dataframeBuilderFCA import get_df_neigbours_answer_for_all_itemIDs
from emmv import emmv_scores

from sklearn.preprocessing import MinMaxScaler

LOTS_OF_TRAINING_TIME = False # Run all
RUN_OPTIONAL = False # Just skip a few

from pyod.models.copod import COPOD
from pyod.models.abod import ABOD
from pyod.models.lof import LOF
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.iforest import IForest
from pyod.models.dif import DIF
from pyod.models.lunar import LUNAR

df, _, _, _ = get_df_neigbours_answer_for_all_itemIDs(join_candidate=True)
df.index = df["TestKey"].astype(int)
df.drop(columns=["TestKey", "CandidateKey"], inplace=True)

df = df.sample(frac=1.)
LEN_TRAIN = np.round(0.99 * len(df), 0).astype(int)
LEN_TEST = len(df) - LEN_TRAIN

scaler = MinMaxScaler()

scaler.fit(df[:LEN_TRAIN])

X_train = scaler.transform(df[:LEN_TRAIN])
X_train, len(X_train)

X_test = scaler.transform(df[LEN_TRAIN:])
X_test, len(X_test)

def data_generator(X, batch_size=1000):
    for i in range(0, len(X), batch_size):
        yield X[i:i + batch_size]

def process_batches(model, X, batch_size=1000):
    anomaly_scores = []

    for batch in data_generator(X, batch_size):
        model.fit(batch)
        batch_scores = model.decision_function(batch)
        anomaly_scores.extend(batch_scores)

    return np.array(anomaly_scores), model

outliers = {}
results = {
    "model" : [],
    "em" : [],
    "mv" : []
}
df_is_anomaly = pd.DataFrame(index=df[:LEN_TRAIN].index)
df_anomaly_scores = pd.DataFrame(index=df[:LEN_TRAIN].index)
df_results = pd.DataFrame(columns=["model", "EM", "MV"])

def predict_model(model, name, X_train, X_test, contamination, df_is_anomaly, results):
    print(f"Training {name}!")

    anomaly_scores, model = process_batches(model, X_train)

    threshold = np.percentile(anomaly_scores, 100 - 100*contamination)
    is_anomaly = anomaly_scores > threshold

    df_anomaly_scores[name] = anomaly_scores
    df_is_anomaly[name] = is_anomaly.astype(int)

    print(f"Amount of detected anomalies: {df_is_anomaly[name].sum()}")

    emmv_waarden = emmv_scores(model, X_test)
    results["model"].append(name)
    results["em"].append(emmv_waarden["em"])
    results["mv"].append(emmv_waarden["mv"])
    print(f"emmv values", emmv_waarden)

    return df_is_anomaly[name]

model = LOF(contamination=0.05)
is_anomaly = predict_model(model=model, name='lof_05', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = LOF(contamination=0.10)
is_anomaly = predict_model(model=model, name='lof_10', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = LOF(contamination=0.01, leaf_size=60, n_neighbors=30)
is_anomaly = predict_model(model=model, name='lof_01_leaf_60_neighbours_30', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

if LOTS_OF_TRAINING_TIME:
    model = LOF(metric='manhattan', contamination=0.05)
    is_anomaly = predict_model(model=model, name='lof_manhattan', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

if LOTS_OF_TRAINING_TIME:
    model = LOF(metric='dice', contamination=0.05)
    model.fit(df)
    outliers["lof_dice"] = model.predict(df)

if RUN_OPTIONAL or LOTS_OF_TRAINING_TIME:
    model = LOF(metric='hamming', contamination=0.05)
    model.fit(df)
    outliers["lof_hamming"] = model.predict(df)

from pyod.models.pca import PCA as pyodPCA

model = pyodPCA(n_components=0.95, svd_solver="full", contamination=0.05)
is_anomaly = predict_model(model=model, name='pca', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = COPOD(contamination=0.05, n_jobs=2)
is_anomaly = predict_model(model=model, name='copod', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = LUNAR(contamination=0.05)
is_anomaly = predict_model(model=model, name='lunar', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

if LOTS_OF_TRAINING_TIME:
    model = KNN(contamination=0.05)
    is_anomaly = predict_model(model=model, name='knn', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = IForest(contamination=0.05)
is_anomaly = predict_model(model=model, name='iforest', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

model = DIF(contamination=0.05)
is_anomaly = predict_model(model=model, name='deep_iforest', X_train=X_train, X_test=X_test, contamination=0.05, df_is_anomaly=df_is_anomaly, results=results)

df_outliers = df_is_anomaly
columns = df_outliers.columns
df_outliers['count'] =  df_outliers.sum(axis=1)
df_outliers['pyod % outlier'] = df_outliers['count'] / len(columns)
df_outliers

df_outliers['count'].value_counts()

TRESHOLD = 0.7
df_outliers["anomaly"] = np.where(df_outliers['pyod % outlier'] >= TRESHOLD, 1, 0)
df_outliers

pd.DataFrame(results)

df_outliers.to_csv("../csv/pyod.csv", index=False)