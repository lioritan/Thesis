# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 14:25:39 2014

@author: liorf
"""
from numpy import *
from matplotlib.mlab import find
from scipy.stats import mode
    
def calc_node_and_leaf_stats(top_node):
    '''return num of nodes, node IG stats'''
    '''return num of leaf, leaf size stats, leaf error rate stats'''

    nodes= [top_node]
    igs = []
    leafs_sz= []
    leafs_misclass = []
    
    num_nodes= 0
    num_leafs=0
    for node in nodes:
        if type(node.justify)==str and (node.justify.startswith('leafed') or node.justify.startswith('not good enough')):
            num_leafs+=1
            leafs_sz.append(len(node.tagging))
            leafs_misclass.append(len(find(node.tagging!=node.chosen_tag))/(1.0*len(node.tagging)))
            continue
        num_nodes+= 1
        igs.append(node.ig)
        nodes.append(node.left_son)
        nodes.append(node.right_son)
    igs=array(igs)
    leafs_sz= array(leafs_sz)
    leafs_misclass= array(leafs_misclass)
    return (num_nodes, mean(igs), median(igs), mode(igs)[0], amax(igs), amin(igs), 
    num_leafs, mean(leafs_sz), median(leafs_sz), mode(leafs_sz)[0], amax(leafs_sz), amin(leafs_sz),
    mean(leafs_misclass), median(leafs_misclass), mode(leafs_misclass)[0], amax(leafs_misclass), amin(leafs_misclass))
    
def find_rec_trees(top_node):
    '''for applying node/leaf stats on recursive trees'''
    nodes= [top_node]
    
    tree_heads= []
    for node in nodes:
        if type(node.justify)==str:
            if node.justify.startswith('leafed'):
                continue
            nodes.append(node.left_son)
            nodes.append(node.right_son)
            continue
        tree_heads.append(node.justify)
    return tree_heads

def calc_rec_tree_stats(top_node):
    '''return num of lvl1 trees, num of lvl2 trees(stats per lvl1 tree and total?)
    difference in IG between nonrec (for lvl1 tree and for lvl2 trees per lvl1 tree+total)'''
    nodes= [top_node]
    
    num_lvl1_trees= 0
    num_lvl2_trees= 0
    num_lvl2_per_lvl1= []
    ig_diff_lvl1= []
    ig_diff_lvl2= []
    
    for node in nodes:
        if type(node.justify)==str:
            if node.justify.startswith('leafed') or node.justify.startswith('not good enough'):
                continue
            nodes.append(node.left_son)
            nodes.append(node.right_son)
            continue
        num_lvl1_trees+=1
        cool_igs= array([a[1] for a in node.cool_things])
        idx= argmax(cool_igs)
        entry= node.cool_things[idx]
        ig_diff_lvl1.append(entry[1]-entry[2])
        
        deeper_stats= calc_rec_tree_stats(node.justify)
        num_lvl2_per_lvl1.append(deeper_stats[0])
        num_lvl2_trees+= deeper_stats[0]
        ig_diff_lvl2.append(deeper_stats[3])
        
    num_lvl2_per_lvl1=array(num_lvl2_per_lvl1)
    ig_diff_lvl1=array(ig_diff_lvl1)
    ig_diff_lvl2=array(ig_diff_lvl2)    
    return num_lvl1_trees, num_lvl2_trees, mean(num_lvl2_per_lvl1), ig_diff_lvl1, ig_diff_lvl2
        