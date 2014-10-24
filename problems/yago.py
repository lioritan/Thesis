
'''File descriptions:
-yagoDBpediaClasses: some stupid shit that relates label(wikicategory) to dbpedia(useless)
-yagoDBpediaInstances: same but with actual concepts(useless)
-yagoFacts: maps fact_id to concept,relation,concept (major component)
-yagoGeonames*: all sorts of data(and metadata) on geography features . Data is the actual relational facts (can probably skip)
-yagoImportantTypes: maps concept to type(wordnet_ /wikicategory_/yago/). this is the tagging thing. (mby important)
-yagoLabels: maps fact id to Concept,M.relation,string where M.relation is label/preferred meaning/? (probably useless)
-yagoLiteralFacts: maps fact_id to concept,relation,concept as well(major component)
-yagoMetaFacts: maps fact_id to fact_id,relation,concept -> so happened in/occured at/more things on events (probably can skip)
-yagoMultilingual*: some wierd multilingual data (useless)
-yagoSchema: metadata on what relations apply on and a few other things (probably not important)
-yagoSimpleTaxonomy: subclass relation between labels(to more abstract labels) (mby important)
-yagoSimpleTypes: maps concept to type/label. Has no wikicategory(but wordnet and yago yes) (mby important)
-yagoSources: how and where we got all of the facts (useless)
-yagoStatistics: useless
-yagoTaxonomy: maps fact_id to label,subclass_of,label (has wikicategory) (mby important)
-yagoTransitiveType: maps concept to label by all possible subclasss that apply to it (mby important, though ImprotantTypes is better)
-yagoTypes: maps fact_id to concept,type,label(only wikicategory) seems to complement ImportantTypes? (mby important)
-yagoWikipediaInfo: info on the wikipedia page of a concept, includes links in the wiki page (not needed for now)
-yagoWordnetDomains: metadata on wordnet labels(useless)
-yagoWordnetIds: same (useless)
'''

#types will probably be important for generalization purposes, for example:
#has_word(X) and X.type('president') and bornIn(X, Y) and Y.type('state/city/region') and Country(Y, 'USA')

'''setups: always need facts and literalFacts
1)simpleTypes, simpleTaxonomy-simple taxonomy(mby add in importantTypes as well?)
2)types, taxonomy, transitiveType-more complex taxonomy(not yet?)
'''

'''relations I need to add:
0)redirected_from->effectivly "same as" using wikepedia(very high prio, but lots of stuff)->
need to collect using rdfs:label with @eng ending->yagoLabels
1)yagoGeonamesData for geography(low prio)->probably not important...
2)yagoMetaFacts for events(somewhat important)->needs id to name mapping...
3)yagoTypes for type info(needed?)
5)literal facts(not yet...)
'''

import re

def read_and_strip_tokens(file_ptr):
    raw_data = [x.split('\t') for x in file_ptr.readlines()]
    for fact in raw_data:
        try:
            fact.remove('')
        except ValueError:
            pass
        try:
            fact.remove('\n')
        except ValueError:
            pass   
    return [[re.sub('_\([^\)]+\)','',x.lower().strip('<>').translate(None,'.,')) for x in fact] for fact in raw_data]   
    
def turn_to_relations(facts, literal_facts):
    rels = {}
    for fact in facts:
        if not rels.has_key(fact[2]):
            rels[fact[2]] = {}
        rels[fact[2]][fact[1]]= fact[-1]
    if literal_facts is None:
        return rels
    for fact in literal_facts:
        if not rels.has_key(fact[2]):
            rels[fact[2]] = {}
        if rels[fact[2]].has_key(fact[0]):
            print 'omg!!!'
            print fact
            rels[fact[2]][fact[1]].add(fact[-1]) 
        else:
            rels[fact[2]][fact[1]]= fact[-1]
        
    return rels

def create_type_relation(type_rel1, type_rel2, taxonomy):
    rel = {}
    for fact in type_rel1:
        rel[fact[0]]= set([fact[2]])
    for fact in type_rel2:
        if rel.has_key(fact[0]):
            rel[fact[0]].add(fact[2])
        else:
            rel[fact[0]]= fact[2]
    for fact in taxonomy:
        if fact[1] != 'rdfs:subclassof':
            continue
        for typeset in rel.values():
            if fact[0] in typeset:
                typeset.add(fact[2])
    for fact in rel:
        rel[fact]=list(rel[fact])#set to list
    return rel

if __name__=='__main__':
    #TODO: skip type relations? is that smart? could make explosion, but also maybe "has word of type fruit" is powerful...
    '''
    ptr1 = open('..\yago2s_tsv\yagoSimpleTypes.tsv','r')
    type_facts1 = read_and_strip_tokens(ptr1)
    ptr1.close()
    ptr1 = open('..\yago2s_tsv\yagoImportantTypes.tsv','r')
    type_facts2 = read_and_strip_tokens(ptr1)
    ptr1.close()
    ptr1 = open('..\yago2s_tsv\yagoSimpleTaxonomy.tsv','r')
    taxonomy_facts = read_and_strip_tokens(ptr1) #take rdfs:subclassOf as type closure?
    ptr1.close()
    
    #build type relation: fact,type and type,supertypes
    type_rel = create_type_relation(type_facts1, type_facts2, taxonomy_facts)
    del type_facts1
    del type_facts2
    del taxonomy_facts
    '''
    #now for facts:
    
    ptr1 = open('..\yago2s_tsv\yagoFacts.tsv','r')
    facts1 = read_and_strip_tokens(ptr1)
    ptr1.close()
    #NOTE: skip literal facts for now(useless without the proper comperators)    
    
    #ptr1 = open('yagoLiteralFacts.tsv','r') #has one extra field since literal(number)
    #facts2 = read_and_strip_tokens(ptr1)
    #ptr1.close()
    other_rels = turn_to_relations(facts1, None)
    del facts1
    #del facts2
    
    #other_rels['types']= type_rel
    #import pickle
    #pickle.dump(other_rels, 'yago_relations.pkl')
    
    #stats:
    #time required: ~2 hours
    #total relations: 38+types(mostly about people, a bit on countries, events)
    #relation sizes: type rel:~3M pairs, others ~2M
    #Named entity structure: lowercase, underscore separates. Note: some html formatting shit!(\xc3)
    #issues: matching people with anything real is unlikley(noise), other things also have some noise like "georgia_(ountry)"
    #possibly UK/united_kingdom and same with US issue...general Named entity problem
    
    