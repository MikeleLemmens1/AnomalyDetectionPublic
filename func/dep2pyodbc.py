'''
This module provides a function to make a connection to the SQL server (CRH or CRH_DWH).
To be able to use this, you need to set a few environment variables in the .env file, located in the root folder.

.env vars:
    HOST = IP or computer name where the SQL server located
    PORT = On which port is the SQL server accesible
    DRIVER = SQL server driver of the host
    USERNAME = sa or username you got from the system admin
    PASSWORD = M0naL1saM1keleAngeL0 or the password you got from the system admin

Returns:
  - pyodbc SQL server connection
'''

import os
from dotenv import load_dotenv
import pyodbc

def dep2connection(database, print_connection_string=False):
    '''
    This function makes a connection to the SQL server (CRH or CRH_DWH).
    To be able to use this, you need to set a few environment variables in the .env file, located in the root folder.

    .env vars:
        HOST = IP or computer name where the SQL server located
        PORT = On which port is the SQL server accesible
        DRIVER = SQL server driver of the host
        USERNAME = sa or username you got from the system admin
        PASSWORD = M0naL1saM1keleAngeL0 or the password you got from the system admin

    Returns:
    - pyodbc SQL server connection
    '''
    load_dotenv()

    HOST = os.getenv("HOST")
    PORT = os.getenv("MSSQL_LOCAL_PORT")
    DRIVER = os.getenv("DRIVER")
    USERNAME = os.getenv("MSSQL_USERNAME")
    PASSWORD = os.getenv("MSSQL_SA_PASSWORD")

    USE_WINDOWS_AUTH = "true" == os.getenv("MSSQL_USE_WIN_AUTH").lower()

    CONNECTION_STRING = ""
    if USE_WINDOWS_AUTH:
        CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={HOST};DATABASE={database};UID={USERNAME};Trusted_Connection=yes"
    else:
        CONNECTION_STRING = f"DRIVER={DRIVER};SERVER={HOST},{PORT};DATABASE={database};UID={USERNAME};PWD={PASSWORD};TrustServerCertificate=YES"

    if print_connection_string:
        print(CONNECTION_STRING)
    return pyodbc.connect(CONNECTION_STRING)
