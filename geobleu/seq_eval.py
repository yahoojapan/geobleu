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
    if len(sys_seq) != len(ans_seq):
        raise ValueError(
            "The length doesn't match between the generated and reference trajectories.")

    for idx, (sys_step, ans_step) in enumerate(zip(sys_seq, ans_seq)):
        sys_d, sys_t = sys_step[:2]
        ans_d, ans_t = ans_step[:2]
        if not (sys_d == ans_d and sys_t == ans_t):
            raise ValueError(
                "Day and time are not consistent at step {}, "
                "d={} and t={} for generated while d={} and t={} for reference.".format(
                    idx, sys_d, sys_t, ans_d, ans_t))

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

def calc_geobleu(sys_seq, ans_seq):
    # check the input arguments
    sys_seq, ans_seq = check_arguments(sys_seq, ans_seq)

    # split the trajectories by day
    sys_dict_by_day = split_trajectory_by_day(sys_seq)
    ans_dict_by_day = split_trajectory_by_day(ans_seq)

    # loop over days, calculating geobleu for each day
    geobleu_val_list = list()
    for d in ans_dict_by_day.keys():
        geobleu_val = calc_geobleu_orig(sys_dict_by_day[d], ans_dict_by_day[d])
        geobleu_val_list.append(geobleu_val)

    # return the average value over days
    return np.mean(geobleu_val_list)

def calc_dtw(sys_seq, ans_seq):
    # check the input arguments
    sys_seq, ans_seq = check_arguments(sys_seq, ans_seq)

    # split the trajectories by day
    sys_dict_by_day = split_trajectory_by_day(sys_seq)
    ans_dict_by_day = split_trajectory_by_day(ans_seq)

    # loop over days, calculating dtw for each day
    dtw_val_list = list()
    for d in ans_dict_by_day.keys():
        dtw_val = calc_dtw_orig(
            sys_dict_by_day[d], 
            ans_dict_by_day[d],
            scale_factor=2.)
        dtw_val_list.append(dtw_val)

    # the average value over days
    return np.mean(dtw_val_list)

