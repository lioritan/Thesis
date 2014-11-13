# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 13:01:55 2014

@author: liorf
"""
import pydot

def clean_tree_for_pickle(tree_node):
    if tree_node.chosen_query is None:
        return
    try:
        clean_tree_for_pickle(tree_node.justify)
    except:
        pass
    #for (tree_root,_,_) in tree_node.cool_things:
    #    clean_tree_for_pickle(tree_root)
    tree_node.chosen_query=None
    clean_tree_for_pickle(tree_node.left_son)
    clean_tree_for_pickle(tree_node.right_son)
    return tree_node
    
def clean_tree_for_pickle_multiclass(tree_node):
    if tree_node.chosen_query is None:
        return
    try:
        clean_tree_for_pickle(tree_node.justify)
    except:
        pass
    #for (tree_root,_,_) in tree_node.cool_things:
    #    clean_tree_for_pickle(tree_root)
    tree_node.chosen_query=None
    for son in tree_node.sons.values():
        clean_tree_for_pickle(son)
    return tree_node
    
def make_graphviz_string(tree):
    '''needs to make a valid representation as DOT data'''
    #on every node: sub-func (include call for tree)
    #recursive sub func for a tree
    pass

def export_to_pdf(tree, filename):
    graphviz_string= make_graphviz_string(tree)
    graph=pydot.graph_from_dot_data(graphviz_string)
    graph.write_pdf(filename)