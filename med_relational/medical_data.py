# -*- coding: utf-8 -*-
"""
Created on Sun Sep 07 14:28:28 2014

@author: liorf
"""

#extract medical RDF facts
'''
*labels are to be ignored*
diseasome_diseases.txt- has disease_name, disease_type, diseaseome_id, lbl
diseasome_treatments- diseasome_id, dailymed/drugbank_id (possible cure,multival). 
NOTE: This is the SAME as dailymedLnkToDiseasome+drugbank_diseasomelinks

dailymedLnkToDiseasome- dailymed_id, diseasome_id (possible cure for,multival)
dailymedLnkToDrugbank- dailymed_id, drugbank_id (same as, not always exists)
dailymed_drugdata- dailymed_id, drug_name, lbl, general_drug, active_moiety(this is essentially the same as general_drug but with unique id)

drugbank_diseasomelinks- drugbank_id, diseasome_id (possible cure for,multival)
drugbank_linkstodailymed- drugbank_id, dailymed_id (same as, not always exists)
drugbank_drugfacts- drugbank_id, drugname, label
drugbank_drugtype- drugbank_id, type (id may have multiple values)
drugbank_drugcategory- drugbank_id, category (id may have multiple values)
drugbank_interactions- drugbank_id, drugbank_id2, text description (pain in the ass to use for now)

sider_links- sider_id, drugbank/dailymed_id or garbadge...(sameas,multival)
sider_links_diseases- sideeffect_id, diseasemed_id(sameas,multival)->this is not needed!
sider_sideeffects- sider_id, side_effect_id, side_effect_name (multival)
'''

import json
import string
import re

def load_from_json(filename):
    fptr=open(filename,'r')
    blpr=json.load(fptr)
    fptr.close()
    return blpr['results']['bindings']

def clean_punctuation_except_underscore(text):
    '''replace punctuation with whitespace'''
    b= string.punctuation.replace('_','')
    b= b.replace('-','')
    return text.translate(string.maketrans(b, ' '*len(b)))

cml= re.compile('([A-Z]+)')
paren= re.compile('[^\(]+\(([^\)]+)\)')
def clean_single(value, is_diseases, is_drug_catorstypes):
    base= value.encode().split('/')[-1]
    
    if is_diseases:
        pugs= base.split(',')
        if len(pugs) > 1: #welcome to suckville! 
            pugs[0]= ' '+pugs[0]
            cleaned= pugs[-1].strip()
            #if has and/with/due/associated in middle ->nothing can be done...
            if cleaned.startswith('deficiency of') or cleaned.startswith('susceptibility to'):
                pugs.reverse()
                for pug in pugs:
                    base+= pug
            elif cleaned.startswith('deficiency') or cleaned.startswith('susceptibility') or cleaned.startswith('and') or cleaned.startswith('due') or cleaned.startswith('with') or cleaned.startswith('associated') or cleaned.startswith('of'): #last stays at end
                fin= pugs.pop() #last one in place...
                pugs.reverse()
                base=''
                for pug in pugs:
                    base+=pug
                base+=fin
            else:
                pugs.reverse()
                base=''
                for pug in pugs:
                    base+=pug
        base= base.replace(' ','_')
        if base[0]=='_':
            base= base[1:]
    if is_drug_catorstypes: 
    #can split using capital letter(camel case), and the word anti. if has parenthesis, take what's inside only
        prn_lst= paren.findall(base)
        if len(prn_lst) > 0: 
            base= prn_lst[0]
        base= base.replace('anti','anti_')
        base= cml.sub(r'_\1', base)
        
    base= base.replace(',', '_')
    base= clean_punctuation_except_underscore(base).replace(' ','').replace('-','_')
    return base.lower()
    
def decode_and_clean_entry(entry, is_diseases=False, is_drugs=False):
    if is_drugs:
        entry[u'id'][u'value']= entry[u'id'][u'value'].lower()
#        print entry
#        entry.values()[0]['value']=entry.values()[0]['value'].lower()
#        print entry
    return [clean_single(x['value'], is_diseases, is_drugs) for x in entry.values()]

