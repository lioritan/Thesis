# -*- coding: utf-8 -*-
"""
Created on Tue Mar 03 04:05:59 2015

@author: liorf
"""

def is_set_valued(relation,relname):
    return relname.startswith('reverse_') or relname=='type' or relname=='possible_cure' or (relname.startswith('drug_') and not relname=='drug_moiety')
    return isinstance(relation.values()[0], list) #general, slow
    
def is_in_relation(x, relation,relname, *args):
    '''args[0]=optional target
    x is a single object. this works fine with [] as param'''
    res=[]
    flag= is_set_valued(relation,relname)
    if flag is False:        
        for y in x:
            bob = relation.get(y)
            if bob is not None:
                res+=[bob]
    else: #relation is reversed
        for y in x:
            res+= relation.get(y, [])
    if len(args)==0:
        return res #list of strings
    return args[0] in res
    
def apply_transforms(relations, transforms, objects):
    '''transforms is list of relation+direction pairs.
    objects is set of objects(set of sets'''
    curr_objs=objects
    for relation in transforms:
        curr_objs= [is_in_relation(obj, relations[relation], relation) for obj in curr_objs]
    return curr_objs

class FeatureGenerationAlt(object):
    def __init__(self, objects, tagging, relations):
        self.objects= objects
        self.tagging= tagging
        self.relations= relations
        
        self.new_features= []
        self.new_justify= []
        
    def generate_features(self, depth):
        pass #if depth=1, go one relation. if depth=2 go 2 relations and so on...
        
        
    
    def get_new_table(self, test):
        all_words=set()
        for words in self.objects:
            all_words.update(words)
        self.table= zeros((len(self.objects), len(all_words)+len(self.new_features)))
        self.test= zeros((len(test), len(all_words)+len(self.new_features)))
        self.feature_names=[]
        for i,word in enumerate(all_words):
            self.table[:,i]= array([1 if (word in obj) else 0 for obj in self.objects])
            self.test[:, i]= array([1 if (word in obj) else 0 for obj in test])
            self.feature_names.append('has word:%s'%(word))
        for j,new_feature in enumerate(self.new_features):
            self.table[:, len(all_words)+j]= array([new_feature(obj) for obj in self.objects])
            self.test[:, len(all_words)+j]= array([new_feature(obj) for obj in test])
            self.feature_names.append(self.new_justify[j])
        return self.table, self.tagging, self.test, self.feature_names