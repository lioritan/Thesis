
from sklearn.datasets import fetch_20newsgroups
from numpy import *
import alg2
import yago

if __name__=='__main__':    
    newsgroups_trn = fetch_20newsgroups(subset='train', remove=('headers', 'footers', 'quotes'))
    newsgroups_tst = fetch_20newsgroups(subset='test', remove=('headers', 'footers', 'quotes'))
    #either 5-fold cross validation or use built-in train/test divide...
    
    #Needs cleaning: remove \n, toLowercase, issues with named entity recognition (Pens, Devils, Jersey) 
    #stuff like misspelings...

    #take 1000 of one category and 50 of all others and do train and shit
    #category=17, has 940
    newsgroups_trn.target[find(newsgroups_trn.target!=17)]=0
    newsgroups_trn.target[find(newsgroups_trn.target==17)]=1
    newsgroups_tst.target[find(newsgroups_tst.target!=17)]=0
    newsgroups_tst.target[find(newsgroups_tst.target==17)]=1
    
    print 'extracting yago...'
    ptr1 = open('..\yago2s_tsv\yagoFacts.tsv','r')
    facts1 = yago.read_and_strip_tokens(ptr1)
    ptr1.close()
    other_rels = yago.turn_to_relations(facts1, None)
    del facts1
    print 'done'
    
    print 'training non-recursive...'
    trn_fixed = array([s.lower().replace('\n','').split(' ') for s in newsgroups_trn.data])
    tst_fixed = array([s.lower().replace('\n','').split(' ') for s in newsgroups_tst.data])
    clf1 = alg2.TreeRecursiveSRLClassifier(trn_fixed,
                                           newsgroups_trn.target, other_rels, [], True)
    clf1.train()
    print 'done!'
    print 'accuracy of non-recursive, non-relational:'
    trn_acc1 = mean(array([clf1.predict(x) for x in trn_fixed], dtype=int)==newsgroups_trn.target.astype(int))
    tst_acc1 = mean(array([clf1.predict(x) for x in tst_fixed], dtype=int)==newsgroups_tst.target.astype(int))
    print trn_acc1,tst_acc1 
    
    #TODO: some unicode issue when trying relations (either word is not unicode or yago...)
    print 'training recursive...'
    clf2 = alg2.TreeRecursiveSRLClassifier(trn_fixed,
                                           newsgroups_trn.target, other_rels, [])
    clf2.train()
    print 'done!'
    print 'accuracy of recursive+relational, 2 lvls deep:'
    trn_acc2 = mean(array([clf2.predict(x) for x in trn_fixed], dtype=int)==newsgroups_trn.target.astype(int))
    tst_acc2 = mean(array([clf2.predict(x) for x in tst_fixed], dtype=int)==newsgroups_tst.target.astype(int))
    print trn_acc2,tst_acc2
    
    