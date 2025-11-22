"""
This module can be used to generate graphs for streamlit to visualize the test details. 

This module includes the following functions: 
    * plot_top_answer_patterns: plots the top answer patterns
"""

import altair as alt

def plot_top_answer_patterns(df):
    """This function plots the top answer patterns. 

    Args:
        df (DataFrame): the dataframe containing the answers 

    Returns:
        Chart: the bar chart 
    """    
    # Combine answers into a single column to analyze patterns
    df['AnswerPattern'] = df['AnswerSequence1'].astype(str) + '-' + df['AnswerSequence2'].astype(str) + '-' + df['AnswerSequence3'].astype(str)
    
    # Count the frequency of each pattern and select the top 10
    pattern_counts = df['AnswerPattern'].value_counts().head(10).reset_index()
    pattern_counts.columns = ['AnswerPattern', 'Frequency']

    # Create the Altair bar chart
    chart = alt.Chart(pattern_counts).mark_bar(color='mediumturquoise', stroke='black').encode(
        x=alt.X('AnswerPattern:O', sort='-y', title='Answer Pattern (Answer1-Answer2-Answer3)'),
        y=alt.Y('Frequency:Q', title='Frequency'),
        tooltip=['AnswerPattern', 'Frequency']
    ).properties(
        title='Top 10 Most Common Answer Patterns',
        width=600,
        height=400
    ).configure_axisX(
        labelAngle=45
    )

    return chart
