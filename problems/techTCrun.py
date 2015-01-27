from numpy import *
#import bruteforce_propo as compete
import alg10_ficuslike as godfish
#import alg7 as compete
#import bruteforce_propo as compete
import yago
import string
import os
import time

from matplotlib.mlab import find

from alg10_ficuslike import ig_ratio
def feature_select_ig(trn, trn_lbl, tst, fraction):
    ig_ratios=[ig_ratio(trn[:,j], trn_lbl) for j in xrange(size(trn,1))]
    idxs= sorted(ig_ratios, reverse=True)[:int(size(trn,1)*fraction)]
    
    return trn[idxs], tst[idxs]

if __name__=='__main__':    
        
    import cPickle as pickle
    fptr=open('yago_relationss_smaller.pkl', 'rb')
    relationss= pickle.load(fptr)
    fptr.close()
    print 'yago loaded'
#    vgjfhjfhj.jfghf()

#    relationss.pop('earth')
#    relationss.pop('reverse_earth')    
#    removed=[]
#    for key in relationss.keys():
#        if key.startswith('reverse_') and max([len(x) for x in relationss[key].values()])>50:
#            removed.append(key)
#            
#    for key in removed:
#        relationss.pop(key)
#    dfgdfgfgf.sfgsfg()
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_processed_fixed/'):
        filenames.sort()
        for filename in filenames:
            fptr=open(path+'/'+filename, 'rb')
            datasets.append(pickle.load(fptr))
            fptr.close()
#    
    res_7=[]
    errs_svm= zeros((100, 3, 12)) #12->feature num percentage: 0.01,0.05,0.1,0.2,...,1.0
    errs_knn= zeros((100,3, 12))
    #errs_tree= zeros((100,3))

    errs_svm_na1= zeros((100,3, 12))
    errs_knn_na1= zeros((100,3, 12))
#    errs_tree_na1= zeros((100,3))
    feature_nums= zeros((100, 3))
    feature_names_list= []
    for count,((trn, trn_lbl),(tst,tst_lbl)) in enumerate(datasets):        
        print count
#        if count >2:
#            break
        if count<50 or count>=51:#each one goes different
            continue
        
        feature_name_trio= []
        training,testing= array(trn, dtype=object), array(tst, dtype=object)
                
        logfile1= open('results%d_log_rec0.txt'%(count), 'w')
        logfile2= open('results%d_log_rec1.txt'%(count), 'w')
        logfile3= open('results%d_log_rec2.txt'%(count), 'w')
        logfiles=[logfile1, logfile2, logfile3]
        for i in [7]: #switch back to [3,7] later. doesn't seem to matter much between 1/3/5 and 7/9(which are worse for tree)
            for d in [0,1,2]:    
                blor= godfish.FeatureGenerationFromRDF(training, trn_lbl, relationss)
                blor.generate_features(30*(d**2), d, i, logfiles[d], 1, 1)  
                logfiles[d].close()
                trn, trn_lbl, tst, feature_names= blor.get_new_table(testing)
                
                for j,fraction in enumerate([0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]):
                    new_trn, new_tst= feature_select_ig(trn, trn_lbl, tst, fraction)
    
                    from sklearn.svm import SVC
                    from sklearn.neighbors import KNeighborsClassifier
#                    from sklearn.tree import DecisionTreeClassifier
    
                    clf= SVC(kernel='linear', C=100)
                    clf.fit(new_trn, trn_lbl)
                    tst_predict= clf.predict(new_tst)
                    errs_svm[count, d, j]= mean(tst_predict!=tst_lbl)

                    clf= KNeighborsClassifier(n_neighbors=1)
                    clf.fit(new_trn, trn_lbl)
                    tst_predict= clf.predict(new_tst)
                    errs_knn[count, d, j]= mean(tst_predict!=tst_lbl)

#                clf=DecisionTreeClassifier(criterion='entropy', min_samples_split=2, random_state=0)
#                clf.fit(trn, trn_lbl)
#                tst_predict= clf.predict(tst)
#                #results:
#                errs_tree[count, d]= mean(tst_predict!=tst_lbl)
#                feature_name_trio.append(feature_names)
#                feature_nums[count, d]= len(blor.new_features)

                    new_trn[new_trn==-100]= -1
                    clf=SVC(kernel='linear', C=100)
                    clf.fit(new_trn, trn_lbl)
                    errs_svm_na1[count, d, j]= mean(clf.predict(new_tst)!=tst_lbl)
                    clf=KNeighborsClassifier(n_neighbors=1)
                    clf.fit(new_trn, trn_lbl)
                    errs_knn_na1[count, d, j]= mean(clf.predict(new_tst)!=tst_lbl)
#                    clf=DecisionTreeClassifier(criterion='entropy',min_samples_split=2, random_state=0)
#                    clf.fit(trn, trn_lbl)
#                    errs_tree_na1[count, d]= mean(clf.predict(tst)!=tst_lbl)
        feature_names_list.append(feature_name_trio)    
        a=(errs_svm[count,:,:], errs_knn[count,:,:], errs_svm_na1[count,:,:], errs_knn_na1[count,:,:],feature_name_trio, feature_nums[count,:])
        with open('results%d.pkl'%(count),'wb') as fptr:
            pickle.dump(a, fptr, -1)     
    with open('final_res.pkl','wb') as fptr:
        pickle.dump((errs_svm, errs_knn, errs_svm_na1, errs_knn_na1, feature_names_list, feature_nums), fptr, -1)
    
