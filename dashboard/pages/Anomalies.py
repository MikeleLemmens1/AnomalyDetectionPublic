"""
This is the anomalie page that show the anomlies per test.

Functions:
    - `func.streamlit.connection.fromDWH`: Provides functions for retrieving test data from the Data Warehouse (DWH).
    - `func.streamlit.graphs.general`: Contains functions for generating general graphs, such as gender and qualification distribution.
    - `func.streamlit.graphs.pyod`: Provides functions for generating graphs related to anomaly detection using PyOD.
    - `func.streamlit.graphs.time_spent`: Contains functions for plotting visualizations related to time spent on tests.
    - `func.streamlit.graphs.same_answers`: Includes functions for visualizing patterns in candidates' answers.
    - `func.streamlit.graphs.test_details`: Contains functions for displaying detailed test results and anomalies.
"""

import func.streamlit.graphs.general as graphs_general
import func.streamlit.graphs.pyod as graphs_pyod
import func.streamlit.graphs.time_spent as graphs_timesp
import func.streamlit.graphs.same_answers as graphs_sameans
import func.streamlit.connection.fromDWH as DWHdata
import func.streamlit.graphs.test_details as test_details
import streamlit as st
from PIL import Image
import pandas as pd
import os
import sys

root = os.path.abspath(".")
sys.path.append(root)

CWD = os.getcwd()
icon = Image.open(os.path.join('dashboard', 'img',
                  'hudson_rgb_icon-blue-01.png'))

st.set_page_config(
    page_title="Overview anomaly",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=icon,
)

# Load data
with st.spinner('We are getting your data!'):
    df_tests = DWHdata.get_general_test_data()
    [df_question_fca, df_question_baq, df_question_sjt, df_question_paq,
        df_question_mdq] = DWHdata.get_all_question_data_with_anomaly()
    
    @st.cache_data
    def load_and_merge_data(df_questions, df_test):
        return pd.merge(df_questions, df_test, on=["TestKey"])

# Page lay-out
# header
header = st.columns((1, 4), gap='medium')
with header[0]:
    logo = Image.open(os.path.join('dashboard', 'img',
                      'hudson_rgb_logo-blue-01.png'))
    st.image(logo)

# Filters
col = st.columns((1, 1, 1, 1), gap='medium')
with col[0]:
    test_list = ['FCA', 'BAQ', 'SJT', 'PAQ', 'MDQ']
    selected_test = st.selectbox('Select a test', test_list)

if selected_test == 'FCA':
    with col[1]:

        df_questions = df_question_fca
        df_test = df_tests[df_tests['Test'] == selected_test]

        anomaly_list = ['Select anomaly', 'Same answers', 'Time', 'DBSCAN', 'Pyod ensemble',
                        'Neighbours', 'COPOD', 'ECOD', 'I Forest', 'LOF']

        selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)


elif selected_test == 'BAQ':
    with col[1]:
        anomaly_list = ['Select anomaly', 'Pyod ensemble', 'COPOD',
                        'ECOD', 'I Forest', 'LOF', 'ABOD']
        df_questions = df_question_baq
        df_test = df_tests[df_tests['Test'] == selected_test]
        selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)

elif selected_test == 'SJT':
    with col[1]:
        anomaly_list = ['Select anomaly', 'Same answers',
                        'Time', 'Pyod ensemble', 'COPOD', 'ECOD', 'I Forest', 'LOF']
        selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)
        df_questions = df_question_sjt
        df_test = df_tests[df_tests['Test'] == selected_test]

elif selected_test == 'PAQ':
    with col[1]:
        anomaly_list = ['Select anomaly','Pyod ensemble', 'COPOD',
                        'ECOD', 'I Forest', 'LOF', 'ABOD']
        selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)
        df_questions = df_question_paq
        df_test = df_tests[df_tests['Test'] == selected_test]

elif selected_test == 'MDQ':
    with col[1]:
        anomaly_list = ['Select anomaly',
                        'COPOD', 'ECOD', 'I Forest', 'LOF', 'ABOD']
        selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)
        df_questions = df_question_mdq
        df_test = df_tests[df_tests['Test'] == selected_test]

else:
    st.subheader("Please select a test")

    # elif selected_test == 'All':
    #     anomaly_list = ['Select anomaly', 'Same answers', 'Time']
    #     selected_anomaly = st.selectbox('Select an anomaly', anomaly_list)

