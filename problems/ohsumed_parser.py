# -*- coding: utf-8 -*-
"""
Created on Sun Sep 07 14:18:37 2014

@author: liorf
"""

#parse documents from OHSUMED-stopword elimination,stemming. Maybe need NER? NER for diseases/treatments?
#do seperate title/abstract
#5 sets of 10 categories
import os
import string
from nltk.corpus import stopwords
import nltk
import re


PATH='./ohsumed-first-20000-docs/ohsumed-first-20000-docs/'

suffix_s=re.compile('s$|s ')
suffix_ies=re.compile('ies$|ies ')
def suffixes_stem(text):  
    #mostly right, sufficient for us. this should come before punctuation removal but after lowercase
    step1= text.replace("'s",'')
    step2= suffix_ies.sub(r'y ', step1)
    return step2
    return suffix_s.sub(r' ', step2)

def clean_1(text):
    '''replace punctuation with whitespace'''
    return text.translate(string.maketrans(string.punctuation, ' '*len(string.punctuation)))

def clean_2(tokenized_text):
    '''lowercase->stopword removal->stemming'''
    tokens= []
    for word in tokenized_text:
        lowercased= word.lower()
        if lowercased in stopwords.words('english'): #bad idea?
            continue
        if lowercased in ['\n', '']:
            continue
        tokens.append(lowercased)
#        if str.find(lowercased, '_')!=-1:
#            tokens.append(lowercased)
#            continue
        #tokens.append(stemmer.stem(lowercased))
#        tokens.append(stemmer.stem(lowercased).encode())#and also stemming!2 hit combo!

    return tokens

suffix_s2=re.compile('s$')    
def medical_NER(text, entities): #does this require extra cleaning? like stopwords?
    '''new idea: has window. add word to window. if window=entity,clear window and add entity and continue.
    if window is start of entity, continue.
    if window is not start of entity, pop first word into text and ask again'''
    new_text=''
    window= ''
    for word in text.lower().split(' '):
        window+= word
        re_ask= True
        while re_ask:
            re_ask= False #if not last case, only one loop
            is_candidate= False
            for entity in entities:
                if window==entity or entity==suffix_s2.sub(r'', window):
                    new_text+= entity+' '
                    window= ''
                    break
                if entity.startswith(window):
                    is_candidate= True
            if len(window)==0:
                break
            if is_candidate:
                window+= '_'
                break
            window_words= window.split('_')
            new_text+= window_words[0]+' '
            if len(window_words)==1:
                window= ''
                break #next word...
            re_ask= True              
            window= reduce(lambda x,y: x+'_'+y, window_words[1:])
    while len(window)> 0:
        is_candidate= False
        for entity in entities:
            if window==entity:
                new_text+= entity+' '
                window= ''
                break
        window_words= window.split('_')
        new_text+= window_words[0]+' '
        if len(window_words)==1:
            window= ''
            break 
        window= reduce(lambda x,y: x+'_'+y, window_words[1:])

    return new_text

def medical_NER2(text): #use metaMAP
    pass

def load_all_from_folder(path, entities):
    docs=[]
    categories=[]
    for path,_,filenames in os.walk(path):
        if len(filenames)==0:
            continue
        category=int(path[-2:], base=10) #two last elements in path are digits for category
        for filename in filenames:
            #print path, filename
            fptr=open(path+'/'+filename,'r')
            title=fptr.readline()
            content=''
            for line in fptr.readlines():
                content+=line
            fptr.close()
            #processing:
            title=clean_2(medical_NER(suffixes_stem(clean_1(title)), entities).split(' '))
            content=clean_2(medical_NER(suffixes_stem(clean_1(content)), entities).split(' '))
            pass
            
            docs.append((title,content))
            categories.append(category)
            if len(categories)%1000==0:
                print len(categories)
            
    return docs, categories

if __name__=='__main__':
    train_folder=PATH+'training/'
    test_folder=PATH+'test/'
    import cPickle
#    nltk.internals.config_java("C:/Program Files/Java/jre7/bin/java.exe")
#    java_path = "C:/Program Files/Java/jre7/bin/java.exe"
#    os.environ['JAVAHOME'] = java_path
    
    #    stanford_NER= NERTagger('./stanford-ner-2014-06-16/stanford-ner-2014-06-16/classifiers/english.all.3class.distsim.crf.ser.gz'
#    , './stanford-ner-2014-06-16/stanford-ner-2014-06-16/stanford-ner.jar')
#    stemmer=EnglishStemmer()
    with open('med_relations.pkl','rb') as fptr:
        (relations, entities)= cPickle.load(fptr)   
    
    (trn, trn_lbl)=load_all_from_folder(train_folder, entities)
    (tst, tst_lbl)=load_all_from_folder(test_folder, entities)
    #1)pick 5 sets of 10 random categories (for a start, take categories 1,4,6,8,10,12,14,20,21,23 (standard split))
    #2)for each set, make all 1v1 problems, build predictors(45 predictors)
    #    count votes for each predictor, category with most votes is tag (keep candidate list)
    
    fptr=open('ohsumed_dataset_parsed.pkl','wb')
    cPickle.dump(((trn,trn_lbl),(tst,tst_lbl)),fptr,-1)
    fptr.close()
    
    
    