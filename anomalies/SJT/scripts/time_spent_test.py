"""
This script performs anomaly detection on a dataset using the time spent on the test. 
"""
# # Total Time Spent on Test

import pandas as pd
import matplotlib.pyplot as plt
import os

root = os.path.abspath(".")

# ## Import Data from csv

sjt_question = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactQuestionSJT.csv'))

# ## Data Preparation

df = sjt_question[["TestKey", "TimeSpent"]]
df_timespent = df.groupby('TestKey')['TimeSpent'].sum().reset_index()

# ## Statistics

mu = df_timespent.TimeSpent.mean()
sigma = df_timespent.TimeSpent.std()

# ## Data Labelling

too_slow = (df_timespent.TimeSpent > (mu + sigma) )

df_timespent['TooSlow'] = False
df_timespent.loc[too_slow, 'TooSlow'] = True

too_fast = (df_timespent.TimeSpent < (mu - sigma) )

df_timespent['TooFast'] = False
df_timespent.loc[too_fast, 'TooFast'] = True


# ## Exporting Data with Anomaly Check

df_timespent['is_anomaly'] = df_timespent.TooFast | df_timespent.TooSlow
df_timespent.is_anomaly = df_timespent.is_anomaly.astype(int)

df_timespent.to_csv(os.path.join(root, 'anomalies', 'SJT', 'csv', 'time_spent_test_checked.csv'), index=False)
