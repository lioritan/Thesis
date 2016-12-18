# -*- coding: utf-8 -*-
"""
Created on Thu Dec 01 22:04:44 2016

@author: Lior
"""

import cPickle

import os
from matplotlib.cbook import flatten

with open('../yago2s_tsv/yago_relations.pkl', 'rb') as fptr:
    relations= cPickle.load(fptr)
print 'yago loaded'
            
entities=set()
for path,dirnames, filenames in os.walk('./techtc_entities/'):
    for filename in filenames:
        fptr=open(path+'/'+filename, 'rb')
        ((trn_ents,_),(tst_ents,_))=cPickle.load(fptr)
        entities.update(flatten(trn_ents))
        entities.update(flatten(tst_ents))
        fptr.close()
        
less_relations = {}
target_entities = set()
print len(entities)

for i,ent in enumerate(entities):
    #print i
    for rel in relations.keys():
        if relations[rel].has_key(ent):
            val = relations[rel][ent]
            if rel!='YAGO:types' and rel!='types':
                target_entities.add(val)
            if not less_relations.has_key(rel):
                less_relations[rel]={ent:val}
            else:
                less_relations[rel][ent]=val

#with open('tmp_rels.pkl','wb') as fptr:
#    cPickle.dump((less_relations,target_entities), fptr, -1)

del entities    
print len(target_entities)
for i,ent in enumerate(target_entities):
    #print i
    for rel in relations.keys():
        if relations[rel].has_key(ent):
            val = relations[rel][ent]
            if not less_relations.has_key(rel):
                less_relations[rel]={ent:val}
            else:
                less_relations[rel][ent]=val

del target_entities                
with open('yago_rels_new.pkl','wb') as fptr:
    cPickle.dump(less_relations, fptr, -1)