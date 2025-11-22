"""
This page displays a list of tests based on various filters and anomaly scores.

Functions:
    - `func.streamlit.connection.fromDWH`: Provides functions for retrieving test data from the Data Warehouse (DWH).
"""

import os
from PIL import Image
import streamlit as st
import sys 

root = os.path.abspath(".")
sys.path.append(root)

import func.streamlit.connection.fromDWH as DWHdata

icon = Image.open(os.path.join('dashboard', 'img', 'hudson_rgb_icon-blue-01.png'))

st.set_page_config(
    page_title="Candidate list",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=icon,
)

# Load data
with st.spinner('We are getting your data!'):
    df = DWHdata.get_general_test_data()

# Page lay-out 
## header
header = st.columns((1, 4), gap='medium')
with header[0]:
    logo = Image.open(os.path.join('dashboard', 'img', 'hudson_rgb_logo-blue-01.png'))
    st.image(logo)

## filters
col = st.columns((1, 1, 1, 1), gap='medium')

with col[0]:
    # Selecteer een test
    test_list = ['All', 'FCA', 'SJT', 'BAQ', 'PAQ', 'MDQ']
    selected_test = st.selectbox('Select a test', test_list)
with col[1]:
    # Selecteer een jaar
    year_list = sorted(df.Year.unique().tolist())[::-1]
    year_list = ['All'] + year_list 
    selected_year = st.selectbox('Select a year', year_list)
with col[2]:
    # Selecteer een gender
    gender_list = df.ChosenGender.unique().tolist()[::-1]
    gender_list = ['All'] + gender_list 
    selected_gender = st.selectbox('Select a gender', gender_list)
with col[3]:
    # Anomaly score slider
    start_value, end_value = st.slider(
        "Select an anomaly score",
        min_value=0.0,
        max_value=1.0,
        value=(0.0, 1.0),
        step=0.01  # You can adjust the step size for finer control
    )
    
    anomaly_score = ['All'] + year_list 

col = st.columns((7, 2), gap='large', vertical_alignment="bottom")

with col[0]:
    # anomaly selection
    options = ["DBSCAN","Neighbours", "TooSlow", "TooFast","PyodEnsemble","Copod", "Ecod", "iForest", "Lof", "Abod"]
    selection = st.pills("Detected anomaly by", options, selection_mode="multi")

with col[1]:
    st.markdown(
        """
        <style>
        .custom-toggle {
            position: relative;
            margin-left: 60px;
            margin-top: 100px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    on = st.toggle("Is anomaly")

df_selected = df
if selected_test != 'All':
    df_selected = df_selected[df_selected.Test == selected_test]
if selected_year != 'All': 
    df_selected = df_selected[df_selected.Year == selected_year]
if selected_gender != 'All':
    df_selected = df_selected[df_selected.ChosenGender == selected_gender]

df_selected = df_selected[(df_selected.AnomalyScore >= start_value) & (df_selected.AnomalyScore <= end_value)]
df_selected = df_selected[df_selected[selection].eq(1).all(axis=1)]

if on:
    df_selected = df_selected[df_selected["IsAnomaly"] == 1]

view_df = df_selected[["Test", "TestKey", "CandidateKey", "InstanceID", "Date", "Organisation", "ChosenGender", "AnomalyScore", "IsAnomaly"]]

streamlit_df = st.dataframe(view_df,use_container_width=True,selection_mode='single-row',hide_index=True,on_select="rerun")

if len(streamlit_df.selection.rows)>0:
    selected_row_index = streamlit_df.selection.rows[0]
    st.session_state['test_key'] = view_df.iloc[selected_row_index]['TestKey']
    st.switch_page("pages/Search_Test.py")