if __name__=='__main__':
    '''problems: 
    1)disease names super noisy: long meaningless numbers, punctuation,words which may of may not be useful/appear, capitalization
    2)drug name noisy: punctuation, things which may or may not appear...some names worthless
    '''
    diseases_full= {} #map from id to name, type
    drugs_full= {} #map from id(prio:drugbank->dailymed->sider) to name, moiety, types, categories, sideefects
    links_full= {} #map from disease_id to drug_id
    
    data_lst= load_from_json('diseasome_diseases_cleaner.txt') #each element is one entry.
    #map of 'value_name' to value(in map form with 'value')
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry, True)#get vals+be rid of unicode
        diseases_full[decoded[2]]= [decoded[0], decoded[1]] #id->name,type
        
    data_lst= load_from_json('drugbank_drugfacts.txt')
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry)#get vals+be rid of unicode
        drugs_full[decoded[1]]= [decoded[0],None,[],[],[]] #id->name, active_moiety, lst of types, lst of category, lst of sideeffect
    data_lst= load_from_json('drugbank_drugtype.txt')
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry, False, True)#get vals+be rid of unicode
        drugs_full[decoded[1]][2].append(decoded[0])
    data_lst= load_from_json('drugbank_drugcategory.txt')
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry, False, True)#get vals+be rid of unicode
        drugs_full[decoded[0]][3].append(decoded[1][:-1])
        
    data_lst= load_from_json('dailymed_lnkTodrugbank.txt')
    mapping={} #dailymed->drugbank. need to clean ids!!!!!!!!!!!!!(last / only)
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry)#get vals+be rid of unicode
        mapping[decoded[0]]=decoded[1]
    data_lst2= load_from_json('dailymed_drugdata.txt')
    for entry in data_lst2:
        decoded=decode_and_clean_entry(entry)#get vals+be rid of unicode
        if len(decoded) < 3: #no moiet
                decoded.append(None)
        if mapping.has_key(decoded[1]):
            drugs_full[mapping[decoded[1]]][1]= decoded[2]
        else:
            #print 'unique id', decoded[1]
            drugs_full[decoded[1]]= [decoded[0], decoded[2], [], [], []]
    
    data_lst= load_from_json('sider_links.txt')
    mapping2={} #sider->dailymed/drugbank. need to clean ids!!!!!!!!!!!!!(last / only)
    for entry in data_lst:
        decoded=decode_and_clean_entry(entry)#get vals+be rid of unicode
        other_entry=decoded[1]
        if mapping2.has_key(decoded[0]):
            continue
        if other_entry.startswith('db'): #drugbank!
            mapping2[decoded[0]]= other_entry
#        elif other_entry[0].isdigit(): #dailymed
#            new_id= mapping.get(other_entry, other_entry) #if mapped, drugbank. otherwise dailymed
#            mapping2[decoded[0]]= new_id
        
    data_lst2= load_from_json('sider_sideeffects.txt')
    for entry in data_lst2:
        decoded=decode_and_clean_entry(entry, True, False)#get vals+be rid of unicode
        if mapping2.has_key(decoded[1]):
            true_key= mapping2[decoded[1]]
            drugs_full[true_key][-1].append(decoded[0])
        else:
            #print 'unique id', decoded[1], decoded
            continue #nope nope nope
#            if drugs_full.has_key(decoded[1]):
#                drugs_full[decoded[1]][-1].append(decoded[0])
#            else:
#                drugs_full[decoded[1]]=[decoded[1], None, [], [], [decoded[0]]]

    data_lst= load_from_json('drugbank_diseasomelinks.txt')    
    extras= load_from_json('dailymed_lnkTodiseasome.txt')
    for entry in data_lst:
        decoded= decode_and_clean_entry(entry)
        if not links_full.has_key(decoded[1]):
            links_full[decoded[1]]= []
        links_full[decoded[1]].append(decoded[0])
    for entry in extras:
        decoded= decode_and_clean_entry(entry)
        if not drugs_full.has_key(decoded[0]):
            continue
        if not links_full.has_key(decoded[1]):
            links_full[decoded[1]]= []
        links_full[decoded[1]].append(decoded[0])
    
    
    #STEP 2: build actual relations
    entities= set()
    relations= {}
    relations['disease_type']= {}
    relations['possible_cure']= {}
    #first: anything doing with diseases
    for (disease_id,[name,d_type]) in diseases_full.items():
        entities.add(name)
        relations['disease_type'][name]= d_type
        if not links_full.has_key(disease_id):
            continue
        tmp= []
        for d_id in links_full[disease_id]:
            tmp.append(drugs_full[d_id][0])
        relations['possible_cure'][name]= tmp
    #second: the drugs
    relations['drug_moiety']= {}
    relations['drug_types']= {}
    relations['drug_categories']= {}
    relations['drug_side_effects']= {}
    for (drug_id, [name, moiety, types, categories, sideeffects]) in drugs_full.items():
        entities.add(name)
        if moiety is not None:
            relations['drug_moiety'][name]= moiety
        if len(types) > 0:
            relations['drug_types'][name]= types
        if len(categories) > 0:
            relations['drug_categories'][name]= categories
        if len(sideeffects) > 0:
            relations['drug_side_effects'][name]= sideeffects
    for key in relations.keys():
        new_key= 'reverse_'+key
        relations[new_key]= {}
        is_set_value= isinstance(relations[key].values()[0], list)
        for (a,b) in relations[key].items():
            if is_set_value:
                for sub_val in b:
                    if relations[new_key].has_key(sub_val):
                        relations[new_key][sub_val].append(a)
                        continue
                    relations[new_key][sub_val]= [a]
                continue
            if relations[new_key].has_key(b):
                relations[new_key][b].append(a)
                continue
            relations[new_key][b]= [a]
    