# Copyright 2023 Yahoo Japan Corporation
#  
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.


from collections import Counter
from multiprocessing import Pool

import numpy as np
from scipy import stats


def gen_ngram_list(seq, n):
    ngram_list = list()
    if len(seq) < n:
        return ngram_list

    for i in range(len(seq) - n + 1):
        ngram = seq[i: i + n]
        ngram_list.append(ngram)

    return ngram_list
        
def calc_distance(point1, point2, scale_factor=1.):
    x_diff = point2[0] - point1[0]
    y_diff = point2[1] - point1[1]
    return np.sqrt(x_diff ** 2. + y_diff ** 2.) / scale_factor

def calc_point_proximity(point1, point2, beta):
    distance = calc_distance(point1, point2)
    return np.exp(-beta * distance)

def calc_ngram_proximity(ngram1, ngram2, beta):
    point_proximity_list = list()
    for point1, point2 in zip(ngram1, ngram2):
        point_proximity_list.append(calc_point_proximity(point1, point2, beta))
        
    return np.prod(point_proximity_list)

def calc_geo_p_n(sys_seq, ans_seq, n, beta):
    sys_ngram_list = gen_ngram_list(sys_seq, n)
    ans_ngram_list = gen_ngram_list(ans_seq, n)

    edge_list = list()
    for sys_id, sys_ngram in enumerate(sys_ngram_list):
        for ans_id, ans_ngram in enumerate(ans_ngram_list):
            ngram_pair = (sys_id, ans_id)
            proximity = calc_ngram_proximity(sys_ngram, ans_ngram, beta)
            edge_list.append((ngram_pair, proximity))
   
    edge_list.sort(key=lambda x: x[1], reverse=True)
    proximity_sum = 0.
    proximity_cnt = 0

    while len(edge_list) > 0:
        best_edge = edge_list[0]
        best_edge_ngram_pair = best_edge[0]
        proximity = best_edge[1]
        
        proximity_sum += proximity
        proximity_cnt += 1
        best_edge_sys_id, best_edge_ans_id = best_edge_ngram_pair
        
        new_edge_list = list()
        for edge in edge_list:
            ngram_pair = edge[0]
            sys_id, ans_id = ngram_pair
            if sys_id == best_edge_sys_id:
                continue
            if ans_id == best_edge_ans_id:
                continue
                
            new_edge_list.append(edge)
            
        edge_list = new_edge_list
        
    geo_p_n = proximity_sum / float(proximity_cnt)
    
    return geo_p_n

def check_arguments(sys_seq, ans_seq):
    # check the input arguments

    # the trajectory length
    if len(sys_seq) == 0:
        raise ValueError("The length of the generated trajectory is 0.")
    if len(ans_seq) == 0:
        raise ValueError("The length of the reference trajectory is 0.")

    if len(sys_seq) != len(ans_seq):
        raise ValueError(
            "The length doesn't match between the generated and reference trajectories.")

    # the number of columns
    sys_len_counter = Counter()
    ans_len_counter = Counter()
    for sys_step, ans_step in zip(sys_seq, ans_seq):
        sys_len_counter[len(sys_step)] += 1
        ans_len_counter[len(ans_step)] += 1
    sys_len_list = list(sys_len_counter.keys())
    ans_len_list = list(ans_len_counter.keys())
    if len(sys_len_list) != 1:
        raise ValueError("The numbers of columns of the generated trajectory are inconsistent: {}".format(sys_len_counter))
    if len(ans_len_list) != 1:
        raise ValueError("The numbers of columns of the reference trajectory are inconsistent: {}".format(ans_len_counter))

    # only (d, t, x, y) and (uid, d, t, x, y) are acceptable, and the format must be
    # the same between the generated and reference
    sys_columns = sys_len_list[0]
    ans_columns = ans_len_list[0]
    if sys_columns != ans_columns:
        raise ValueError("The numbers of columns are different between the generated and reference trajectories.")
    if sys_columns not in {4, 5}:
        raise ValueError("The numbers of columns must be 4, (d, t, x, y), or 5, (uid, d, t, x, y).")

    # if the format is (uid, d, t, x, y), drop the uid column, making it (d, t, x, y)
    if sys_columns == 5:
        sys_seq = [step[1:] for step in sys_seq]
        ans_seq = [step[1:] for step in ans_seq]

    # consistency of day and time
    for idx, (sys_step, ans_step) in enumerate(zip(sys_seq, ans_seq)):
        sys_d, sys_t = sys_step[:2]
        ans_d, ans_t = ans_step[:2]
        if not (sys_d == ans_d and sys_t == ans_t):
            raise ValueError(
                "Day and time are not the same at step {}, "
                "d={} and t={} for generated while d={} and t={} for reference.".format(
                    idx, sys_d, sys_t, ans_d, ans_t))

    # sort by day and time just in case
    sys_seq.sort(key=lambda x: (x[0], x[1]))
    ans_seq.sort(key=lambda x: (x[0], x[1]))
    return sys_seq, ans_seq

