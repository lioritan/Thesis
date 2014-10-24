from numpy import *
#import alg4 as alg2
#import bruteforce_propo as compete
#import alg4geq as bullcrap
#import alg4geq2 as bullcrap2
import alg6 as godfish
import yago
#from nltk.tag.stanford import NERTagger
#from nltk.corpus import stopwords
#from nltk.stem.porter import PorterStemmer
#from nltk.stem.snowball import EnglishStemmer
import string
#import nltk
import os
import time


def process_techTC_doc(fptr):
    '''turn to documents.
    Each <dmoz_doc> is one example doc, contains several <dmoz_subdoc>'''
    res=[]
    line=fptr.readline()
    while len(line)>0:#not EOF
        if str.find(line, '<dmoz_doc>')!=-1: #start of new doc
            tmp=''
            line=fptr.readline()#goto id=x line
            line=fptr.readline()#do nothing with id=x line, goto text
            while str.find(line, '</dmoz_doc>')==-1:#not end of doc
                if str.find(line, 'dmoz_subdoc')!=-1 or str.find(line, 'Title:')!=-1:
                    #ignore tag lines and page title
                    line=fptr.readline()
                    continue
                tmp=tmp+line
                line=fptr.readline()
            res.append(tmp)
            line=fptr.readline() #move to next doc
        else:
            print 'error!'
            print line
            exit()
    return res
    
def clean_punctuation(text):
    '''replace punctuation with whitespace'''
    return text.translate(string.maketrans(string.punctuation, ' '*len(string.punctuation)))

def tokenize_and_find_named_entities(text, NERTagger_obj):
    #return NERTagger_obj.tag()
    tokenized_text= NERTagger_obj.tag(text.split())
    tokens=[]
    construct=None
    last_label=None
    for word,label in tokenized_text:
        if label!='O':
            if last_label is None:
                construct=word
                last_label=label
                continue
            elif label==last_label:
                #tokens.append(construct)#TODO:add partial things!
                construct=construct+'_'+word
                continue
        if last_label is not None:
            tokens.append(construct)
        tokens.append(word)
        construct=None
        last_label=None
        
    if last_label is not None:#edge case
        tokens.append(construct)
    return tokens

def clean_tokens(tokenized_text, stemmer):
    '''lowercase->stopword removal->stemming'''
    tokens= []
    for word in tokenized_text:
        lowercased= word.lower()
        if lowercased in stopwords.words('english'):
            continue
        if str.find(lowercased, '_')!=-1:
            tokens.append(lowercased)
            continue
        #tokens.append(stemmer.stem(lowercased))
        tokens.append(stemmer.stem(lowercased).encode())#and also stemming!2 hit combo!

    return tokens

def calc_bep(predictions, labels):
    '''precision-recall break even point is the value for which 
    precision (predict true and got right/predicted true) and
    recall (predict true and got right/ all true) are the same.
    between 0 and 1, higher is better.
    
    This should be calculated per category and averaged.
    Relevant ML because gives you a point to tune parameters with respect to?
    also if clssfiy by threshold-now you know which one to choose
    
    
    in my case probably want accuracy, possibly also precsion, recall, f-measure
    '''
    pass

if __name__=='__main__':    
    
    MAX_SPLIT_FACTOR= 1000 #any reverse relation with over 1:1000 multiplicity is bad...

#    print 'extracting yago...'
#    before=time.time()
#    ptr1 = open('..\yago2s_tsv\yagoFacts.tsv','r')
#    facts1 = yago.read_and_strip_tokens(ptr1)
#    ptr1.close()
#    relationss = yago.turn_to_relations(facts1, None)
#    del facts1
#    for key in relationss.keys():
#        new_key= 'reverse_'+key
#        relationss[new_key]= {}
#        for (a,b) in relationss[key].items():
#            if relationss[new_key].has_key(b):
#                relationss[new_key][b].append(a)
#                continue
#            relationss[new_key][b]= [a]
#        val_lens=array([len(val) for val in relationss[new_key].values()])
#        if max(val_lens)>MAX_SPLIT_FACTOR:
#            relationss.pop(new_key)
#    after=time.time()
#    print 'done. time:'
#    print after-before #~1 minute, 20% memory    
    
