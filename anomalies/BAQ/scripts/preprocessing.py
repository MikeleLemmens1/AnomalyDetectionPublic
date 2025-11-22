"""
Script for preprocessing BA51 data.

Steps:
1. Load and clean data:
   - Read `FactTest.csv` and `FactQuestionBAQ.csv`, drop unnecessary columns, and merge on `TestKey`.
2. Separate normative and ipsative data:
   - Create separate DataFrames for normative (`Norm1` to `Norm5`) and ipsative (`Ips1` to `Ips5`) responses.
3. Reshape data:
   - Melt normative and ipsative DataFrames to long format and extract question numbers.
   - Pivot both DataFrames to wide format, filling missing values with `0.0`.
4. Merge results:
   - Combine normative and ipsative data into a single DataFrame.
5. Export results:
   - Save normative, ipsative, and combined DataFrames as separate CSV files.

Dependencies:
- pandas, os

Inputs:
- `./decoded_data/BA51/FactTest.csv`
- `./decoded_data/BA51/FactQuestionBaq.csv`

Outputs:
- `preprocessed_data_norm.csv`: Preprocessed normative data.
- `preprocessed_data_ips.csv`: Preprocessed ipsative data.
- `preprocessed_data.csv`: Combined normative and ipsative data.

All files are saved in `anomalies/BAQ/csv`.
"""

import os
import pandas as pd

current_dir = os.path.abspath("decoded_data")

# getting data
df_test = pd.read_csv(os.path.join(current_dir, 'BA51', 'FactTest.csv'))
df_question = pd.read_csv(os.path.join(current_dir, 'BA51', 'FactQuestionBAQ.csv'))


df_test.drop(columns=['VersionNumber', 'Test', 'ModifiedDateKey', 'CreatedDateKey'], inplace=True)
df_question.drop(columns=['Test'], inplace=True)

df = df_question.merge(df_test, on='TestKey')

# Apart ipsative en normative

# DataFrame met alleen de Norm-kolommen
df_norm = df[['TestKey','NormItemID', 'Norm1', 'Norm2', 'Norm3', 'Norm4', 'Norm5']]

# DataFrame met alleen de Ips-kolommen
df_ips = df[['TestKey', 'IpsItemID', 'Ips1', 'Ips2', 'Ips3', 'Ips4', 'Ips5']]
# ## Cleaning

# ### Normative
df_melted_norm = df_norm.melt(id_vars=['TestKey', 'NormItemID'], 
                    value_vars=['Norm1', 
                                'Norm2',
                                'Norm3',
                                'Norm4',
                                'Norm5'], 
                    var_name='answer_type', 
                    value_name='Answer')
df_melted_norm['QuestionNr'] = df_melted_norm['answer_type'].str.extract(r'(\d+)', expand=False).astype('Int8')
df_melted_norm.drop(columns=["answer_type"], inplace=True)



df_pivot_norm = df_melted_norm.pivot_table(index='TestKey', 
                                columns=['NormItemID', 'QuestionNr'], 
                                values='Answer', 
                                aggfunc='first')
df_pivot_norm.columns = [f'Q{q}_A{a}_norm' for q, a in df_pivot_norm.columns]
df_pivot_norm.fillna(0.0, inplace=True)

# ### Ipsatives
df_melted_ips = df_ips.melt(id_vars=['TestKey', 'IpsItemID'], 
                    value_vars=['Ips1', 
                                'Ips2',
                                'Ips3',
                                'Ips4',
                                'Ips5'], 
                    var_name='answer_type', 
                    value_name='Answer')
df_melted_ips['QuestionNr'] = df_melted_ips['answer_type'].str.extract(r'(\d+)', expand=False).astype('Int8')
df_melted_ips.drop(columns=["answer_type"], inplace=True)


df_pivot_ips = df_melted_ips.pivot_table(index='TestKey', 
                                columns=['IpsItemID', 'QuestionNr'], 
                                values='Answer', 
                                aggfunc='first')
df_pivot_ips.columns = [f'Q{q}_A{a}_ips' for q, a in df_pivot_ips.columns]
df_pivot_ips.fillna(0.0, inplace=True)

df_pivot_ips.drop_duplicates(inplace=True)
df_pivot_norm.drop_duplicates(inplace=True)

df_alles = df_pivot_norm.merge(df_pivot_ips, on=['TestKey'])

# df_dupl.set_index('TestKey', inplace=True)

current_dir = os.path.abspath("anomalies")

# getting data
df_pivot_ips.to_csv(os.path.join(current_dir, 'BAQ','csv', 'preprocessed_data_ips.csv'))
df_pivot_norm.to_csv(os.path.join(current_dir, 'BAQ', 'csv','preprocessed_data_norm.csv'))
df_alles.to_csv(os.path.join(current_dir, 'BAQ', 'csv','preprocessed_data.csv'))