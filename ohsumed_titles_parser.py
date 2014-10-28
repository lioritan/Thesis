# -*- coding: utf-8 -*-
"""
Created on Wed Sep 17 16:05:41 2014

@author: liorf
"""
import cPickle
import string
from nltk.corpus import stopwords
import re

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

if __name__=='__main__':
    with open('med_relations.pkl','rb') as fptr:
        (relations, relation_entities)= cPickle.load(fptr)  
    fptr=open('ohsumed.91.txt','r') #24,122 relevant articles
    
    #if line starts with .I ->new message
    articles=[]
    line=fptr.readline()
    latest_article= None
    tags=''
    while len(line)>0 : #not EOF
        if line.startswith('.I'): #new article
            if latest_article is not None:
                paper_title_raw= clean_1(latest_article[0]).lower()
                stemmed_and_nerd= medical_NER(suffixes_stem(paper_title_raw), relation_entities)
                latest_article= (clean_2(stemmed_and_nerd.split(' ')), latest_article[1])
                articles.append(latest_article)
            latest_article=None
        if line.startswith('.M'): #tags. next few lines are ';'-seperated categories
            tags=''
            line=fptr.readline()
            while not line.startswith('.'):
                tags+=line.replace('.\n','')
                line=fptr.readline()
            continue #work on new line
        if line.startswith('.T'): #title-we want it. it's in the next line
            line=fptr.readline()
            tag_list= tags.split(';')
            tag_list= [a for a in tag_list if a.find('/')!=-1]
            #we want only the ones with '/' in them, and we need to work smart
            latest_article= (line.replace('.\n',''), tag_list)
        if latest_article is not None and line.startswith('.W'):
            #has an abstract-do not want this article!
            latest_article= None 
        line=fptr.readline()
    fptr.close()
    
    Note: I need to mention the MeSH data dictionary thing
    mapping= {} #map mesh term to higher level mesh term
    with open('mtrees2015.bin','r') as fptr:
        for line in fptr.readlines():
            splitted= line.split(';')
            top_level= splitted[1].split('.')[0].strip()
            mapping[splitted[0]]= top_level
            
    articles_fixed= []
    for article in articles:
        new_tags= set()
        for tag in article[1]:
            #clean whitespaces, remove all after first / and match
            fixed_tag= tag.split('/')[0].strip()
            new_tags.add(mapping.get(fixed_tag, fixed_tag))
        articles_fixed.append((article[0], new_tags))
        
    #now we can easily take top 20-30 cats... top 20 have>1000
    #we can also go for C01 to C26... and only take those with over 500-14 cats (cutoff if more. mby 750(12 cats)/800(11 cats)/850(10 cats) better cutoff?)
    reverse_thing={}
    for art in articles_fixed:
        for cat in art[1]:
            if not reverse_thing.has_key(cat):
                reverse_thing[cat]= []
            reverse_thing[cat]+=[art[0]]
    final_articles=[]
    tagging=[]
    for cat in ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09']+['C'+str(x) for x in range(10, 21)+range(22,27)]:
        if len(reverse_thing[cat]) < 850:
            continue
        for i, page in enumerate(reverse_thing[cat]):
            if i> 850: #cutoff
                break
            final_articles.append(page)
            tagging.append(int(cat[1:]))
            
    with open('ohsumed_titles_parsed_complete.pkl', 'wb') as fptr:
        cPickle.dump((final_articles, tagging), fptr, -1)