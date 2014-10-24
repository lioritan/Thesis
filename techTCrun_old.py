from numpy import *
import alg4 as alg2
import bruteforce_propo as compete
import yago
from nltk.tag.stanford import NERTagger
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
import string
import nltk
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
            elif label==last_label:
                construct=construct+'_'+word
            else:
                tokens.append(construct)
                construct=None
                last_label=None
        else:
            if last_label is None:
                tokens.append(word)
            else:
                tokens.append(construct)
                construct=None
                last_label=None
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
        tokens.append(stemmer.stem(lowercased))
    return tokens

    

if __name__=='__main__':    
    
    
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
#    after=time.time()
#    print 'done. time:'
#    print after-before #~1 minute, 20% memory    
    
#    import pickle
#    fptr=open('yago_relationss.pkl','r')  
#    relationss=pickle.load(fptr)
#    fptr.close()
    
#    fptr=open('yago_relationss.pkl','w')
#    pickle.dump(relationss, fptr)
#    fptr.close()
    
    nltk.internals.config_java("C:/Program Files/Java/jre7/bin/java.exe")
    java_path = "C:/Program Files/Java/jre7/bin/java.exe"
    os.environ['JAVAHOME'] = java_path
    
    import pickle
#    stanford_NER= NERTagger('./stanford-ner-2014-06-16/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz',
#    './stanford-ner-2014-06-16/stanford-ner-2014-06-16/stanford-ner.jar')
#    stemmer= PorterStemmer()
    #for all 100 datasets
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_processed/'):
        for filename in filenames:
            fptr=open(path+'/'+filename, 'r')
            datasets.append(pickle.load(fptr))
            fptr.close()
            
#        if len(filenames)==0:
#            print 'first_step'
#            continue
        #print filenames
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
#        fptr=open('techtcdata%d.pkl'%(count),'w')
#        pickle.dump(((trn,trn_lbl),(tst,tst_lbl)), fptr)
#        fptr.close()
#        count+=1
        
    '''
    print 'building dataset'
    before=time.time()
    techTC1_pos=open('./techtc100/Exp_1622_42350/all_pos.txt','r')
    techTC1_neg=open('./techtc100/Exp_1622_42350/all_neg.txt','r')    
    pos1=process_techTC_doc(techTC1_pos)
    neg1=process_techTC_doc(techTC1_neg)
    techTC1_neg.close()
    techTC1_pos.close()
    trn= []
    trn_lbl = []
    tst= []
    tst_lbl= []
    stanford_NER= NERTagger('./stanford-ner-2014-06-16/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz',
    './stanford-ner-2014-06-16/stanford-ner-2014-06-16/stanford-ner.jar')
    stemmer= PorterStemmer()
    is_trn = True
    for doc in pos1:
        if len(doc)==0:
            continue
        new_doc=clean_tokens(tokenize_and_find_named_entities(clean_punctuation(doc), stanford_NER), stemmer)
        if is_trn is True:
            trn.append(new_doc)
            trn_lbl.append(1)
        else:
            tst.append(new_doc)
            tst_lbl.append(1)
        is_trn = not is_trn
    for doc in neg1:
        if len(doc)==0:
            continue
        new_doc=clean_tokens(tokenize_and_find_named_entities(clean_punctuation(doc), stanford_NER), stemmer)
        if is_trn is True:
            trn.append(new_doc)
            trn_lbl.append(0)
        else:
            tst.append(new_doc)
            tst_lbl.append(0)
        is_trn = not is_trn
    #some final stuff:
    trn_lbl= array(trn_lbl, dtype=int)
    tst_lbl= array(tst_lbl, dtype=int)
    after=time.time()
    print 'done. time:'
    print after-before #~11 minutes for 200 docs(~6 per 100), basically no mem
    '''