#    import pickle
#    fptr=open('yago_relationss.pkl','r')  
#    relationss=pickle.load(fptr)
#    fptr.close()
#    
#    fptr=open('yago_relationss.pkl','w')
#    pickle.dump(relationss, fptr)
#    fptr.close()
#    ptr1 = open('..\yago2s_tsv\yagoSimpleTypes.tsv','r')
#    type_facts1 = yago.read_and_strip_tokens(ptr1)
#    ptr1.close()
#    ptr1 = open('..\yago2s_tsv\yagoImportantTypes.tsv','r')
#    type_facts2 = yago.read_and_strip_tokens(ptr1)
#    ptr1.close()
#    ptr1 = open('..\yago2s_tsv\yagoSimpleTaxonomy.tsv','r')
#    taxonomy_facts = yago.read_and_strip_tokens(ptr1) #take rdfs:subclassOf as type closure?
#    ptr1.close()
#    print 'let it rip!'
#    type_rel = yago.create_type_relation(type_facts1, type_facts2, taxonomy_facts)
#    print 'done'
#    del type_facts1
#    del type_facts2
#    del taxonomy_facts
#    relationss['type']=type_rel

#    import pickle
#    fptr=open('type_rel1.pkl','r')  
#    type_rel=pickle.load(fptr)
#    relationss['type']=type_rel
#    fptr.close()
    
    import cPickle as pickle
    fptr=open('yago_relationss_full.pkl', 'rb')
    relationss= pickle.load(fptr)
    fptr.close()
    print 'yago loaded'

#    for path,dirnames, filenames in os.walk('./techtc_processed/'):
#        for filename in filenames:
#            fptr=open(path+'/'+filename, 'r')
#            data=pickle.load(fptr)
#            fptr.close()
#            
#            fptr=open('./techtc_processed_fixed/'+filename,'wb')
#            pickle.dump(data,fptr)
#            fptr.close()
    
#    for i,((trn,trn_lbl),(tst,tst_lbl)) in enumerate(datasets):
#        fptr=open('./techtc_processed_fixed/data%d.pkl'%(i), 'wb')
#        pickle.dump(((trn,trn_lbl),(tst,tst_lbl)), fptr)
#        fptr.close()
            
    
#    nltk.internals.config_java("C:/Program Files/Java/jre7/bin/java.exe")
#    java_path = "C:/Program Files/Java/jre7/bin/java.exe"
#    os.environ['JAVAHOME'] = java_path
    
#    stanford_NER= NERTagger('./stanford-ner-2014-06-16/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz'
#    , './stanford-ner-2014-06-16/stanford-ner-2014-06-16/stanford-ner.jar')
#    #stemmer= PorterStemmer()
#    stemmer=EnglishStemmer()
#    #for all 100 datasets
#    count=0
#    for path,dirnames,filenames in os.walk('./techtc100/'):            
#        if len(filenames)==0:
#            print 'first_step'
#            continue
#        print filenames
#        neg_file=open(path+'/'+filenames[0], 'r')#first file always the negative
#        pos_file=open(path+'/'+filenames[1], 'r')#second file always the positive
#        pos1=process_techTC_doc(pos_file)
#        neg1=process_techTC_doc(neg_file)
#        pos_file.close()
#        neg_file.close()
#        trn= []
#        trn_lbl = []
#        tst= []
#        tst_lbl= []
#        is_trn = True
#        for i,doc_set in enumerate([pos1, neg1]):
#            for doc in doc_set:
#                if len(doc)==0:
#                    continue
#                new_doc=clean_tokens(tokenize_and_find_named_entities(clean_punctuation(doc), stanford_NER), stemmer)
#                if is_trn is True:
#                    trn.append(new_doc)
#                    trn_lbl.append(1 if i==0 else 0)
#                else:
#                    tst.append(new_doc)
#                    tst_lbl.append(1 if i==0 else 0)
#                is_trn= not is_trn
#        trn_lbl= array(trn_lbl, dtype=int)
#        tst_lbl= array(tst_lbl, dtype=int)
#        fptr=open('./techtc_processed/techtcdata%d.pkl'%(count),'w')
#        pickle.dump(((trn,trn_lbl),(tst,tst_lbl)), fptr)
#        fptr.close()
#        count+=1
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_processed_fixed/'):
        filenames.sort()
        for filename in filenames:
            fptr=open(path+'/'+filename, 'rb')
            datasets.append(pickle.load(fptr))
            fptr.close()
    
