"""
This is the search candidate page. On this page you can search a canidate by candidateId.

Functions:
    - `func.streamlit.connection.fromDWH`: Provides functions for retrieving test data from the Data Warehouse (DWH).
    - `func.streamlit.exporteren.export_candidate`: Provides a function so you can export a candidate to pdf.
"""

import func.LLM as llm
import func.streamlit.connection.fromDWH as DWHdata
import func.streamlit.exporteren.export_candidate as exp
import os
from PIL import Image
import streamlit as st
import pandas as pd
import sys
from dotenv import load_dotenv
import time

root = os.path.abspath(".")
sys.path.append(root)


icon = Image.open(os.path.join('dashboard', 'img',
                  'hudson_rgb_icon-blue-01.png'))

st.set_page_config(
    page_title="Specific candidate",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=icon,
)

# Load data
with st.spinner('We are getting your candidates data!'):
    df = DWHdata.get_general_test_data()
    [df_question_fca, df_question_baq, df_question_sjt, df_question_paq,
        df_question_mdq] = DWHdata.get_all_question_data_with_anomaly()

# Page lay-out
header = st.columns((1, 4), gap='medium')
with header[0]:
    logo = Image.open(os.path.join('dashboard', 'img',
                      'hudson_rgb_logo-blue-01.png'))
    st.image(logo)

col = st.columns((4, 1), gap='medium')

with col[0]:
    title_placeholder = st.empty()

    with title_placeholder:
        st.title("Search Candidate Key")

search_bar = st.empty()

# Session state
if 'candidate_key' in st.session_state:
    candidate_key = st.session_state['candidate_key']
else:
    candidate_key = None

if candidate_key is None:
    candidate_key = search_bar.text_input(
        'Search on candidate key', key="klein_scherm")
else:
    candidate_key = candidate_key

with col[1]:
    back_button = st.button("Search new candidate", key='back')

if back_button and 'candidate_key' in st.session_state:
    # Reset the session state for candidate_key
    st.session_state.pop('candidate_key', None)
    st.rerun()

