'''
This module prepares a dataframe to train on.
It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
Each row represents a test instance.

Input:
  - ./decoded_data/PAQ/FactQuestionPAQ.csv
  - ./decoded_data/PAQ/FactTest.csv
  - ./decoded_data/DimCandidate.csv

This module includes the following functions: 
    * get_df_column_per_combination: prepares a dataframe to train on
    * get_distances_indices_sklearn_NearestNeighbors: trains sklearn NearestNeighbors and returns the neighbours
    * neighbors_distances_indices_to_readable_df: pretifies the output from get_distances_indices_sklearn_NearestNeighbors into a dataframe
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
TEST_TYPE = "PAQ"

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
    - ./decoded_data/PAQ/FactQuestionPAQ.csv
    - ./decoded_data/PAQ/FactTest.csv
    - ./decoded_data/DimCandidate.csv

    Parameters:
    - join_candidate (Boolean): wheter to join candidate information in the df_pivot 

    Returns:
    - df_pivot: dataframe with an answer for each possible question, potentially joined with candidate information
    - df_test: general testinformation for each test instance
    - df_answer: all indiviual answers of each test
    - df_candidate: the candidates that filled PAQ
    '''

    df_test = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, TEST_TYPE, "FactTest.csv"))
    df_question = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, TEST_TYPE, f"FactQuestion{TEST_TYPE}.csv"))
    candidateKeys = tuple(df_test["CandidateKey"].to_list())
    df_candidate = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, "DimCandidate.csv"))
    df_candidate = df_candidate[df_candidate["CandidateKey"].isin(candidateKeys)]
    if df_question.columns.__contains__("InstanceID"):
        df_question.drop(columns="InstanceID", inplace=True)
    if df_test.columns.__contains__("Test"):
        df_test.drop(columns="Test", inplace=True)

    # Only for PAQ (only 1 version)
    df_test.drop(columns="VersionNumber", inplace=True)
    df_question = df_question[df_question["RightStatement"] != "ZZZ_0"] # Remove like half of the records
    df_question = df_question[df_question["AnswerVal"] != 0] # Will become zero anyway

    # General methods again

    df_test["FinishDateTime"] = pd.to_datetime(df_test["CreatedDateKey"] * 1e6, format="%Y%m%d%H%M%S")
    days_since_epoch = round(round(time.time()) / (60 * 60 * 24))
    df_test["DaysAgo"] = df_test["FinishDateTime"].apply(lambda date : days_since_epoch - (date.timestamp() / 60 / 60 / 24)).astype(int)
    # df_test.drop(columns="FinishDateTime", inplace=True)

    df_question['LeftRightStatement'] = df_question["LeftStatement"] + df_question["RightStatement"]
    # df_question['RightLeftStatement'] = df_question["RightStatement"] + df_question["LeftStatement"]
    # df_question.rename(columns={"AnswerVal" : "AnswerValLR"}, inplace=True)
    # df_question['AnswerValRL'] = 6 - df_question["AnswerValLR"]

    # Pivoting the DataFrame
    df_pivot = df_question.pivot_table(index='TestKey',
                                    columns=['LeftRightStatement'],
                                    values='AnswerVal',
                                    aggfunc='first')
    # df_pivot.columns = [f'Q{q}_A{a}' for q, a in df_pivot.columns]
    df_pivot.fillna(0, inplace=True)

    df_test.index = df_test["TestKey"]
    cols_test_for_pivot = ["DaysAgo", "CandidateKey"] # Removed VersionNumber for PAQ
    df_pivot.loc[df_test["TestKey"], cols_test_for_pivot] = df_test[cols_test_for_pivot]
    df_test.reset_index(drop=True, inplace=True)


    if join_candidate:
        # This part is randomly altering the index, so re-add Testkey
        df_pivot["TestKey"] = df_pivot.index
        df_pivot = pd.merge(left=df_pivot, right=df_candidate, how='left', on="CandidateKey")
        df_pivot = pd.get_dummies(df_pivot, columns=["InstanceID", "ChosenLanguage", "ChosenGender", "Gender", "Qualification"], dtype=int)
        df_pivot.drop(columns=["Organisation", "ID"], inplace=True)

    if min_max_scale:
        scaler = MinMaxScaler()
        columns_min_max=["DaysAgo"]
        scaler.fit(df_pivot[columns_min_max])
        print(scaler.transform(df_pivot[columns_min_max]))
        col_renamed = [f"{col}_scaled" for col in columns_min_max]
        df_pivot[col_renamed] = scaler.transform(df_pivot[columns_min_max])
        df_pivot.drop(columns=columns_min_max, inplace=True)


    return df_pivot, df_test, df_question, df_candidate

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

