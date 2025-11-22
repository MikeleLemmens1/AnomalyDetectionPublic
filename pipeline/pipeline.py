import os
import sys
import subprocess

root = os.path.abspath(".")
sys.path.append(root)

from func.dep2pyodbc import dep2connection
from func.logger import get_info_logger, get_error_logger

tests_list = ['FCA', 'SJT', 'PAQ', 'BAQ', 'MDQ']
warnings_to_ignore = ["SettingWithCopyWarning", "UserWarning", "DeprecationWarning", "FutureWarning", "WARNING"]

def check_and_install_dependencies():
    """
    This is a fuction that installs all modules that are needed to run this pipeline successfully
    """
    print("Checking and installing necessary modules")
    try:
        path_to_requirements = os.path.abspath("requirements.txt")

        process = subprocess.Popen(['python', '-m', 'pip', 'install', '-r', path_to_requirements, '--upgrade'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True,
                                    bufsize=0)
        while True:
            output = process.stdout.readline()
            if output:
                info_logger.info(output.strip())
            if process.poll() is not None:
                break
        
        error = process.stderr.read()
        if error and not any(warning in error for warning in warnings_to_ignore):
            raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
        
        info_logger.info("All necessary modules are installed")

    except subprocess.CalledProcessError as cpe:
        raise Exception(f"Something went wrong when installing a python module:\n{cpe.stderr}")
    except Exception as e:
        raise Exception(f"Something went wrong when installing a python module:\n{e}")


def check_and_create_directories():
    """
    This function makes sure all necessary folders are present in the repository
    """
    print("Creating necessary directories")

    directories = [
        os.path.abspath("anomalies/BAQ/csv"),
        os.path.abspath("anomalies/FCA/csv"),
        os.path.abspath("anomalies/MDQ/csv"),
        os.path.abspath("anomalies/PAQ/csv"),
        os.path.abspath("anomalies/SJT/csv"),
        os.path.abspath("decoded_data/BA51"),
        os.path.abspath("decoded_data/FCA"),
        os.path.abspath("decoded_data/MDQ"),
        os.path.abspath("decoded_data/PAQ"),
        os.path.abspath("decoded_data/SJT"),
    ]

    for path in directories:
        os.makedirs(path, exist_ok=True)
    
    info_logger.info("Directories are checked and created")

def build_datawarehouse():
    """
    This function builds the datawarehouse

    Scripts:
        /DEP2-G2/DWH/implement_DWH/DWH_implementatie.sql
    """
    # to create the datawarehouse you first need to be connected to a different database
    channel = dep2connection("CRH")
    channel.autocommit = True
    cursor = channel.cursor()

    try:
        info_logger.info("Creating the database")
        cursor.execute("DROP DATABASE IF EXISTS CRH_DWH")
        cursor.execute("CREATE DATABASE CRH_DWH")
        cursor.execute("USE CRH_DWH")

        # run script to create the tables in the datawarehouse
        path = os.path.abspath("DWH/implement_DWH/DWH_implementatie.sql")

        with open(path, 'r') as file:
            script = file.read()
            # Split on GO, ignoring case and removing whitespace
            statements = [s.strip() for s in script.split('GO') if s.strip()]

        info_logger.info("Creating the dim tables and FactTest")    
        
        for statement in statements:
            try:
                cursor.execute("BEGIN TRANSACTION")
                cursor.execute(statement)
                cursor.execute("COMMIT TRANSACTION")
            except Exception as e:
                cursor.execute("ROLLBACK TRANSACTION")
                error_logger.error(f"Error executing statement: {e}")
                raise
        
    except Exception as e:
        raise Exception(f"Something went wrong when creating the datawarehouse:\n{e}")

def add_question_tables():
    """
    This funtion adds the question tables for each test to the data warehouse

    Scripts:
        /DEP2-G2/DWH/implement_DWH/FCA.sql
        /DEP2-G2/DWH/implement_DWH/SJT.sql
        /DEP2-G2/DWH/implement_DWH/PAQ.sql
        /DEP2-G2/DWH/implement_DWH/BAQ.sql
        /DEP2-G2/DWH/implement_DWH/MDQ.sql
    """
    channel = dep2connection("CRH_DWH")
    cursor = channel.cursor()

    info_logger.info("Creating the FactQuestion tables")

    for test in tests_list:
        path_fca = os.path.abspath(f"DWH/implement_DWH/{test}.sql")
        try:
            with open(path_fca, 'r') as file:
                script_fca = file.read()
                statements = [s.strip() for s in script_fca.split('GO') if s.strip()]
            
            for statement in statements:
                cursor.execute(statement)
            channel.commit()
        except Exception as e:
            raise Exception(f"Something went wrong when creating the tables for {test}:\n{e}")

def run_candidate_scripts():
    """
    This function first creates a CSV with the data for DimCandidate.
    The second action of this function fills the data into the DimCandidate table in the DWH.

    Scripts:
        /DEP2-G2/decoderen/dim_candidate_csv_for_DWH.py
        /DEP2-G2/DWH/fill_DWH/Candidate_fill.py
        
    Output files:
        /DEP2-G2/decoded_data/DimCandidate.csv
    """

    info_logger.info("Creating the CSV for candidates and putting the data in the datawarehouse")
    # CSV
    try:
        path_candidate = os.path.abspath("decoderen/dim_candidate_csv_for_DWH.py")
        process = subprocess.Popen(['python', '-u', path_candidate],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True,
                         bufsize=0)
        while True:
            output = process.stdout.readline()
            if output:
                info_logger.info(output.strip())
            if process.poll() is not None:
                break
        
        error = process.stderr.read()
        if error and not any(warning in error for warning in warnings_to_ignore):
            raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
        
        info_logger.info("DimCandidate.csv created")
    except subprocess.CalledProcessError as cpe:
        raise Exception(f"Something went wrong when creating the CSV for DimCandidate:\n{cpe.stderr}")
    except Exception as e:
        raise Exception(f"Something went wrong when creating the CSV for DimCandidate:\n{e}")

    # Fill
    try:
        info_logger.info("Started filling DimCandidate, could take a while. Please wait.")
        path_candidate = os.path.abspath("DWH/fill_DWH/Candidate_fill.py")
        process = subprocess.Popen(['python', '-u', path_candidate],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         text=True,
                         bufsize=0)
        while True:
            output = process.stdout.readline()
            if output:
                info_logger.info(output.strip())
            if process.poll() is not None:
                break
        
        error = process.stderr.read()
        if error and not any(warning in error for warning in warnings_to_ignore):
            raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
        
        info_logger.info("Filled DimCandidate")
    except subprocess.CalledProcessError as cpe:
        raise Exception(f"Something went wrong when trying to add the data to DimCandidate:\n{cpe.stderr}")
    except Exception as e:
        raise Exception(f"Something went wrong when trying to add the data to DimCandidate:\n{e}")

def run_csv_scripts():
    """
    This function creates all necessary CSVs for each test in the DWH

    Scripts:
        /DEP2-G2/decoderen/FCA_csv_for_DWH.py
        /DEP2-G2/decoderen/SJT_csv_for_DWH.py
        /DEP2-G2/decoderen/PAQ_csv_for_DWH.py
        /DEP2-G2/decoderen/BAQ_csv_for_DWH.py
        /DEP2-G2/decoderen/MDQ_csv_for_DWH.py
    
    Output files:
        /DEP2-G2/decoded_data/FCA/DimCompetence.csv
        /DEP2-G2/decoded_data/FCA/FactTest.csv
        /DEP2-G2/decoded_data/FCA/FactQuestionFCA.csv

        /DEP2-G2/decoded_data/SJT/FactTest.csv
        /DEP2-G2/decoded_data/SJT/FactQuestionSJT.csv

        /DEP2-G2/decoded_data/PAQ/FactTest.csv
        /DEP2-G2/decoded_data/PAQ/FactQuestionPAQ.csv

        /DEP2-G2/decoded_data/BA51/FactTest.csv
        /DEP2-G2/decoded_data/BA51/FactQuestionBAQ.csv

        /DEP2-G2/decoded_data/MDQ/FactTest.csv
        /DEP2-G2/decoded_data/MDQ/FactQuestionMDQ.csv
    """
    info_logger.info("Creating the CSVs that are needed for the anomaly scripts")

    for test in tests_list:
        try:
            path_fca = os.path.abspath(f"decoderen/{test}_csv_for_DWH.py")
            process = subprocess.Popen(['python', '-u', path_fca],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        bufsize=0)
            
            while True:
                output = process.stdout.readline()
                if output:
                    info_logger.info(output.strip())
                if process.poll() is not None:
                    break
            
            error = process.stderr.read()
            if error and not any(warning in error for warning in warnings_to_ignore):
                raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
            
            info_logger.info(f"CSVs for {test} created")
        except subprocess.CalledProcessError as cpe:
            raise Exception(f"Something went wrong when creating one of the CSVs for {test}:\n{cpe.stderr}")
        except Exception as e:
            raise Exception(f"Something went wrong when creating one of the CSVs for {test}:\n{e}")

def run_anomaly_scripts():
    """
    This function runs the scripts for anomaly detection

    Scripts:
        /DEP2-G2/anomalies/FCA_detection.py
        /DEP2-G2/anomalies/SJT_detection.py
        /DEP2-G2/anomalies/PAQ_detection.py
        /DEP2-G2/anomalies/BAQ_detection.py
        /DEP2-G2/anomalies/MDQ_detection.py
    
    Output files:
        /DEP2-G2/decoded_data/FCA/DimTestAnomalies.csv
        /DEP2-G2/decoded_data/FCA/DimQuestionAnomalies.csv
        /DEP2-G2/decoded_data/SJT/DimTestAnomalies.csv
        /DEP2-G2/decoded_data/SJT/DimQuestionAnomalies.csv
        /DEP2-G2/decoded_data/PAQ/DimTestAnomalies.csv
        /DEP2-G2/decoded_data/BA51/DimTestAnomalies.csv
        /DEP2-G2/decoded_data/MDQ/DimTestAnomalies.csv
    """
    info_logger.info("Searching for anomalies")

    for test in tests_list:
        try:
            path_fca = os.path.abspath(f"anomalies/{test}_detection.py")
            process = subprocess.Popen(['python', '-u', path_fca],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             text=True,
                             bufsize=0)
            
            while True:
                output = process.stdout.readline()
                if output:
                    info_logger.info(output.strip())
                if process.poll() is not None:
                    break
            
            error = process.stderr.read()
            if error and not any(warning in error for warning in warnings_to_ignore):
                raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
            
            info_logger.info(f"Found anomalies in {test}")
        except subprocess.CalledProcessError as cpe:
            raise Exception(f"Something went wrong when looking for anomalies in {test}:\n{cpe.stderr}")
        except Exception as e:
            raise Exception(f"Something went wrong when looking for anomalies in {test}:\n{e}")

def run_fill_scripts():
    """
    This function runs the scripts that write the data of each test to the DWH

    Scripts:
        /DEP2-G2/DWH/fill_DWH/FCA_fill.py
        /DEP2-G2/DWH/fill_DWH/SJT_fill.py
        /DEP2-G2/DWH/fill_DWH/PAQ_fill.py
        /DEP2-G2/DWH/fill_DWH/BAQ_fill.py
        /DEP2-G2/DWH/fill_DWH/MDQ_fill.py
    """
    info_logger.info("Filling the datawarehouse")

    for test in tests_list:
        try:
            path_fca = os.path.abspath(f"DWH/fill_DWH/{test}_fill.py")
            process = subprocess.Popen(['python', '-u', path_fca],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            bufsize=0)
            
            while True:
                output = process.stdout.readline()
                if output:
                    info_logger.info(output.strip())
                if process.poll() is not None:
                    break
            
            error = process.stderr.read()
            if error and not any(warning in error for warning in warnings_to_ignore):
                raise subprocess.CalledProcessError(process.returncode, process.args, output, error)
            
            info_logger.info(f"{test} data is now in the correct tables")
        except subprocess.CalledProcessError as cpe:
            raise Exception(f"Something went wrong when trying to add the data from {test} to the datawarehouse:\n{cpe.stderr}")
        except Exception as e:
            raise Exception(f"Something went wrong when trying to add the data from {test} to the datawarehouse:\n{e}")

def run_after_filling():
    """
    Thist funtion runs the script that makes the final changes to the data in the DWH and optimizes the DWH

    Scripts:
        /DEP2-G2/DWH/implement_DWH/run_after_filling_dwh.sql
        /DEP2-G2/DWH/implement_DWH/indexing.sql
    """

    channel = dep2connection("CRH_DWH")
    cursor = channel.cursor()

    info_logger.info("Adding indexes and indexed views")
    try:
        path_index =  os.path.abspath("DWH/implement_DWH/indexing.sql")
        with open(path_index, 'r') as file:
            script = file.read()
            statements = [s.strip() for s in script.split('GO') if s.strip()]
        
        for statement in statements:
            cursor.execute(statement)
        channel.commit()
    except Exception as e:
        raise Exception(f"Something went wrong when adding the indexing:\n{e}")
    
    info_logger.info("Final touches to the DWH")
    path_after_filling = os.path.abspath("DWH/implement_DWH/run_after_filling_dwh.sql")
    try:
        with open(path_after_filling, 'r') as file:
            script = file.read()
            statements = [s.strip() for s in script.split('GO') if s.strip()]
        
        for statement in statements:
            cursor.execute(statement)
        channel.commit()
    except Exception as e:
        raise Exception(f"Something went wrong when running the final file:\n{e}")
    


if __name__ == "__main__":
    try:
        os.makedirs(os.path.abspath("logger"), exist_ok=True)
        info_logger = get_info_logger()
        error_logger = get_error_logger()
        check_and_install_dependencies()
        check_and_create_directories()
        build_datawarehouse()
        add_question_tables()
        run_candidate_scripts()
        run_csv_scripts()
        run_anomaly_scripts()
        run_fill_scripts()
        run_after_filling()
        info_logger.info("All done!")
    except Exception as e:
        error_logger.error(e)
    