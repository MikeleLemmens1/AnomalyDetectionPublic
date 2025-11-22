"""
This module can be used to generate graphs for streamlit to visualize the pyod methods. 

This module includes the following functions: 
    * plot_boolean_pie: plots a boolean pie 
    * plot_anomaly_per_year: plots the occurence of the anomaly per year
"""

import altair as alt
import pandas as pd

def plot_boolean_pie(df, column_name):
    """This function plots a boolean pie. 

    Args:
        df (DataFrame): the dataframe 
        column_name (str): the column containing boolean values

    Returns:
        Chart: the piechart
    """   
    # Verander 0 naar False en 1 naar True
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


def plot_anomaly_per_year(df, column_name):
    """This function plots the occurence of the anomaly per year. 

    Args:
        df (DataFrame): the dataframe
        column_name (str): the name of the column that contains the anomaly conclusion

    Returns:
        Chart: the barchart 
    """    
    # Filteren van rijen waar anomaly_score gelijk is aan 1 en groeperen op jaar
    result = df[df[column_name] == 1].groupby('Year').size().reset_index(name='Count')

    # Altair grafiek maken
    chart = alt.Chart(result).mark_bar().encode(
        x=alt.X('Year:O', title='Jaar'),
        y=alt.Y('Count:Q', title='Aantal Rijen'),
        color=alt.Color('Year:O', scale=alt.Scale(scheme='viridis'),
                        legend=None)
    ).properties(
        title='Number of Rows per Year with Anomaly Score = 1',
        width=600,
        height=400
    )

    return chart
