# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 11:04:46 2014

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
import cPickle
import alg10_ficuslike as alg

def solve_multiclass(trn, trn_lbl, lbl_vals, tst, tst_lbl, relations,logfile, d=0, stopthresh=10, version=1):
    blor= alg.FeatureGenerationFromRDF(trn, trn_lbl, relations)
    blor.generate_features(30*(d**2), d, 7, logfile, stopthresh, version)  
    trn, trn_lbl, tst, feature_names= blor.get_new_table(tst)
#    from sklearn.feature_selection import SelectKBest
#    feature_selector= SelectKBest(chi2, k=100)
#    trn= feature_selector.fit_transform(trn, trn_lbl)
#    tst= feature_selector.transform(tst)
    
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    
    clf= SVC(kernel='linear', C=100)
#    clf= KNeighborsClassifier(n_neighbors=3)
#    clf=DecisionTreeClassifier(criterion='entropy', min_samples_split=2, random_state=0)
    clf.fit(trn, trn_lbl)
    
    tst_predict= clf.predict(tst)
    err= mean(tst_predict!=tst_lbl)
    return err, tst_predict, blor.feature_names, len(blor.new_features)

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
    i=0
    for j in xrange(3):
        
        logfile1= open('run_log_rec%d_%d.txt'%(j,i), 'w')
        error, tst_predict, feature_names, num_new= solve_multiclass(trn, trn_lbl,label_names, tst, tst_lbl, 
                                                              relations,logfile1, 0, 10, 1)
        logfile1.close()
        print error
        with open('result_rec%d%d.pkl'%(j,i), 'wb') as fptr:
            cPickle.dump((error,tst_predict, feature_names, num_new), fptr, -1)
    
