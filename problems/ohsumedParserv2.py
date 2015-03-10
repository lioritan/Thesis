# -*- coding: utf-8 -*-
"""
Created on Mon Mar 09 16:51:16 2015

@author: liorf
"""

import requests
import string

def find_wiki_tags(text): #need to wait like 1 second between requests. also, send RAW text!
    reply= requests.get('http://wikipedia-miner.cms.waikato.ac.nz/services/wikify?',
                        params={'source':text,'responseFormat':'json'})
    reply_as_json= reply.json()
    entities= reply_as_json['detectedTopics']
    new_doc= reply_as_json['wikifiedDocument']
    
    entities= []    
    for entity_dict in entities:
        raw_entity= entity_dict['title']
        entities.append(process_raw_entity(raw_entity))
    
    return entities, new_doc

def process_raw_entity(entity):
    no_punc= entity.translate(string.maketrans("",""), string.punctuation)
    return no_punc.lower().replace(' ','_')
    
import re    
suffix_s=re.compile('s$|s ')
suffix_ies=re.compile('ies$|ies ')
def suffixes_stem(text):  
    #mostly right, sufficient for us. this should come before punctuation removal but after lowercase
    step1= text.replace("'s",'')
    step2= suffix_ies.sub(r'y ', step1)
    return step2

from nltk.corpus import stopwords
find_tags= re.compile('\[\[([^\]\|]+)(\|[^\]]+)?\]\]')
def newdoc_to_words(text):
    #This line finds tag, replaces with entity (take the second one=raw if more than one, and replaces spaces with _ so we got NER.
    fixed_entities_string= find_tags.sub(lambda x:x.group(1 if x.group(2) is None else 2).replace(' ','_'), text).replace('|','')
    #now, we need to stem,lowercase,remove punctuation[except _],remove stopwords
    no_punct=  fixed_entities_string.translate(string.maketrans("",""), string.punctuation.replace('_',''))
    lowercased= no_punct.lower()
    words= []
    for word in lowercased.split(' '):
        if word in stopwords.words('english'): #bad idea?
            continue
        if word in ['\n', '']:
            continue
        if word.find('_')!=-1: #no stemming entities!
            words.append(word)
            continue
        words.append(suffixes_stem(word))
    return words  

def build_relations_from_raw_entities(processed_entities_list, fact_file):
    sorted_entities= sorted(frozenset(processed_entities_list))
    #get a list of entities, get the relevant facts, build a table
    i=0
    relations= {}
    with open(fact_file, 'rb') as fptr:
        for line in fptr:
            rdf_triplet=line.split('\t')[:3]
            entity= process_raw_entity(rdf_triplet[0])
            while entity > sorted_entities[i]: #new entity is past the current one, so go forward
                i+=1
            if entity < sorted_entities[i]: #entity not relevant
                continue
            #so now, we got a match!
            if not relations.has_key(rdf_triplet[1]):
                relations[rdf_triplet[1]]= {}
            if relations[rdf_triplet[1]].has_key(rdf_triplet[0]):
                relations[rdf_triplet[1]][rdf_triplet[0]].add(rdf_triplet[2])
            else:
                relations[rdf_triplet[1]][rdf_triplet[0]]= set([rdf_triplet[2]])
    return relations 

import cPickle
import time
if __name__=='__main__':
    with open('ohsumed_titles_raw.pkl', 'rb') as fptr:
        (raw_articles, tagging)= cPickle.load(fptr)
    new_articles,entities_for_articles= [], []
    entity_list= []
    for i,article in enumerate(raw_articles):
        print 'working on %d'%(i)
        entities, raw_new= find_wiki_tags(article)
        new_doc= newdoc_to_words(raw_new)
        new_articles.append(new_doc)
        entities_for_articles.append(entities)
        entity_list.extend(entities)
        time.sleep(1) #avoid going too far...
    with open('ohsumed_titles_final.pkl', 'wb') as fptr:
        cPickle.dump((new_articles,entities_for_articles, tagging), fptr, -1)
    relations= build_relations_from_raw_entities(entity_list, 'freebase-easy-14-04-14/less_facts.txt')
    with open('ohsumed_titles_final.pkl', 'wb') as fptr:
        cPickle.dump(relations, fptr, -1)

#building raw documents
#if __name__=='__main__':
#    fptr=open('ohsumed.91.txt','r')
#    
#    articles=[]
#    line=fptr.readline()
#    latest_article= None
#    tags=''
#    while len(line)>0 : #not EOF
#        if line.startswith('.I'): #new article
#            if latest_article is not None:
#                #paper_title_raw= clean_1(latest_article[0]).lower()
#                #stemmed_and_nerd= medical_NER(suffixes_stem(paper_title_raw), relation_entities)
#                #latest_article= (clean_2(stemmed_and_nerd.split(' ')), latest_article[1])
#                articles.append(latest_article)
#            latest_article=None
#        if line.startswith('.M'): #tags. next few lines are ';'-seperated categories
#            tags=''
#            line=fptr.readline()
#            while not line.startswith('.'):
#                tags+=line.replace('.\n','')
#                line=fptr.readline()
#            continue #work on new line
#        if line.startswith('.T'): #title-we want it. it's in the next line
#            line=fptr.readline()
#            tag_list= tags.split(';')
#            tag_list= [a for a in tag_list if a.find('/')!=-1]
#            #we want only the ones with '/' in them, and we need to work smart
#            latest_article= (line.replace('.\n',''), tag_list)
#        if latest_article is not None and line.startswith('.W'):
#            #has an abstract-do not want this article!
#            latest_article= None 
#        line=fptr.readline()
#    fptr.close()
#    
#    #Note: I need to mention the MeSH data dictionary thing
#    mapping= {} #map mesh term to higher level mesh term
#    with open('mtrees2015.bin','r') as fptr:
#        for line in fptr.readlines():
#            splitted= line.split(';')
#            top_level= splitted[1].split('.')[0].strip()
#            mapping[splitted[0]]= top_level
#            
#    articles_fixed= []
#    for article in articles:
#        new_tags= set()
#        for tag in article[1]:
#            #clean whitespaces, remove all after first / and match
#            fixed_tag= tag.split('/')[0].strip()
#            new_tags.add(mapping.get(fixed_tag, fixed_tag))
#        articles_fixed.append((article[0], new_tags))
#        
#    #now we can easily take top 20-30 cats... top 20 have>1000
#    #we can also go for C01 to C26... and only take those with over 500-14 cats (cutoff if more. mby 750(12 cats)/800(11 cats)/850(10 cats) better cutoff?)
#    reverse_thing={}
#    for art in articles_fixed:
#        for cat in art[1]:
#            if not reverse_thing.has_key(cat):
#                reverse_thing[cat]= []
#            reverse_thing[cat]+=[art[0]]
#    final_articles=[]
#    tagging=[]
#    for cat in ['C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C07', 'C08', 'C09']+['C'+str(x) for x in range(10, 21)+range(22,27)]:
#        if len(reverse_thing[cat]) < 850:
#            continue
#        for i, page in enumerate(reverse_thing[cat]):
#            if i> 850: #cutoff
#                break
#            final_articles.append(page)
#            tagging.append(int(cat[1:]))
#            
#    with open('ohsumed_titles_raw.pkl', 'wb') as fptr:
#        cPickle.dump((final_articles, tagging), fptr, -1)