"""
This module can be used to generate graphs for streamlit to visualize the same answers anomalies. 

This module includes the following functions: 
    * plot_same_answers_distribution: plots the distribution of the same answer percentage
    * plot_boolean_pie: plots a boolean pie 
    * plot_categorical_bar: plots the bar chart from a category 
    * plot_percentage_bar: plots a bar chart from a dataset containing percentages
    * plot_percentage_histogram: plots a histogram from a dataset containing percentages
"""

import pandas as pd
import altair as alt

# Per Question


def plot_same_answers_distribution(df, title='Distributie of Same Answer Percentages', bins=20):
    """This function plots the distribution of the same answer percentage. 

    Args:
        df (DataFrame): the dataframe
        title (str, optional): the title that will be given to the graph. Defaults to 'Distributie van Same Answer Percentages'.
        bins (int, optional): the amount of bars on the barchart. Defaults to 20.

    Returns:
        Chart: the bar chart 
    """    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('SameAnswerPercentage:Q', bin=alt.Bin(
            maxbins=bins), title='Same Answer Percentage (%)'),
        y=alt.Y('count():Q', title='Aantal'),
        tooltip=['count():Q']
    ).properties(
        title=title,
        width=400,
        height=300
    )
    return chart


def plot_boolean_pie(df, column_name):
    """This function plots a boolean pie. 

    Args:
        df (DataFrame): the dataframe 
        column_name (str): the column containing boolean values

    Returns:
        Chart: the piechart
    """ 
    value_counts = df[column_name].value_counts()

    pie_data = pd.DataFrame({
        'Category': ['True', 'False'],
        'Count': [value_counts.get(True, 0), value_counts.get(False, 0)]
    })

    pie_data['Percentage'] = pie_data['Count'] / pie_data['Count'].sum() * 100

    chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", scale=alt.Scale(
            domain=['True', 'False'], range=['#1f77b4', '#ff7f0e'])),
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


def plot_categorical_bar(df, column_name):
    """This function plots the bar chart from a category. 
    Args:
        df (DataFrame): the dataframe
        column_name (str): the name from the column containing the category. 

    Returns:
        Chart: the bar chart 
    """    
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(f'{column_name}:N', sort='-y'),
        y='count()',
        color=f'{column_name}:N'
    ).properties(
        title=f'Distribution of {column_name}',
        width=400,
        height=300
    )
    return chart

# Per Test

def plot_percentage_bar(df, column_name):
    """This function plots a bar chart from a dataset containing percentages. 

    Args:
        df (DataFrame): the dataframe
        column_name (str): the name of the column containing the percentages

    Returns:
        Chart: the bar chart 
    """    
    # Create the chart
    chart = alt.Chart(df).mark_bar(color='#ffb3ba', stroke='black').encode(
        x=alt.X(f'{column_name}:Q', bin=alt.Bin(step=5), title='Percentage'),
        y=alt.Y('count():Q', title='Count'),
        tooltip=[
            alt.Tooltip(f'{column_name}:Q', title='Percentage', format='.2f'),
            alt.Tooltip('count():Q', title='Count')
        ]
    ).properties(
        # title=f'Distribution of {column_name}',
        width=400,
        height=300
    )
    return chart


def plot_percentage_histogram(df, column_name, bin_step=5):
    """This function plots a histogram from a dataset containing percentages. 

    Args:
        df (DataFrame): the dataframe
        column_name (str): the name of the column containing the percentages
        bins (int, optional): the amount of bars on the barchart. Defaults to 20.

    Returns:
        Chart: the histogram
    """
    chart = alt.Chart(df).mark_bar(color='#d9b3ff', stroke='black').encode(
        x=alt.X(
            f'{column_name}:Q',
            bin=alt.Bin(step=bin_step),
            # scale=alt.Scale(domain=[0, 100]),
            title='Percentage'
        ),
        y=alt.Y('count():Q', title='Frequency'),
        tooltip=[
            alt.Tooltip(f'{column_name}:Q', title='Percentage', format='.2f'),
            alt.Tooltip('count():Q', title='Frequency')
        ]
    ).properties(
        # title=f'Histogram of {column_name}',
        width=400,
        height=300
    )

    return chart
