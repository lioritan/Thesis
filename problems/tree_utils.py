# -*- coding: utf-8 -*-
"""
Created on Thu Nov 13 13:01:55 2014

@author: liorf
"""
import pydot
import matplotlib.pyplot as plt
from numpy import *

def plot_accuracies(rec0, reci, filename):
    plt.scatter(1-rec0, 1-reci)
    plt.plot(arange(0.0,1.0,0.05), arange(0.0,1.0,0.05))
    plt.savefig(filename)

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
    tree_string='digraph Tree{\n graph [compound=true];\n'
    
    def print_node(node, free_id):
        '''prints a node. handles recursive trees
        return lowest free id, string'''
        res='n%d [shape=box, style="filled", label="'%free_id
        free_id+=1
        if type(node.justify)==str: #I have a recursive tree
            res+= node.justify+'\n nsamples:%d\n IG:%f"];\n'%(len(node.objects),node.ig)
            return res, free_id
        res+= 'clf%d(%s)\n nsamples:%d\n IG:%f"];\n'%(free_id-1, str(node.justify.transforms), len(node.objects),node.ig)
        res+= 'n%d -> n%d [lhead=cluster_clf%d arrowhead=vee];\n'%(free_id-1, free_id, free_id-1)
        res+= 'subgraph cluster_clf%d { \n'%(free_id-1)
        recursive_tree, new_id= recurse(node.justify, free_id)
        res+= recursive_tree+'}\n'
        return res, new_id
    
    def recurse(node, free_id):
        '''do for sons. right now this is non-multiclass(multiclass easy to add)
        return lowest free id, string'''
        if type(node.justify)==str and node.justify.startswith('leafed'):
            return 'n%d [shape=box, style="filled", label="LEAF\n nsamples:%d\n"];\n'%(free_id, len(node.objects)), free_id+1
        res, new_id= print_node(node, free_id)
        res+= 'n%d -> n%d [label="n"];\n'%(free_id, new_id)
        left_side, new_id= recurse(node.left_son, new_id)
        res+= left_side
        res+= 'n%d -> n%d [label="y"];\n'%(free_id, new_id)
        right_side, new_id= recurse(node.right_son, new_id)
        res+= right_side
        return res, new_id
    
    tree_string+=recurse(tree.query_tree, 0)[0]
    tree_string+= '}'
    return tree_string

def export_to_pdf(tree, filename):
    graphviz_string= make_graphviz_string(tree)
    graph=pydot.graph_from_dot_data(graphviz_string)
    graph.set_graphviz_executables({'dot':'C:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe'})
    graph.write_pdf(filename)
    
def working_export_patchfix(tree, filename):
    graphviz_string= make_graphviz_string(tree)
    graph=pydot.graph_from_dot_data(graphviz_string)
    graph.write(filename) #now, convert this manually