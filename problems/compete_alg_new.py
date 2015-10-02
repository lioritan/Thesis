# -*- coding: utf-8 -*-
"""
Created on Fri Oct 02 11:51:27 2015

@author: Lior
"""

from random import choice
from numpy import *
from matplotlib.cbook import flatten

import time

def is_relation_key(x, relation):
    res=[]
    for y in x:
        if relation.has_key(y):
            res.append(y)
    return res

def is_set_valued(relation,relname):
    return True #new one for ohsumed
    return relname.startswith('reverse_') or relname=='type' or relname=='possible_cure' or (relname.startswith('drug_') and not relname=='drug_moiety')
    return relname.startswith('reverse_') or relname=='type' #yago
    return isinstance(relation.values()[0], list) #general, slow

def is_in_relation(x, relation,relname, *args):
    '''args[0]=optional target
    x is a single object. this works fine with [] as param'''
    res=[]
    flag= is_set_valued(relation,relname)
    if flag is False:        
        for y in x:
            bob = relation.get(y)
            if bob is not None:
                res+=[bob]
    else: #relation is reversed
        for y in x:
            res+= relation.get(y, [])
    if len(args)==0:
        return res #list of strings
    return args[0] in res
    
def apply_transforms(relations, transforms, objects):
    '''transforms is list of relation+direction pairs.
    objects is set of objects(set of sets'''
    curr_objs=objects
    for relation in transforms:
        curr_objs= [is_in_relation(obj, relations[relation], relation) for obj in curr_objs]
    return curr_objs

class FeatureGenerationAlt(object):
    def __init__(self, objects, entities, tagging, relations):
        self.objects= objects
        self.entities= entities
        self.tagging= tagging
        self.relations= relations
        
        self.new_features= []
        self.new_justify= []
    
    def generate_features(self, n, max_depth):
        NA_VAL=-100
        if max_depth<1:
            return
        for relation in random.choice(self.relations.keys(), n, True):
            new_obs_for_rel= apply_transforms(self.relations, [relation], self.entities)
            flattened_obs = list(frozenset(flatten(new_obs_for_rel)))
            if len(flattened_obs)==0:
                continue
            ob = random.choice(flattened_obs, 1)
            self.new_features.append(lambda x, rel=relation, t=ob: 1 if is_in_relation(x, self.relations[rel], rel, t) else NA_VAL if len(is_in_relation(x, self.relations[rel], rel))==0 else 0 )
            self.new_justify.append('is in relation %s with %s'%(relation, ob))
            if max_depth==2:
                relation2 = choice(self.relations.keys())
                newer_obs= apply_transforms(self.relations, [relation2], new_obs_for_rel)
                flattened_obs_2 = list(frozenset(flatten(newer_obs)))
                if len(flattened_obs_2)==0:
                    continue
                new_ob = random.choice(flattened_obs_2, 1)
                self.new_features.append(lambda x, trans=[relation,relation2], t=new_ob: 1 if t in apply_transforms(self.relations, trans, [x])[0] else NA_VAL if len(apply_transforms(self.relations, trans, [x])[0])==0 else 0)
                self.new_justify.append('is in relations %s,%s with %s'%(relation, relation2, new_ob))        
    
    def get_new_table(self, test, test_ents):
        all_words=set()
        for words in self.objects:
            all_words.update(words)
        self.table= zeros((len(self.objects), len(all_words)+len(self.new_features)))
        self.test= zeros((len(test), len(all_words)+len(self.new_features)))
        self.feature_names=[]
        for i,word in enumerate(all_words):
            self.table[:,i]= array([1 if (word in obj) else 0 for obj in self.objects])
            self.test[:, i]= array([1 if (word in obj) else 0 for obj in test])
            self.feature_names.append('has word:%s'%(word))
        for j,new_feature in enumerate(self.new_features):
            self.table[:, len(all_words)+j]= array([new_feature(ent) for ent in self.entities])
            self.test[:, len(all_words)+j]= array([new_feature(ent) for ent in test_ents])
            self.feature_names.append(self.new_justify[j])
        return self.table, self.tagging, self.test, self.feature_names
        
