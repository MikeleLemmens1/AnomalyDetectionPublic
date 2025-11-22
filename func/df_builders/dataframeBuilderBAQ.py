'''
This module prepares a dataframe to train on.
It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
Each row represents a test instance.

Provides extra functions, when started from a preprocessed_data.csv

Input:
  - ./decoded_data/BAQ/FactQuestionBAQ.csv
  - ./decoded_data/BAQ/FactTest.csv
  - ./decoded_data/DimCandidate.csv
  - ./anomalies/BAQ/preprocessed_data.csv

This module includes the following functions: 
    * get_df_column_per_combination: prepares a dataframe to train on
    * get_distances_indices_sklearn_NearestNeighbors: trains sklearn NearestNeighbors and returns the neighbours
    * neighbors_distances_indices_to_readable_df: pretifies the output from get_distances_indices_sklearn_NearestNeighbors into a dataframe
    * add_days_ago: adds the column daysAgo in the given dataframe
    * add_version: adds the columns for each version in the given dataframe
    * add_candidate: adds the column candidateKey in the given dataframe 
    * load_df_test: is a helper function loading df test
    * load_df_candidate: s a helper function loading df candidate
'''

import pandas as pd
import numpy as np
import time
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
pd.set_option("display.max_columns", None)
cwd = os.getcwd()

from dotenv import load_dotenv
load_dotenv()

MAIN_FOLDER = os.getenv("PROJECT_FOLDER")
ANOMALIES = "anomalies"
DECODED_DATA = "decoded_data"
TEST_TYPE = "BAQ"
# TODO : potential update when converted to .py
BAQ_FOLDER = os.path.join(MAIN_FOLDER, ANOMALIES, TEST_TYPE)

def get_df_column_per_combination(
        join_candidate = False,
        min_max_scale = False
    ):
    '''
    This function prepares a dataframe to train on.
    It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
    Each row represents a test instance.

    If needed, candidate information can be joined directly.

    Input:
    - ./decoded_data/BAQ/FactQuestionBAQ.csv
    - ./decoded_data/BAQ/FactTest.csv
    - ./decoded_data/DimCandidate.csv

    Parameters:
    - join_candidate (Boolean): wheter to join candidate information in the df_pivot 

    Returns:
    - df_pivot: dataframe with an answer for each possible question, potentially joined with candidate information
    - df_test: general testinformation for each test instance
    - df_answer: all indiviual answers of each test
    - df_candidate: the candidates that filled BAQ
    '''
    df = pd.read_csv(os.path.join(BAQ_FOLDER, "csv", "preprocessed_data.csv"))
    df.index = df["TestKey"]
    df_test = load_df_test()
    df, df_test = add_days_ago(df, df_test=df_test)
    df = add_candidate(df, df_test=df_test)
    df = add_version(df, df_test=df_test, one_hot=True)

    if join_candidate:
        df_candidate = load_df_candidate()
        df = pd.merge(left=df, right=df_candidate, how='left', on="CandidateKey")
        df = pd.get_dummies(df, columns=["InstanceID", "ChosenLanguage", "ChosenGender", "Gender", "Qualification"], dtype=int)
        df.drop(columns=["Organisation", "ID"], inplace=True)

    if min_max_scale:
        scaler = MinMaxScaler()
        columns_min_max=["DaysAgo"]
        scaler.fit(df[columns_min_max])
        df["DaysAgo"] = pd.DataFrame(scaler.transform(df[columns_min_max]), columns=columns_min_max)

    return df, None, None, None

def get_distances_indices_sklearn_NearestNeighbors(df, n_neighbors=3):
    '''
    This function trains sklearn NearestNeighbors and returns the neighbours.

    Parameters:
    - df: df to train on
    - n_neighbours (default 3): amount of neighbours to keep

    Returns:
    - n_neigbours for each datarow in df -> distances, indices
    '''
    nbrs = NearestNeighbors(n_neighbors=n_neighbors).fit(df)
    return nbrs.kneighbors(df)

