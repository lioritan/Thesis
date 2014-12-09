# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 14:31:08 2014

@author: liorf
"""

import cPickle
from numpy import *
from matplotlib.mlab import find
from tree_stats import *
import matplotlib.pyplot as plt
from matplotlib.cbook import flatten

def load_trees_and_oracle(filename):
    with open(filename, 'rb') as fptr:
        all_results= cPickle.load(fptr)
    rec0= array([rec[3] for rec in all_results])
    rec0_trees= [rec[0] for rec in all_results]
    rec1= array([rec[4] for rec in all_results])
    rec1_trees= [rec[1] for rec in all_results]
    rec2= array([rec[5] for rec in all_results])
    rec2_trees= [rec[2] for rec in all_results]
    
    errs= hstack((rec0,rec1,rec2))
    oracle= array(amin(errs, axis=1))[:,newaxis]
    idxs= argmin(errs, axis=1)
    oracle_trees= [rec0_trees[i] if idxs[i]==0 else rec1_trees[i] if idxs[i]==1 else rec2_trees for i in range(100)]
    
    return rec0_trees, rec1_trees, rec2_trees, errs, oracle, idxs, oracle_trees
    
def turn_to_useful_things(rec0, rec1, rec2, errs, filter_lvl=0.0):
    '''create a,b,c,d, better/worse_trees_lvlX + baselines
    then make a1,a2,a3,a4, a1/a3_extra and trees and trees_extra and trees_trees.
    make sure all are flattened! to make it easy to use
    then for each i, calc stats to file'''
    a=find(errs[:,0]>errs[:,1]+filter_lvl)
    b=find(errs[:,0]<errs[:,1]-filter_lvl)
    c=find(errs[:,0]>errs[:,2]+filter_lvl)
    d=find(errs[:,0]<errs[:,2]-filter_lvl)
    better_lvl1_trees=array(rec1)[a]
    better_lvl2_trees=array(rec2)[c]
    worse_lvl1_trees=array(rec1)[b]
    worse_lvl2_trees=array(rec2)[d]
    mapping1= {'tree_sz':0, 'mean_ig':1, 'med_ig':2, 'max_ig':3, 'mean_lf_sz':5, 'med_lf_sz':6, 
    'relative_mean_lf_sz':7, 'relative_med_lf_sz':8, 'depth':9, 'laceness':10} #map stat name to i value for base stats
    mapping2= {'ig_diff':3, 'num_featureRelations_in_newprob':4, 'examples_base':5, 'misclass_base':6, 'misclass_ratio_base':7, 
    'examples_newprob':8, 'misclass_newprob':9, 'misclass_ratio_newprob':10, 'misclass_ratio_newprob_by_ratio_old':11,
    'depth_where_tree_used':12, 'new_problems':13, 'good_new_problems04':14, 'newprob_n':15, 'newprob_n_ratio':16,
    'examples_leftson':17, 'misclass_leftson':18, 'misclass_ratio_leftson':19, 'misclass_ratio_leftson_by_ratio_old':20,
    'examples_rightson':21, 'misclass_rightson':22, 'misclass_ratio_rightson':23, 'misclass_ratio_rightson_by_ratio_old':24,
    'misclass_ratio_rightson_by_ratio_leftson':25, 'max_obj_multiplicity':26, 'mean_obj_multip':27, 'mean_obj_multip_filtered':28,
    'max_obj_multip_error':29, 'max_multip_error_by_total_multip':30,
    'mean_obj_multip_error':31, 'mean_obj_multip_error_filtered':32, 'mean_multip_error_by_total_multip':33,'mean_multip_error_by_total_multip_filtered':34} #map stat name to i val for rec_trees_stats
    
    all_stats_lvl1_better= {} #map of statistic name->tuple of values for it 
    all_stats_lvl1_worse= {}
    all_stats_lvl2_better= {}
    all_stats_lvl2_worse= {}
    a1=[calc_node_and_leaf_stats(t.query_tree) for t in better_lvl1_trees]
    a3=[calc_node_and_leaf_stats(t.query_tree) for t in better_lvl2_trees]
    a5=[calc_node_and_leaf_stats(t.query_tree) for t in worse_lvl1_trees]
    a7=[calc_node_and_leaf_stats(t.query_tree) for t in worse_lvl2_trees]
    #calc stats
    for name,i in mapping1.items(): #basic
        all_stats_lvl1_better[name]= get_stats(array([t[i] for t in a1]))
        all_stats_lvl1_worse[name]= get_stats(array([t[i] for t in a5]))
        all_stats_lvl2_better[name]= get_stats(array([t[i] for t in a3]))
        all_stats_lvl2_worse[name]= get_stats(array([t[i] for t in a7]))
        
    a1=[calc_rec_tree_stats(t.query_tree) for t in better_lvl1_trees]
    a2=[calc_rec_tree_stats(t.query_tree) for t in worse_lvl1_trees]
    a3=[calc_rec_tree_stats(t.query_tree) for t in better_lvl2_trees]
    a4=[calc_rec_tree_stats(t.query_tree) for t in worse_lvl2_trees]
    for name,i in mapping2.items(): #extra
        all_stats_lvl1_better[name]= get_stats(list(flatten(array([t[i] for t in a1]))))
        all_stats_lvl1_worse[name]= get_stats(list(flatten(array([t[i] for t in a2]))))
        all_stats_lvl2_better[name]= get_stats(list(flatten(array([t[i] for t in a3]))))
        all_stats_lvl2_worse[name]= get_stats(list(flatten(array([t[i] for t in a4]))))
    a1=[calc_node_and_leaf_stats(a) for a in list(flatten([find_rec_trees(t.query_tree) for t in better_lvl1_trees]))]
    a2=[calc_node_and_leaf_stats(a) for a in list(flatten([find_rec_trees(t.query_tree) for t in worse_lvl1_trees]))]
    a3=[calc_node_and_leaf_stats(a) for a in list(flatten([find_rec_trees(t.query_tree) for t in better_lvl2_trees]))]
    a4=[calc_node_and_leaf_stats(a) for a in list(flatten([find_rec_trees(t.query_tree) for t in worse_lvl2_trees]))]
    for name,i in mapping1.items(): #tree stats. need to flatten
        all_stats_lvl1_better[name+'_lvl1']= get_stats(array([t[i] for t in a1]))
        all_stats_lvl1_worse[name+'_lvl1']= get_stats(array([t[i] for t in a2]))
        all_stats_lvl2_better[name+'_lvl1']= get_stats(array([t[i] for t in a3]))
        all_stats_lvl2_worse[name+'_lvl1']= get_stats(array([t[i] for t in a4]))
    
    a3=[calc_rec_tree_stats(q) for q in list(flatten([find_rec_trees(t.query_tree) for t in better_lvl2_trees]))]
    a4=[calc_rec_tree_stats(q) for q in list(flatten([find_rec_trees(t.query_tree) for t in worse_lvl2_trees]))]
    for name,i in mapping2.items(): #tree extra stats (lvl2 only). need to flatten
        all_stats_lvl2_better[name+'_lvl1']= get_stats(list(flatten(array([t[i] for t in a3]))))
        all_stats_lvl2_worse[name+'_lvl1']= get_stats(list(flatten(array([t[i] for t in a4]))))
    
    a3=[calc_node_and_leaf_stats(rt) for rt in list(flatten([[find_rec_trees(a) for a in find_rec_trees(t.query_tree)] for t in better_lvl2_trees]))]
    a4=[calc_node_and_leaf_stats(rt) for rt in list(flatten([[find_rec_trees(a) for a in find_rec_trees(t.query_tree)] for t in worse_lvl2_trees]))]
    for name,i in mapping1.items(): #tree stats (lvl2 only). need to flatten
        all_stats_lvl2_better[name+'_lvl2']= get_stats(array([t[i] for t in a3]))
        all_stats_lvl2_worse[name+'_lvl2']= get_stats(array([t[i] for t in a4]))
    
    #write them to file
    return all_stats_lvl1_better, all_stats_lvl1_worse, all_stats_lvl2_better, all_stats_lvl2_worse

#problem: hist with nan, inf    
def export_to_hists(better, worse, i, filter_lvl=0.0):
    #i == tree_max_depth, so either 1 or 2

    #This will still not work!!! anything with trees needs to be divided during stat building!    

    for stat in better.keys():
        first= nan_to_num(array([x if not isinf(x) else 100 for x in better[stat][0]]))
        second= nan_to_num(array([x if not isinf(x) else 100 for x in worse[stat][0]]))
        plt.hist([first, second], bins=20,normed=True)
        plt.title(stat)
        plt.savefig('lvl%d filter %f '%(i, filter_lvl)+stat+'.png')
        plt.close()
        
