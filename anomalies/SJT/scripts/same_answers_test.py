"""
This script performs anomaly detection on a dataset by checking for identical answers within the test. 
"""

import pandas as pd
import numpy as np
import os

root = os.path.abspath(".")

# ## Import Data from csv


sjt_test = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactTest.csv'))
sjt_question = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactQuestionSJT.csv'))

# ## Data Preparation

df = sjt_question[["TestKey", "AnswerSequence1", "AnswerSequence2", "AnswerSequence3"]]
df.head(25)

all_test_answers = df.groupby(['TestKey']).agg({
    'AnswerSequence1': list,
    'AnswerSequence2': list,
    'AnswerSequence3': list
}).reset_index()

all_test_answers['AllAnswers'] = all_test_answers.apply(
    lambda row: np.array(row['AnswerSequence1'] + row['AnswerSequence2'] + row['AnswerSequence3']),
    axis=1
)

all_test_answers = all_test_answers[['TestKey', 'AllAnswers']]

# ## Detection function

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

all_test_answers.drop(columns=["AllAnswers"], inplace=True)
all_test_answers['is_anomaly'] = all_test_answers.SameAnswerPercentage >= 50
all_test_answers.is_anomaly = all_test_answers.is_anomaly.astype(int)

all_test_answers.to_csv(os.path.join(root, 'anomalies', 'SJT', 'csv', 'same_answers_test_checked.csv'), index=False)
