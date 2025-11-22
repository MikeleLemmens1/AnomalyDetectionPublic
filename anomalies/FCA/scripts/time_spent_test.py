"""
This script performs anomaly detection on a dataset using the time spent on the test. 
"""

import pandas as pd
import os  

current_dir = os.path.abspath("decoded_data")
fca_question = pd.read_csv(os.path.join(current_dir, 'FCA', 'FactQuestionFCA.csv'))

# Data Preparation
df = fca_question[["TestKey", "TimeSpent"]]
df_timespent = df.groupby('TestKey')['TimeSpent'].sum().reset_index()

# ## Statistics
# LET OP: hier gedaan op hele kleine steekproef, dit moet berekend worden op de populatie! 

mu = df_timespent.TimeSpent.mean()
sigma = df_timespent.TimeSpent.std()

# ## Data Labelling

# ### Too slow
# We will now figure out on which tests the candidate spent "too much time". 
too_slow = (df_timespent.TimeSpent > (mu + sigma) )

df_timespent['TooSlow'] = False
df_timespent.loc[too_slow, 'TooSlow'] = True

# ### Too fast
# We will now figure out on which tests the candidate spent "too little time". 

too_fast = (df_timespent.TimeSpent < (mu - sigma) )

df_timespent['TooFast'] = False
df_timespent.loc[too_fast, 'TooFast'] = True

# ## Exporting Data with Anomaly Check

df_timespent['is_anomaly'] = df_timespent.TooFast | df_timespent.TooSlow
df_timespent.is_anomaly = df_timespent.is_anomaly.astype(int)
current_dir = os.path.abspath("anomalies")
df_timespent.to_csv(os.path.join(current_dir, 'FCA','csv', 'time_spent_test_checked.csv'), index=False)
