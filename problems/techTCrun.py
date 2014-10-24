from numpy import *
#import bruteforce_propo as compete
import alg6 as godfish
#import alg7 as compete
import bruteforce_propo as compete
import yago
import string
import os
import time

if __name__=='__main__':    
        
    import cPickle as pickle
#    fptr=open('yago_relationss_smaller.pkl', 'rb')
#    relationss= pickle.load(fptr)
#    fptr.close()
#    print 'yago loaded'
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
            
#    datasets=[]
#    for path,dirnames, filenames in os.walk('./techtc_processed_fixed/'):
#        filenames.sort()
#        for filename in filenames:
#            fptr=open(path+'/'+filename, 'rb')
#            datasets.append(pickle.load(fptr))
#            fptr.close()
#    
    count=0
    res_7=[]
    for ((trn, trn_lbl),(tst,tst_lbl)) in datasets:
        print count
        count+=1
        if count>11:#each one goes different
            continue
        
        errs_non_recurse=[]
        errs_rel=[]
        hug1=[]
        hug2=[]
        hug3=[]
        vars_non=[]
        vars_=[]
        vars_2=[]
        vars_3=[]
        vars_rel=[]
        
        
        for i in [3]: #switch back to [3,7] later. doesn't seem to matter much between 1/3/5 and 7/9(which are worse for tree)
            
#            blah11= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0,0,i, True)
#            blah11.train()#non recursive
#            pred11=array([blah11.predict(x) for x in tst])
#            errs_non_recurse.append(mean(pred11!=tst_lbl)) 
#            vars_non.append(std(pred11!=tst_lbl))
#            
#            blah12= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0,0,i)
#            blah12.train()#non recursive
#            pred12=array([blah12.predict(x) for x in tst])
#            errs_rel.append(mean(pred12!=tst_lbl)) 
#            vars_rel.append(std(pred12!=tst_lbl))
#            
#            before=time.time()
#            bc= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(1**2), 1, i)
#            bc.train()#non recursive
#            predx=array([bc.predict(x) for x in tst])
#            hug1.append(mean(predx!=tst_lbl)) 
#            vars_.append(std(predx!=tst_lbl))
#            print time.time()-before
#            
#            
#            before=time.time()
#            bc2= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(2**2), 2, i)
#            bc2.train()#recursive, somewhere around best only...
#            print time.time()-before
#            predy=array([bc2.predict(x) for x in tst])
#            hug2.append(mean(predy!=tst_lbl)) 
#            vars_2.append(std(predy!=tst_lbl))
            
            blah12= compete.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0,0,i,True)
            blah12.train()#non recursive
            pred12=array([blah12.predict(x) for x in tst])
            errs_rel.append(mean(pred12!=tst_lbl)) 
            vars_rel.append(std(pred12!=tst_lbl))
            
            before=time.time()
            bc= compete.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(1**2), 0, i)
            bc.train()#non recursive
            predx=array([bc.predict(x) for x in tst])
            hug1.append(mean(predx!=tst_lbl)) 
            vars_.append(std(predx!=tst_lbl))
            print time.time()-before
            
            
            before=time.time()
            bc2= compete.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(2**2), 1, i)
            bc2.train()#recursive, somewhere around best only...
            print time.time()-before
            predy=array([bc2.predict(x) for x in tst])
            hug2.append(mean(predy!=tst_lbl)) 
            vars_2.append(std(predy!=tst_lbl))
            #Note: 100*(d**2) barely scales to 4, and would likely fail for 5
            #2*(d**2)
            a=(blah12, bc, bc2, bc3
            ,errs_rel, hug1, hug2, hug3
            ,vars_rel, vars_, vars_2, vars_3)
            res_7.append(a)
            fgfgfk.g()
            
            before=time.time()
            bc3= compete.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(3**2), 3, i)
            bc3.train()#recursive, somewhere around best only...
            print time.time()-before
            predz=array([bc3.predict(x) for x in tst])
            hug3.append(mean(predz!=tst_lbl)) 
            vars_3.append(std(predz!=tst_lbl))
            #Note: 100*(d**2) barely scales to 4, and would likely fail for 5
        
#        a=(blah11, blah12, bc, bc2
#        ,errs_non_recurse, errs_rel, hug1, hug2
#        ,vars_non, vars_rel, vars_, vars_2)
#        res_7.append(a)
#        godfish.clean_tree_for_pickle(blah11.query_tree)
#        godfish.clean_tree_for_pickle(blah12.query_tree)
#        godfish.clean_tree_for_pickle(bc.query_tree)
#        godfish.clean_tree_for_pickle(bc2.query_tree)
#        with open('results%d.pkl'%(count),'wb') as fptr:
#            pickle.dump(a, fptr, -1)
        a=(blah12, bc, bc2, bc3
        ,errs_rel, hug1, hug2, hug3
        ,vars_rel, vars_, vars_2, vars_3)
        res_7.append(a)
        godfish.clean_tree_for_pickle(blah12.query_tree)
        godfish.clean_tree_for_pickle(bc.query_tree)
        godfish.clean_tree_for_pickle(bc2.query_tree)
        godfish.clean_tree_for_pickle(bc3.query_tree)
        with open('results%d.pkl'%(count),'wb') as fptr:
            pickle.dump(a, fptr, -1)
#        
    with open('final_res11.pkl','wb') as fptr:
        pickle.dump(res_7, fptr, -1)
    
