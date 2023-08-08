# geobleu
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python implementation of GEO-BLEU, a similarity evaluation method for trajectories

https://dl.acm.org/doi/abs/10.1145/3557915.3560951

[HuMob Challenge 2023](https://connection.mit.edu/humob-challenge-2023) uses GEO-BLEU as one of the two evaluation metrics, and this repository provides necessary resources for the evaluation.

GEO-BLEU is a similarity measure with a stronger focus on local features, as in similarity measures for natural language processing (e.g. BLEU). The more similar two trajectories, the larger the value. It gives 1 to two identical trajectories.

The other, Dynamic Time Warping (DTW), is a distance measure comparing trajectories as a whole with step-by-step alignment. The more similar two trajectories, the smaller the value. It gives 0 to two identical trajectories.

**Note:** 

* As of Aug 1 (JST), execution of the evaluation fuctions are parallelized with multiprocessing, by splitting the calculation task on a per-day basis, and you can specify the number of processes by a keyword argument "processes" in both calc_geobleu() and calc_dtw() as in the sample code in "Example usage" section below. The default value is 4. You can just leave it as default if you don't need to accelerate the calculation.
* The evaluation functions now support the 5-column format (uid, d, t, x, y) for each step in trajectories, which will be used in actual submission data, in addition to the original 4-column (d, t, x, y). The number of columns must be the same among all the steps in two given trajectories.
* Two evaluation functions for HuMob Challenge 2023, calc_geobleu() and calc_dtw(), were implemented on Jul 18 (JST). Please reinstall the package if you are using a previous version.


## Installation
After downloading the repository and entering into it, execute the installation command as follows:
```
python3 setup.py install
```
or
```
pip3 install .
```

Prerequisites: numpy, scipy

## Evaluatoin functions (per uid) for HuMob Challenge 2023
#### Overview
This package provides two per-uid evaluation functions, calc_geobleu() and calc_dtw(), for the actual tasks. Both functions receive generated and reference trajectories belonging on a uid as the arguments and give the similarity value for GEO-BLEU and distance for DTW respectively. A trajectory is assumed to be a list of tuples, each representing (d, t, x, y) or (uid, d, t, x, y), and the values of days and times must be the same between generated and reference at each step. Internally, both functions evaluate trajectories day by day and return the average over the days.

The final score for the tasks will be the average of these functions' output over all the uid's. Resultantly, one submission for a task will have two final scores, one based on GEO-BLEU and the other based on DTW.

Typical scale of GEO-BLEU scores for the tasks is quite small, often on the order of 10^-3 or 10^-4, due to the calculation involving exponential terms taking negative input values. We organizers are considering presenting submissions' performances in per mille or ppm.


#### Example usage
The following example calculates GEO-BLEU and DTW for two sample trajectories of a uid.
```
import geobleu

# tuple format: (d, t, x, y)
generated = [
    (60, 12, 84, 88),
    (60, 15, 114, 78),
    (60, 21, 121, 96),
    (61, 12, 78, 86),
    (61, 13, 89, 67),
    (61, 17, 97, 70),
    (61, 20, 96, 70),
    (61, 24, 111, 80),
    (61, 25, 114, 78),
    (61, 26, 99, 70),
    (61, 38, 77, 86),
    (62, 12, 77, 86),
    (62, 14, 102, 129),
    (62, 15, 104, 131),
    (62, 17, 106, 131),
    (62, 18, 104, 110)]

reference = [
    (60, 12, 82, 93),
    (60, 15, 114, 78),
    (60, 21, 116, 96),
    (61, 12, 82, 84),
    (61, 13, 89, 67),
    (61, 17, 97, 70),
    (61, 20, 91, 67),
    (61, 24, 109, 82),
    (61, 25, 110, 78),
    (61, 26, 99, 70),
    (61, 38, 77, 86),
    (62, 12, 77, 86),
    (62, 14, 97, 125),
    (62, 15, 104, 131),
    (62, 17, 106, 131),
    (62, 18, 103, 111)]

geobleu_val = geobleu.calc_geobleu(generated, reference, processes=3)
print("geobleu: {}".format(geobleu_val))

dtw_val = geobleu.calc_dtw(generated, reference, processes=3)
print("dtw: {}".format(dtw_val))

# geobleu: 0.21733678721880598
# dtw: 5.889002930255253
```

#### Hyperparameter settings
As for the hyperparameters for GEO-BLEU, we use N = 3 (using unigram, bigram, and trigram), w_n = 1/3 (modified precisions are geometric-averaged with equal weights), and beta = 0.5 (so that the proximity between two points becomes e^-1 when they are 1 km away).

For DTW, we use 1 km as the unit length, dividing the distance calculated with cell coordinates by 2 internally.


## Sample implementation of GEO-BLEU itself
Using the installed package, you can evaluate the similarity between generated and reference trajectories, giving the generated one as the first argument and the reference one as the second to its function calc_geobleu_orig().
```
import geobleu

generated = [(1, 1), (2, 2), (3, 3)]
reference = [(1, 1), (1, 1), (1, 2), (2, 2), (2, 2)]

similarity = geobleu.calc_geobleu_orig(generated, reference)
print(similarity)
```

