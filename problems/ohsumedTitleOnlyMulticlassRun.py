# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 11:04:46 2014

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
import cPickle
import alg10_ficuslike as alg
from sklearn.cross_validation import StratifiedKFold

from alg10_ficuslike import ig_ratio
def feature_select_ig(trn, trn_lbl, tst, fraction):
    ig_ratios=[(ig_ratio(trn[:,j], trn_lbl), j) for j in xrange(size(trn,1))]
    sorted_features_by_ig= sorted(ig_ratios, reverse=True)[:int(size(trn,1)*fraction)]
    idxs=[b for a,b in sorted_features_by_ig]
    
    return trn[:, idxs], tst[:, idxs]

def solve_multiclass(trn, trn_lbl, tst, tst_lbl, relations,logfile, fractions, d=0, stopthresh=10, version=1):
    blor= alg.FeatureGenerationFromRDF(trn, trn_lbl, relations)
    blor.generate_features(30*(d**2), d, 7, logfile, stopthresh, version)  
    trn, trn_lbl, tst, feature_names= blor.get_new_table(tst)

    #TODO: selection, run all 5...
    
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    blah1=zeros(19)
    blah2=zeros(19)
    blah3=zeros(19)
    blah4=zeros(19)
    blah5=zeros(19)
    for i,fraction in enumerate(fractions):
        new_trn, new_tst= feature_select_ig(trn, trn_lbl, tst, fraction)
        
        clf= SVC(kernel='linear', C=100)
        clf.fit(new_trn, trn_lbl)    
        blah1[i]= mean(clf.predict(new_tst)!=tst_lbl)
        
        clf= KNeighborsClassifier(n_neighbors=3)
        clf.fit(new_trn, trn_lbl)    
        blah2[i]= mean(clf.predict(new_tst)!=tst_lbl)
        
        clf=DecisionTreeClassifier(criterion='entropy', min_samples_split=2, random_state=0)
        clf.fit(new_trn, trn_lbl)    
        blah3[i]= mean(clf.predict(new_tst)!=tst_lbl)
        
        new_trn[new_trn==-100]= -1
        
        clf= KNeighborsClassifier(n_neighbors=3)
        clf.fit(new_trn, trn_lbl)    
        blah4[i]= mean(clf.predict(new_tst)!=tst_lbl)
        
        clf= SVC(kernel='linear', C=100)
        clf.fit(new_trn, trn_lbl)    
        blah5[i]= mean(clf.predict(new_tst)!=tst_lbl)
        
    return blah1, blah2, blah3, blah4, blah5, len(blor.new_features)

if __name__=='__main__':
    with open('med_relations.pkl','rb') as fptr:
        (relations, entities)= cPickle.load(fptr) 
        
    with open('ohsumed_titles_parsed_complete.pkl','rb') as fptr:
        (articles,labels)= cPickle.load(fptr) 
    
    (articles,labels)= (array(articles), array(labels))  
    print shape(articles), shape(labels)
    label_names=array([1, 4, 6, 8, 10, 13, 14, 17, 20, 23])   
    data,data_labels=[],[]
    for label in label_names:
        idxs=find(labels==label)
        data+=[x for x in articles[idxs]]
        data_labels+=[x for x in labels[idxs]]
    data, data_labels= array(data, dtype=object), array(data_labels)
    svm_errs=zeros((10,3,19)) 
    knn_errs=zeros((10,3,19)) 
    tree_errs=zeros((10,3,19)) 
    svm_na1_errs=zeros((10,3,19)) 
    knn_na1_errs=zeros((10,3,19)) 
    feature_nums=zeros((10,3)) 
    i=0
    for trn_idxs, tst_idxs in StratifiedKFold(labels, n_folds=10):
        trn=articles[trn_idxs]
        trn_lbl=labels[trn_idxs]
        tst=articles[tst_idxs]
        tst_lbl=labels[tst_idxs]
        
        for d in [0,1,2]:
            logfile1= open('run_log_rec%d_%d.txt'%(d,i), 'w')
            blah1, blah2, blah3, blah4, blah5, num_new= solve_multiclass(trn, trn_lbl, tst, tst_lbl, relations,logfile1,
                                                              [0.005,0.0075,0.01,0.025,0.05,0.075,0.1,0.125,0.15,0.175,0.2, 0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
                                                              , 0, 1, 1)
            logfile1.close()
            svm_errs[i, d, :]= blah1
            knn_errs[i, d, :]= blah2
            tree_errs[i,d, :]= blah3
            svm_na1_errs[i, d, :]= blah4
            knn_na1_errs[i, d, :]= blah5
            feature_nums[i, d]=num_new
        with open('result_%d.pkl'%(i), 'wb') as fptr:
            cPickle.dump((svm_errs[i,:,:], knn_errs[i,:,:], tree_errs[i,:,:], svm_na1_errs[i,:,:], knn_na1_errs[i,:,:], feature_nums[i,:]), fptr, -1)
        i+=1
        
        
    
