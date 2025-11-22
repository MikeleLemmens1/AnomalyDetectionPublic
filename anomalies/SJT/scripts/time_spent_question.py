"""
This script performs anomaly detection on a dataset using the time spent on the question. 
"""

import pandas as pd
import os

root = os.path.abspath(".")

# ## Import Data from csv

sjt_question = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactQuestionSJT.csv'))

# ## Detection Function

df_items = sjt_question[["ItemID", "TimeSpent"]]

df_items = df_items.groupby('ItemID')['TimeSpent'].agg(['mean', 'std']).reset_index().rename(columns={"mean":"MeanTimeSpent", "std":"StdTimeSpent"})
df_items.fillna(0, inplace=True)
df_items.set_index("ItemID", inplace=True)
df_items.head()


df_items["MaxTime"] = df_items["MeanTimeSpent"] + df_items["StdTimeSpent"]
df_items["MinTime"] = df_items["MeanTimeSpent"] - df_items["StdTimeSpent"]
df_items.head()


df = sjt_question[["QuestionKey", "ItemID", "TimeSpent"]]
df.head()


def detect_too_slow(ItemId, TimeSpent):
    if TimeSpent > df_items.MaxTime[ItemId]:
        return True
    return False

def detect_too_fast(ItemId, TimeSpent):
    if TimeSpent < df_items.MinTime[ItemId]:
        return True
    return False


# ## Data Labelling


df["TooSlow"] = df.apply(lambda row: detect_too_slow(row['ItemID'], row['TimeSpent']), axis=1)
df["TooFast"] = df.apply(lambda row: detect_too_fast(row['ItemID'], row['TimeSpent']), axis=1)

# ## Exporting Data with Anomaly Check

df['is_anomaly'] = df.TooFast | df.TooSlow
df.is_anomaly = df.is_anomaly.astype(int)

df.to_csv(os.path.join(root, 'anomalies', 'SJT', 'csv', 'time_spent_question_checked.csv'), index=False)
