# -*- coding: utf-8 -*-
"""
Created on Fri Nov 21 14:25:39 2014

@author: liorf
"""
from numpy import *
from matplotlib.mlab import find
import alg7
from matplotlib.cbook import flatten

    
def calc_node_and_leaf_stats(top_node):
    '''return num of nodes, node IG stats'''
    '''return num of leaf, leaf size stats, leaf error rate stats'''

    nodes= [top_node]
    igs = []
    leafs_sz= []
    leafs_misclass = []
    
    num_nodes= 0
    num_leafs=0
    tree_depth= 0
    top_node.curr_depth= 0
    for node in nodes:
        tree_depth= max(tree_depth, node.curr_depth)
        if type(node.justify)==str and (node.justify.startswith('leafed') or node.justify.startswith('not good enough')):
            num_leafs+=1
            leafs_sz.append(len(node.tagging))
            leafs_misclass.append(len(find(node.tagging!=node.chosen_tag))/(1.0*len(node.tagging)))
            continue
        num_nodes+= 1
        igs.append(node.ig)
        node.left_son.curr_depth= node.curr_depth+1
        node.right_son.curr_depth= node.curr_depth+1
        nodes.append(node.left_son)
        nodes.append(node.right_son)
    igs=array(igs)
    leafs_sz= array(leafs_sz)
    leafs_misclass= array(leafs_misclass)
    return (num_nodes, mean(igs), median(igs), amax(igs), 
    num_leafs, mean(leafs_sz), median(leafs_sz), mean(1.0*leafs_sz/len(top_node.tagging)),
    median(1.0*leafs_sz/len(top_node.tagging)), tree_depth #inc_leaves
    , num_leafs-tree_depth #if 0, lace, if more->more balanced
    )
    
#def get_stats(a1, a2=None):
#    the_thing=a1
#    if a2 is not None:
#        the_thing=a1-a2
#        return mean(the_thing), median(the_thing), amax(the_thing), amin(the_thing), mean(a1), median(a1)
#    return mean(the_thing), median(the_thing), amax(the_thing), amin(the_thing)
    
def get_stats(a1, a2=None):
    the_thing=a1
    if a2 is not None:
        the_thing=a1-a2
        return the_thing, mean(the_thing), median(the_thing), mean(a1), median(a1)
    return the_thing, mean(the_thing), median(the_thing)
    
def find_rec_trees(top_node):
    '''for applying node/leaf stats on recursive trees'''
    nodes= [top_node]
    
    tree_heads= []
    for node in nodes:
        if type(node.justify)==str:
            if node.justify.startswith('leafed') or node.justify.startswith('not good enough'):
                continue
            nodes.append(node.left_son)
            nodes.append(node.right_son)
            continue
        tree_heads.append(node.justify)
        nodes.append(node.left_son)
        nodes.append(node.right_son)
    return tree_heads

