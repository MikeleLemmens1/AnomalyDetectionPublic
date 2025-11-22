"""
Script for preprocessing PAQ data.

Steps:
1. Load and clean data:
   - Read `FactTest.csv` and `FactQuestionPAQ.csv`, drop unnecessary columns, and merge on `TestKey`.
2. Process dates:
   - Convert `CreatedDateKey` to `datetime`, extract `Year`, `Month`, and `Day`, and drop the original column.
3. Clean and encode:
   - Remove missing values, drop duplicates, and encode `LeftStatement` and `RightStatement` using `LabelEncoder`.
4. Validate data:
   - Ensure `AnswerVal` is an integer and within the range [1, 2, 3, 4, 5].
5. Export results:
   - Save the cleaned DataFrame as `preprocessed_data.csv`.

Inputs:
- `./decoded_data/PAQ/FactTest.csv` 
- `./decoded_data/PAQ/FactQuestionPAQ.csv`

Output:
- `preprocessed_data.csv` in `anomalies/PAQ/csv`.
"""

import pandas as pd
from sklearn.preprocessing import LabelEncoder
import os

current_dir = os.path.abspath("decoded_data")

df_test = pd.read_csv(os.path.join(current_dir, 'PAQ', 'FactTest.csv'))
df_question = pd.read_csv(os.path.join(current_dir, 'PAQ', 'FactQuestionPAQ.csv'))
df_test.drop(columns=['VersionNumber', 'Test'], inplace=True)
df_test.head()

df_question.drop(columns=['InstanceID', 'Test'], inplace=True)
df_question.head()

df = df_question.merge(df_test, on='TestKey')
df.head()

df["CreatedDateKey"] = pd.to_datetime(df.CreatedDateKey, format="%Y%m%d")
df.head()

df['Year'] = pd.DatetimeIndex(df['CreatedDateKey']).year
df['Month'] = pd.DatetimeIndex(df['CreatedDateKey']).month
df['Day'] = pd.DatetimeIndex(df['CreatedDateKey']).dayofweek
df.drop(columns=['CreatedDateKey'], inplace=True)

df.dropna(inplace=True)

le = LabelEncoder()
df['LeftStatement'] = le.fit_transform(df['LeftStatement'])
df['RightStatement'] = le.fit_transform(df['RightStatement'])

only_int = df.AnswerVal.apply(lambda x: x % 1 == 0).all()

if only_int:
    df['AnswerVal'] = df['AnswerVal'].astype(int)
df.info()

is_valid = df['AnswerVal'].isin([1, 2, 3, 4, 5]).all()

if not is_valid: 
    print("Some values in the AnswerVal column do not fall in the permitted range.")
    df = df[df['AnswerVal'].isin([1, 2, 3, 4, 5])]
else: 
    print("All values in the AnswerVal column fall in the permitted range.")

# ### Export to csv
current_dir = os.path.abspath("anomalies")

df.drop_duplicates(inplace=True)
df.set_index('TestKey', inplace=True)
df.to_csv(os.path.join(current_dir, 'PAQ', 'csv','preprocessed_data.csv'))
