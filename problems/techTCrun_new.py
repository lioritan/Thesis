# -*- coding: utf-8 -*-
"""
Created on Sat May 07 11:38:00 2016

@author: Lior
"""

from numpy import *
import os
import cPickle
import alg10_ohsumed_ver as alg

from matplotlib.mlab import find

from alg10_ohsumed_ver import ig_ratio
def feature_select_ig(trn, trn_lbl, tst, fraction):
    ig_ratios=[(ig_ratio(trn[:,j], trn_lbl), j) for j in xrange(size(trn,1))]
    sorted_features_by_ig= sorted(ig_ratios, reverse=True)[:int(size(trn,1)*fraction)]
    idxs=[b for a,b in sorted_features_by_ig]
    
    return trn[:, idxs], tst[:, idxs]

if __name__=='__main__':    
    with open('yago_relationss_smaller.pkl', 'rb') as fptr:
        relationss= cPickle.load(fptr)
    print 'yago loaded'
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_processed_fixed/'):
        filenames.sort()
        for filename in filenames:
            fptr=open(path+'/'+filename, 'rb')
            datasets.append(cPickle.load(fptr))
            fptr.close()
   
    print 'ready to start'
    svm_accs= zeros((100, 3, 19)) #12->feature num percentage: 0.01,0.05,0.1,0.2,...,1.0
    knn_accs= zeros((100,3, 19))
    tree_accs= zeros((100,3,19))

    feature_nums= zeros((100, 3))
    feature_names_list= []
    for count,((trn, trn_lbl),(tst,tst_lbl)) in enumerate(datasets):        
        print count
        if count!=31: #and count!=37 and count!=43:
            continue
        
        training,testing= array(trn, dtype=object), array(tst, dtype=object)
                
        logfile1= open('results%d_log_rec0.txt'%(count), 'w')
        logfile2= open('results%d_log_rec1.txt'%(count), 'w')
        logfile3= open('results%d_log_rec2.txt'%(count), 'w')
        logfiles=[logfile1, logfile2, logfile3]
        feature_thing = []
        for d in [0,1,2]:    
            blor= alg.FeatureGenerationFromRDF(training, training, trn_lbl, relationss)
            blor.generate_features(30*(d**2), d, 7, 20, logfiles[d], 7) #20=max_tree_depth where we generate features 
            logfiles[d].close()
            trn, trn_lbl, tst, feature_names, feature_trees= blor.get_new_table(testing, testing)
            feature_nums[count, d]= len(blor.new_features)
            for f_number,(rel,rec_tree) in enumerate(feature_trees):
                alg.clean_tree_for_pickle(rec_tree.query_tree)
            feature_thing.append(feature_trees)
            with open('trn_and_tst_%d_%d.pkl'%(d, count), 'wb') as fptr:
                cPickle.dump((trn, trn_lbl, tst, tst_lbl), fptr, -1)
                
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
        with open('detailed%d.pkl'%(count), 'wb') as fptr:
            cPickle.dump(feature_thing, fptr, -1)
#    with open('final_res.pkl','wb') as fptr:
#        pickle.dump((errs_svm, errs_knn, errs_svm_na1, errs_knn_na1, feature_names_list, feature_nums), fptr, -1)
    
