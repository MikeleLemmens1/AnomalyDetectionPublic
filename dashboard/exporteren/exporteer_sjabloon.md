# Hudson anomalies

## General information

**Test type**: {Test}  
**Created on**: {Date}  
**TestKey**: {TestKey}  
**Organisation**: {Organisation}  
**Language**: {ChosenLanguage}  
**Anomaly Score**: {AnomalyScore}

## Test Anomaly Detection

- {Is_it_an_anomaly}

### DBscan ({Dbscan})

DBSCAN is an unsupervised clustering algorithm. From a complete dataset, core instances are searched, which are instances that lie within a certain euclidean distance (epsilon=2) from defined number of other instances (min_samples=50). Clusters are then formed by grouping all instances that lie within that distance from at least one of these core instances. A collection of core instances can fall within the same cluster. All instances that do not lie within the distance epsilon of a core instance are considered anomalous

DBscan {Dbscan_ww} detect this anomaly, meaning it {dbscan_wasnt} clusterd in any nearby group.

## Pyod Ensemble ({pyodensemble})

The ensemble is a way to represent consensus of multiple different pyod models on different dataframe types to know wheter an instance is considered an anomaly or not. Each indiviual decision maker takes out 5% of the tests which it thinks to be strange. Some models may look in its neighbourhood, others might compare towards the average or cluster center in general, while others may be calculating angles between different points.

{pyod_ensemble_sentence}

## Pyod COPOD ({COPOD})

COPOD is a method used to find data points that don't fit with the rest.
It works by comparing pairs of data points and looking for those that stand out.
This method is good for complex data with lots of dimensions.

## Pyod ECOD ({ECOD})

ECOD uses a measure called entropy to find outliers.
It checks how much "surprise" there is in the data and identifies points that are unusual.
ECOD is useful when the data has a complex structure or when it's hard to predict what normal data should look like....

## Pyod IForest ({IForest})

Isolation Forest (iForest) works by creating random "trees" to separate data points from each other.
The easier it is to separate a point, the more likely it is an outlier.
This method is fast and works well for large sets of data, making it great for real-time checks.

{iForest_sentence}

## Pyod LOF ({LOF})

Local Outlier Factor (LOF) looks at the density of data points in a local area and identifies those that don't match.
It's good for finding outliers in data where different parts of the data have different patterns or densities.

In a local neighbourhood, this test was considered {lof_word} test.

## Pyod ABOD ({ABOD})

ABOD (Angle-Based Outlier Detection) finds outliers by looking at the angles between data points and their neighbors.
If the angles are unusual compared to the rest of the data, the point is flagged as an outlier.
This method works well for complex, multidimensional data and helps identify points that stand out in a unique way.
It's great for spotting anomalies that might be missed by simpler distance-based methods.

By comparing the angels, this test was considered {abod_word} test.

## Time ({time})

The time the candidate spent on completing the entire test is used to first calucate the average and the standard deviation (std). Afterwards every test is checked and tests that took more than the average plus the std are considered significantly slower, while tests that took less than the average minus the std are considered significantly faster.

{timespent} {time_sentence}

## Same answer ({sameanswer})

This detection method first determines which answer was given most often within the test. It then calculates the percentage of answers that correspond to the most frequently given answer and saves this value as 'SameAnswerPercentage'. If the percentage is any higher than 50% the test is flagged as an anomaly.

{same_answer_precent} {same_anwser_sentence}
