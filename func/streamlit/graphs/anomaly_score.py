"""
This module can be used to generate graphs for streamlit to visualizing the anomaly score. 

This module includes the following functions: 
    * plot_boolean_pie: plots a boolean pie
    * plot_score_barchart: plots a barchart based on the anomaly score
"""

import pandas as pd
import altair as alt
import numpy as np

def plot_boolean_pie(df, column_name):
    """This function plots a boolean pie. 

    Args:
        df (DataFrame): the dataframe 
        column_name (str): the column containing boolean values

    Returns:
        Chart: the piechart
    """    
    df[column_name] = df[column_name].apply(lambda x: False if x == 0 else True)
    
    value_counts = df[column_name].value_counts()
    
    pie_data = pd.DataFrame({
        'Category': ['False', 'True'],
        'Count': [value_counts.get(False, 0), value_counts.get(True, 0)]
    })

    pie_data['Percentage'] = pie_data['Count'] / pie_data['Count'].sum() * 100

    chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(domain=['True', 'False'], range=['#1f77b4', '#ff7f0e'])),
        tooltip=[
            alt.Tooltip("Category:N"),
            alt.Tooltip("Count:Q"),
            alt.Tooltip("Percentage:Q", format=".1f")
        ]
    ).properties(
        width=400,
        height=400
    )

    return chart

def plot_score_barchart(df):
    """This function plots a barchart based on the anomaly score. 

    Args:
        df (Dataframe): the dataframe

    Returns:
        Chart: the barchart
    """    
    # Waarden groeperen in bereiken
    bin_edges = np.arange(0, 0.61, 0.15)  # Bepaal de intervallen (bijv. 0-0.2, 0.2-0.4, ...)
    df['range'] = pd.cut(df['anomaly_score'], bins=bin_edges)

    # Groeperen op bereik en frequentie tellen
    binned_data = df['range'].value_counts().reset_index()
    binned_data.columns = ['range', 'count']
    binned_data['range'] = binned_data['range'].astype(str)  # Naar string voor Altair

    # Staafdiagram met Altair
    chart = alt.Chart(binned_data).mark_bar().encode(
        alt.X('range:O', title='Anomaly Score Range', sort=None),
        alt.Y('count:Q', title='Frequency'),
        tooltip=['range', 'count']
    ).properties(
        title="Frequency of Anomaly Scores by Range"
    )
    return chart