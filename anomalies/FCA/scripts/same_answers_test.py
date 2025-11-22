"""
This script performs anomaly detection on a dataset by checking for identical answers within the test. 
"""

import pandas as pd
import numpy as np
import os

# ## Import Data from csv
current_dir = os.path.abspath("decoded_data")

# getting data
fca_question = pd.read_csv(os.path.join(current_dir, 'FCA', 'FactQuestionFCA.csv'))
fca_test = pd.read_csv(os.path.join(current_dir, 'FCA', 'FactTest.csv'))

# ## Data Preparation
df = fca_question[["TestKey", "Answer1", "Answer2", "Answer3"]]


# Groepeer de data per CandidateId, en behoud ook InstanceId
all_test_answers = df.groupby(['TestKey']).agg({
    'Answer1': list,
    'Answer2': list,
    'Answer3': list
}).reset_index()

# Voeg alle antwoorden samen in een enkele array
all_test_answers['AllAnswers'] = all_test_answers.apply(
    lambda row: np.array(row['Answer1'] + row['Answer2'] + row['Answer3']),
    axis=1
)

# Behoud de kolommen CandidateId, InstanceId en AllAnswers
all_test_answers = all_test_answers[['TestKey', 'AllAnswers']]

# ## Detection function

def detect_same_answers(FCATestKey, print_result=False):
    answers = all_test_answers[all_test_answers['TestKey'] == FCATestKey].reset_index().AllAnswers[0]

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
        print(f"Candidate {FCATestKey} answered {most_common_ans} on {perc}% of the questions.")
    return perc

# ## Exporting Data with Anomaly Check

all_test_answers['SameAnswerPercentage'] = all_test_answers['TestKey'].apply(detect_same_answers)

all_test_answers.drop(columns=["AllAnswers"], inplace=True)

all_test_answers['is_anomaly'] = all_test_answers.SameAnswerPercentage >= 50
all_test_answers.is_anomaly = all_test_answers.is_anomaly.astype(int)

current_dir = os.path.abspath("anomalies")
all_test_answers.to_csv(os.path.join(current_dir, 'FCA', 'csv','same_answers_test_checked.csv'))
