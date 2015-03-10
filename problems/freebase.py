# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 14:36:00 2015

@author: liorf
"""

'''
step 1:
Freebase common->build entity disambig: for each line, take type.object.name with @en in end (mby also want common.topic.alias?)
Freebase medicine-> for each line, take it, put into relation(ex. disease.symptoms, disease.treatments) with value (disambig both)
->now you have medical relations
---be careful with type.object.type , since it's type info you want to take all possible ones! in fact, make set for all!
[save which entities got a match]

step 2:
for each entity in that got a match which is not medical, we possibly want things it connects to?
This is possibly overkill (gets out of hand quickly for depth 2 info like gender and CoO).
Basically, this is for later mby and probably don't go more than 1 level deep because our alg doesn't 
'''

import cPickle
from numpy import *

#def build_disambig_requirements(medical_dump):
#    '''for all entities in medical domain, build a list of them'''
#    entities=set()
#    with open(medical_dump, 'r') as fptr:
#        for line in fptr.readlines():
#            rdf_triplet= line.split('\t')[0:3] #the last one is just a dot...
#            entities.add(rdf_triplet[0])
#            if rdf_triplet[-1].startswith('<http'):
#                entities.add(rdf_triplet[-1])
#    return list(entities)

def make_sorted_entity_list(ohsumed_docs):
    '''Make a sorted list of all entities in OHSUMED subset'''
    entity_list=set()
    for doc in ohsumed_docs:
        entity_list.update(doc)
    return sorted(entity_list)
    
def filter_relational_data(sorted_entities, raw_facts, outfile):
    'take out all non-relevant relational data'''
    i=0
    with open(outfile, 'w') as fptr_out:
        with open(raw_facts, 'rb') as fptr_in:
            line= fptr_in.readline() #could do for line in fptr_in
            while i<len(sorted_entities) and line!='':
                triplet=line.split('\t')[0:3]
                if triplet[0].find('(') != -1:
                    line= fptr_in.readline()
                    continue
                entity= triplet[0].replace(' ','_').lower()
                if entity<sorted_entities[i]: 
                    line= fptr_in.readline()
                    continue
                if entity> sorted_entities[i]:
                    i+=1
                    continue
                fptr_out.write(line)
                line= fptr_in.readline()
    
def build_relations(facts):
    relations= {}
    with open(facts, 'r') as fptr:
        for line in fptr.readlines():
            rdf_triplet= [str_process(x) for x in line.split('\t')[0:3]] #the last one is just a dot...
            if not relations.has_key(rdf_triplet[1]):
                relations[rdf_triplet[1]]= {}
            if relations[rdf_triplet[1]].has_key(rdf_triplet[0]):
                relations[rdf_triplet[1]][rdf_triplet[0]].add(rdf_triplet[2])
            else:
                relations[rdf_triplet[1]][rdf_triplet[0]]= set([rdf_triplet[2]])        
    return relations

import string
def str_process(entity_name):
    #single word, lowercaps, remove punctuation marks. anything else?
    entity_name=  entity_name.translate(string.maketrans("",""), string.punctuation)
    return entity_name.replace(' ','_').lower()

#OBJECT_NAME= '<http://rdf.freebase.com/ns/type.object.name>'
#def build_disabmig(entity_list, common_dump, is_also_connected_info=False):
#    '''takes a list of entities and builds disabmig.
#    If flag is True, we also request the 1 lvl connected info relations (like gender for people?) worry about this later!'''
#    disambig_map= {}
#    with open(common_dump, 'r') as fptr:
#        current_entity, is_disambig_curr= fptr.readline().split(' ')[0], False
#        for line in fptr.readlines():
#            rdf_triplet= line.split('\t')[0:3] #the last one is just a dot...
#            if rdf_triplet[0]==current_entity and is_disambig_curr:
##                if is_also_connected_info:
##                    pass #find connected info somehow
#                continue
#            if rdf_triplet[0]!=current_entity:
#                current_entity= rdf_triplet[0]
#                is_disambig_curr= False
#            if current_entity not in entity_list:
#                continue #irrelevant
#            if rdf_triplet[1]==OBJECT_NAME and rdf_triplet[2].endswith('@en'):
#                disambig_map[rdf_triplet[0]]= str_process(rdf_triplet[2].split('"')[1])
#                is_disambig_curr= True
#    return disambig_map
#
#def extract_medical_relations(disambig, medical_dump):
#    '''takes the medical dump and turns it to a proper relational DB for our alg'''
#    relations= {}
#    with open(medical_dump, 'r') as fptr:
#        for line in fptr.readlines():
#            rdf_triplet= line.split('\t')[0:3] #the last one is just a dot...
#            if not relations.has_key(rdf_triplet[1]):
#                relations[rdf_triplet[1]]= {}
#            key_name= disambig[rdf_triplet[0]]
#            val_name= disambig.get(rdf_triplet[2], str_process(rdf_triplet[2]))
#            if relations[rdf_triplet[1]].has_key(key_name):
#                relations[rdf_triplet[1]][key_name].add(val_name)
#            else:
#                relations[rdf_triplet[1]][key_name]= set([val_name])        
#    return relations

if __name__=='__main__': #TODO
    with open('C:\Users\liorf\Documents\GitHub\Thesis\problems\ohsumed_titles_parsed_complete.pkl','rb') as fptr:
        (articles,labels)= cPickle.load(fptr) 
    
    (articles,labels)= (array(articles), array(labels))  
    print shape(articles), shape(labels)
    label_names=array([1, 4, 6, 8, 10, 13, 14, 17, 20, 23])   
    data,data_labels=[],[]
    for label in label_names:
        idxs=find(labels==label)
        data+=[x for x in articles[idxs]]
        data_labels+=[x for x in labels[idxs]]
    data, data_labels= array(data, dtype=object), array(data_labels)
    print len(data)
    
    entity_list=make_sorted_entity_list(data)
    print len(entity_list)
    filter_relational_data(entity_list, 'freebase-easy-14-04-14/facts.txt', 'filtered_facts.txt')
#    disambig_required= build_disambig_requirements('freebase-medicine')
#    disambig_table= build_disabmig(disambig_required, 'freebase-common2')
#    
#    relations= extract_medical_relations(disambig_table, 'freebase-medicine')
    #Now: build the reverse:
    pass

#    with open('', 'wb') as fptr:
#        cPickle.dump(relations, fptr, -1)