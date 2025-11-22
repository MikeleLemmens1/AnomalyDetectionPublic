"""Candidate Fill

This script fills all tables in the DWH with all Candidate related data.  

This script requires that the DWH is set-up according to the instructions in the `./README.md`. 
"""
import pandas as pd
import numpy as np
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

from func.dwh_actions import insert

path = os.path.abspath("decoded_data/DimCandidate.csv")
df_candidate = pd.read_csv(path)

df_candidate = df_candidate.replace(np.nan, None)

print("filling DimCandidate")
insert(
    df=df_candidate,
    table='DimCandidate'
)

print("All done!")
