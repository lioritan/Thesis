# -*- coding: utf-8 -*-
"""
Created on Sat Jan 03 18:31:46 2015

@author: liorf
"""

import cPickle
from random import sample
from numpy import *

from sklearn.datasets import fetch_20newsgroups

def make_subset(data, labels, cat_size, legal_cats=None):
    '''
    cat_size= desired size for each label
    Note: this expects data only from labels given.
    '''
#    print len(data), len(labels)
    new_data= []
    new_labels= []
    categories= frozenset(labels)
    if legal_cats is not None:
        categories= frozenset(legal_cats)
    for cat in categories:
        inds= find(labels==cat)
        sub_inds= sample(inds, cat_size)
        for ind in sub_inds:
            new_data.append(data[ind])
            new_labels.append(labels[ind])
    return array(new_data, dtype=object), array(new_labels)
        #pick cat_size inds at randm, then put them in...


if __name__=='__main__':
    pass
    #do for OHSUMED, OHSUMED titles only, 20NG
    
    #50 train for each cat+50 test -> 100xnum_cats
    #ohsumed datasets: needs more things (need to first filter out the categories!)
    
#    with open('./problems/ohsumed_dataset_parsed.pkl', 'rb') as fptr:
#        ((data, labels), (_,_))= cPickle.load(fptr)
#        data,labels= array(data), array(labels)
#        (data, labels)= make_subset(data, labels, 100, [1,4,6,8,10,12,14,20,21,23])
#        with open('./problems/ohsumed_small_subset.pkl','wb') as fptt:
#            cPickle.dump((data,labels), fptt, -1)
#    print 'one'
#    with open('./problems/ohsumed_titles_parsed_complete.pkl', 'rb') as fptr:
#        (data, labels)= cPickle.load(fptr)
#        data,labels= array(data), array(labels)
#        (data, labels)= make_subset(data, labels, 100, [1, 4, 6, 8, 10, 13, 14, 17, 20, 23])
#        with open('./problems/ohsumed_titles_only_small_subset.pkl','wb') as fptt:
#            cPickle.dump((data,labels), fptt, -1)
#    print 'two'
    
    
#    newsgroups = fetch_20newsgroups(subset='all', remove=('headers', 'footers', 'quotes'))
#    fixed_data = array([s.lower().replace('\n','').split(' ') for s in newsgroups.data])
#    (data, labels)= make_subset(fixed_data, newsgroups.target, 100)
#    with open('./problems/20NG_small_subset.pkl', 'wb') as fptr:
#        cPickle.dump((data, labels), fptr, -1)
#    print 'three'