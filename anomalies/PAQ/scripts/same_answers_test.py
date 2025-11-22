"""
This script performs anomaly detection on a dataset by checking for identical answers within the test. 
"""

import pandas as pd
import numpy as np
import os

current_dir = os.path.abspath("anomalies")


# Import Data from csv
# paq_question = pd.read_csv("../../../decoded_data/PAQ/FactQuestionPAQ.csv")
paq_question = pd.read_csv(os.path.join(current_dir, 'PAQ', 'csv','preprocessed_data.csv'))

# Data Preparation

# The only data cleaning that needs to happen here is getting rid of the coloms we won't need in this anomaly detection. There seem to be no empty fields or suspicious values to worry about. 
df = paq_question[["QuestionKey", "AnswerVal", "TestKey"]]
df.info()

# Same Anwsers on Test Anomaly

# Groepeer de data per CandidateId, en behoud ook InstanceId
all_test_answers = df.groupby(['TestKey']).agg({
    'AnswerVal': list
}).reset_index()

# Voeg alle antwoorden samen in een enkele array
all_test_answers['AllAnswers'] = all_test_answers.apply(
    lambda row: np.array(row['AnswerVal']),
    axis=1
)

def detect_same_answers(TestKey, print_result=False):
    answers = all_test_answers[all_test_answers['TestKey'] == TestKey].reset_index().AllAnswers[0]

    ans_count = {
        0:0, 
        1:0, 
        2:0,
        3:0,
        4:0,
        5:0
        }
    total_count = 0

    for i in answers: 
        ans_count[i] += 1
        total_count += 1

    max_count = max(ans_count.values())
    most_common_ans = max(ans_count, key=ans_count.get)
    perc = (max_count/total_count) * 100
    if print_result:
        print(f"Candidate {TestKey} answered {most_common_ans} on {perc}% of the questions.")
    return perc

# ## Exporting Data with Anomaly Check

all_test_answers['SameAnswerPercentage'] = all_test_answers['TestKey'].apply(detect_same_answers)
all_test_answers.drop(columns=["AllAnswers", "AnswerVal"], inplace=True)
all_test_answers['is_anomaly'] = all_test_answers.SameAnswerPercentage >= 50
all_test_answers.is_anomaly = all_test_answers.is_anomaly.astype(int)


all_test_answers.to_csv(os.path.join(current_dir, 'PAQ', 'csv','same_answers_test_checked.csv'))