#    datasets=[]
#    res_3=[]
#    for path,dirnames, filenames in os.walk('./techtc_processed2/'):
#        for filename in filenames:
#            fptr=open(path+'/'+filename, 'r')
#            datasets.append(pickle.load(fptr))
#            fptr.close()
#           
            
#    ffff.ffff()    
    count=0
    res_7=[]
    for ((trn, trn_lbl),(tst,tst_lbl)) in datasets:
        print count
        count+=1
#        if count<=90:#each one goes different
#            continue

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
        
        
        for i in [3,7]: #doesn't seem to matter much between 1/3/5 and 7/9(which are worse for tree)
            
            blah11= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0,0,i, True)
            blah11.train()#non recursive
            pred11=array([blah11.predict(x) for x in tst])
            errs_non_recurse.append(mean(pred11!=tst_lbl)) 
            vars_non.append(std(pred11!=tst_lbl))
            
            blah12= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],0,0,i)
            blah12.train()#non recursive
            pred12=array([blah12.predict(x) for x in tst])
            errs_rel.append(mean(pred12!=tst_lbl)) 
            vars_rel.append(std(pred12!=tst_lbl))
            
            before=time.time()
            bc= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(1**2), 1, i)
            bc.train()#non recursive
            predx=array([bc.predict(x) for x in tst])
            hug1.append(mean(predx!=tst_lbl)) 
            vars_.append(std(predx!=tst_lbl))
            print time.time()-before
            
            
            before=time.time()
            bc2= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(2**2), 2, i)
            bc2.train()#recursive, somewhere around best only...
            print time.time()-before
            predy=array([bc2.predict(x) for x in tst])
            hug2.append(mean(predy!=tst_lbl)) 
            vars_2.append(std(predy!=tst_lbl))
            
            #debug me!!
            before=time.time()
            bc3= godfish.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [],100*(3**2), 3, i)
            bc3.train()#recursive, somewhere around best only...
            print time.time()-before
            predz=array([bc3.predict(x) for x in tst])
            hug3.append(mean(predz!=tst_lbl)) 
            vars_3.append(std(predz!=tst_lbl))
            
            #Note: 100*(d**2) barely scales to 4, and would likely fail for 5
            
        res_7.append((blah11, blah12, bc, bc2, bc3
        ,errs_non_recurse, errs_rel, hug1, hug2, hug3
        ,vars_non, vars_rel, vars_, vars_2, vars_3))
        
    fptr=open('results_techtc_1.pkl','wb')
    for rec in res_7:
        godfish.clean_tree_for_pickle(rec[0].query_tree)
        godfish.clean_tree_for_pickle(rec[1].query_tree)
        godfish.clean_tree_for_pickle(rec[2].query_tree)
        godfish.clean_tree_for_pickle(rec[3].query_tree)
        godfish.clean_tree_for_pickle(rec[4].query_tree)
        
    pickle.dump(res_7, fptr)
    fptr.close()
    
