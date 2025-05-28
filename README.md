# geobleu
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Python implementation of GEO-BLEU, a similarity evaluation method for trajectories

https://dl.acm.org/doi/abs/10.1145/3557915.3560951

[GIS Cup 2025](https://sigspatial2025.sigspatial.org/giscup/) uses GEO-BLEU as the evaluation metric, and this repository provides necessary resources for the evaluation.

GEO-BLEU is a similarity measure with a stronger focus on local features, as in similarity measures for natural language processing (e.g. BLEU). The more similar two trajectories are, the larger the value. It assigns a score of 1 to two identical trajectories.

**Note:**

* May 28: The validation tool and the parameters for GEO-BLEU have been updated to be compatible with the tasks of GIS Cup 2025.

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

## Evaluatoin functions (per uid) for GIS Cup 2025
#### Overview
This package provides a per-uid evaluation function, calc_geobleu_single(), for comparing two trajectories under the conditions of the GIS Cup. The function receives generated and reference trajectories belonging to a uid as the arguments and give the similarity value for GEO-BLEU. A trajectory is assumed to be a list of tuples, each representing (d, t, x, y) or (uid, d, t, x, y), and the values of days and times must be the same between generated and reference at each step. Internally, the function evaluate trajectories day by day and return the average over the days.

The final score for each city will be the average of the function's output over all the uid's.

#### Example usage of the evaluation functions
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

geobleu_val = geobleu.calc_geobleu_single(generated, reference, processes=3)
print("geobleu: {}".format(geobleu_val))

# geobleu: 0.07556369896234784
```

#### Hyperparameter settings
As for the hyperparameters for GEO-BLEU, we use N = 5 (using unigrams, bigrams, up to 5-grams), w_n = 1/5 (modified precisions are geometric-averaged with equal weights), and beta = 0.5 (so that the proximity between two points becomes e^-1 when they are 1 km away).

#### Validation tool
You can check whether your submission files conform to the task requirements using a standalone Python program, `validator.py`. It takes the task ID, the corresponding training data file path, and the submission file path as arguments, and it emits errors if it finds any issues with the formatting or inconsistencies between the training data and the given submission file. A submission file may begin with the header line `uid,d,t,x,y`, but omitting it is also acceptable.

For example, assuming task B's training data after decompression is at `foo/city_B_challengedata.csv`, and your submission file for task B before compression is at `bar/baz_task_b_humob.csv`, the command will be:
```
python3 validator.py b foo/city_B_challengedata.csv bar/baz_task_b_humob.csv
```

The line number and the step number in a trajectory in error messages are 0-indexed. If the tool doesn't find any issues, it will simply say "Validation finished without errors!".

## Simple interface for evaluating a trajectory pair
Using the installed package, you can evaluate the similarity between generated and reference trajectories, giving the generated one as the first argument and the reference one as the second to its function calc_geobleu_orig().
```
import geobleu

generated = [(1, 1), (2, 2), (3, 3)]
reference = [(1, 1), (1, 1), (1, 2), (2, 2), (2, 2)]

similarity = geobleu.calc_geobleu_orig(generated, reference)
print(similarity)
```

