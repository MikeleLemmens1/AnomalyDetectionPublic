"""
Script for preprocessing MDQ data.

Steps:
1. Load and clean data:
   - Read `FactTest.csv` and `FactQuestionMDQ.csv`, drop unnecessary columns, and merge on `TestKey`.
2. Process dates:
   - Convert `CreatedDateKey` to `datetime`, extract `Year`, `Month`, and `Day`, and drop the original column.
3. Reshape data:
   - Melt the DataFrame to long format, create a `QuestionNr` column based on answer type, and drop the `answer_type` column.
4. Pivot data:
   - Create a pivot table with `itemId` and `QuestionNr` as columns, fill missing values with `0.0`, and reset the index.
5. Export results:
   - Save the preprocessed DataFrame as `preprocessed_data.csv`.

Dependencies:
- pandas, os

Inputs:
- `./decoded_data/MDQ/FactTest.csv`
- `./decoded_data/MDQ/FactQuestionMDQ.csv`

Output:
- `preprocessed_data.csv` in `anomalies/MDQ/csv`.
"""


import pandas as pd
import os

current_dir = os.path.abspath("decoded_data")

# getting data
# df = pd.read_csv('../csv/preprocessed_data.csv')
df_test = pd.read_csv(os.path.join(current_dir, 'MDQ', 'FactTest.csv'))
df_question = pd.read_csv(os.path.join(current_dir, 'MDQ', 'FactQuestionMDQ.csv'))

df_test.drop(columns=['VersionNumber', 'Test', 'ModifiedDateKey'], inplace=True)
df_question.drop(columns=['Test'], inplace=True)
df = df_question.merge(df_test, on='TestKey')

# Date
df["CreatedDateKey"] = pd.to_datetime(df.CreatedDateKey, format="%Y%m%d")
df['Year'] = pd.DatetimeIndex(df['CreatedDateKey']).year
df['Month'] = pd.DatetimeIndex(df['CreatedDateKey']).month
df['Day'] = pd.DatetimeIndex(df['CreatedDateKey']).dayofweek
df.drop(columns=['CreatedDateKey'], inplace=True)

# Cleaning
df.drop_duplicates(inplace=True)
df.dropna(inplace=True)

# Samenvoegen 
# Step 1: Melt the dataframe
df_melted = df.melt(id_vars=['TestKey', 'itemId', 'QuestionKey', 'CandidateKey'], 
                    value_vars=['FirstVal', 'SecondVal', 'ThirdVal', 'FourthVal', 'FifthVal', 'SixthVal'], 
                    var_name='answer_type', 
                    value_name='Answer')

# Step 2: Create a QuestionNr column
df_melted['QuestionNr'] = df_melted['answer_type'].map({
    'FirstVal': 1, 'SecondVal': 2, 'ThirdVal': 3,
    'FourthVal': 4, 'FifthVal': 5, 'SixthVal': 6
})

# Step 3: Drop the answer_type column
df_melted.drop(columns=["answer_type"], inplace=True)

# Step 4: Create the pivot table
df_pivot = df_melted.pivot_table(index=['TestKey', 'CandidateKey'], 
                                 columns=['itemId', 'QuestionNr'], 
                                 values='Answer', 
                                 aggfunc='first')

# Step 5: Rename the columns
df_pivot.columns = [f'Q{q}_A{a}' for q, a in df_pivot.columns]

# Step 6: Fill NaN values with 0.0
df_pivot.fillna(0.0, inplace=True)

# Optional: Reset the index if you want TestKey and CandidateKey as columns
df_pivot.reset_index(inplace=True)

current_dir = os.path.abspath("anomalies")

df_pivot.to_csv(os.path.join(current_dir, 'MDQ', 'csv', 'preprocessed_data.csv'), index=False)