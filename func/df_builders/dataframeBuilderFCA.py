'''
This module prepares a dataframe to train on.
It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
Each row represents a test instance.

Input:
  - ./decoded_data/FCA/FactQuestionFCA.csv
  - ./decoded_data/FCA/FactTest.csv
  - ./decoded_data/DimCandidate.csv

This module includes the following functions: 
    * get_df_column_per_combination: prepares a dataframe to train on
    * get_distances_indices_sklearn_NearestNeighbors: trains sklearn NearestNeighbors and returns the neighbours
    * neighbors_distances_indices_to_readable_df: pretifies the output from get_distances_indices_sklearn_NearestNeighbors into a dataframe
'''

import numpy as np
import pandas as pd
import time
from sklearn.neighbors import NearestNeighbors
import os

from dotenv import load_dotenv

load_dotenv()


MAIN_FOLDER = os.getenv("PROJECT_FOLDER")
SUB1 = "decoded_data"
SUB2 = "FCA"

def get_df_column_per_combination(join_candidate=False):
    '''
    This function prepares a dataframe to train on.
    It uses the FactTest and FactQuestion csv's, melts and pivots it to an answer for each possible, historic question.
    Each row represents a test instance.

    If needed, candidate information can be joined directly.

    Input:
    - ./decoded_data/FCA/FactQuestionFCA.csv
    - ./decoded_data/FCA/FactTest.csv
    - ./decoded_data/DimCandidate.csv

    Parameters:
    - join_candidate (Boolean): wheter to join candidate information in the df_pivot 

    Returns:
    - df_pivot: dataframe with an answer for each possible question, potentially joined with candidate information
    - df_test: general testinformation for each test instance
    - df_answer: all indiviual answers of each test
    - df_candidate: the candidates that filled FCA
    '''

    MAIN_FOLDER = os.getenv("PROJECT_FOLDER")
    df_test = pd.read_csv(os.path.join(MAIN_FOLDER, SUB1, SUB2, "FactTest.csv"))
    df_question = pd.read_csv(os.path.join(MAIN_FOLDER, SUB1, SUB2, "FactQuestionFCA.csv"))
    candidateKeys = tuple(df_test["CandidateKey"].to_list())
    df_candidate = pd.read_csv(os.path.join(MAIN_FOLDER, SUB1, "DimCandidate.csv"))
    df_candidate = df_candidate[df_candidate["CandidateKey"].isin(candidateKeys)]


    df_test["FinishDateTime"] = pd.to_datetime(df_test["CreatedDateKey"] * 1e6 + df_test["TestFinishTimeKey"], format="%Y%m%d%H%M%S")
    # df_test["year"] = df_test["FinishDateTime"].dt.year
    # # df_test["month"] = df_test["CreatedDateKey"].dt.month
    # # df_test["day"] = df_test["CreatedDateKey"].dt.month

    # For each answer in seq[1,2,3], make 1 line per answer
    # df_test = 160k records
    # df_question = 3 miljoen questions
    # df_melted = 9 miljoen total answers
    df_melted = df_question.melt(id_vars=['TestKey', 'ItemId'],
                     value_vars=['Answer1',
                                 'Answer2',
                                 'Answer3'],
                     var_name='answer_type',
                     value_name='Answer')
    df_melted['QuestionNr'] = df_melted['answer_type'].str.slice(len('Answer')).astype('Int8')
    df_melted.drop(columns=["answer_type"], inplace=True) # Drop col with values AnswerX as string

    # Pivoting the DataFrame
    df_pivot = df_melted.pivot_table(index='TestKey',
                                  columns=['ItemId', 'QuestionNr'],
                                  values='Answer',
                                  aggfunc='first')
    df_pivot.columns = [f'Q{q}_A{a}' for q, a in df_pivot.columns]


    # Hours and Days ago
    days_since_epoch = round(round(time.time()) / (60 * 60 * 24))
    hours_since_epoch = round(round(time.time()) / (60 * 60))
    df_test["DaysAgo"] = df_test["FinishDateTime"].apply(lambda date : days_since_epoch - (date.timestamp() / 60 / 60 / 24)).astype(int)
    df_test["HoursAgo"] = df_test["FinishDateTime"].apply(lambda dt : hours_since_epoch - (dt.timestamp() / 60 / 60)).astype(int)

    df_test.index = df_test["TestKey"]
    cols_test_for_pivot = ["DaysAgo", "HoursAgo", "VersionNumber", "CandidateKey"]
    df_pivot.loc[df_test["TestKey"], cols_test_for_pivot] = df_test[cols_test_for_pivot]
    df_test.reset_index(drop=True, inplace=True)

    

    df_test.index = df_test.TestKey
    # df_pivot = df_pivot.join(df_test[["TestKey", "VersionNumber"]], on="TestKey", how="left")
    df_test.reset_index(drop=True, inplace=True)
    df_pivot = pd.get_dummies(df_pivot, columns=["VersionNumber"], dtype=int)
    
    if join_candidate:
        # This part is randomly altering the index, so re-add Testkey
        df_pivot["TestKey"] = df_pivot.index
        df_pivot = pd.merge(left=df_pivot, right=df_candidate, how='left', on="CandidateKey")
        df_pivot = pd.get_dummies(df_pivot, columns=["InstanceID", "ChosenLanguage", "ChosenGender", "Gender", "Qualification"], dtype=int)
        df_pivot.drop(columns=["Organisation", "ID"], inplace=True)
        
    df_pivot.fillna(0.0, inplace=True)

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

# Could have been in neighbours.py itself.
def neighbors_distances_indices_to_readable_df(df, indices, distances):
    """
    Pretifies the output from get_distances_indices_sklearn_NearestNeighbors into a dataframe

    Parameters:
        - df: original dataframe that is fitted on
        - indices: indices of the neighours for the given distance
        - distances: distances of the neighbours for the given indice
    """
    results = [np.column_stack((df.index, df.iloc[indices[:, i]].index, distances[:, i])) for i in range(1, indices.shape[1])]
    df_close_neighbours = pd.DataFrame(np.concatenate(results), columns=["TestKey", "neighbourKey", "distance"])
    df_close_neighbours["TestKey"] = df_close_neighbours.TestKey.astype(int)
    df_close_neighbours["neighbourKey"] = df_close_neighbours.neighbourKey.astype(int)
    df_close_neighbours = df_close_neighbours[df_close_neighbours.TestKey != df_close_neighbours.neighbourKey]
    df_close_neighbours["minFCAKey"] = df_close_neighbours[["TestKey","neighbourKey"]].min(axis='columns')
    return df_close_neighbours
