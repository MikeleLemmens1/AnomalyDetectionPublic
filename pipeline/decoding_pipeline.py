import os
import sys
import subprocess

root = os.path.abspath(".")
sys.path.append(root)

from func.logger import get_info_logger, get_error_logger

tests_list = ['FCA', 'SJT', 'PAQ', 'BAQ', 'MDQ']
warnings_to_ignore = ["SettingWithCopyWarning", "UserWarning", "DeprecationWarning"]

def check_and_create_decode_directories():
    """
    This function creates the necessary folders for the decoding
    """
    directories = [
        os.path.abspath("decoderen/raw_data"),
    ]

    for path in directories:
        os.makedirs(path, exist_ok=True)
    
    info_logger.info("Directories for decoded CSVs are created")

def decode_tests():
    """
    This function runs all scripts that decode the tests and puts the decoded data into CSV files

    Scripts:
        /DEP2-G2/decoderen/decodeer_scripts/decoderen_FCA.py
        /DEP2-G2/decoderen/decodeer_scripts/decoderen_SJT.py
        /DEP2-G2/decoderen/decodeer_scripts/decoderen_PAQ.py
        /DEP2-G2/decoderen/decodeer_scripts/decoderen_BAQ.py
        /DEP2-G2/decoderen/decodeer_scripts/decoderen_MDQ.py

    Output files:
        /DEP2-G2/decoderen/raw_data/decoded_fca.csv
        /DEP2-G2/decoderen/raw_data/decoded_sjt.csv
        /DEP2-G2/decoderen/raw_data/decoded_paq.csv
        /DEP2-G2/decoderen/raw_data/decoded_baq.csv
        /DEP2-G2/decoderen/raw_data/decoded_mdq.csv
    """
    for test in tests_list:
        try:
            path = os.path.abspath(f"decoderen/decodeer_scripts/decoderen_{test}.py")
            process = subprocess.Popen(['python', '-u', path],
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
            raise Exception(f"Something went wrong when decoding the data for {test}:\n{cpe.stderr}")
        except Exception as e:
            raise Exception(f"Something went wrong when decoding the data for {test}\n{e}")


if __name__ == "__main__":
    try:
        os.makedirs(os.path.abspath("logger"), exist_ok=True)
        info_logger = get_info_logger()
        error_logger = get_error_logger()
        check_and_create_decode_directories()
        decode_tests()
        info_logger.info("All done!")
    except Exception as e:
        error_logger.error(e)