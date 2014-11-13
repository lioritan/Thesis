# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 11:04:46 2014

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
import cPickle
import alg7_multiclass as alg

def solve_multiclass(trn, trn_lbl, lbl_vals, tst, tst_lbl, relations, d=0):
    clf= alg.TreeRecursiveSRLClassifier(trn, trn_lbl, relations, [], 100*(d**2), d, 3)
    clf.train()
    
    tst_predict= array([clf.predict(x) for x in tst])
    err= mean(tst_predict!=tst_lbl)
    return err, tst_predict, clf

#def solve_multiclass(trn, trn_lbl, lbl_vals, tst, tst_lbl, relations, d=0):
#    clfs=[]
#    for i,lbl in enumerate(lbl_vals):
#        for j,lbl2 in enumerate(lbl_vals):
#            if j<=i:
#                continue
#            idxs= find(any(vstack((trn_lbl==lbl,trn_lbl==lbl2)),axis=0))
#            new_trn= trn[idxs]
#            new_lbl= ((trn_lbl[idxs]-lbl2)/(lbl-lbl2)).astype(int) #binarize
#            clf= alg7.TreeRecursiveSRLClassifier(new_trn, new_lbl, relations, [], 100*(d**2), d, 3)
#            clf.train()
#            clfs.append((clf, lbl, lbl2))
#    def predict_label(x, descriptors=clfs):
#        mappify={}
#        mappify.update([t[::-1] for t in enumerate(lbl_vals)]) #switch i,val for val,i
#        votes= zeros(len(lbl_vals))
#        for clf,lbl1,lbl2 in clfs:
#            label= clf.predict(x)
#            if label==1:
#                votes[mappify[lbl1]]+=1
#            else:
#                votes[mappify[lbl2]]+=1
#        return lbl_vals[argmax(votes)]
#    tst_predict= array([predict_label(x) for x in tst])
#    err= mean(tst_predict!=tst_lbl)
#    return err, tst_predict, clfs, predict_label
    

if __name__=='__main__':
    with open('med_relations.pkl','rb') as fptr:
        (relations, entities)= cPickle.load(fptr) 
        
    with open('ohsumed_titles_parsed_complete.pkl','rb') as fptr:
        (articles,labels)= cPickle.load(fptr) 
    
    (articles,labels)= (array(articles), array(labels))  
    print shape(articles), shape(labels)
    label_names=array([1, 4, 6, 8, 10, 13, 14, 17, 20, 23])    
    #split train/test: (something like 600:251?)
    trn= []
    trn_lbl= []
    tst= []
    tst_lbl= []
    for lbl in label_names:
        idxs= find(labels==lbl)
        al= idxs[:600]
        ah= idxs[600:]
        trn+= [x for x in articles[al]]
        trn_lbl+= [x for x in labels[al]]
        tst+= [x for x in articles[ah]]
        tst_lbl+= [x for x in labels[ah]]
    
    ((trn, trn_lbl), (tst, tst_lbl))= ((array(trn), array(trn_lbl)), (array(tst), array(tst_lbl)))    

    error, tst_predict, clf= solve_multiclass(trn, trn_lbl,label_names, tst, tst_lbl, 
                                                              relations, 0)
    print error
#    #make a few more by random pick of 10 categories...
    with open('result_nonrec.pkl','wb') as fptr:
        cPickle.dump((error, tst_predict, alg.clean_tree_for_pickle(clf.query_tree)), fptr, -1)
#    
    error, tst_predict, clf= solve_multiclass(trn, trn_lbl,label_names, tst, tst_lbl, 
                                                              relations, 1)
#    error, tst_predict, clfs, decision_func= solve_multiclass(trn, trn_lbl,[1,4], tst, tst_lbl, 
#                                                              relations, 1)
    print error
    #make a few more by random pick of 10 categories...
    with open('result_rec1.pkl','wb') as fptr:
        cPickle.dump((error, tst_predict,alg.clean_tree_for_pickle(clf.query_tree)), fptr, -1)
    
    error, tst_predict, clf= solve_multiclass(trn, trn_lbl,label_names, tst, tst_lbl, 
                                                              relations, 2)
    print error
    #make a few more by random pick of 10 categories...
    with open('result_rec2.pkl','wb') as fptr:
        cPickle.dump((error, tst_predict, alg.clean_tree_for_pickle(clf.query_tree)), fptr, -1)
        
        
    #fix alg to support multiclass-voting?(keep binary in trees somehow-relabeling, use info-gain-ratio)
