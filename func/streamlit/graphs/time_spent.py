"""
This module can be used to generate graphs for streamlit to visualize the time spent anomalies. 

This module includes the following functions: 
    * plot_time_spent_distribution: plots the distribution of the time spent percentage
    * plot_avg_time_per_item: plots the average time spent per item
    * plot_too_fast_or_slow: 
    * plot_time_spent_pie: plots a pie chart of the time spent anomaly catagories (Normal, TooFast, TooSlow)
"""

import pandas as pd
import altair as alt


def plot_time_spent_distribution(df):
    """This function plots the distribution of the time spent percentage. 

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the bar chart 
    """
    # Basis histogram voor de TimeSpent-kolom
    histogram = alt.Chart(df).mark_bar(color='skyblue', stroke='black').encode(
        x=alt.X('TimeSpent:Q', bin=alt.Bin(maxbins=100), title='Time Spent (seconds)'),
        y=alt.Y('count()', title='Frequency')
    )

    # Density plot overlay
    density = alt.Chart(df).transform_density(
        'TimeSpent',
        as_=['TimeSpent', 'density'],
    ).mark_area(color='black', opacity=0.3).encode(
        x='TimeSpent:Q',
        y='density:Q'
    )

    # Berekening van mean en median
    mean_time = df['TimeSpent'].mean()
    median_time = df['TimeSpent'].median()

    # Verticale lijn voor het gemiddelde
    mean_line = alt.Chart(pd.DataFrame({'TimeSpent': [mean_time]})).mark_rule(color='red', strokeDash=[5,5]).encode(
        x='TimeSpent:Q'
    )
    

    # Verticale lijn voor de mediaan
    median_line = alt.Chart(pd.DataFrame({'TimeSpent': [median_time]})).mark_rule(color='green', strokeDash=[5,5]).encode(
        x='TimeSpent:Q'
    )

    # Annotaties voor de gemiddelde en mediane waarden
    mean_text = mean_line.mark_text(
        align='left', baseline='middle', dx=5, color='red'
    ).encode(text=alt.value(f'Mean: {mean_time:.2f}'))

    median_text = median_line.mark_text(
        align='left', baseline='middle', dx=5, color='green'
    ).encode(text=alt.value(f'Median: {median_time:.2f}'))

    # Combineer alle lagen
    chart = (histogram + density + mean_line + median_line + mean_text + median_text).properties(
        width=600,
        height=300
    )

    return chart

def plot_avg_time_per_item(df):
    """This function plots the average time spent per item. 

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the bar chart
    """    
    avg_time_per_item = df.groupby('ItemID')['TimeSpent'].mean().sort_values(ascending=False).reset_index()
    chart = alt.Chart(avg_time_per_item).mark_bar(color='skyblue', stroke='black').encode(
        y=alt.X('TimeSpent:Q', title='Average Time Spent (seconds)'),
        x=alt.Y('ItemID:O', sort='-x', title='Item ID'),
        tooltip=['ItemID', 'TimeSpent']
    ).properties(
        width=800,
        height=400
    )

    return chart

def plot_too_fast_or_slow(df):
    """Plots a bar chart of the time spent anomaly catagories (Normal, TooFast, TooSlow). 

    Args:
        df (DataFrame): the dataframe 
    
    Returns:
        Chart: the bar chart 
    """    
    def categorize_speed(row):
        if row['TooFast']:
            return 'Too Fast'
        elif row['TooSlow']:
            return 'Too Slow'
        else:
            return 'Normal Range'

    df['TimeCategory'] = df.apply(categorize_speed, axis=1)

    df['TimeCategory'] = pd.Categorical(df['TimeCategory'], 
                                        categories=['Too Slow', 'Normal Range', 'Too Fast'], 
                                        ordered=True)
    

    return alt.Chart(df).mark_bar().encode(
        x='TimeCategory',
        y='count()',
        color='TimeCategory'
    ).properties(
        # title='Time Spent Category'
    )

def plot_time_spent_pie(df):
    """This function plots a pie chart of the time spent anomaly catagories (Normal, TooFast, TooSlow). 

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the pie chart 
    """    
    # Calculate counts
    too_slow_count = df['TooSlow'].sum()
    too_fast_count = df['TooFast'].sum()
    normal_count = len(df) - too_slow_count - too_fast_count

    # Create a DataFrame for the pie chart data
    pie_data = pd.DataFrame({
        'Category': ['Too Slow', 'Too Fast', 'Normal'],
        'Count': [too_slow_count, too_fast_count, normal_count]
    })
    # Calculate percentages
    pie_data['Percentage'] = pie_data['Count'] / pie_data['Count'].sum() * 100
    # Create the pie chart using Altair
    chart = alt.Chart(pie_data).mark_arc().encode(
        theta=alt.Theta(field="Count", type="quantitative"),
        color=alt.Color(field="Category", type="nominal", 
                    scale=alt.Scale(domain=["Too Slow", "Too Fast", "Normal"], 
                                    range=["skyblue", "cornflowerblue", "deepskyblue"])),
        tooltip=[
            alt.Tooltip("Category:N"),
            alt.Tooltip("Count:Q"),
            alt.Tooltip("Percentage:Q", format=".1f")
        ]
    ).properties(
        width=300,
        height=300
    )

    return chart
