"""
Script for preprocessing SJT data.

Steps:
1. Load and clean data:
   - Read `FactTest.csv` and `FactQuestionSJT.csv`, drop unnecessary columns, and merge on `TestKey`.
2. Process date information:
   - Convert `CreatedDateKey` to `datetime`, extract `Year`, `Month`, and `Day`, and drop the original column.
3. Handle `TimeSpent`:
   - Separate rows with and without `TimeSpent` and proceed without the `TimeSpent` column.
4. Reshape data:
   - Melt the DataFrame to long format, extract question numbers, and pivot to wide format.
   - Fill missing values with `0.0`.
5. Add metadata:
   - Merge the pivoted data with `Year`, `Month`, and `Day` information.
6. Export results:
   - Save the preprocessed DataFrame as `preprocessed_data.csv`.

Dependencies:
- pandas, os

Inputs:
- `./decoded_data/SJT/FactTest.csv` 
- `./decoded_data/SJT/FactQuestionSJT.csv`

Output:
- `preprocessed_data.csv` in `anomalies/SJT/csv`.
"""

import pandas as pd
import os

root = os.path.abspath(".")

df_test = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactTest.csv'))
df_question = pd.read_csv(os.path.join(root, 'decoded_data', 'SJT', 'FactQuestionSJT.csv'))

df_test.drop(columns=['VersionNumber', 'TimeSpent', 'Test'], inplace=True)
df_question.drop(columns=['InstanceID', 'Test'], inplace=True)
df = df_question.merge(df_test, on='TestKey')

# ### CreatedDate

df["CreatedDateKey"] = pd.to_datetime(df.CreatedDateKey, format="%Y%m%d")

df['Year'] = pd.DatetimeIndex(df['CreatedDateKey']).year
df['Month'] = pd.DatetimeIndex(df['CreatedDateKey']).month
df['Day'] = pd.DatetimeIndex(df['CreatedDateKey']).dayofweek
df.drop(columns=['CreatedDateKey'], inplace=True)

# #### TimeSpent

time_zero = (df.TimeSpent == 0).sum()
time_not_zero = (df.TimeSpent != 0).sum()

df_no_time = df.drop(columns=['TimeSpent'])
df_time = df[df.TimeSpent != 0]

df = df_no_time

df_melted = df.melt(id_vars=['TestKey', 'ItemID'], 
                    value_vars=['AnswerSequence1', 
                                'AnswerSequence2',
                                'AnswerSequence3'], 
                    var_name='answer_type', 
                    value_name='Answer')
df_melted['QuestionNr'] = df_melted['answer_type'].str.slice(len('AnswerSequence')).astype('Int8')
df_melted.drop(columns=["answer_type"], inplace=True)

df_pivot = df_melted.pivot_table(index='TestKey', 
                                columns=['ItemID', 'QuestionNr'], 
                                values='Answer', 
                                aggfunc='first')
df_pivot.columns = [f'Q{q}_A{a}' for q, a in df_pivot.columns]
df_pivot.fillna(0.0, inplace=True)

df_add = df[["TestKey", "Year", "Month", "Day"]]
df_pivot = df_pivot.merge(df_add, on='TestKey')

df_dupl = df_pivot.drop_duplicates()

df_dupl.to_csv(os.path.join(root, 'anomalies', 'SJT', 'csv', 'preprocessed_data.csv'), index=False)
