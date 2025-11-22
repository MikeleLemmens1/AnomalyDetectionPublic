"""
This module includes the following functions: 
    * export_markdown_to_pdf: generates a PDF report for a given candidate's test results based on a Markdown template 
"""

import pandas as pd
import markdown2
import pdfkit
import os
import sys
from io import BytesIO
from dotenv import load_dotenv
import tempfile

load_dotenv()

root = os.path.abspath(".")
sys.path.append(root)


def export_markdown_to_pdf(candidate):
    """
    This function generates a PDF report for a given candidate's test results based on a Markdown template.

    This function processes the test results of a candidate, dynamically fills in a Markdown 
    template with extracted and formatted data, converts the filled Markdown into HTML, and 
    exports the final report as a PDF file.

    Parameters:
        candidate (pd.DataFrame): A DataFrame containing test result details for a candidate. 

    Returns:
        BytesIO: A BytesIO object containing the binary content of the generated PDF.

    Notes:
        - The function assumes that the Markdown template is located at 
          `dashboard/exporteren/exporteer_sjabloon.md`.
        - The PDF generation uses `markdown2` to convert Markdown to HTML and `pdfkit` to 
          generate the PDF.
        - Missing or unavailable data is replaced with default values, and logical flags 
          for anomalies are formatted into human-readable sentences.

    Dependencies:
        - `os`: For file path management.
        - `pandas`: For data manipulation.
        - `markdown2`: For converting Markdown to HTML.
        - `pdfkit`: For generating PDFs from HTML.
        - `tempfile`: For creating temporary files.
        - `BytesIO`: For returning the PDF as an in-memory binary stream.
    """

    with open(os.path.join('dashboard', 'exporteren', 'exporteer_sjabloon.md'), 'r', encoding='utf-8') as file:
        markdown_template = file.read()

    # Extract values from the DataFrame or dictionary
    candidateKey = candidate['CandidateKey'].iloc[0] if not candidate['Test'].empty else 'N/A'
    test = candidate['Test'].iloc[0] if not candidate['Test'].empty else 'N/A'
    date = candidate['Date'].iloc[0] if not candidate['Date'].empty else 'N/A'
    testKey = candidate['TestKey'].iloc[0] if not candidate['TestKey'].empty else 'N/A'
    organisation = candidate['Organisation'].iloc[0] if not candidate['Organisation'].empty else 'N/A'
    chosenLanguage = candidate['ChosenLanguage'].iloc[0] if not candidate['ChosenLanguage'].empty else 'N/A'
    anomalyscore = str(candidate['AnomalyScore'].iloc[0]
                       ) if not candidate['AnomalyScore'].empty else 'N/A'
    isanomaly = int(candidate['IsAnomaly'].iloc[0]
                    ) if not candidate['IsAnomaly'].empty else 'N/A'
    dbscan = candidate['DBSCAN'].iloc[0] if not candidate['DBSCAN'].empty else 0
    copod = candidate['Copod'].iloc[0] if not candidate['Copod'].empty else 0
    ecod = candidate['Ecod'].iloc[0] if not candidate['Ecod'].empty else 0
    iForest = candidate['iForest'].iloc[0] if not candidate['iForest'].empty else 0
    lof = candidate['Lof'].iloc[0] if not candidate['Lof'].empty else 0
    abod = candidate['Abod'].iloc[0] if not candidate['Abod'].empty else 0
    toofast = candidate['TooFast'].iloc[0] if not candidate['TooFast'].empty else 0
    tooslow = candidate['TooSlow'].iloc[0] if not candidate['TooSlow'].empty else 0
    timespent = candidate['TimeSpent'].iloc[0] if not candidate['TimeSpent'].empty else -10
    sameanswer_pr = candidate['SameAnswer'].iloc[0] if not candidate['SameAnswer'].empty else 0
    pyodensemble = candidate['PyodEnsemble'].iloc[0] if not candidate['PyodEnsemble'].empty else 0

    if isanomaly == 1:
        is_it_an_anomaly = f"This test is considered an anomaly. A breakdown can be found below."
    elif float(anomalyscore) > 0:
        is_it_an_anomaly = f"This test isn't considered an anomaly, but has at least one detection algorithm that detected this test as an anomaly."
    else:
        is_it_an_anomaly = f"This test isn't considered an anomaly."

    # DBSCAN
    if dbscan == 1:
        dbscan = str(True)
        dbscan_ww = 'did'
        dbscan_wasnt = ""
    else:
        dbscan = str(False)
        dbscan_ww = "didn't"
        dbscan_wasnt = "wasn't"

    # PYOD ENSEMBLE
    if pyodensemble == 1:
        pyodensemble = str(True)
        pyod_ensemble_sentence="The test has been detected as an anomaly by the ensemble approach, where multiple models collectively decided that this result is anomalous"
    else:
        pyodensemble = str(False)
        pyod_ensemble_sentence="The test has not been detected as an anomaly by the ensemble approach, where the majority of the models did not identify any abnormal behavior."


    # COPOD
    if copod == 1:
        copod = str(True)
    else:
        copod = str(False)

    # ECOD
    if ecod == 1:
        ecod = str(True)
    else:
        ecod = str(False)

    # IFOREST
    if iForest == 1:
        iForest = str(True)
        iForest_sentence = "Your test was easily seperatable by the IForest trees. Which means it was flagged as an anomaly."
    else:
        iForest = str(False)
        iForest_sentence = "our test wasn't as easily seperatable by the IForest trees. Which means it wasn't flagged as an anomaly."

    # LOF
    if lof == 1:
        lof = str(True)
        lof_word = "an anomalous"
    else:
        lof = str(False)
        lof_word = "a normal"

    # ABOD
    if abod == 1:
        abod = str(True)
        abod_word = "an anomalous"
    else:
        abod = str(False)
        abod_word = "a normal"

    # TIME
    if toofast == 1:
        time = str(True)
        time_sentence = "This test was completed significantly faster than the average, and is considered to be too fast."
    elif tooslow == 1:
        time = str(True)
        time_sentence = "This test took significantly longer than the average, and is considered to be too slow."
    else:
        time = str(False)
        time_sentence = "The candidate finished this test in a reasonable amount of time, indicating no anomalies."

    if pd.isna(timespent):
        timespent = "The time of this candidate was not recorded."
        time_sentence = "This candidate could not be tested for this anomaly."
    else:
        timespent = f"The time of this person is {timespent}."

    # SAME ANSWER
    if pd.isna(sameanswer_pr):
        sameanswer = str(False)
        same_answer_precent = f"This was not calculated for this test."
        same_anwser_sentence = "This means this test was not flagged by this anomaly."
    elif sameanswer_pr > 50:
        sameanswer = str(True)
        same_answer_precent = f"Same answer percentage is {sameanswer_pr}%."
        same_anwser_sentence = "This means this test was flagged by this anomaly."
    else:
        sameanswer = str(False)
        same_answer_precent = f"Same answer percentage is {sameanswer_pr}%."
        same_anwser_sentence = "This means this test was not flagged by this anomaly."

    # Voeg de tabel in de Markdown-sjabloon
    ingevulde_markdown = markdown_template.format(
        Test=test,
        Date=date,
        TestKey=testKey,
        Organisation=organisation,
        ChosenLanguage=chosenLanguage,
        AnomalyScore=anomalyscore,
        Is_it_an_anomaly=is_it_an_anomaly,
        Dbscan=dbscan,
        Dbscan_ww=dbscan_ww,
        dbscan_wasnt=dbscan_wasnt,
        COPOD=copod,
        ECOD=ecod,
        IForest=iForest,
        LOF=lof,
        ABOD=abod,
        lof_word=lof_word,
        abod_word=abod_word,
        iForest_sentence=iForest_sentence,
        time=time,
        time_sentence=time_sentence,
        timespent=timespent,
        sameanswer=sameanswer,
        same_answer_precent=same_answer_precent,
        same_anwser_sentence=same_anwser_sentence,
        pyodensemble=pyodensemble,
        pyod_ensemble_sentence=pyod_ensemble_sentence
    )

    try:
        # Convert the filled-in Markdown to HTML
        html_output = f"<style>body {{ font-family: serif; }}</style>" + \
            markdown2.markdown(ingevulde_markdown)
        
        config = pdfkit.configuration(wkhtmltopdf=os.getenv('EXPORTER'))

        # Use a temporary file to save the PDF
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            pdfkit.from_string(html_output, temp_pdf.name, configuration=config)
            temp_pdf.seek(0)
            pdf_content = temp_pdf.read()
        
        return BytesIO(pdf_content)
    
    except  FileNotFoundError as e:
        # Als het sjabloonbestand niet gevonden wordt, vang de fout op
        raise FileNotFoundError(f"Markdown template file not found: {e}")
    except KeyError as e:
        # Als er een probleem is met de DataFrame (bijv. ontbrekende kolommen), vang de fout op
        raise KeyError(f"Missing expected data column: {e}")
    except OSError as e:
        # Als er een OSError is (zoals het niet kunnen vinden van wkhtmltopdf), geef een specifieke foutmelding
        raise KeyError(f"Error generating PDF: {e}. Please ensure wkhtmltopdf is installed correctly.: {e}")
    except Exception as e:
        # Vang andere onverwachte fouten op
        raise Exception(f"An unexpected error occurred: {e}")
