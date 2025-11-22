"""
This script performs anomaly detection on a dataset using the time spent on the question. 
"""
import pandas as pd
import os
# # Total Time Spent on Question
# Checks the time the candidate spend on a question. 
# 
# The test will be marked as "too slow" if the time it took was more than the mean plus the standard deviation and marked as "too fast" if the time it took was more than the mean minus the standard deviation. 
# 
# The mean and the standard deviation are calculated over all questions with the same ItemId. 

# ## Import Data from csv
current_dir = os.path.abspath("decoded_data")
fca_question = pd.read_csv(os.path.join(current_dir, 'FCA', 'FactQuestionFCA.csv'))

# ## Detection Function

# The standerd deviation can return Nan if the variation is too small. We will in that case work with zero. 
df_items = fca_question[["ItemId", "TimeSpent"]]

df_items = df_items.groupby('ItemId')['TimeSpent'].agg(['mean', 'std']).reset_index().rename(columns={"mean":"MeanTimeSpent", "std":"StdTimeSpent"})
df_items.fillna(0, inplace=True)
df_items.set_index("ItemId", inplace=True)

df_items["MaxTime"] = df_items["MeanTimeSpent"] + df_items["StdTimeSpent"]
df_items["MinTime"] = df_items["MeanTimeSpent"] - df_items["StdTimeSpent"]

df = fca_question[["QuestionKey", "ItemId", "TimeSpent"]]

def detect_too_slow(ItemId, TimeSpent):
    if TimeSpent > df_items.MaxTime[ItemId]:
        return True
    return False

def detect_too_fast(ItemId, TimeSpent):
    if TimeSpent < df_items.MinTime[ItemId]:
        return True
    return False

# ## Data Labelling
df["TooSlow"] = df.apply(lambda row: detect_too_slow(row['ItemId'], row['TimeSpent']), axis=1)
df["TooFast"] = df.apply(lambda row: detect_too_fast(row['ItemId'], row['TimeSpent']), axis=1)

# ## Exporting Data with Anomaly Check
current_dir = os.path.abspath("anomalies")
df.to_csv(os.path.join(current_dir, 'FCA','csv', 'time_spent_question_checked.csv'), index=False)