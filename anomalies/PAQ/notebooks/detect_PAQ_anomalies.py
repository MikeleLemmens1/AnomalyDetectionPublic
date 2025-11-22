import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import os

current_dir = os.path.abspath("anomalies")

scripts = [
    'preprocessing_pyod.ipynb', 
    'preprocessing_per_statement_type.ipynb', 
    'preprocessing_per_question.ipynb', 
    'same_answers_test.ipynb',
    'anomalies_pyod.ipynb',
    'anomalies_dbscan.py',
    ]

for script in scripts:
    notebook_path = os.path.join(current_dir, 'PAQ', 'scripts', script)
    with open(notebook_path) as f:
        nb = nbformat.read(f, as_version=4)
    ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
    try:
        ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
        print(f"Notebook {script} executed successfully!")
    except Exception as e:
        print(f"An error occurred while executing the notebook: {str(e)}")

# execute merge script to combine and create Dims 

notebook_path = os.path.join(current_dir, 'PAQ', 'merge.ipynb')
with open(notebook_path) as f:
    nb = nbformat.read(f, as_version=4)
ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
try:
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(notebook_path)}})
    print(f"Final notebook executed successfully!")
except Exception as e:
    print(f"An error occurred while executing the notebook: {str(e)}")