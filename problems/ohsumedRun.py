# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 10:34:44 2014

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
import cPickle
import alg7


def solve_multiclass(trn, trn_lbl, lbl_vals, tst, tst_lbl, relations, d=0):
    clfs=[]
    for i,lbl in enumerate(lbl_vals):
        for j,lbl2 in enumerate(lbl_vals):
            if j<=i:
                continue
            idxs= find(any(vstack((trn_lbl==lbl,trn_lbl==lbl2)),axis=0))
            new_trn= trn[idxs]
            new_lbl= ((trn_lbl[idxs]-lbl2)/(lbl-lbl2)).astype(int) #binarize
            clf= alg7.TreeRecursiveSRLClassifier(new_trn, new_lbl, relations, [], 100*(d**2), d, 3)
            clf.train()
            clfs.append((clf, lbl, lbl2))
    def predict_label(x, descriptors=clfs):
        mappify={}
        mappify.update([t[::-1] for t in enumerate(lbl_vals)]) #switch i,val for val,i
        votes= zeros(len(lbl_vals))
        for clf,lbl1,lbl2 in clfs:
            label= clf.predict(x)
            if label==1:
                votes[mappify[lbl1]]+=1
            else:
                votes[mappify[lbl2]]+=1
        return lbl_vals[argmax(votes)]
    tst_predict= array([predict_label(x) for x in tst])
    err= mean(tst_predict!=tst_lbl)
    return err, tst_predict, clfs, predict_label
    

if __name__=='__main__':
    with open('med_relations.pkl','rb') as fptr:
        (relations, entities)= cPickle.load(fptr) 
        
    with open('ohsumed_dataset_parsed.pkl','rb') as fptr:
        ((trn,trn_lbl), (tst,tst_lbl))= cPickle.load(fptr) 
    
    trn,trn_lbl, tst, tst_lbl= (array([a+b for (a,b) in trn]), array(trn_lbl), array([a+b for (a,b) in tst]), array(tst_lbl))    
    #make divisions to small datasets(10 cats multiclass). categories go 1 to 23
    #split STANDARD: c1, c4, c6, c8, c10, c12, c14, c20, c21, c23
    
#    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4,6,8,10,12,14,20,21,23], tst, tst_lbl, 
#                                                              relations, 0)
                                                              
#    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4], tst, tst_lbl, 
#                                                              relations, 0)
#    print error
#    #make a few more by random pick of 10 categories...
#    with open('result_nonrec.pkl','wb') as fptr:
#        cPickle.dump((error, tst_predict, [(alg7.clean_tree_for_pickle(x[0].query_tree), x[1],x[2]) for x in clfs]), fptr, -1)
#    
    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4,6,8,10,12,14,20,21,23], tst, tst_lbl, 
                                                              relations, 1)
#    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4], tst, tst_lbl, 
#                                                              relations, 1)
    print error
    fkfgkfkg.fgfgfg()()
    #make a few more by random pick of 10 categories...
    with open('result_rec1.pkl','wb') as fptr:
        cPickle.dump((error, tst_predict, [(alg7.clean_tree_for_pickle(x[0].query_tree), x[1],x[2]) for x in clfs]), fptr, -1)
    
    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4,6,8,10,12,14,20,21,23], tst, tst_lbl, 
                                                              relations, 2)
    print error
    #make a few more by random pick of 10 categories...
    with open('result_rec2.pkl','wb') as fptr:
        cPickle.dump((error, tst_predict, [(alg7.clean_tree_for_pickle(x[0].query_tree), x[1],x[2]) for x in clfs]), fptr, -1)
        
        
    #fix alg to support multiclass-voting?(keep binary in trees somehow-relabeling, use info-gain-ratio)