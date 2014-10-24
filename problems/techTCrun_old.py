from numpy import *

import alg6 as godfish
import alg5_workstypes as alg
import string
import os
import time

if __name__=='__main__':    
        
    import cPickle as pickle
    fptr=open('yago_relationss_full.pkl', 'rb')
    relationss= pickle.load(fptr)
    fptr.close()
    print 'yago loaded'
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_processed_fixed/'):
        filenames.sort()
        for filename in filenames:
            fptr=open(path+'/'+filename, 'rb')
            datasets.append(pickle.load(fptr))
            fptr.close()
    
    count=0
    res_7=[]
    for ((trn, trn_lbl),(tst,tst_lbl)) in datasets:
        print count
        count+=1
        if count>15:#each one goes different
            continue
        
        #make validation
        true_trn=trn
        tru_lbl=trn_lbl
        
        trn=true_trn[7:-7]
        trn_lbl=tru_lbl[7:-7]
        vld=true_trn[:7]+true_trn[-7:]
        vld_lbl=hstack((tru_lbl[:7],tru_lbl[-7:]))        
        
        errs_non_recurse=[]
        errs_rel=[]
        hug1=[]
        hug2=[]
        vars_non=[]
        vars_=[]
        vars_2=[]
        vars_rel=[]
        
        
        for i in [3,7]: #doesn't seem to matter much between 1/3/5 and 7/9(which are worse for tree)
            
            alg.SPLIT_THRESH= i
            alg.MAX_DEPTH= 0
            blah11= alg.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0, True)
            blah11.train(vld, vld_lbl)#non recursive
            pred11=array([blah11.predict(x) for x in tst])
            errs_non_recurse.append(mean(pred11!=tst_lbl)) 
            vars_non.append(std(pred11!=tst_lbl))
            
            alg.MAX_DEPTH= 0
            blah12= alg.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0)
            blah12.train(vld, vld_lbl)#non recursive
            pred12=array([blah12.predict(x) for x in tst])
            errs_rel.append(mean(pred12!=tst_lbl)) 
            vars_rel.append(std(pred12!=tst_lbl))

            alg.MAX_DEPTH= 1
            before=time.time()
            bc= alg.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],5*(1**2))
            bc.train(vld, vld_lbl)#non recursive
            predx=array([bc.predict(x) for x in tst])
            hug1.append(mean(predx!=tst_lbl)) 
            vars_.append(std(predx!=tst_lbl))
            print time.time()-before
            
            
            alg.MAX_DEPTH= 2
            before=time.time()
            bc2= alg.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],5*(2**2))
            bc2.train(vld, vld_lbl)#recursive, somewhere around best only...
            print time.time()-before
            predy=array([bc2.predict(x) for x in tst])
            hug2.append(mean(predy!=tst_lbl)) 
            vars_2.append(std(predy!=tst_lbl))
            
            #Note: 100*(d**2) barely scales to 4, and would likely fail for 5
        a=(blah11, blah12, bc, bc2
        ,errs_non_recurse, errs_rel, hug1, hug2
        ,vars_non, vars_rel, vars_, vars_2)
        res_7.append(a)
        godfish.clean_tree_for_pickle(blah11.query_tree)
        godfish.clean_tree_for_pickle(blah12.query_tree)
        godfish.clean_tree_for_pickle(bc.query_tree)
        godfish.clean_tree_for_pickle(bc2.query_tree)
        with open('results%d.pkl'%(count),'wb') as fptr:
            pickle.dump(a, fptr, -1)
        
    with open('final_res15.pkl','wb') as fptr:
        pickle.dump(res_7, fptr, -1)
