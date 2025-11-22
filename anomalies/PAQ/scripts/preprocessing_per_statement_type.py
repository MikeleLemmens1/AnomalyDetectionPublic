"""
Script for preprocessing PAQ data per statement type.

Steps:
1. Load and clean data
2. Process dates
3. Clean and encode
4. Validate data
5. Count the answers per statement type
6. Export results


Inputs:
- `./decoded_data/PAQ/FactTest.csv` 
- `./decoded_data/PAQ/FactQuestionPAQ.csv`

Output:
- `preprocessed_data.csv` in `anomalies/PAQ/csv`.
- `preprocessing_pyod.csv` in `anomalies/PAQ/csv`.
"""

import pandas as pd
import os

root = os.path.abspath(".")

df_test = pd.read_csv(os.path.join(root, 'decoded_data', 'PAQ', 'FactTest.csv'))
df_question = pd.read_csv(os.path.join(root, 'decoded_data', 'PAQ', 'FactQuestionPAQ.csv'))

df_test.drop(columns=['VersionNumber', 'Test'], inplace=True)
df_question.drop(columns=['InstanceID', 'Test'], inplace=True)

df = df_question.merge(df_test, on='TestKey')

# ### CreatedDate

df["CreatedDateKey"] = pd.to_datetime(df.CreatedDateKey, format="%Y%m%d")
df['Year'] = pd.DatetimeIndex(df['CreatedDateKey']).year
df['Month'] = pd.DatetimeIndex(df['CreatedDateKey']).month
df['Day'] = pd.DatetimeIndex(df['CreatedDateKey']).dayofweek
df.drop(columns=['CreatedDateKey'], inplace=True)

# ## Cleaning
df.dropna(inplace=True)

# ### Make numerical
only_int = df.AnswerVal.apply(lambda x: x % 1 == 0).all()
if only_int:
    print('In the column AnswerVal none of the values have a value that needs to be stored as a float, therefor we can change the datatype to integer.')
    df['AnswerVal'] = df['AnswerVal'].astype(int)

# ### Foutieve waarden

is_valid = df['AnswerVal'].isin([1, 2, 3, 4, 5]).all()

if not is_valid: 
    print("Some values in the AnswerVal column do not fall in the permitted range.")
    df = df[df['AnswerVal'].isin([1, 2, 3, 4, 5])]
else: 
    print("All values in the AnswerVal column fall in the permitted range.")

df.to_csv(os.path.join(root, 'anomalies', 'PAQ', 'csv', 'preprocessed_data.csv'), index=False)

len(df.LeftStatement.unique())

df['LeftStatement_type'] = df['LeftStatement'].str.split('_').str[0]

start = len(df.RightStatement.unique())
df['RightStatement_type'] = df['RightStatement'].str.split('_').str[0]
end = len(df.RightStatement_type.unique())

print('original length:', start)
print('remaining length:', end)

df.drop(columns=['RightStatement', 'LeftStatement'], inplace=True)

df['score_left'] = 6 - df.AnswerVal
df['score_right'] = df.AnswerVal
df.drop(columns=['AnswerVal'], inplace=True)

left = df.groupby(['TestKey', 'LeftStatement_type'])['score_left'].sum().unstack(fill_value=0)
left.reset_index(inplace=True)

right = df.groupby(['TestKey', 'RightStatement_type'])['score_right'].sum().unstack(fill_value=0)
right.reset_index(inplace=True)

res = left.merge(right, on='TestKey')

res.to_csv(os.path.join(root, 'anomalies', 'PAQ', 'csv', 'preprocessing_pyod.csv'), index=False)
