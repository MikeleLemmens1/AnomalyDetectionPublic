"""Candidate csv for DWH

This script prepares raw decoded canidate data to usable csv-files for anomaly detection and later implementation in the DWH. 

This script requires that the CRH database is set-up as described in the `./README.md`. 
"""

import pandas as pd
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection

channel = dep2connection("CRH")

print("Collecting the data")
df_candidate = pd.read_sql("SELECT * FROM Candidate", channel)

print("Create dataframe with the correct data")
df_candidate_dwh = df_candidate[[
    "ID", "InstanceID", "OrganizationGUID", "LanguageGUID", "GenderChoice",
    "Gender", "Qualification"
]]

df_candidate_dwh["CandidateKey"] = df_candidate_dwh["ID"].astype(str) + df_candidate_dwh["InstanceID"].astype(str)
df_candidate_dwh["CandidateKey"].astype(int)

df_candidate_dwh = df_candidate_dwh[[
    "CandidateKey", "ID", "InstanceID", "OrganizationGUID",
    "LanguageGUID", "GenderChoice", "Gender", "Qualification"
    ]]

# put columns in the same order as the DWH table
df_candidate_dwh.rename(columns={
        'OrganizationGUID': 'Organisation',
        'LanguageGUID': 'ChosenLanguage', 
        'GenderChoice': 'ChosenGender',
    }, 
    inplace=True)

print("Creating the CSVs")
path = os.path.abspath("decoded_data/DimCandidate.csv")

df_candidate_dwh.to_csv(path, index=False)

