"""
This script performs anomaly detection on a dataset by checking for identical answers within the question. 
"""

import pandas as pd
import pyodbc  
import matplotlib.pyplot as plt
import os

current_dir = os.path.abspath("decoded_data")

# getting data
fca_question = pd.read_csv(os.path.join(current_dir, 'FCA', 'FactQuestionFCA.csv'))

# ## Data Preparation
# 
# The only data cleaning that needs to happen here is getting rid of the coloms we won't need in this anomaly detection. There seem to be no empty fields or suspicious values to worry about. 
df = fca_question[["QuestionKey", "Answer1", "Answer2", "Answer3"]]

## Data Labelling
# We will now figure out on which tests the candidate filled out exactly the same answer for every question. 
same_answers = (df['Answer1'] == df['Answer2']) & (df['Answer2'] == df['Answer3'])
df['SameAnswers'] = False
df.loc[same_answers, 'SameAnswers'] = True

# ## Exporting Data with Anomaly Check
df = df[["QuestionKey", "SameAnswers"]]
df.set_index("QuestionKey", inplace=True)

current_dir = os.path.abspath("anomalies")
df.to_csv(os.path.join(current_dir, 'FCA', 'csv','same_answers_question_checked.csv'))
