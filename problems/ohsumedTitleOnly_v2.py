# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 12:34:42 2015

@author: liorf
"""


from numpy import *
from matplotlib.mlab import find
import cPickle
import alg10_ohsumed_ver as alg
from sklearn.cross_validation import StratifiedKFold

from alg10_ohsumed_ver import ig_ratio
def feature_select_ig(trn, trn_lbl, tst, fraction):
    ig_ratios=[(ig_ratio(trn[:,j], trn_lbl), j) for j in xrange(size(trn,1))]
    sorted_features_by_ig= sorted(ig_ratios, reverse=True)[:int(size(trn,1)*fraction)]
    idxs=[b for a,b in sorted_features_by_ig]
    
    return trn[:, idxs], tst[:, idxs]
    
def calc_stats(predicted, actual):
    '''accuracy,precision,recall,F1'''
    sums_of_things= [0.0,0.0,0.0]
    for cat in frozenset(actual):
        pos_idxs= find(predicted==cat)
        tp= len(find(predicted[pos_idxs]==actual[pos_idxs]))
        tp_fp= len(pos_idxs)
        tp_fn= len(find(actual==cat))
        #print tp, tp_fp, tp_fn, cat, predicted, mean(predicted!=actual)
        sums_of_things[0]+= tp*1.0/tp_fp if tp_fp>0 else 0.0
        sums_of_things[1]+= tp*1.0/tp_fn
        sums_of_things[2]+= tp*2.0/(tp_fp+tp_fn)
    means_of_things= [x/len(frozenset(actual)) for x in sums_of_things]
    return array([mean(predicted==actual),means_of_things[0],means_of_things[1],means_of_things[2]])

def solve_multiclass(trn, trn_ents, trn_lbl, tst, tst_ents,tst_lbl, relations,logfile, fractions, d=0, stopthresh=10):
    blor= alg.FeatureGenerationFromRDF(trn, trn_ents, trn_lbl, relations)
    blor.generate_features(400*(d**2), d, 81, logfile, stopthresh)  
    trn, trn_lbl, tst, feature_names,_= blor.get_new_table(tst, tst_ents)

    #TODO: selection, run all 5...
    
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    blah1=zeros((19,4)) #accuracy,precision,recall,F1
    blah2=zeros((19,4))
    blah3=zeros((19,4))
    for i,fraction in enumerate(fractions):
        new_trn, new_tst= feature_select_ig(trn, trn_lbl, tst, fraction)
        
        clf= SVC(kernel='linear', C=100)
        clf.fit(new_trn, trn_lbl)    
        blah1[i,:]= calc_stats(clf.predict(new_tst),tst_lbl)
        
        clf= KNeighborsClassifier(n_neighbors=3)
        clf.fit(new_trn, trn_lbl)    
        blah2[i,:]= calc_stats(clf.predict(new_tst),tst_lbl)
        
        clf=DecisionTreeClassifier(criterion='entropy', min_samples_split=8, random_state=0)
        clf.fit(new_trn, trn_lbl)    
        blah3[i,:]= calc_stats(clf.predict(new_tst),tst_lbl)
               
    return blah1, blah2, blah3, len(blor.new_features)

if __name__=='__main__':
    with open('ohsumed_relations_new_small.pkl','rb') as fptr:
        relations= cPickle.load(fptr) 
        
    with open('ohsumed_titles_final.pkl','rb') as fptr:
        (articles,entities,labels)= cPickle.load(fptr) 
    
    (articles,entities,labels)= (array(articles), array(entities), array(labels))  
    print shape(articles), shape(labels)
    label_names=array([1,20])#([1, 4, 6, 8, 10, 13, 14, 17, 20, 23])   
    data,ents,data_labels=[],[],[]
    for label in label_names:
        idxs=find(labels==label)
        data+=[x for x in articles[idxs]]
        ents+=[x for x in entities[idxs]]
        data_labels+=[x for x in labels[idxs]]
    data,ents, data_labels= array(data, dtype=object), array(ents, dtype=object), array(data_labels)
    svm_accs=zeros((10,3,19, 4)) 
    knn_accs=zeros((10,3,19, 4)) 
    tree_accs=zeros((10,3,19, 4)) 
    feature_nums=zeros((10,3)) 
    #with open('folds_2cats.pkl','wb') as fptr:
    #    cPickle.dump(StratifiedKFold(data_labels, n_folds=10),fptr,-1)
    #gdgdg.dfddg()
    with open('folds.pkl','rb') as fptr:
        kfold=cPickle.load(fptr)
    for f,(trn_idxs, tst_idxs) in enumerate(kfold):
        if f!=0:
            continue
        trn=articles[trn_idxs]
        trn_lbl=data_labels[trn_idxs]
        trn_ents=ents[trn_idxs]
        tst=articles[tst_idxs]
        tst_lbl=data_labels[tst_idxs]
        tst_ents=ents[tst_idxs]
        
        for d in [0,1,2]:
            logfile1= open('run_log_rec%d_%d.txt'%(d,f), 'w')
            blah1, blah2, blah3, num_new= solve_multiclass(trn, trn_ents, trn_lbl, tst, tst_ents, tst_lbl, relations, logfile1,
                                                              [0.005,0.0075,0.01,0.025,0.05,0.075,0.1,0.125,0.15,0.175,0.2, 
                                                               0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0] , d, 17)
            logfile1.close()
            svm_accs[f, d, :, :]= blah1
            knn_accs[f, d, :, :]= blah2
            tree_accs[f,d, :, :]= blah3
            feature_nums[f, d]=num_new
        with open('result_fold_%d.pkl'%(f), 'wb') as fptr:
            cPickle.dump((svm_accs[f,:,:,:], knn_accs[f,:,:,:], tree_accs[f,:,:,:], feature_nums[f,:]), fptr, -1)
        
        
    
