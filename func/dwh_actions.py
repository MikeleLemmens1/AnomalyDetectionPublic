"""
This module is used for initializing the connection with the database and retrieving data from it or inserting data into the database. 

This module includes the following functions: 
    * insert: inserts a dataframe into a table in the DWH
    * get_max_anomaly_key: looks up what the highest key is in a specific table and returns it. 
"""

import sys 
import os

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

print("Connecting to database")
channel = dep2connection("CRH_DWH")
cursor = channel.cursor()

def insert(df, table):
    """
    This function inserts a dataframe into a table in the DWH. 

    Args:
        df (DataFrame): the dataframe that needs to be written to the DWH
        table (str): the name of the table the dataframe needs to be written to
    """
    print(f"Filling {table}")

    columns = ""
    for i in range(len(df.columns) - 1):
        col = df.columns[i]
        columns += col + ", "

    col = df.columns[i+1]
    columns += col

    values = ""
    for _ in range(len(df.columns) - 1) : 
        values += "?,"
    values += "?"

    query = f"""
                INSERT INTO {table}({columns})
                VALUES({values})
                """

    for _, row in df.iterrows():
        row = list(row)
        cursor.execute(query, row)
    channel.commit()

    print(f"Filled {table} in DWH")

def get_max_anomaly_key(table='DimQuestionAnomalies'):
    """
    This function looks up what the highest key is in a table and returns this. 

    Args:
        table (str, optional): The table of which the max key needs to be found. Defaults to 'DimQuestionAnomalies'.

    Returns:
        int: the highest key from the table
    """
    query = f"SELECT MAX(AnomaliesKey) AS 'key' FROM {table}"
    max_key = cursor.execute(query).fetchall()
    return max_key[0][0]


# channel.close()