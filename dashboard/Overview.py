"""
This is the overview page. It show general data and graphs.

Functions:
    - `func.streamlit.graphs.general`: Contains functions for generating various graphs.
    - `func.streamlit.connection.fromDWH`: Provides functions for retrieving test data from the data warehouse (DWH).
"""

import os
from PIL import Image
import streamlit as st
import pandas as pd
import os
import sys 

root = os.path.abspath(".")
sys.path.append(root)

import func.streamlit.graphs.general as graph
import func.streamlit.connection.fromDWH as DWHdata

# Page configuration
icon = Image.open(os.path.join('dashboard', 'img', 'hudson_rgb_icon-blue-01.png'))

st.set_page_config(
    page_title="Hudson dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon=icon,
)

# Load data

with st.spinner('We are getting your data!'):
    df = DWHdata.get_general_test_data()

# Page lay-out 

header = st.columns((1, 4), gap='medium')
with header[0]:
    logo = Image.open(os.path.join('dashboard','img', 'hudson_rgb_logo-blue-01.png'))
    st.image(logo)

col = st.columns((1, 1, 1, 1), gap='medium')

with col[0]:
    test_list = ['All', 'FCA', 'BAQ', 'SJT', 'PAQ', 'MDQ']
    selected_test = st.selectbox('Select a test', test_list)
with col[1]:
    year_list = sorted(df.Year.unique().tolist())[::-1]
    year_list = ['All'] + year_list 
    selected_year = st.selectbox('Select a year', year_list)

df_selected = df

if selected_test != 'All':
    df_selected = df_selected[df_selected.Test == selected_test]

if selected_year != 'All':
    df_selected = df_selected[df_selected.Year == selected_year]

## display information         
col = st.columns((5, 5, 2), gap='medium')
with col[0]:
    st.markdown(f'#### Gender Distribution for {selected_test}')
    chart = graph.plot_gender_distribution(df_selected)
    st.altair_chart(chart, use_container_width=True) 
with col[1]:
    st.markdown(f'#### Qualification Distribution for {selected_test}')
    chart_qual = graph.plot_qualification_distribution(df_selected)
    st.altair_chart(chart_qual, use_container_width=True)  

st.markdown("##### Number of Anomalies per Qualification")
chart = graph.plot_anomalies_per_qualification(df_selected)
st.altair_chart(chart, use_container_width=True) 

## display counts
col1, col2, col3 = st.columns(3)

test_count = len(df_selected)
candidate_count = len(pd.unique(df_selected['CandidateKey']))

col1.metric("Test count", test_count)
col2.metric("Candidate count", candidate_count)