if __name__=='__main__':
    #Toy example for debugging
    messages=['cocoa price increase in 1964 because of cuban_missile_crisis', 
            'cocoa kill person according to research from france university',
            'rice price worldwide in constant decrease due to export increase from china since 1990',
            'pineapple cake serve in oslo_peace_conference',
            'apple is not actual forbidden fruit scientist say actually pear instead',
            '20 person dead 40 injure in earthquake in turkey',
            'u.s. is no longer largest consumer of goods according to survey',
            'potato consumption in u.s. increase due new potato craze',
            'edward_snoden_leak put nsa in bad spot president barrack_obama to give statement tomorrow',
            'dog not allergic to cocoa according to new study from mit',
            'ireland_potato_famine memorial day riot cause 4 dead', #hard one since potato is america but still stuff. Mby a noisy example?
            'wheat and cucumber consumption on worldwide decline except in u.s.',
            'new corn based recipe will rock your world',
            'broccoli vote funny word of year read more inside',
            'new president of mexico allergic to avocado cannot eat guacamole',
            'india origin of moussaka eggplant import to turkey from india',
            'oslo_peace_conference best thing ever',
            '10 year since oslo_peace_conference what change',
            'cuban_missile_crisis cause rise in potato price',
            'paris celebrate memorial french_revolution with cake',
            'orange most cultivate fruit in world according to recent survey',
            'sweet_potato diet increase in popularity due to celebrity endorsement',
            'cat allergic to pepper according to new study from mit',
            'ginger cost skyrocket due to u.s. sushi craze in los_angeles',
            'bible forbid sweet_potato according to rabi from israel',
            '2016_olympics possible not take place in brazil but in mexico',
            'canada_squash soup recipe popular in u.s.'
            ] #messages on fruits/veggies that originally from america is concept. have some fruit, some america, some both, some neither
    msg_entities= [['cocoa', 'cuban_missile_crisis'],
                   ['cocoa', 'france'],
                    ['rice', 'china'],
                    ['pineapple', 'oslo_peace_conference'],
                   ['apple', 'pear'],
                   ['turkey'],
                   ['u.s.'],
                   ['u.s.', 'potato'],
                   ['edward_snoden_leak', 'barrack_obama'],
                   ['cocoa'],
                   ['ireland_potato_famine'],
                   ['wheat', 'cucumber', 'u.s.'],
                   ['corn'],
                   ['broccoli'],
                   ['mexico', 'avocado'],
                   ['india', 'eggplant', 'turkey'],
                   ['oslo_peace_conference'],
                   ['oslo_peace_conference'],
                   ['cuban_missile_crisis', 'potato' ],
                   ['paris', 'french_revolution'],
                   ['orange'],
                   ['sweet_potato'],
                   ['pepper'],
                   ['ginger', 'u.s.', 'los_angeles'],
                   ['sweet_potato', 'israel'],
                   ['2016_olympics', 'brazil', 'mexico'],
                   ['canada_squash', 'u.s.']
]
    msg_entities= array(msg_entities, dtype=object)
    msg_objs=array([a.split(' ') for a in messages], dtype=object)
    message_labels = (array([1,1,-1,1,-1,-1,-1,1,-1,1,1,-1,1,-1,1,-1,-1,
                             -1,1,-1,-1,1,1,-1,1,-1,1])+1)/2
    test_msgs= ['potato and tomato sound the same and also come from same continent list of 10 things from the new world which surprise',
                '2014_israel_president_election soon 6 candidate for title',
                'eggplant soup popular in asia',
                'pumpkin cost worldwide increase 40 percent during halloween',
                'tomato favourite fruit of italy',
                'massive news coverage of 2016_olympics expect due to location',
                'rice has medical quality according to mit research',
                'pumpkin may color urine if consume in large quantity',
                'religious riot in europe',
                'cocoa ban in china lifted']#this test set is too hard. pumpkin is impossible, and cocoa_ban is kind of also impossible
    tst_ents= [['potato', 'tomato'],
                   ['2014_israel_president_election'],
                   ['eggplant', 'asia'],
                   ['pumpkin'],
                   ['tomato', 'italy'],
                   ['2016_olympics'],
                   ['rice'],
                   ['pumpkin'],
                   ['europe'],
                   ['cocoa','china']
]
    tst_ents= array(tst_ents, dtype=object)
    test=[a.split(' ') for a in test_msgs]
    test_lbl= (array([1,-1,-1,1,1,-1,-1,1,-1,1])+1)/2
    relations={}
    relations['type']={'potato':'vegetable', 'cuban_missile_crisis':'event', 'cocoa':'fruit', 'france':'country', 'rice':'cereal', 'china':'country', 'pineapple':'fruit', 'oslo_peace_conference':'event'
                        , 'apple':'fruit', 'pear':'fruit', 'turkey':'country', 'u.s.':'country', 'edward_snoden_leak':'event', 'nsa':'organization', 'obama':'person', 'dog':'animal', 'mit':'university',
                            'ireland_potato_famine':'event', 'wheat':'cereal', 'cucumber':'vegetable', 'chile':'country', 'cuba':'country', 'venezuela':'country', 'brazil':'country', 'norway':'country',
                            'italy':'country', 'syria':'country', 'india':'country', 'norway':'country', 'ireland':'country', 'north_america':'continent', 'south_america':'continent', 'europe':'continent', 
                            'asia':'continent', 'tomato':'fruit', '2014_israel_president_election':'event', 'israel':'country', 'mexico':'country'}
    relations['country_of_origin']={'potato':'chile', 'cocoa':'venezuela', 'rice':'china', 'pineapple':'brazil', 'apple':'turkey', 'pear':'italy', 'wheat':'syria', 'cucumber':'india', 'tomato':'mexico',
                                        'broccoli':'italy', 'corn':'mexico', 'avocado':'mexico', 'eggplant':'india', 'orange':'china', 'sweet_potato':'peru','pumpkin':'u.s.','pepper':'mexico','ginger':'china', 'canada_squash':'canada',
                                        'blarf':'ggg','nof':'fluff','poo':'goffof','fgfgfgfg':'gggg','a':'b', 'r':'f','t':'t'}#applys to fruits/vegs/crops
    relations['continent']={'cuba':'south_america', 'france':'europe', 'china':'asia', 'norway':'europe', 'turkey':'asia', 'u.s.':'north_america',
                            'chile':'south_america', 'venezuela':'south_america', 'brazil':'south_america', 'italy':'europe', 'ireland':'europe', 'syria':'asia', 'india':'asia',
                            'mexico':'south_america', 'israel':'asia', 'vatican':'europe','russia':'asia', 'peru':'south_america', 'canada':'north_america',
                            'f':'g','b':'c','ggg':'fff','fluff':'t','t':'t','d':'d'}#apply to country
    relations['capital_of']={'paris':'france', 'washington_dc':'u.s.','china':'beijing','mexico':'mexico_city','brazil':'brasilia','cuba':'havana','norway':'oslo','turkey':'ankara','chile':'santiago','venezuela':'caracas','italy':'rome','vatican':'vatican_city','ireland':'dublin','syria':'damascus','india':'new_delhi', 'russia':'muscow',
                            'f':'f','r':'r','d':'d','q':'p','fff':'ffg'}
    relations['city_of']={'paris':'france','los_angeles':'u.s.', 'washington_dc':'u.s.','china':'beijing','mexico':'mexico_city','brazil':'brasilia','cuba':'havana','norway':'oslo','turkey':'ankara','chile':'santiago','venezuela':'caracas','italy':'rome','vatican':'vatican_city','ireland':'dublin','syria':'damascus','india':'new_delhi', 'russia':'muscow',
                            'f':'f','t':'t','q':'q','p':'p'}
    relations['president_of']={'vladimir_putin':'russia','barrack_obama':'u.s.',
    'q':'f', 'r':'r', 'f':'f','b':'c','t':'t','d':'d'}
