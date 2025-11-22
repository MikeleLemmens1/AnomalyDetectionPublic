'''
This module prepares a dataframe to train on.
It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
Each row represents a test instance.

Input:
  - ./decoded_data/SJT/FactQuestionSJT.csv
  - ./decoded_data/SJT/FactTest.csv
  - ./decoded_data/DimCandidate.csv

This module includes the following functions: 
    * get_df_column_per_combination: prepares a dataframe to train on
    * get_distances_indices_sklearn_NearestNeighbors: trains sklearn NearestNeighbors and returns the neighbours
'''

import numpy as np
import pandas as pd
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
TEST_TYPE = "SJT"

def get_df_column_per_combination(join_candidate=False, min_max_scale=False):
    '''
    This function prepares a dataframe to train on.
    It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
    Each row represents a test instance.

    If needed, candidate information can be joined directly.

    Input:
    - ./decoded_data/SJT/FactQuestionSJT.csv
    - ./decoded_data/SJT/FactTest.csv
    - ./decoded_data/DimCandidate.csv

    Parameters:
    - join_candidate (Boolean): wheter to join candidate information in the df_pivot 

    Returns:
    - df_pivot: dataframe with an answer for each possible question, potentially joined with candidate information
    - df_test: general testinformation for each test instance
    - df_answer: all indiviual answers of each test
    - df_candidate: the candidates that filled SJT
    '''
    MAIN_FOLDER = os.getenv("PROJECT_FOLDER")
    df_test = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, TEST_TYPE, "FactTest.csv"))
    df_question = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, TEST_TYPE, f"FactQuestion{TEST_TYPE}.csv"))
    candidateKeys = tuple(df_test["CandidateKey"].to_list())
    df_candidate = pd.read_csv(os.path.join(MAIN_FOLDER, DECODED_DATA, "DimCandidate.csv"))
    df_candidate = df_candidate[df_candidate["CandidateKey"].isin(candidateKeys)]
    if df_question.columns.__contains__("InstanceID"):
        df_question.drop(columns="InstanceID", inplace=True)
    if df_test.columns.__contains__("Test"):
        df_test.drop(columns="Test", inplace=True)


    df_test["FinishDateTime"] = pd.to_datetime(df_test["CreatedDateKey"] * 1e6, format="%Y%m%d%H%M%S")

    answer_col_name = "AnswerSequence"
    df_melted = df_question.melt(id_vars=['TestKey', 'ItemID'],
                        value_vars=[f"{answer_col_name}1",
                                    f"{answer_col_name}2",
                                    f"{answer_col_name}3"],
                        var_name='answer_type',
                        value_name='Answer')
    df_melted['QuestionNr'] = df_melted['answer_type'].str.slice(len(answer_col_name)).astype('Int8')
    df_melted.drop(columns=["answer_type"], inplace=True) # Drop col with values AnswerX as string

    # Pivoting the DataFrame
    df_pivot = df_melted.pivot_table(index='TestKey',
                                    columns=['ItemID', 'QuestionNr'],
                                    values='Answer',
                                    aggfunc='first')
    df_pivot.columns = [f'Q{q}_A{a}' for q, a in df_pivot.columns]

    df_pivot = df_pivot.fillna(0)
    days_since_epoch = round(round(time.time()) / (60 * 60 * 24))
    df_test["DaysAgo"] = df_test["FinishDateTime"].apply(lambda date : days_since_epoch - (date.timestamp() / 60 / 60 / 24)).astype(int)
    # df_test.drop(columns="FinishDateTime", inplace=True)

    df_test.index = df_test["TestKey"]
    cols_test_for_pivot = ["DaysAgo", "VersionNumber", "CandidateKey"]
    df_pivot.loc[df_test["TestKey"], cols_test_for_pivot] = df_test[cols_test_for_pivot]
    df_test.reset_index(drop=True, inplace=True)

    df_pivot = pd.get_dummies(df_pivot, columns=["VersionNumber"], dtype=int)

    if join_candidate:
        # This part is randomly altering the index
        df_pivot["TestKey"] = df_pivot.index
        df_pivot = pd.merge(left=df_pivot, right=df_candidate, how='left', on="CandidateKey")
        df_pivot = pd.get_dummies(df_pivot, columns=["InstanceID", "ChosenLanguage", "ChosenGender", "Gender", "Qualification"], dtype=int)
        df_pivot.drop(columns=["Organisation", "ID"], inplace=True)

    if min_max_scale:
        scaler = MinMaxScaler()
        columns_min_max=["DaysAgo"]
        scaler.fit(df_pivot[columns_min_max])
        df_pivot["DaysAgo"] = pd.DataFrame(scaler.transform(df_pivot[columns_min_max]), columns=columns_min_max)
    return df_pivot, df_test, df_question, df_candidate

# Could have been in neighbours.py itself.
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