#    import pickle
#    fptr=open('data1.pkl','r')    
#    ((trn,trn_lbl),(tst,tst_lbl))=pickle.load(fptr)
#    fptr.close()
#    true_trn=trn
#    tru_lbl=trn_lbl
#    
#    trn=true_trn[7:-7]
#    trn_lbl=tru_lbl[7:-7]
#    vld=true_trn[:7]+true_trn[-7:]
#    vld_lbl=hstack((tru_lbl[:7],tru_lbl[-7:]))
#        
#    errs_non_recurse=[]
#    times_non_recurse=[]
#    errs_recurse=[]
#    times_recurse=[]
#    for i in xrange(1, 10, 2): #doesn't seem to matter much between 1/3/5 and 7/9(which are worse for tree)
#        compete.SPLIT_THRESH=i
#        blah11= compete.TreeRecursiveSRLClassifier(true_trn, tru_lbl, relationss, [], True)
#        before=time.time()
#        blah11.train()
#        after=time.time()
#        #print 'done. time:'
#        #print after-before #~80 seconds
#        pred11=array([blah11.predict(x) for x in tst])
#        #print mean(pred11!=tst_lbl) #25% error
#        errs_non_recurse.append(mean(pred11!=tst_lbl))
#        times_non_recurse.append(after-before)
#        
#        alg2.SPLIT_THRESH=i
#        alg2.MAX_DEPTH=2
#        blah4= alg2.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [])
#        before=time.time()
#        blah4.train(vld, vld_lbl)
#        after=time.time()
#        #print 'done. time:'
#        #print after-before #~
#        pred4=array([blah4.predict(x) for x in tst])
#        #print mean(pred4!=tst_lbl)
#        errs_recurse.append(mean(pred4!=tst_lbl))
#        times_recurse.append(after-before)
#        
#    print errs_non_recurse
#    print times_non_recurse
#    print errs_recurse
#    print times_recurse
#    #and run!
#    print 'training regular tree'
#    blah1= alg2.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [], True)
#    before=time.time()
#    blah1.train(vld, vld_lbl)
#    after=time.time()
#    print 'done. time:'
#    print after-before #~80 seconds
#    pred1=array([blah1.predict(x) for x in tst])
#    print mean(pred1!=tst_lbl) #25% error
#    blah11= compete.TreeRecursiveSRLClassifier(true_trn, tru_lbl, relationss, [], True)
#    before=time.time()
#    blah11.train()
#    after=time.time()
#    print 'done. time:'
#    print after-before #~80 seconds
#    pred11=array([blah11.predict(x) for x in tst])
#    print mean(pred11!=tst_lbl) #25% error
##    print 0.246913580247
#    print 'doing someting silly'
#    alg2.MAX_DEPTH=0
#    blah2= alg2.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [])
#    before=time.time()
#    blah2.train(vld, vld_lbl)
#    after=time.time()
#    print 'done. time:'
#    print after-before #~100 seconds
#    pred2=array([blah2.predict(x) for x in tst])
#    print mean(pred2!=tst_lbl)
#    compete.MAX_DEPTH=0
#    blah21= compete.TreeRecursiveSRLClassifier(true_trn, tru_lbl, relationss, [])
#    before=time.time()
#    blah21.train()
#    after=time.time()
#    print 'done. time:'
#    print after-before #~80 seconds
#    pred21=array([blah21.predict(x) for x in tst])
#    print mean(pred21!=tst_lbl) #25% error
#    #6 relations skipped due to size
##    print 0.234567901235
#    print 'training depth 1'
#    alg2.MAX_DEPTH=1
#    blah3= alg2.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [])
#    before=time.time()
#    blah3.train(vld, vld_lbl)
#    after=time.time()
#    print 'done. time:'
#    print after-before #~
#    pred3=array([blah3.predict(x) for x in tst])
#    print mean(pred3!=tst_lbl)
#    compete.MAX_DEPTH=1
#    blah31= compete.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [])
#    before=time.time()
#    blah31.train()
#    after=time.time()
#    print 'done. time:'
#    print after-before #~80 seconds
#    pred31=array([blah31.predict(x) for x in tst])
#    print mean(pred31!=tst_lbl) #25% error
#    print 'training full thing'
#    alg2.MAX_DEPTH=2
#    blah4= alg2.TreeRecursiveSRLClassifier(trn, trn_lbl, relationss, [])
#    before=time.time()
#    blah4.train(vld, vld_lbl)
#    after=time.time()
#    print 'done. time:'
#    print after-before #~
#    pred4=array([blah4.predict(x) for x in tst])
#    print mean(pred4!=tst_lbl)
#    print 'training full thing'
    #problem relations: reverse_islocatedin(90K), reverse_hasgender(>100K)
    #a bit less of an issue: reverse_wasbornin(30K), reverse_iscitizenof(25K), reverse_diedin(13K)
    #30K->2 minutes. 261->no IG but simple shit, 255 with IG(so same...)
    