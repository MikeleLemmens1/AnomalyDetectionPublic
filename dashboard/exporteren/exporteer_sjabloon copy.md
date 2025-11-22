# Hudson anomalies

![img](img/logo.jpg) Hudsons personality tests.

## General information

| **Label**    | **Waarde**       |
| ------------ | ---------------- |
| Test type    | {Test}           |
| Created on   | {Date}           |
| TestKey      | {TestKey}        |
| Organisation | {Organisation}   |
| Language     | {ChosenLanguage} |

## Test Anomaly Detection

Chose between

{is_it_an_anomaly}

- This test is considered an anomaly. : {**merge_statistical_percentiles**}. A breakdown can be found below.
- This test isn't considered an anomaly, but has at least one detection algorithm that detected this test as an anomaly.
- This test isn't considered an anomaly

TODO : tabel, maar dan wel gedraaid. (aangezien één test)
![Merge](img/exporteer_sjabloon_anomaly_merge.png)

### Time spent {Timespent}

> The average time spent by candidates on this test is {avg_hours} hours {avg_minutes} minutes {avg_seconds}. This candidate spent {timespent_hours} hours {timespent_minutes} minutes {timespent_seconds} seconds on this test."

If too slow: The test is classified as too slow. This means the test spend more time on the test than the average plus the standard deviation

If too fast: The test is classified as too fast. This means the candidate spend less time on the test than the average minus the standard deviation

If normal: The answering speed of the test is in line with other candidates.

## Same answer (True/False)

The **same answers** simply tells us whether the candidate gave the exact same answer on every part of the question. When this value exceeds our defined _THRESHOLD_, it will be considered an anomaly by this standard.

True:
66% of the answers were the same. Which is higher then normal, thus considered an anomaly.
False:
66% of the answers were the same. Which is considered to be in a normal range.

## DBscan (True/False)

DBSCAN is an unsupervised clustering algorithm. From a complete dataset, core instances are searched, which are instances that lie within a certain euclidean distance (epsilon=2) from defined number of other instances (min_samples=50). Clusters are then formed by grouping all instances that lie within that distance from at least one of these core instances. A collection of core instances can fall within the same cluster. All instances that do not lie within the distance epsilon of a core instance are considered anomalous

DBscan {did/didnt't} detect this anomaly, meaning it {wasn't} clusterd in any nearby group.

## Neighbours (True/False)

Neighbours kijkt naar in de buurt liggende resultaten en kijkt naar tijd (binnen het uur, twee uur) + som van verschil in antwoorden distance(4,4) = 0 + distance(4,2) = 2, die aftand wordt euclidisch (via de vierkantswortel) voorgesteld waardoor; Lig je heel dicht (gelijkaardige antwoorden) bij een ander resultaat op korte tijd, dan zal je hier hoog op scoren.
It could mean, two or more people cheated by looking at each others answers.

Closest neighbour was test {TestKey}
Finish time: {Finish time}
Neighbour: {Finish time}
Distance: {Distance}

![Function comparing nearest test](img/exporteer_sjabloon_neighbours.png)

## Pyod COPOD (True/False)

COPOD is a method used to find data points that don't fit with the rest.
It works by comparing pairs of data points and looking for those that stand out.
This method is good for complex data with lots of dimensions.

## Pyod ECOD (True/False)

ECOD uses a measure called entropy to find outliers.
It checks how much "surprise" there is in the data and identifies points that are unusual.
ECOD is useful when the data has a complex structure or when it's hard to predict what normal data should look like....

## Pyod IForest (True/False)

Isolation Forest (iForest) works by creating random "trees" to separate data points from each other.
The easier it is to separate a point, the more likely it is an outlier.
This method is fast and works well for large sets of data, making it great for real-time checks.

Your test was easily seperatable by the IForest trees.
Your test wasn't as easily seperatable by the IForest trees.

## Pyod LOF (True/False)

Local Outlier Factor (LOF) looks at the density of data points in a local area and identifies those that don't match.
It's good for finding outliers in data where different parts of the data have different patterns or densities.

In a local neighbourhood, this test was considered {an anomalous}/{a normal} test.

## Pyod ABOD (True/False)

ABOD (Angle-Based Outlier Detection) finds outliers by looking at the angles between data points and their neighbors.
If the angles are unusual compared to the rest of the data, the point is flagged as an outlier.
This method works well for complex, multidimensional data and helps identify points that stand out in a unique way.
It's great for spotting anomalies that might be missed by simpler distance-based methods.

By comparing the angels, this test was considered an {anomalous/normal.}
