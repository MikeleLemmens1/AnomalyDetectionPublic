"""
This script performs anomaly detection on a dataset by checking for identical answers within the question. 
"""
# # Same Anwser Anomaly

import pandas as pd
import os

root = os.path.abspath(".")

# ## Import Data from csv

fca_question = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactQuestionSJT.csv'))

# ## Data Preparation

df = fca_question[["QuestionKey", "AnswerSequence1", "AnswerSequence2", "AnswerSequence3"]]

# ## Data Labelling

same_answers = (df['AnswerSequence1'] == df['AnswerSequence2']) & (df['AnswerSequence2'] == df['AnswerSequence3'])
df['SameAnswers'] = False
df.loc[same_answers, 'SameAnswers'] = True

# ## Exporting Data with Anomaly Check

df = df[["QuestionKey", "SameAnswers"]]

df['is_anomaly'] = df.SameAnswers 
df.is_anomaly = df.is_anomaly.astype(int)


df.to_csv(os.path.join(root, 'anomalies', 'SJT', 'csv', 'same_answers_question_checked.csv'), index=False)