#    relations['calorie_content_kcal']={'tomato':18, 'potato':77, 'rice':365, 'pineapple':50, 'apple':52, 'pear':57, 'wheat':327, 'cucumber':16}#apply to fruit/vegetable, numeric. missing for cocoa
    relations['happend_in_place']={'cuban_missile_crisis':'cuba', 'oslo_peace_conference':'norway', 'edward_snoden_leak':'u.s.', 'ireland_potato_famine':'ireland', '2014_israel_president_election':'israel','french_revolution':'france','2016_olympics':'brazil', 'cocoa_ban':'china',
                                    'fu':'f','r':'r','b':'b','c':'c','d':'d'}#apply to event(cuba missile crisis)
    #relations['happend_on_date']={'cuban_missile_crisis':1962, 'oslo_peace_conference':1993, 'edward_snoden_leak':2013, 'ireland_potato_famine':1845, '2014_israel_president_election':2014} #apply to event, numeric
    for rel in relations.keys():
        for key,val in relations[rel].items():
            relations[rel][key]=set([val])

    for key in relations.keys():
        new_key= 'reverse_'+key
        relations[new_key]= {}
        for (a,b) in relations[key].items():
            for i in b:
                if relations[new_key].has_key(i):
                    relations[new_key][i].add(a)
                    continue
                relations[new_key][i]= set([a])
            
    blor= FeatureGenerationAlt(msg_objs,msg_entities,  message_labels, relations)
    before=time.time()
    blor.generate_features(200, 2)    
    #blah3=TreeRecursiveSRLClassifier(msg_objs, message_labels, relations, [], 200, 2, 3, logfile)    
    #blah3.train(1)
    print time.time()-before
    trn, trn_lbl, tst, feature_names= blor.get_new_table(test, tst_ents)
    
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.feature_selection import SelectKBest

#    feature_selector= SelectKBest(chi2, k=100)
#    filtered_trn= feature_selector.fit_transform(trn, trn_lbl)
#    filtered_tst= feature_selector.transform(tst)
    blah3= SVC(kernel='linear', C=100)
#    blah3= KNeighborsClassifier(n_neighbors=5)
#    blah3= DecisionTreeClassifier(criterion='entropy', min_samples_split=2)
    blah3.fit(trn, trn_lbl)
    
    pred3trn=blah3.predict(trn)
    print mean(pred3trn!=trn_lbl)
    pred3tst=blah3.predict(tst)
    print mean(pred3tst!=test_lbl)
    print len(blor.new_features)
    print blor.feature_names[-30:]