def neighbors_distances_indices_to_readable_df(df, indices, distances, n_neighbours=3):
    """
    Pretifies the output from get_distances_indices_sklearn_NearestNeighbors into a dataframe

    Parameters:
        - df: original dataframe that is fitted on
        - indices: indices of the neighours for the given distance
        - distances: distances of the neighbours for the given indice
    Returns:
        - df_close_neighbous: dataframe containing close neighbours and the relative distance for each test instance
    """
    df_close_neighbors = pd.DataFrame(columns=["TestKey", "neighbourKey", "distance", "minKey"])
    for i in np.arange(n_neighbours):
        testkeys = indices[:, i].tolist()
        distance = distances[:, i].tolist()
        neighbours = df.iloc[testkeys].index.tolist()
        testkeys = df.iloc[np.arange(len(testkeys))].index.tolist()
        # print(testkeys)
        # print(distance)
        # print(neighbours)
        minima = np.minimum(testkeys, neighbours)
        df_neighbours_i = pd.DataFrame(data={
            "TestKey" : testkeys,
            "neighbourKey" : neighbours,
            "distance" : distance,
            "minKey" : minima
        })
        df_close_neighbors = pd.concat([df_close_neighbors,df_neighbours_i], ignore_index=True)
    # Drop self references
    return df_close_neighbors[df_close_neighbors["TestKey"] != df_close_neighbors["neighbourKey"]]

def add_days_ago(df : pd.DataFrame, df_test=None):
    """
    This function adds the column daysAgo in the given dataframe. 
    When df_test is provided, it will not fetch the dataframe itself

    Parameters:
        - df: preprocessed dataframe
        - df_test: test info, needed for info when the test finished, if not provided, fetches from FactTest.csv
    
    Returns:
        - given df with an extra column DaysAgo
    """
    if df_test is None:
        df_test = load_df_test()
    df_test["FinishDateTime"] = pd.to_datetime(df_test["CreatedDateKey"] * 1e6, format="%Y%m%d%H%M%S")
    df = df.join(df_test["FinishDateTime"])
    days_since_epoch = round(round(time.time()) / (60 * 60 * 24))
    df["DaysAgo"] = df["FinishDateTime"].apply(lambda date : 0 if pd.isnull(date) else days_since_epoch - (date.timestamp() / 60 / 60 / 24)).astype(int)
    df.drop(columns="FinishDateTime", inplace=True)
    return df, df_test

def add_version(df : pd.DataFrame, df_test : pd.DataFrame = None, one_hot=False):
    """
    This function adds the columns for each version in the given dataframe. 
    When df_test is provided, it will not fetch the dataframe itself

    Parameters:
        - df: preprocessed dataframe
        - df_test: test info, needed for info about the testversion, if not provided, fetches from FactTest.csv
        - one_hot: whether version is a string or one_hot_encoding.
    
    Returns:
        - given df with an extra column(s) VersionNumber(s)
    """
    if df_test is None:
        df_test = load_df_test()
    
    df = df.join(df_test["VersionNumber"])
    if one_hot:
        return pd.get_dummies(df, columns=["VersionNumber"], dtype=int)
    return df

def add_candidate(df : pd.DataFrame, df_test : pd.DataFrame = None):
    """
    This function adds the column candidateKey in the given dataframe.
    When df_test is provided, it will not fetch the dataframe itself

    Parameters:
        - df: preprocessed dataframe
        - df_test: test info, needed for info about the candidate, if not provided, fetches from FactTest.csv
    
    Returns:
        - given df with an extra column CandidateKey
    """
    if df_test is None:
        df_test = load_df_test()
    return df.join(df_test["CandidateKey"].astype(int))

def load_df_test():
    """
    Helper function loading df test
    
    Returns:
        - df_test: test info
    """
    df_test = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, "BA51", "FactTest.csv"))
    df_test.index = df_test["TestKey"]
    return df_test

def load_df_candidate():
    """
    Helper function loading df candidate
    Filters only the candidates of BAQ
    
    Returns:
        - df_candidate: candidate info
    """
    df_test = load_df_test()
    candidateKeys = tuple(df_test["CandidateKey"].to_list())
    df_candidate = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, "DimCandidate.csv"))
    df_candidate = df_candidate[df_candidate["CandidateKey"].isin(candidateKeys)]
    return df_candidate