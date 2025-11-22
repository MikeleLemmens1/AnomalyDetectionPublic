"""
This module can be used to connect to the DWH to retrieve the data needed for the dashboard. The data get cashed in streamlit to optimize performance. 

This module includes the following functions: 
    * get_general_test_data: retrieves the general data from the DWH
    * get_all_question_data_with_anomaly: retrieves data regarding the questions and their anomalies from the DWH for each test
    * get_question_with_anomaly: retrieves data regarding the questions and their anomalies from the DWH for one testtype
"""

import pyodbc
import pandas as pd
import streamlit as st

import os
from dotenv import load_dotenv

pd.set_option("display.max_columns", None)

load_dotenv()

HOST = os.getenv("HOST")
PORT = os.getenv("MSSQL_LOCAL_PORT")
DATABASE = os.getenv("DATABASE")
DB_DWH = os.getenv("DB_DWH")
DRIVER = os.getenv("DRIVER")
USERNAME = os.getenv("MSSQL_USERNAME")
PASSWORD = os.getenv("MSSQL_SA_PASSWORD")

USE_WINDOWS_AUTH = "true" == os.getenv("MSSQL_USE_WIN_AUTH").lower()

CONNECTION_STRING_DWH = ""
if USE_WINDOWS_AUTH:
    # print("USING WINDOWS")
    CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={HOST};DATABASE={DATABASE};UID={USERNAME};Trusted_Connection=yes"
    CONNECTION_STRING_DWH = f"DRIVER={DRIVER};SERVER={HOST};DATABASE={DB_DWH};UID={USERNAME};Trusted_Connection=yes"
else:
    # print("USING LINUX/DOCKER")
    CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={HOST},{PORT};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=YES"
    CONNECTION_STRING_DWH = f"DRIVER={DRIVER};SERVER={HOST},{PORT};DATABASE={DB_DWH};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=YES"

dwh_connection = pyodbc.connect(CONNECTION_STRING_DWH)

# Get dataframes from DWH 

@st.cache_data
def get_general_test_data():
    """This function retrieves the general data from the DWH

    Returns:
        DataFrame: a dataframe conatining the columns: TestKey, Test, TimeSpent, Date, Year and all information about the testee and the test anomalies. 
    """    
    query = """
        select t.TestKey, t.Test, t.TimeSpent, d.Date, d.Year, c.*, ta.*
        from FactTest t 
        join DimTestAnomalies ta on ta.AnomaliesKey = t.AnomaliesKey
        join DimDate d on d.DateKey = t.CreatedDateKey
        join DimCandidate c on c.CandidateKey = t.CandidateKey 
    """
    return pd.read_sql(query, dwh_connection)

@st.cache_data
def get_all_question_data_with_anomaly():
    """This function retrieves data regarding the questions and their anomalies from the DWH for each test.  

    Returns:
        [DataFrame]: a list of dataframes per test 
    """    
    all_dfs = []
    for test in ['FCA', 'BAQ', 'SJT', 'PAQ', 'MDQ']:
        df = get_question_with_anomaly(test)
        # Verwijder dubbele kolommen in de DataFrame
        df = df.loc[:, ~df.columns.duplicated()]
        all_dfs.append(df)
    return all_dfs

# @st.cache_data
def get_question_with_anomaly(test='SJT'):
    """This function retrieves data regarding the questions and their anomalies from the DWH for one testtype. 

    Args:
        test (str, optional): the type of test that will be retrieved. Defaults to 'SJT'.

    Returns:
        DataFrame: a dataframe containing the information about the questions and their anomalies
    """    
    if test in ['FCA', 'BAQ', 'SJT', 'PAQ', 'MDQ']:
        query = f"""
            select * 
            from DimQuestionAnomalies qa 
            inner join FactQuestion{test} q on q.AnomaliesKey = qa.AnomaliesKey
        """
        df = pd.read_sql(query, dwh_connection)
        df = df.loc[:, ~df.columns.duplicated()]
    return df
