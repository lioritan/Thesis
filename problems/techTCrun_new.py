# -*- coding: utf-8 -*-
"""
Created on Sat May 07 11:38:00 2016

@author: Lior
"""

from numpy import *
import os
import cPickle
import copy_reg
from types import FunctionType
#import alg11_flatten as alg
#import alg10_ohsumed_flatten as alg
import compete_alg_isa as alg

from matplotlib.mlab import find

from alg10_ohsumed_ver import ig_ratio

def stub_pickler(obj):
    return stub_unpickler, ()
def stub_unpickler():
    return "STUB"
copy_reg.pickle(
    FunctionType,
    stub_pickler, stub_unpickler)
    
    
def feature_select_ig(trn, trn_lbl, tst, fraction):
    ig_ratios=[(ig_ratio(trn[:,j], trn_lbl), j) for j in xrange(size(trn,1))]
    sorted_features_by_ig= sorted(ig_ratios, reverse=True)[:int(size(trn,1)*fraction)]
    idxs=[b for a,b in sorted_features_by_ig]
    
    return trn[:, idxs], tst[:, idxs]

import sys
if __name__=='__main__':    
    #with open('yago_relationss_smaller.pkl', 'rb') as fptr:
    with open('yago_rels_new_with_reverse.pkl', 'rb') as fptr:
    #with open('less_freebase_techtc.pkl', 'rb') as fptr:
        relationss= cPickle.load(fptr)
    print 'yago loaded'
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_entities/'):
        filenames.sort()
        for filename in filenames:
            fptr=open(path+'/'+filename, 'rb')
            datasets.append(cPickle.load(fptr))
            fptr.close()
    finaru=[]        
    for path,dirnames, filenames in os.walk('./techtc_pkls/'):
        filenames.sort()
        for i,filename in enumerate(filenames):
            fptr=open(path+'/'+filename, 'rb')
            ((raw_trn, _),(raw_tst,_))=cPickle.load(fptr)
            aaa = (datasets[i][0][0],datasets[i][0][1],[a.split(' ') for a in raw_trn])
            bbb = (datasets[i][1][0],datasets[i][1][1],[a.split(' ') for a in raw_tst])
            finaru.append((aaa,bbb))
            fptr.close()
   
    print 'ready to start'
    svm_accs= zeros((100, 3, 19)) #12->feature num percentage: 0.01,0.05,0.1,0.2,...,1.0
    knn_accs= zeros((100,3, 19))
    tree_accs= zeros((100,3,19))

    feature_nums= zeros((100, 3))
    feature_names_list= []
    for count,((trn, trn_lbl, trn_raw),(tst,tst_lbl, tst_raw)) in enumerate(finaru):        
        print count
        #if count<int(sys.argv[1]) or count>=int(sys.argv[2]): #and count!=37 and count!=43:
        #    continue
        
        training,testing= array(trn, dtype=object), array(tst, dtype=object)
        raw1,raw2= array(trn_raw, dtype=object), array(tst_raw, dtype=object)
                
        #logfile1= open('results%d_log_rec0.txt'%(count), 'w')
        #logfile2= open('results%d_log_rec1.txt'%(count), 'w')
        #logfile3= open('results%d_log_rec2.txt'%(count), 'w')
        #logfiles=[logfile1, logfile2, logfile3]
        feature_thing = []
        for d in [1]:    
            blor= alg.FeatureGenerationFromRDF(training, training, trn_lbl, relationss)
            #blor.generate_features(100*(d**2), d, 7, 20, logfiles[d],7) #20=max_tree_depth where we generate features 
            blor.generate_features()
            #logfiles[d].close()
            trn, trn_lbl, tst, feature_names, feature_trees= blor.get_new_table(testing, testing)
            feature_nums[count, d]= len(blor.new_features)
            #for f_number,(rel,rec_tree) in enumerate(feature_trees):
            #    alg.clean_tree_for_pickle(rec_tree.query_tree)
            #    rec_tree.relations = None
            #    rec_tree.good_recs = None
            #feature_thing.append(feature_trees)
            with open('trn_and_tst_%d_%d.pkl'%(d, count), 'wb') as fptr:
                cPickle.dump((trn, trn_lbl, tst, tst_lbl), fptr, -1)
            #outer_tree = blor.blah
            #alg.clean_tree_for_pickle(outer_tree.query_tree)
            #outer_tree.relations = None
            #outer_tree.good_recs = None
            #import pdb
            #pdb.set_trace()
            #with open('outer_tree%d_%d.pkl'%(d,count), 'wb') as fptr:
            #    cPickle.dump(outer_tree, fptr, -1)
            for j,fraction in enumerate([0.005,0.0075,0.01,0.025,0.05,0.075,0.1,0.125,0.15,0.175,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]):
                new_trn, new_tst= feature_select_ig(trn, trn_lbl, tst, fraction)
  
                from sklearn.svm import SVC
                from sklearn.neighbors import KNeighborsClassifier
                from sklearn.tree import DecisionTreeClassifier
    
                clf= SVC(kernel='linear', C=10)
                clf.fit(new_trn, trn_lbl)
                tst_predict= clf.predict(new_tst)
                svm_accs[count, d, j]= mean(tst_predict==tst_lbl)

                clf= KNeighborsClassifier(n_neighbors=3)
                clf.fit(new_trn, trn_lbl)
                tst_predict= clf.predict(new_tst)
                knn_accs[count, d, j]= mean(tst_predict==tst_lbl)

                clf=DecisionTreeClassifier(criterion='entropy', min_samples_split=9, random_state=0)
                clf.fit(new_trn, trn_lbl)
                tst_predict= clf.predict(new_tst)
                tree_accs[count,d,j] = mean(tst_predict==tst_lbl)

        a=(svm_accs[count,:,:], knn_accs[count,:,:], tree_accs[count,:,:], feature_nums[count,:])
        with open('results%d.pkl'%(count),'wb') as fptr:
            cPickle.dump(a, fptr, -1)     
        #with open('detailed%d.pkl'%(count), 'wb') as fptr:
        #    cPickle.dump(feature_thing, fptr, -1)
#    with open('final_res.pkl','wb') as fptr:
#        pickle.dump((errs_svm, errs_knn, errs_svm_na1, errs_knn_na1, feature_names_list, feature_nums), fptr, -1)
    
