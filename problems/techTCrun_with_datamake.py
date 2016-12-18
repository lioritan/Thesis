from numpy import *
#import alg4 as alg2
#import bruteforce_propo as compete
#import alg4geq as bullcrap
#import alg4geq2 as bullcrap2
#import alg6 as godfish
#import yago
#from nltk.tag.stanford import NERTagger
#from nltk.corpus import stopwords
#from nltk.stem.porter import PorterStemmer
#from nltk.stem.snowball import EnglishStemmer
import string
#import nltk
import os
import time
import cPickle

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
import re    
def clean_my_doc(doc):
    no_lines=doc.replace('\n','')
    no_pngs = re.sub("\[.*?\]","" , no_lines)
    return no_pngs

def fix_double_url_string(string_to_fix):
    return string_to_fix.decode('unicode_escape').decode('unicode_escape').encode('utf-8')
    
import requests    

def get_text_entities_from_site(doc):
    res_json = requests.post("https://gate.d5.mpi-inf.mpg.de/aida/service/disambiguate", data={'text':doc})
    start_ind = res_json.content.find('"allEntities":[')+15
    end_ind = res_json.content.find('],"entityMetadata"')
    if start_ind == end_ind:
        return []
    return [fix_double_url_string(entity) for entity in res_json.content[start_ind:end_ind].replace('"','').split(',')]
    
if __name__=='__main__':    
    
    MAX_SPLIT_FACTOR= 1000 #any reverse relation with over 1:1000 multiplicity is bad...
    

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
#        for i,doc_set in enumerate([pos1, neg1]):
#            alldocs=[]
#            alldoc_lbls=[]
#            for doc in doc_set:
#                if len(doc)==0:
#                    continue
#                alldocs.append(doc)
#                alldoc_lbls.append(1 if i==0 else 0)
#            trn_inds = random.choice(arange(len(alldocs)),size=int(len(alldocs)*3/4),replace=False)
#            for j,doc in enumerate(alldocs):
#                if j in trn_inds:
#                    trn.append(doc)
#                    trn_lbl.append(alldoc_lbls[j])
#                else:
#                    tst.append(doc)
#                    tst_lbl.append(alldoc_lbls[j])
                
#        trn_lbl= array(trn_lbl, dtype=int)
#        tst_lbl= array(tst_lbl, dtype=int)
#        fptr=open('./techtc_pkls/techtc_raw%d.pkl'%(count),'wb')
#        cPickle.dump(((trn,trn_lbl),(tst,tst_lbl)), fptr, -1)
#        fptr.close()
#        count+=1
            
    datasets=[]
    for path,dirnames, filenames in os.walk('./techtc_pkls/'):
        filenames.sort()
        for i,filename in enumerate(filenames):
            if i<28:
                continue
            fptr=open(path+'/'+filename, 'rb')
            ((trn,trn_lbl),(tst,tst_lbl)) = cPickle.load(fptr)
            fptr.close()
            trn_ents=[]
            tst_ents=[]
            print i
            for j,doc in enumerate(trn):
                print '    %d'%j
                trn_ents.append(get_text_entities_from_site(doc))
            for doc in tst:
                tst_ents.append(get_text_entities_from_site(doc))
            with open(path+'/entities_'+filename, 'wb') as fptr2:
                cPickle.dump(((trn_ents,trn_lbl),(tst_ents,tst_lbl)), fptr2, -1)
            time.sleep(1)
            