if selected_anomaly in ['Same answers', 'Time'] and selected_test in ['FCA', 'SJT']:
    with col[2]:
        test_question_list = ['per test', 'per question']
        test_or_question = st.selectbox('Choose data', test_question_list)

df_alles = df_test

# Apply filters

# Separate data
# df_question_time = df_questions[["QuestionKey", "ItemID","TimeSpent","TooSlow","TooFast"]]
df_test_time = df_tests[["TestKey", "TimeSpent", "TooSlow", "TooFast"]]

df_question_same_ans = df_questions[["QuestionKey", "TestKey", "SameAnswer"]]
df_test_same_ans = df_tests[["TestKey", "SameAnswer"]]


df_view_pyod = df_test[["TestKey", "Date", "CandidateKey",
                        "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]
# Custom graphs and flagged tests

st.subheader(f"{selected_anomaly} in {selected_test} tests")
col = st.columns((5, 7), gap='medium')

if selected_anomaly == 'Same answers':
    if test_or_question == 'per test':
        col = st.columns((5, 10), gap='medium')
        with col[0]:
            st.markdown(f'##### Distribution of same answer')
            chart = graphs_sameans.plot_percentage_bar(
                df_test_same_ans, "SameAnswer")
            st.altair_chart(chart, use_container_width=True)
        with col[1]:
            st.markdown(
                f'##### Histogram of same answer Percentage Distribution')
            chart = graphs_sameans.plot_percentage_histogram(
                df_test_same_ans, "SameAnswer", bin_step=1)
            st.altair_chart(chart, use_container_width=True)

        view_df = df_test[["Test", "TestKey", "CandidateKey",
                           "Date", "Organisation", "ChosenGender", "TimeSpent",
                           "SameAnswer", "AnomalyScore"]]
        view_df = view_df[view_df['SameAnswer'] >= 40]

        df_test = df_test[df_test['SameAnswer'] >= 40]

        st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

        streamlit_df = st.dataframe(view_df,
                                    use_container_width=True,
                                    selection_mode='single-row',
                                    hide_index=True,
                                    on_select="rerun")

        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = df_test_same_ans.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")

    elif test_or_question == 'per question':
        with col[0]:
            st.markdown("""This detection method analyses the answers on subquestions within a question. It simply checks whether the answer to every subquestion is the same, 
                        and if so, detects the 'SameAnswer' anomaly within the question.
                        """)

        with col[1]:
            chart = test_details.plot_top_answer_patterns(df_questions)
            st.altair_chart(chart, use_container_width=True)

        df_test = df_test[["TestKey", "CandidateKey", "Qualification", "Gender", "Date", "Year"]]
        df_test = pd.merge(df_questions, df_test, on=["TestKey"])

        st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")
        df_test = df_test[df_test['SameAnswer'] == 1]
        view_df = df_test[["TestKey","CandidateKey", "Date",'ItemID', "TimeSpent", "AnswerSequence1", "AnswerSequence2", "AnswerSequence3"]]
        streamlit_df = st.dataframe(view_df, use_container_width=True,
                                        selection_mode='single-row', hide_index=True, on_select="rerun")

        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'Time':
    if test_or_question == 'per test':
        with col[0]:
            st.markdown(f'#### Time fast anomaly for {selected_test}')
            chart = graphs_timesp.plot_too_fast_or_slow(df_test_time)
            st.altair_chart(chart, use_container_width=True)
        with col[1]:
            st.markdown(
                f'#### Pie Chart of Time Spent on Test {selected_test}')
            chart = graphs_timesp.plot_time_spent_pie(df_test_time)
            st.altair_chart(chart, use_container_width=True)

        st.markdown(f'#### Distribution of Time Spent on Test {selected_test}')
        chart = graphs_timesp.plot_time_spent_distribution(df_test_time)
        st.altair_chart(chart, use_container_width=True)

        view_df = df_test[["Test", "TestKey", "CandidateKey", "InstanceID",
                           "Date", "Organisation", "ChosenGender",
                           "SameAnswer", "TooFast", "TooSlow", "TimeSpent"]]

        view_df_fast = view_df[view_df['TooFast']]
        view_df_slow = view_df[view_df['TooSlow']]

        df_test = df_test[(df_test["TooFast"] == 1) |
                          (df_test['TooSlow'] == 1)]

        st.subheader("Significantly quickly filled out tests:")
        streamlit_df = st.dataframe(view_df_fast,
                                    use_container_width=True,
                                    selection_mode='single-row',
                                    hide_index=True,
                                    on_select="rerun")
        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")

        st.subheader("Significantly slowly filled out tests:")
        streamlit_df = st.dataframe(view_df_slow,
                                    use_container_width=True,
                                    selection_mode='single-row',
                                    hide_index=True,
                                    on_select="rerun")
        
        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")

    elif test_or_question == 'per question':
        df_test = df_test[["TestKey", "CandidateKey", "Qualification", "Gender", "Date", "Year"]]
        df_test = pd.merge(df_questions, df_test, on=["TestKey"])
        df_alles = df_test

        with col[0]:
            st.markdown("""The time the candidate spent on completing a question is used to first calucate the average and the standard deviation (std).
                        Afterwards every test is checked and tests that took more than the average plus the std are considered significantly slower, while 
                        questiones that took less than the average minus the std are considered significantly faster. 
                        """)
        with col[1]:
            st.markdown(
                f'##### Time Spent anomalies per Question {selected_test}')
            chart = graphs_timesp.plot_time_spent_pie(df_test)
            st.altair_chart(chart, use_container_width=True)

        # st.markdown(
        #     f'#### Distribution of Time Spent on Question {selected_test}')
        # chart = graphs_timesp.plot_time_spent_distribution(df_questions)
        # st.altair_chart(chart, use_container_width=True)

        st.markdown(f'#### Average Time per Item {selected_test}')
        chart = graphs_timesp.plot_avg_time_per_item(df_test)
        st.altair_chart(chart, use_container_width=True)

        
        st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")
        df_test = df_test[(df_test["TooFast"] == 1) |
                          (df_test['TooSlow'] == 1)]
        view_df = df_test[["TestKey","CandidateKey", "Date",'ItemID', "TimeSpent", "AnswerSequence1", "AnswerSequence2", "AnswerSequence3", "TooFast", "TooSlow"]]
        view_df_fast = view_df[view_df['TooFast']]
        view_df_slow = view_df[view_df['TooSlow']]

        st.subheader("Significantly quickly filled out tests:")
        streamlit_df = st.dataframe(view_df_fast,
                                    use_container_width=True,
                                    selection_mode='single-row',
                                    hide_index=True,
                                    on_select="rerun")
        
        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")

        st.subheader("Significantly slowly filled out tests:")
        streamlit_df = st.dataframe(view_df_slow,
                                    use_container_width=True,
                                    selection_mode='single-row',
                                    hide_index=True,
                                    on_select="rerun")

        if len(streamlit_df.selection.rows) > 0:
            selected_row_index = streamlit_df.selection.rows[0]
            st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
            st.switch_page("pages/Search_Test.py")



elif selected_anomaly == 'Pyod ensemble':

    with col[0]:
        st.markdown("""The ensemble is a way to represent consensus of multiple different pyod models on different dataframe types to know wheter an 
                    instance is considered an anomaly or not. Each indiviual decision maker takes out 5% of the tests which it thinks to be strange. Some models may look in its 
                    neighbourhood, others might compare towards the average or cluster center in general, while others may be calculating angles between different points.
                    """)

    with col[1]:
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "PyodEnsemble")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_test[df_test['PyodEnsemble'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'DBSCAN':
    
    with col[0]:

        st.markdown("""DBSCAN is an unsupervised clustering algorithm. Core instances are identified from a complete dataset, which are instances that lie within a certain Euclidean 
                    distance (epsilon=2) from a predefined number of other instances (min_samples=50). Clusters are then formed by grouping all instances that lie within that distance from 
                    at least one of these core instances. A set of core instances can fall within the same cluster. All instances that do not lie within the epsilon distance from a core 
                    instance are considered anomalies
                    """)

    with col[1]:

        chart = graphs_pyod.plot_anomaly_per_year(df_test, "DBSCAN")
        st.altair_chart(chart, use_container_width=True)


    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_test[df_test['DBSCAN'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'Neighbours':
    with col[0]:
        st.markdown("""
            Neighbours looks at nearby results, considering both time (within the hour, two hours) and the sum of the difference in answers (distance(4,4) = 0 + distance(4,4) = 2). 
            This distance is represented using Euclidean distance (via the square root). Therefore, if you are very close (similar answers) to another result within a short time,
            you will score high here.
        """)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")
    df_test = df_test[df_test['Neighbours'] == 1]
    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df,
                                use_container_width=True,
                                selection_mode='single-row',
                                hide_index=True,
                                on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'COPOD':
    # col = st.columns((4, 5, 2), gap='medium')
    with col[0]:
        tekst = '''
            COPOD is a method used to find data points that don't fit with the rest. 
            It works by comparing pairs of data points and looking for those that stand out. 
            This method is good for complex data with lots of dimensions.
            '''
        st.markdown(tekst)

    with col[1]:
        # st.markdown(f'#### Same answer pie chart {selected_test}')
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "Copod")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_tests[df_tests['Copod'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'ECOD':
    with col[0]:
        tekst = '''
            ECOD uses a measure called entropy to find outliers. 
            It checks how much "surprise" there is in the data and identifies points that are unusual. 
            ECOD is useful when the data has a complex structure or when it's hard to predict what normal data should look like.
            '''
        st.markdown(tekst)

    with col[1]:
        # st.markdown(f'#### Same answer pie chart {selected_test}')
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "Ecod")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_tests[df_tests['Ecod'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")


elif selected_anomaly == 'I Forest':
    with col[0]:
        tekst = '''
            Isolation Forest (iForest) works by creating random "trees" to separate data points from each other. 
            The easier it is to separate a point, the more likely it is an outlier. 
            This method is fast and works well for large sets of data, making it great for real-time checks.
            '''
        st.markdown(tekst)

    with col[1]:
        st.markdown(f'#### Same answer pie chart {selected_test}')
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "iForest")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_tests[df_tests['iForest'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'LOF':
    with col[0]:
        tekst = '''
            Local Outlier Factor (LOF) looks at the density of data points in a local area and identifies those that don't match. 
            It's good for finding outliers in data where different parts of the data have different patterns or densities.
            '''
        st.markdown(tekst)

    with col[1]:
        st.markdown(f'#### Same answer pie chart {selected_test}')
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "Lof")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_tests[df_test['Lof'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

elif selected_anomaly == 'ABOD':
    with col[0]:
        tekst = '''
            ABOD (Angle-Based Outlier Detection) finds outliers by looking at the angles between data points and their neighbors. 
            If the angles are unusual compared to the rest of the data, the point is flagged as an outlier. 
            This method works well for complex, multidimensional data and helps identify points that stand out in a unique way. 
            It's great for spotting anomalies that might be missed by simpler distance-based methods.
            '''
        st.markdown(tekst)

    with col[1]:
        st.markdown(f'#### Same answer pie chart {selected_test}')
        chart = graphs_pyod.plot_anomaly_per_year(df_test, "Abod")
        st.altair_chart(chart, use_container_width=True)

    st.subheader(f"{selected_test} tests flagged by {selected_anomaly}")

    df_test = df_test[df_test['Abod'] == 1]

    view_df = df_test[["TestKey", "Date", "CandidateKey",
                       "ChosenLanguage", "Gender", "Qualification", "AnomalyScore"]]

    streamlit_df = st.dataframe(view_df, use_container_width=True,
                                selection_mode='single-row', hide_index=True, on_select="rerun")

    if len(streamlit_df.selection.rows) > 0:
        selected_row_index = streamlit_df.selection.rows[0]
        st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
        st.switch_page("pages/Search_Test.py")

else:
    with col[0]:
        # st.subheader('Please select an anomaly')
        st.info('Please select an anomaly', icon="ℹ️")

# st.subheader(f"Effect of {selected_anomaly} on {selected_test} test results")
if selected_anomaly != 'Select anomaly':
    st.subheader(
        f"Comparison of {selected_anomaly} anomaly within {selected_test} tests")

col = st.columns((1, 1), gap='medium')
if selected_anomaly != 'Select anomaly':
    with col[0]:
        st.caption(f"Qualification distribution for {selected_test}")
        chart = graphs_general.plot_qualification_distribution(df_alles)
        st.altair_chart(chart, use_container_width=True)

    with col[1]:
        st.caption(
            f"Qualification distribution for {selected_test} tests flagged by {selected_anomaly}")
        chart = graphs_general.plot_qualification_distribution(df_test)
        st.altair_chart(chart, use_container_width=True)

    with col[0]:
        st.caption(f"Gender distribution for {selected_test}")
        chart = graphs_general.plot_gender_distribution(df_alles)
        st.altair_chart(chart, use_container_width=True)

    with col[1]:
        st.caption(
            f"Gender distribution for {selected_test} tests flagged by {selected_anomaly}")
        chart = graphs_general.plot_gender_distribution(df_test)
        st.altair_chart(chart, use_container_width=True)

    # del df_test
    # del df_questions

    # import gc
    # gc.collect()
