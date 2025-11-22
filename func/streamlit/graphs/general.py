"""
This module can be used to generate graphs for streamlit. 

This module includes the following functions: 
    * plot_gender_distribution: plots the gender distribution
    * plot_qualification_distribution: plots the qualification distribution
    * plot_anomalies_per_qualification: plots the amount of anomalies per qualification
"""

import pandas as pd
import altair as alt

def plot_gender_distribution(df):
    """This function plots the gender distribution.

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the barchart
    """    
    gender_count = {
        'Female': df[df['Gender'] == 'Gender_Female']['Year'].count(),
        'Male': df[df['Gender'] == 'Gender_Male']['Year'].count(),
        'Other': df[df['Gender'] == 'Gender_Unknown']['Year'].count()
    }

    gender_df = pd.DataFrame({
        'Gender': list(gender_count.keys()),
        'Count': list(gender_count.values())
    })

    # What does Gender:O mean?
    chart = alt.Chart(gender_df).mark_bar(color='#ffb3ba', stroke='black').encode(
        x=alt.X('Gender:O', title='Gender'),
        y=alt.Y('Count:Q', title='Number of Participants'),
        color=alt.Color('Gender:N', scale=alt.Scale(domain=['Female', 'Male', 'Other'],
                                                    range=['#aec6cf', '#b2f2bb', '#fff9b0']),
                        legend=None
                        ),
        tooltip=['Gender', 'Count']
    ).properties(
        # title=f'Number of Participants per Gender in {year}',
        width=400,
        height=300
    )

    return chart


def plot_qualification_distribution(df):
    """This function plots the qualification distribution.

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the barchart
    """     
    qualification_count = {
        'Vocational': df[df['Qualification'] == 'Qualification_Vocational']['Year'].count(),
        'Secondary': df[df['Qualification'] == 'Qualification_Secondary']['Year'].count(),
        'PostGraduate': df[df['Qualification'] == 'Qualification_PostGraduate']['Year'].count(),
        'Professional': df[df['Qualification'] == 'Qualification_Professional']['Year'].count(),
        'Bachelor': df[df['Qualification'] == 'Qualification_Bachelor']['Year'].count(),
        'Master': df[df['Qualification'] == 'Qualification_Master']['Year'].count(),
        'PHD': df[df['Qualification'] == 'Qualification_PHD']['Year'].count(),
        'MBA': df[df['Qualification'] == 'Qualification_MBA']['Year'].count(),
    }

    qual_df = pd.DataFrame({
        'Qualification': list(qualification_count.keys()),
        'Count': list(qualification_count.values())
    })

    chart = alt.Chart(qual_df).mark_bar(color='#ffb3ba', stroke='black').encode(
        x=alt.X('Qualification:O', title='Qualification'),
        y=alt.Y('Count:Q', title='Number of Participants'),
        tooltip=['Qualification', 'Count']
    ).properties(
        width=400,
        height=300
    )

    return chart


def plot_anomalies_per_qualification(df):
    """This function plots the amount of anomalies per qualification.

    Args:
        df (DataFrame): the dataframe

    Returns:
        Chart: the barchart
    """

    anomaly_count = {
        'Vocational': df[(df['Qualification'] == 'Qualification_Vocational') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'Secondary': df[(df['Qualification'] == 'Qualification_Secondary') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'PostGraduate': df[(df['Qualification'] == 'Qualification_PostGraduate') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'Professional': df[(df['Qualification'] == 'Qualification_Professional') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'Bachelor': df[(df['Qualification'] == 'Qualification_Bachelor') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'Master': df[(df['Qualification'] == 'Qualification_Master') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'PHD': df[(df['Qualification'] == 'Qualification_PHD') & (df['IsAnomaly'] == 1)]['Year'].count(),
        'MBA': df[(df['Qualification'] == 'Qualification_MBA') & (df['IsAnomaly'] == 1)]['Year'].count(),
    }

    anomaly_df = pd.DataFrame({
        'Qualification': list(anomaly_count.keys()),
        'Count': list(anomaly_count.values())
    })

    chart = alt.Chart(anomaly_df).mark_bar(color='#d9b3ff', stroke='black').encode(
        x=alt.X('Qualification:O', title='Qualification'),
        y=alt.Y('Count:Q', title='Number of Anomalies'),
        tooltip=['Qualification', 'Count']
    ).properties(
        # title=f'Number of Anomalies per Qualification in {year}',
        width=400,
        height=300
    )

    return chart