def calc_rec_tree_stats(top_node):
    '''return num of lvl1 trees, num of lvl2 trees(stats per lvl1 tree and total?)
    difference in IG between nonrec (for lvl1 tree and for lvl2 trees per lvl1 tree+total)'''
    nodes= [top_node]
    
    num_lvl1_trees= 0
    num_lvl2_trees= 0
    num_lvl2_per_lvl1= []
        
    ig_diff_lvl1= []
    num_problems_lvl1= []
    num_good_problems_lvl1= []
    n_lvl1= []
    n_relative_lvl1= []
    tree_node_depth_lvl1= [] #TODO? add ratio of this to num_ex/misclass/misclass_ratio?
    #mby add: ratio of depth to recursive tree depth?
    max_tree_mult_lvl1= []
    mean_tree_mult_lvl1= []
    mean_tree_mult_filtered_lvl1= []
    max_mult_error_lvl1= [] #total vals in feature vals that don't fit classifier decision  
    max_mult_error_ratio_lvl1= [] #ratio between total vals in feature vals and those above
    mean_mult_error_lvl1= [] #total vals in feature vals that don't fit classifier decision  
    mean_mult_error_filtered_lvl1= []
    mean_mult_error_ratio_lvl1= [] #ratio between total vals in feature vals and those above    
    mean_mult_error_ratio_filtered_lvl1= []
    
    num_ex_lvl1= []
    misclass_lvl1= []
    num_ex_left_son_lvl1= []
    num_ex_right_son_lvl1= []
    misclass_left_son_lvl1= []
    misclass_right_son_lvl1= []
    num_ex_newprob_lvl1= []
    misclass_newprob_lvl1= []
    
    num_relations_for_newprob_lvl1= []
    
    for node in nodes:
        if type(node.justify)==str:
            if node.justify.startswith('leafed') or node.justify.startswith('not good enough'):
                continue
            nodes.append(node.left_son)
            nodes.append(node.right_son)
            continue
        nodes.append(node.left_son)
        nodes.append(node.right_son)
        num_lvl1_trees+=1
        cool_igs= array([a[1] for a in node.cool_things])
        idx= argmax(cool_igs)
        entry= node.cool_things[idx]
        ig_diff_lvl1.append(entry[1]-entry[2])
        num_problems_lvl1.append(len(cool_igs))
        num_good_problems_lvl1.append(len(find(cool_igs>0.04))) #can try different vals later...
        n_lvl1.append([n[1] for n in node.bttoo if n[0]==node.justify.transforms[-1]][0])
        n_relative_lvl1.append(n_lvl1[-1]*1.0/node.n)
        tree_node_depth_lvl1.append(node.curr_depth)
        #more stats:
        num_ex_lvl1.append(len(node.tagging))
        misclass_lvl1.append(len(find(node.tagging!=node.chosen_tag)))
        num_ex_left_son_lvl1.append(len(node.left_son.tagging))
        misclass_left_son_lvl1.append(len(find(node.left_son.tagging!=node.left_son.chosen_tag)))
        num_ex_right_son_lvl1.append(len(node.right_son.tagging))
        misclass_right_son_lvl1.append(len(find(node.right_son.tagging!=node.right_son.chosen_tag)))
        num_ex_newprob_lvl1.append(len(node.justify.tagging))
        misclass_newprob_lvl1.append(len(find(node.justify.tagging!=node.justify.chosen_tag)))
        
        calc_node_and_leaf_stats(node.justify)
        deeper_stats= calc_rec_tree_stats(node.justify)
        num_lvl2_per_lvl1.append(deeper_stats[0])
        num_lvl2_trees+= deeper_stats[0]
        
        relevant_features= []
        for relation in node.relations.keys():
            if len(node.justify.transforms)>1 and (relation==node.justify.transforms[-1] or relation=='reverse_'+node.justify.transforms[-1] or relation==node.justify.transforms[-1].replace('reverse_','')):
                continue #no using the relation you came with on the way back...
            feature_vals=[set(list(flatten(alg7.is_in_relation(obj, node.relations[relation],relation)))) for obj in node.justify.objects] #apply_transforms_other(self.relations, [relation], self.objects) #
            val_lens=[len(val) for val in feature_vals]
            if sum(val_lens)==0 : #no objects have relevant values. This may leave us with objects whose feature values are [], which means any query will return false...
                continue #not relevant
            relevant_features.append(relation) #does not take into account >MAX_SIZE...
        num_relations_for_newprob_lvl1.append(len(relevant_features))
        
        #calc ignore values/misclass/both ratio thing    
        #need to ask how many in val lens are > 1, and also different tag by recursive clf...
        feature_vals= []
        rel= node.justify.transforms[-1]
        if len(node.transforms)==0:
            feature_vals=[set(alg7.is_relation_key(obj, node.relations[rel])) for obj in node.objects]
        else:
            feature_vals=[set(alg7.is_in_relation(obj, node.relations[rel],rel)) for obj in node.objects] #apply_transforms_other(self.relations, [relation], self.objects) #
        val_lens=array([len(val) for val in feature_vals])
        max_tree_mult_lvl1.append(amax(val_lens))
        mean_tree_mult_lvl1.append(mean(val_lens))
        mean_tree_mult_filtered_lvl1.append(mean(val_lens[nonzero(val_lens)]))
        def find_tagging(top_node, train_point):
            #finds tagging without the query func...
            if type(top_node.justify)==str and (top_node.justify.startswith('leafed') or top_node.justify.startswith('not good enough')):
                return top_node.chosen_tag
            if train_point==[]:
                return find_tagging(top_node.left_son if []==top_node.left_son.objects[-1] else top_node.right_son, train_point)
            if train_point in list(flatten(top_node.left_son.objects)):
                return find_tagging(top_node.left_son, train_point)
            return find_tagging(top_node.right_son, train_point)
        def find_mult_tagging(top_node, feature_val):
            #finds real tag using the fact that that's what the sons are responsible for...
            for obj in top_node.right_son.objects:
                if not len(obj)==len(feature_val):
                    continue
                if all([feature_val[i]==obj[i] for i in xrange(len(feature_val))]):
                    return 1
            return 0
                    
        vals_tags=[[find_tagging(node.justify, val) for val in vals] if len(vals)>0 else [find_tagging(node.justify, [])] for vals in feature_vals]
        obj_tags= [find_mult_tagging(node, val) for val in node.objects]
        bads= array([len(find(array(thing)!= obj_tags[i])) for i,thing in enumerate(vals_tags)])
        max_mult_error_lvl1.append(amax(bads)) #should be 0 or 1
        max_mult_error_ratio_lvl1.append(amax(bads/val_lens)) #seems wrong! should be 0 or inf
        mean_mult_error_lvl1.append(mean(bads))
        filtered= bads[nonzero(bads)]
        mean_mult_error_filtered_lvl1.append(mean(filtered) if len(filtered)>0 else 0)
        mean_mult_error_ratio_lvl1.append(mean(bads/val_lens))
        mean_mult_error_ratio_filtered_lvl1.append(mean(filtered/val_lens[nonzero(bads)]) if len(filtered)>0 else 0)
        
    blah1= array(misclass_lvl1)*1.0/array(num_ex_lvl1)
    blah2= array(misclass_newprob_lvl1)*1.0/array(num_ex_newprob_lvl1)
    blah3= array(misclass_left_son_lvl1)*1.0/array(num_ex_left_son_lvl1)
    blah4= array(misclass_right_son_lvl1)*1.0/array(num_ex_right_son_lvl1)
    blah5= blah2/blah1 #misclass ratio new/old
    blah6= blah4/blah3 #misclass ration right/left
    blah7= blah3/blah1 #misclass ration left/old(parent)
    blah8= blah4/blah1 #ratio right/old
    
    return (num_lvl1_trees, num_lvl2_trees, mean(num_lvl2_per_lvl1), ig_diff_lvl1, num_relations_for_newprob_lvl1,
    num_ex_lvl1, misclass_lvl1, blah1, num_ex_newprob_lvl1, misclass_newprob_lvl1, blah2,
    blah5, tree_node_depth_lvl1, num_problems_lvl1, num_good_problems_lvl1, n_lvl1, n_relative_lvl1, 
    num_ex_left_son_lvl1, misclass_left_son_lvl1, blah3, blah7,
    num_ex_right_son_lvl1, misclass_right_son_lvl1, blah4, blah8, blah6,
    max_tree_mult_lvl1, mean_tree_mult_lvl1, mean_tree_mult_filtered_lvl1, max_mult_error_lvl1, max_mult_error_ratio_lvl1, 
    mean_mult_error_lvl1, mean_mult_error_filtered_lvl1, mean_mult_error_ratio_lvl1, mean_mult_error_ratio_filtered_lvl1)
        