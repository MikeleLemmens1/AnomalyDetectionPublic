"""
This module includes the following functions: 
    * python_script: runs the python script at the indicated location
    * compare_anomaly_models: compares the result from all supplied anomaly models and calculates the anomaly score
    * calculate_anomaly_threshold: caluculates the anomaly threshold based on the interquartile range
"""
import subprocess
import pandas as pd
import time

def python_script(path, arguments=""):
    """This function runs the python script at the indicated location

    Args:
        path (str): path to the python script. 
        arguments (str, optional): takes the arguments that will be passed to the python script. Defaults to "".

    Raises:
        subprocess.CalledProcessError: when an error occured while running the script
        Exception: when the script at the indicated location could not be run
    """    
    warnings_to_ignore = ["SettingWithCopyWarning", "UserWarning", "DeprecationWarning", "FutureWarning"]
    try:
        print(f"Started {path} script")
        start = time.time()
        process = subprocess.Popen(['python', '-u', path, arguments],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True,
                         bufsize=0)
        while True:
            output = process.stdout.readline().strip()
            if output:
                print("- ", output)
            if process.poll() is not None:
                break
            
        error = process.stderr.read()
        if error and not any(warning in error for warning in warnings_to_ignore):
            raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
        
        end = time.time()
        seconds = end-start
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        print(f"Script {path} ran succesfully in {minutes}min {seconds}sec")
    except subprocess.CalledProcessError as cpe:
        raise Exception(f"Something went wrong while running {path}:\n{cpe.stderr}")
    except Exception as e:
        raise Exception(f"Couldn't run script {path}\n{e}")


def compare_anomaly_models(*model_dfs, id_column='TestKey'):
    """Compares the result from all supplied anomaly models and calculates the anomaly score. 

    Args:
        *model_dfs (DataFrame, str): a number of at least 3 tuples consisting of first a dataframe that has at least a column with the name of the "id_column" and a column "is_anomaly", and second the name of the detection method. 
        id_column (str, optional): the name of the column used to compare the anomaly detection methods. Defaults to 'TestKey'.

    Returns:
        DataFrame: a dataframe with a column for each detection method in the form of <provided method name>_anomaly and a column anomaly_score with the percentages of methods that were flagged. 
    """    
    df_combined = pd.DataFrame({id_column: model_dfs[0][0][id_column]})
    
    number_of_anomalies = 0
    model_names = []
    for df, model_name in model_dfs:
        number_of_anomalies +=1 
        model_names.append(model_name)
        df_combined = df_combined.merge(
            df[[id_column, 'is_anomaly']],
            on=id_column,
            suffixes=('', f'_{model_name}')
        )
        df_combined = df_combined.rename(columns={'is_anomaly': f'{model_name}_anomaly'})
    
    anomaly_columns = [col for col in df_combined.columns if col.endswith('_anomaly')]
    df_combined['anomaly_count'] = df_combined[anomaly_columns].sum(axis=1)
    df_combined['anomaly_score'] = df_combined['anomaly_count'] / number_of_anomalies 
    df_combined.drop(columns=['anomaly_count'], inplace=True)
    return df_combined

def calculate_anomaly_threshold(df, column='anomaly_score', multiplier=1.5):
    """Caluculates the anomaly threshold based on the interquartile range. 

    Args:
        df (DataFrame): the dataframe 
        column (str, optional): name of the column in the dataframe that the threshold will be calculated on. Defaults to 'anomaly_score'.
        multiplier (float, optional): multiplier used to calculate the threshold. Defaults to 1.5.

    Returns:
        float: the calculated threshold
    """    
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    threshold = Q3 + (multiplier * IQR)
    return threshold

def conclude_anomaly(df):
    """Makes a conclusion per test on whether the test is an anomaly or not, based on the calculated threshold. 

    Args:
        df (DataFrame): the dataframe that has an "is_anomaly" column. 

    Returns:
        DataFrame: the dataframe with an 'is_anomaly' column added
        float: the calculated threshold
        float: the percentile of tests that were determined to be anomalies 
    """    
    threshold = calculate_anomaly_threshold(df)
    df['is_anomaly'] = df['anomaly_score'] > threshold
    df.is_anomaly = df.is_anomaly.astype(int)
    percentile = (df['anomaly_score'] <= threshold).mean() * 100
    return df, threshold, percentile