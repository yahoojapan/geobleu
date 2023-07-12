# Copyright 2023 Toru Shimizu, Yahoo Japan Corporation
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
        
def calc_distance(point1, point2):
    x_diff = point2[0] - point1[0]
    y_diff = point2[1] - point1[1]
    return np.sqrt(x_diff ** 2. + y_diff ** 2.)

def calc_point_proximity(point1, point2, beta):
    distance = calc_distance(point1, point2)
    return np.exp(-beta * distance)

def calc_ngram_proximity(ngram1, ngram2, beta):
    point_proximity_list = list()
    for point1, point2 in zip(ngram1, ngram2):
        point_proximity_list.append(calc_point_proximity(point1, point2, beta))
        
    return np.prod(point_proximity_list)

def calc_geo_p_n(sys_seq, ans_seq, n, beta, trace=False):
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

# == public method ==
def calc_geobleu_orig(sys_seq, ans_seq, max_n=3, beta=0.5, weights=None, trace=False):
    p_n_list = list()
    for i in range(1, max_n + 1):
        p_n = calc_geo_p_n(sys_seq, ans_seq, i, beta)
        p_n_list.append(p_n)
        
    brevity_penalty = 1. if len(sys_seq) > len(ans_seq) \
        else np.exp(1. - len(ans_seq) / float(len(sys_seq)))
        
    return brevity_penalty * stats.mstats.gmean(p_n_list)