def split_trajectory_by_day(seq):
    dict_by_day = dict()
    for d, t, x, y in seq:
        if d not in dict_by_day.keys():
            dict_by_day[d] = list()
        dict_by_day[d].append((x, y))

    return dict_by_day

def calc_geobleu_orig_wrapper_humob23(arg):
    sys_seq = arg[0]
    ans_seq = arg[1]
    return calc_geobleu_orig(sys_seq, ans_seq, max_n=3, beta=0.5, weights=None)

def calc_dtw_orig_wrapper_humob23(arg):
    sys_seq = arg[0]
    ans_seq = arg[1]
    return calc_dtw_orig(sys_seq, ans_seq, scale_factor=2.)

# == public method ==
def calc_geobleu_orig(sys_seq, ans_seq, max_n=3, beta=0.5, weights=None):
    p_n_list = list()
    seq_len_min = min(len(sys_seq), len(ans_seq))
    max_n_alt = min(max_n, seq_len_min)

    for i in range(1, max_n_alt + 1):
        p_n = calc_geo_p_n(sys_seq, ans_seq, i, beta)
        p_n_list.append(p_n)
        
    brevity_penalty = 1. if len(sys_seq) > len(ans_seq) \
        else np.exp(1. - len(ans_seq) / float(len(sys_seq)))
        
    return brevity_penalty * stats.mstats.gmean(p_n_list)

def calc_dtw_orig(sys_seq, ans_seq, scale_factor=1.):
    n, m = len(sys_seq), len(ans_seq)
    dtw_matrix = np.zeros((n + 1, m + 1))

    for i in range(n + 1):
        for j in range(m + 1):
            dtw_matrix[i, j] = np.inf
    dtw_matrix[0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = calc_distance(sys_seq[i - 1], ans_seq[j - 1], scale_factor=scale_factor)
            last_min = np.min([dtw_matrix[i - 1, j], dtw_matrix[i, j - 1], dtw_matrix[i - 1, j - 1]])
            dtw_matrix[i, j] = cost + last_min
    return dtw_matrix[-1, -1]

def calc_geobleu(sys_seq, ans_seq, processes=4):
    # check the input arguments
    sys_seq, ans_seq = check_arguments(sys_seq, ans_seq)

    # split the trajectories by day
    sys_dict_by_day = split_trajectory_by_day(sys_seq)
    ans_dict_by_day = split_trajectory_by_day(ans_seq)

    # loop over days, calculating geobleu for each day
    arg_list = list()
    for d in ans_dict_by_day.keys():
        arg = (
            sys_dict_by_day[d],
            ans_dict_by_day[d],
        )
        arg_list.append(arg)

    with Pool(processes=processes) as p:
        geobleu_val_list = p.map(calc_geobleu_orig_wrapper_humob23, arg_list)

    # return the average value over days
    return np.mean(geobleu_val_list)

def calc_dtw(sys_seq, ans_seq, processes=4):
    # check the input arguments
    sys_seq, ans_seq = check_arguments(sys_seq, ans_seq)

    # split the trajectories by day
    sys_dict_by_day = split_trajectory_by_day(sys_seq)
    ans_dict_by_day = split_trajectory_by_day(ans_seq)

    # loop over days, calculating dtw for each day
    # loop over days, calculating geobleu for each day
    arg_list = list()
    for d in ans_dict_by_day.keys():
        arg = (
            sys_dict_by_day[d],
            ans_dict_by_day[d],
        )
        arg_list.append(arg)

    with Pool(processes=processes) as p:
        dtw_val_list = p.map(calc_dtw_orig_wrapper_humob23, arg_list)

    # the average value over days
    return np.mean(dtw_val_list)

