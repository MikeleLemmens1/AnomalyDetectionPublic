# Notes of the unsupervised clustering experimentation

This report keeps track of the steps I have followed in search for the best clustering model

## Encoded data

1. I have used a dataframe with the complete bytestrings as one of the colums - FAILED because KMeans can only work with numbers

2. I have transformed these bytestrings into bitstrings of 6400 bits - FAILED because KMeans converts these into out-of-bounds integers

3. I have split all these bitstrings into separate items of 128 bits - FAILED because the numbers are in bounds, but still extremely large (exp 120+) - REMARK: This does not organize the questions using the item numbers, the first column is the first item regardless of its item number. This compares items with different ID's as if they were the same, which is wrong

4. I have normalized the bitstrings so that they fall in a small range - FAILED because there is probably a significant precision loss

5. I have transformed these normalized bitstrings to a 2D space, the instances are spread out like this:

 ![bitstrings split per item](./img/pca2_bitstring_per_item.png)

6. There are some instances that are not part of the big blob, but when plotting the cluster centers for n_clusters = [1 or 2], the centers are not where I would have expected them:

 ![2 Cluster centers](./img/KM_cluster_centers_bitstrings.png)

  SUCCESS, but not qualitatively. I could draw a line and separate the instances that are visually separated:
  
   ![Visual separation](./img/KM2_visual_separation.png)

   This separates **about 23 instances**. I plot the distances to the cluster center (KM with 1 cluster) and see that most instances are within an arbitrary distance of 5:

   ![Distances to 1 cluster center](./img/KM1_distances.png)

   Isolating the instances that are further than a distance of 10 yields **about 1500 instances**.

Although I'm capable of separating instances, I can hardly call this an effective nor qualitative anomaly detection. I abandon the idea of clustering encoded data even before trying out other models (I get the idea that models don't work with encrypted data)

## Decoded data

There are 2 groups of data that need clustering:

- A dataset with test instances as rows
- A dataset with question instances as rows

I begin with the former: **I gather all the items for each test instance in rows**, exploding the full dataset to have 657 answer columns. Each column shows the answer of sequenceID 1, 2 or 3 for a specific itemID. Because every test instance has only 20-40 items while there are +200 possible itemID's, I get a dataset full of NaN's. I make aggregations on the answer columns (mean, std, min, max and sum), and calculate the ratio of each given answer to the total amount of filled in answers. I scale all features (which ignores NaN's), after which I use a SimpleImputer to fill in NaN's with 0 (which is the mean of every column after scaling). I let the imputer add a column with an indicator of which values are imputed. The categorical columns ('Gender', 'ChosenGender', 'ChosenLanguage', 'Qualification') are one hot encoded.

I have the following possible datasets:

- One with all columns, incl the scaled and imputed answer columns with its indicators. This is over 1340 columns if I include the categorical columns
- One without the categorical values
- One with only the aggregated columns and TimeSpentTest (this is the first one I used to explore the models)
- One with aggregations, TimeSpentTest and the categorical values

I experiment with KMeans:

- I use the default KMeans, which is not compatible with large dimensionality (therefore +1300-col datasets won't work)
- I use the accelerated KMeans, which does not work well when the data is not well separable
- I use MiniBatchKMeans, also without a result

**TODO:** try KMeans with pca, but I have no big expectations

I experiment with DBScan:

- DBScan does not scale well with a large amount of instances, but the default model with eps=0.05 does fit quickly.
- I use a gridsearch to tweak which combinations of eps and min_samples work. Training is feasible quite quickly. Parameter grid: min_s = [3, 5, 10, 20] and eps = [0.01,0.05,0.2,0.5]
- The default setting yields labels, and -1 should mean that the instance is not allocated to a cluster. Strangely, only <10% of the instances get a label!=-1, so it seems to work the other way around. I separate the instances and get a visual result on which at least some of the labels look like real anomalies:\
![DBScan_default](./img/DBScan_default_first_anomalies.png)

I need to experiment with setting eps to a different value. Making it smaller will make more instances to fall out of a cluster, hopefully yielding less a subset with less than 5% of the instances AND still keeping the instances that seem to be at the boundaries of the blob. The first model that moves in the right direction has eps=2 and min_samples=20. This is the first set of parameters that succesfully filters out a substantially smaller amount of anomalies:\
![Better DBScan](image.png)\
Note that in contrast to the red instances, the yellow ones are the ones that are considered as noise. In the former model, the red dots were actually inside defined clusters (so the opposite of anomalies). TODO: further tweak the model in order for the amount of anomalies to be lower than a self-defined threshold (say 5% for example) and return the results in any way

**NEXT UP:**

Try out GMM and other models

**Dataset of questions**: I have used a dataset with test instances on the rows, but it might also be usefull to do the same process with questions as rows. We probably need to count the number of questions labeled as anomaly per test instance, and arbitrarily set a threshold that stands for the amount of question anomalies a test should have for the complete test to be indicated as an anomaly.

## Idea

It might not return adequate results, but if we manage to get models to indicate whether test instances are marked as an anomaly or not, we could use these marks as labels to use supervised training in order to classify new instances. (This might not give good results, but we can at least try and tweak the accuracy). If this works, this would be epic and an ideal solution to the customer's needs.