if candidate_key and not back_button:

    search_bar.empty()
    title_placeholder.empty()

    with col[0]:
        st.title(f'Candidate Key: {candidate_key}')

    try:
        selected_candidate = df[(df.CandidateKey == int(candidate_key))]

        fca_test = selected_candidate[selected_candidate.Test == 'FCA']
        sjt_test = selected_candidate[selected_candidate.Test == 'SJT']

        # Voorbeeld data dictionary
        data = {
            "Label": [
                "Test type",
                "Created on",
                "Test",
                "Organisation",
                "Language",
                "Anomaly Score"
            ],
            "Waarde": [
                [str(selected_candidate['Test'].values[0])][0],
                [str(selected_candidate['Date'].values[0])][0],
                [str(selected_candidate['TestKey'].values[0])][0],
                [str(selected_candidate['Organisation'].values[0])][0],
                [str(selected_candidate['ChosenLanguage'].values[0])][0],
                [str(selected_candidate['AnomalyScore'].values[0])][0],
            ]
        }

        # Maak een DataFrame van de data
        df_info = pd.DataFrame(data)
        st.table(df_info)

        # ANOMALIES
        st.subheader("Test Anomaly Detection", divider="gray")

        st.markdown("#### Per Test")

        view_df = selected_candidate[['SameAnswer', "TooSlow", "TooFast", "DBSCAN",
                                      "Neighbours", "PyodEnsemble", "Copod", "Ecod", "iForest", "Lof", "Abod", "AnomalyScore", "IsAnomaly"]]
        st.dataframe(view_df)

        def render_detection_message(label, description):
            """
            Renders a markdown message for detected anomalies with the provided label and description.

            Args:
                label (str): The name of the detected anomaly (e.g., "TooSlow", "TooFast").
                description (str): A detailed explanation of the detected anomaly and its implications.
            """
            body = f"""
            ##### {label}: DETECTED

            {description}
            """
            st.markdown(body)

        # Controle en rendering
        if selected_candidate.TooSlow is not None and not pd.isna(selected_candidate.TooSlow.iloc[0]) and int(selected_candidate.TooSlow.iloc[0]) == 1:
            expl = """
            The time the candidate spent on completing the entire test is used to first calucate the average and the standard deviation (std). Afterwards every test is checked and 
            tests that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
            significantly faster. 
            """
            render_detection_message(
                "TooSlow", expl)

        if selected_candidate.TooFast is not None and not pd.isna(selected_candidate.TooFast.iloc[0]) and int(selected_candidate.TooFast.iloc[0]) == 1:
            expl = """
            The time the candidate spent on completing the entire test is used to first calucate the average and the standard deviation (std). Afterwards every test is checked and 
            tests that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
            significantly faster. 
            """
            render_detection_message(
                "TooFast", expl)

        if selected_candidate.SameAnswer is not None and not pd.isna(selected_candidate.SameAnswer.iloc[0]) and int(selected_candidate.SameAnswer.iloc[0]) == 1:
            expl = """
            This detection method first determines which answer was given most often within the test. It then calculates the percentage of answers that correspond to the most 
            frequently given answer and saves this value as 'SameAnswerPercentage'. If the percentage is any higher than 50% the test is flagged as an anomaly. 
            """
            render_detection_message(
                "SameAnswer", expl)

        if selected_candidate.DBSCAN is not None and not pd.isna(selected_candidate.DBSCAN.iloc[0]) and int(selected_candidate.DBSCAN.iloc[0]) == 1:
            expl = """
            DBSCAN is an unsupervised clustering algorithm. It starts with identifying core instances first, which are instances that are located within a certain euclidian distance 
            from other instances. The amount of other instances it needs to have within this distance is set before training this model. When these instances are marked, clusters are 
            formed by gathering all instances (even other core instances) that lie within a preset distance of a core instance in a cluster. Overlapping clusters are merged into one. 
            When this is done for all core instances, the majority of non-core instances will be allocated to a cluster. All those that are not allocated are considered to be an anomaly.
            """
            render_detection_message(
                "DBSCAN", expl)

        if selected_candidate.Neighbours is not None and not pd.isna(selected_candidate.Neighbours.iloc[0]) and int(selected_candidate.Neighbours.iloc[0]) == 1:
            expl = """
            K Nearest Neighbours measures the distance between data points. "K" is a preset integer that this model will take as a parameter, which represents the amount of closest 
            neighbouring instances that will be used to calculate a total distance measure per instance. The instances that have a large average distance to it's neighbours are considered 
            less normal. This way, a ranking can be made to identify the most abnormal instances (and label them as anomalies).
            """
            render_detection_message(
                "Neighbours", expl)
        
        if selected_candidate.PyodEnsemble is not None and not pd.isna(selected_candidate.PyodEnsemble.iloc[0]) and int(selected_candidate.PyodEnsemble.iloc[0]) == 1:
            expl = """
            The ensemble is a way to represent consensus of multiple different pyod models on different dataframe types to know wheter an instance is considered an anomaly or not. 
            Each indiviual decision maker takes out 5% of the tests which it thinks to be strange. Some models may look in its neighbourhood, others might compare towards the 
            average or cluster center in general, while others may be calculating angles between different points.
            """
            render_detection_message(
                "Pyod Ensemble", expl)

        if selected_candidate.Copod is not None and not pd.isna(selected_candidate.Copod.iloc[0]) and int(selected_candidate.Copod.iloc[0]) == 1:
            expl = """
            COPOD is a method that looks at how data points relate to each other to find unusual patterns. It works by checking how likely it is for each data point to fit with the rest. 
            If a data point is very unlikely compared to the others, COPOD flags it as an anomaly. This means the flagged point behaves very differently from what is normal in the dataset.
            In simple terms, this point stands out because it doesn't follow the same pattern as most of the data.
            """
            render_detection_message("Copod", expl)

        if selected_candidate.Ecod is not None and not pd.isna(selected_candidate.Ecod.iloc[0]) and int(selected_candidate.Ecod.iloc[0]) == 1:
            expl = """
            ECOD (Empirical Cumulative Outlier Detection) is a method that finds unusual data points by comparing how each point ranks among all the others. It looks at each feature 
            separately and checks how extreme a point is compared to the rest of the data. If a point is very different in one or more features, 
            ECOD marks it as an anomaly. This means the flagged point doesn't fit the usual patterns found in the data. In simple terms, it's like spotting something that's 
            far off from the rest when looking at each characteristic individually.
            """
            render_detection_message("Ecod", expl)

        if selected_candidate.iForest is not None and not pd.isna(selected_candidate.iForest.iloc[0]) and int(selected_candidate.iForest.iloc[0]) == 1:
            expl = """
            iForest (Isolation Forest) is a method that finds anomalies by isolating data points. It works by randomly splitting the data and checking how quickly each point can
            be separated from the rest. Points that are isolated faster are flagged as anomalies because they behave differently from most of the data. 
            This means the flagged points stand out because they don't fit in with the usual groups or patterns. In simple terms, iForest spots outliers by seeing which 
            points are easiest to separate from the rest.
            """
            render_detection_message(
                "iForest", expl)

        if selected_candidate.Lof is not None and not pd.isna(selected_candidate.Lof.iloc[0]) and int(selected_candidate.Lof.iloc[0]) == 1:
            expl = """
            LOF (Local Outlier Factor) is a method that finds anomalies by looking at how close a data point is to its neighbors. It compares the density of points around each data 
            point with the density of its neighbors. If a point is in a much less dense area than the points around it, LOF flags it as an anomaly. This means 
            the flagged point doesn't fit because it's far from where similar points are grouped. In simple terms, LOF spots outliers by finding points that are isolated 
            compared to their surroundings.
            """
            render_detection_message("Lof", expl)

        if selected_candidate.Abod is not None and not pd.isna(selected_candidate.Abod.iloc[0]) and int(selected_candidate.Abod.iloc[0]) == 1:
            expl = """
            ABOD (Angle-Based Outlier Detection) is a method that identifies anomalies by looking at the angles between data points. It compares the angle formed between 
            a point and its neighbors to see if it's significantly different from the others. If a point creates unusual angles with its neighbors, it is flagged as an anomaly. 
            This means the point behaves differently in relation to others in the dataset. In simple terms, ABOD detects outliers by finding points that don't align well 
            with the pattern formed by nearby points.
            """
            render_detection_message(
                "Abod", expl)

        if [str(selected_candidate['Test'].values[0])][0] == 'FCA':
            df_question = df_question_fca[(
                df_question_fca.TestKey == int(selected_candidate.TestKey))]

            if not df_question.empty:

                st.markdown("#### Per Question")
                view_df = df_question[['ItemID', 'SameAnswer', "TooSlow", "TooFast",
                                       "AnswerSequence1", "AnswerSequence2", "AnswerSequence3"]]
                st.dataframe(view_df)

                if df_question.TooSlow is not None and not pd.isna(df_question.TooSlow.iloc[0]) and int(df_question.TooSlow.iloc[0]) == 1:
                    expl="""
                    The time the candidate spent on completing a question is used to first calucate the average and the standard deviation (std). Afterwards every question is checked and 
                    questions that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
                    significantly faster.
                    """
                    render_detection_message(
                        "TooSlow", expl)

                if df_question.TooFast is not None and not pd.isna(df_question.TooFast.iloc[0]) and int(df_question.TooFast.iloc[0]) == 1:
                    expl="""
                    The time the candidate spent on completing a question is used to first calucate the average and the standard deviation (std). Afterwards every question is checked and 
                    questions that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
                    significantly faster.
                    """
                    render_detection_message(
                        "TooFast", expl)

                if df_question.SameAnswer is not None and not pd.isna(df_question.SameAnswer.iloc[0]) and int(df_question.SameAnswer.iloc[0]) == 1:
                    expl="""
                    This detection method first determines which answer was given most often within the test. It then calculates the percentage of answers that correspond to the most 
                    frequently given answer and saves this value as 'SameAnswerPercentage'. If the percentage is any higher than 50% the test is flagged as an anomaly.
                    """
                    render_detection_message(
                        "SameAnswer", expl)

        elif [str(selected_candidate['Test'].values[0])][0] == 'SJT':
            df_question = df_question_sjt[(
                df_question_sjt.TestKey == int(selected_candidate.TestKey))]

            if not df_question.empty:

                st.markdown("#### Per Question")
                view_df = df_question[['ItemID', 'SameAnswer', "TooSlow", "TooFast",
                                       "AnswerSequence1", "AnswerSequence2", "AnswerSequence3"]]
                st.dataframe(view_df)

                if df_question.TooSlow is not None and not pd.isna(df_question.TooSlow.iloc[0]) and int(df_question.TooSlow.iloc[0]) == 1:
                    expl="""
                    The time the candidate spent on completing a question is used to first calucate the average and the standard deviation (std). Afterwards every question is checked and 
                    questions that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
                    significantly faster.
                    """
                    render_detection_message(
                        "TooSlow", expl)

                if df_question.TooFast is not None and not pd.isna(df_question.TooFast.iloc[0]) and int(df_question.TooFast.iloc[0]) == 1:
                    expl="""
                    The time the candidate spent on completing a question is used to first calucate the average and the standard deviation (std). Afterwards every question is checked and 
                    questions that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered 
                    significantly faster.
                    """
                    render_detection_message(
                        "TooFast", expl)

                if df_question.SameAnswer is not None and not pd.isna(df_question.SameAnswer.iloc[0]) and int(df_question.SameAnswer.iloc[0]) == 1:
                    expl="""
                    This detection method first determines which answer was given most often within the test. It then calculates the percentage of answers that correspond to the most 
                    frequently given answer and saves this value as 'SameAnswerPercentage'. If the percentage is any higher than 50% the test is flagged as an anomaly.
                    """
                    render_detection_message(
                        "SameAnswer", expl)
        st.subheader("AI-generated overview", divider="gray")

        st.warning('Warning: this overview is generated using a large language model and can never be guaranteed to only give correct information. Make sure to proof-read all information in the overview, before sharing with clients.', icon="⚠️")


        def stream_data(tekst):
            """
            This function streams text word by word with a small delay between each word, simulating a typing effect.

            Args:
                tekst (str): The text to stream, split into words.

            Yields:
                str: Each word in the input text with a delay.
            """
            for word in tekst.split(" "):
                yield word + " "
                time.sleep(0.05)

        button_llm = st.empty()
        if button_llm.button("Generate overview"):
            # Clear the button
            button_llm.empty()

            load_dotenv()
            HF_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

            dict = selected_candidate.to_dict(orient='records')[0]
            result = llm.get_summary_from_dict(dict, HF_TOKEN)
            st.write_stream(stream_data(result))

        st.subheader("Export", divider="gray")

        
        # Generate the PDF
        pdf_bytes = exp.export_markdown_to_pdf(selected_candidate)

        # Bied de PDF aan als downloadbaar bestand
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"candidate_{candidate_key}.pdf",
            mime="application/pdf"
            )

    except KeyError as k:
        st.error(f"Error generating PDF. Please ensure wkhtmltopdf is installed correctly.", icon="🚨")

    except Exception as e:
        # Toon een generieke foutmelding
        st.error(
            "Invalid candidate ID. Please check your input and try again.", icon="🚨")
