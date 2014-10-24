# -*- coding: utf-8 -*-
"""
Created on Tue Aug 26 11:32:31 2014

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
from scipy.stats import mode

import time
        
def entropy(tags): #this is 0 if all same tag, 1 if uniform, lower=better
    '''computes entropy on tags. Assumes binary 0-1 tagging only.(not +-1 !!!)
    entropy= sum(-f*log2(f)) where f are the frequencies of each value'''
    freqs = bincount(tags)/(1.0*len(tags))
    nonzeros= find(freqs !=0)
    if size(nonzeros)<= 1:
        return 0.0 #edge case
    tmp = freqs[nonzeros]
    return sum(-tmp*log2(tmp))    
    
#TODO: info_gain_ratio for non binary features and possibly need to do AIC/BIC  ?  
def info_gain(curr_node_tags, feature_values): #0 if same divide, 1 if perfect
    '''computes simple info-gain for a split. '''

    curr_ent = entropy(curr_node_tags) #current entropy H(T)
    #sum over all values: #elements with this value/#total elements * entropy(elements with this value)
    cond_ent = 0.0
    total_elem_sz = 1.0*len(curr_node_tags)
    
    for value in set(feature_values):
        locs= find(feature_values == value)
        value_prob = len(locs)/total_elem_sz
        cond_ent += value_prob*entropy(curr_node_tags[locs])
    return curr_ent- cond_ent

def is_set_valued(relation,relname):
    return relname.startswith('reverse_') or relname=='type'
    return isinstance(relation.values()[0], list)

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
    
def apply_transforms(relations, transforms, objects, *args):
    '''transforms is list of relation+direction pairs.
    objects is set of objects(set of sets'''
    curr_objs=objects
    for relation in transforms:
        curr_objs= [is_in_relation(obj, relations[relation],relation) for obj in curr_objs]
    if len(args)==0:
        return curr_objs
    return array([1 if args[0] in blub else 0 for blub in curr_objs])

def split_and_subtree(query_chosen, recursive_step_obj):
    query_results=array([query_chosen(x) for x in recursive_step_obj.objects])
    pos_inds=find(query_results==1)
    neg_inds=find(query_results!=1)
    recursive_step_obj.left_son= TreeRecursiveSRLStep(recursive_step_obj.objects[neg_inds], recursive_step_obj.tagging[neg_inds], recursive_step_obj.relations, recursive_step_obj.transforms, recursive_step_obj.n, recursive_step_obj.MAX_DEPTH, recursive_step_obj.SPLIT_THRESH, recursive_step_obj.cond)
    recursive_step_obj.right_son=TreeRecursiveSRLStep(recursive_step_obj.objects[pos_inds], recursive_step_obj.tagging[pos_inds], recursive_step_obj.relations, recursive_step_obj.transforms, recursive_step_obj.n, recursive_step_obj.MAX_DEPTH, recursive_step_obj.SPLIT_THRESH, recursive_step_obj.cond)
    return query_chosen,recursive_step_obj.left_son,recursive_step_obj.right_son
 
        
#MAX_DEPTH=2 #TODO!
#SPLIT_THRESH=3 #TODO!
MAX_SIZE= 5000 #TODO: change this in future(needed to make it run fast)
IGTHRESH=0.05
#BAD_RELATION=False
class TreeRecursiveSRLStep(object):
    def __init__(self, objects, tagging, relations, steps_to_curr, n, MAX_DEPTH, SPLIT_THRESH,cond=False):
        self.relations= relations
        self.objects =array(objects)
        self.tagging=tagging
        if len(objects) > 0:
            self.chosen_tag= mode(tagging)[0] 
        else:
            self.chosen_query=None
            self.justify='no objects'
            self.chosen_tag=None
        self.transforms= steps_to_curr        
        self.ig = -1.0
        self.chosen_query=None
        self.cond=cond
        self.n=n
        self.MAX_DEPTH=MAX_DEPTH
        self.SPLIT_THRESH=SPLIT_THRESH
        
    def pick_split_query(self):
        '''pick one query(if simple query on objects give high IG, do that, otherwise go recursive and build tree as query'''
        all_words=set()
        for words in self.objects:
            for word in words:
                all_words.add(word)
        max_ig,best_word=-1.0,''
        for word in all_words:
            word_ig= info_gain(self.tagging, array([1 if (word in obj) else 0 for obj in self.objects]))
            if word_ig>=max_ig:
                max_ig,best_word=word_ig,word
        self.chosen_query, self.ig, self.justify=lambda x: 1 if (best_word in x) else 0, max_ig, 'hasword:'+best_word
        if self.cond is True:
            return split_and_subtree(self.chosen_query, self)
        
        #Build relation-based features(super table) for objects, see if any query good enough
        best_ig, transforms_used, constant= self.ig,[],''
        depth=0
        transforms=[([],self.n)]
        while depth<self.MAX_DEPTH+1:
            pagu=[]
            new_transforms=[]
            #print len(base_vals)
            #print depth
            for base_transforms,n in transforms:
                for relation in self.relations:  
                    if len(base_transforms)>0 and (relation==base_transforms[-1] or relation=='reverse_'+base_transforms[-1] or relation==base_transforms[-1].replace('reverse_','')):
                        continue #no using the relation you came with on the way back...
                    feature_vals= apply_transforms(self.relations, base_transforms+[relation],self.objects)
                    if sum(map(len, feature_vals))==0 : #no objects have relevant values. This may leave us with objects whose feature values are [], which means any query will return false...
                        continue #not relevant
            
                    relation_constants= set()
                    for obj in feature_vals:
                        for const in obj:
                            relation_constants.add(const)
            
                    avg_for_rel=0.0
                    sz=len(relation_constants)
                    if sz>=MAX_SIZE:
                        continue #For now, skip. 
                    relation_constants.add(None)                 

                    for const in relation_constants:
                        labels= None
                        if const is None:
                            labels= array([1 if len(val)==0 else 0 for val in feature_vals])
                        else:
                            labels= array([1 if const in val else 0 for val in feature_vals])
                
                        ig_for_const= info_gain(self.tagging,labels)
                        avg_for_rel+=ig_for_const
                        if ig_for_const>=best_ig and ig_for_const> IGTHRESH:
                            best_ig, transforms_used, constant= ig_for_const, base_transforms+[relation],const    
                    
                    new_transforms.append((relation, avg_for_rel/len(relation_constants)))
                    del feature_vals
                    del relation_constants
                if len(new_transforms)==0:
                    break #no more recursion
                #now we subsample            
                transforms_pos, avg_igs= zip(*new_transforms)
                #transforms_pos, avg_igs= self.filter_bad_rels(transforms_pos, avg_igs)
                if len(transforms_pos)==0:
                    break #no more recursion
            
                avg_igs= array(avg_igs)
                transforms_pos= array(transforms_pos, dtype=object)
                choices=random.choice(transforms_pos, n, True, avg_igs/sum(avg_igs))
                temp={}
                for relation in choices:
                    if temp.has_key(relation):
                        temp[relation]+=1
                        continue
                    temp[relation]=1
        
                for (a,b) in temp.items():
                    pagu.append((base_transforms+[a],b))
            #print transforms
            transforms= pagu
            depth+=1
        
        #print best_ig, self.ig
        if best_ig >= self.ig:
            if constant is None:
                self.chosen_query= lambda x: 1 if len(apply_transforms(self.relations, transforms_used, [x])[0])==0 else 0
            else:
                self.chosen_query= lambda x: apply_transforms(self.relations, transforms_used, [x], constant)[0]            
            self.ig, self.justify= best_ig, str(transforms_used)+' '+str(constant)
        
        if self.ig <= 0: #no query is useful
            self.chosen_query=None
            print 'big problem'
            return None,None,None
        
        return split_and_subtree(self.chosen_query, self)
        
    def filter_bad_rels(self, relations, value_things):
        #filter transforms+non-relevant since doesn't apply
        #relations-relations I consider moving to
        new_rel_fet=[]
        new_avg_ig=[]
        for i,relation in enumerate(relations):
            if relation in self.transforms or 'reverse_'+relation in self.transforms or relation.replace('reverse_','') in self.transforms:
                continue
            
            if value_things[i]<=0.0:
                continue #ig is 0->no point
            
            barf=False
            new_objs=apply_transforms(self.relations, [relation], self.objects)
            if sum([len(obj) for obj in new_objs])==0:#all objects are []
                continue
            for other_rel in self.relations.keys():
                if other_rel==relation or other_rel=='reverse_'+relation or other_rel==relation.replace('reverse_',''):
                    continue
                feature_vals=[is_in_relation(obj, self.relations[other_rel]) for obj in new_objs]
                val_lens=[len(val) for val in feature_vals]
                if sum(val_lens)>0 :
                    barf=True
                    break
            if barf:   
                new_rel_fet.append(relation)
                new_avg_ig.append(value_things[i]) 
        return new_rel_fet, array(new_avg_ig)
        
class TreeRecursiveSRLClassifier(object):
    def __init__(self, objects, tagging, relations, transforms, n, MAX_DEPTH, SPLIT_THRESH, cond=False):
        self.relations= relations
        self.objects =objects
        self.tagging=tagging
        self.transforms=transforms
        self.cond=cond
        self.n=n
        self.MAX_DEPTH=MAX_DEPTH
        self.SPLIT_THRESH=SPLIT_THRESH
        
    def train(self):
        self.tree_sets= [TreeRecursiveSRLStep(self.objects, self.tagging, self.relations, self.transforms, self.n, self.MAX_DEPTH, self.SPLIT_THRESH, self.cond)] #initally all in same node
        for node in self.tree_sets:
            if len(node.objects)<=self.SPLIT_THRESH or all(node.tagging==1) or all(node.tagging==0):#consistent/too small to split 
                node.justify='leafed(thresh/constistant)'
                node.chosen_query=None
                continue #leaf
            _,left, right=node.pick_split_query()
            if left is None or right is None:
                node.chosen_query=None
                continue#another leaf case...
            self.tree_sets.append(left)
            self.tree_sets.append(right)            
        self.query_tree=self.tree_sets[0] #root
        
    def predict(self, new_object):
        
        curr_node= self.query_tree
        if curr_node.chosen_tag is None:#edge case in the case of consistent
            return 0#some arbitrary rule
        while curr_node.chosen_query is not None:
            if curr_node.right_son.chosen_tag is None: #query splits all to one side
                curr_node=curr_node.left_son
                continue
            if curr_node.left_son.chosen_tag is None: #other side
                curr_node=curr_node.right_son
                continue
            transformed_obj= apply_transforms(curr_node.relations, curr_node.transforms, [new_object]) 
            query_val= curr_node.chosen_query(transformed_obj[0]) #this works
            if query_val==1:
                curr_node=curr_node.right_son
            else:
                curr_node=curr_node.left_son
        return int(curr_node.chosen_tag)
        
        
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
            'new corn based recipe will rock your word',
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
    msg_objs=[a.split(' ') for a in messages]
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
                'religious riot in the_netherlands',
                'cocoa ban in china lifted']#this test set is too hard. pumpkin is impossible, and cocoa_ban is kind of also impossible
    test=[a.split(' ') for a in test_msgs]
    test_lbl= (array([1,-1,-1,1,1,-1,-1,1,-1,1])+1)/2
    vld_msgs=['rome less visit than vatican_city according to census data',
               'why the french_revolution help shape the world today',
               'sweet_potato famine suspect in ireland connection to ireland_potato_famine suspect',
               'doctor treat cancer with salad claim pepper and tomato have medicinal effects',
               'russia annex crimea_peninsula president vladimir_putin to make statement',
               'fish cost worldwide increase due to over-fishing',
               'cocoa flavor orange tree develop in mit',
               'pineapple goes well with avocado according to flavor specialist',
               'orange orange in the_netherlands',
               'corn voted most corny new world food']
    vld=[a.split(' ') for a in vld_msgs]
    vld_lbls=(array([-1,-1,1,1,-1,-1,1,1,-1,1])+1)/2
    relations={}
#    relations['type']={'potato':'vegetable', 'cuban_missile_crisis':'event', 'cocoa':'fruit', 'france':'country', 'rice':'cereal', 'china':'country', 'pineapple':'fruit', 'oslo_peace_conference':'event'
#                        , 'apple':'fruit', 'pear':'fruit', 'turkey':'country', 'u.s.':'country', 'edward_snoden_leak':'event', 'nsa':'organization', 'obama':'person', 'dog':'animal', 'mit':'university',
#                            'ireland_potato_famine':'event', 'wheat':'cereal', 'cucumber':'vegetable', 'chile':'country', 'cuba':'country', 'venezuela':'country', 'brazil':'country', 'norway':'country',
#                            'italy':'country', 'syria':'country', 'india':'country', 'norway':'country', 'ireland':'country', 'north_america':'continent', 'south_america':'continent', 'europe':'continent', 
#                            'asia':'continent', 'tomato':'fruit', '2014_israel_president_election':'event', 'israel':'country', 'mexico':'country'}
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
    #relations['calorie_content_kcal']={'tomato':18, 'potato':77, 'rice':365, 'pineapple':50, 'apple':52, 'pear':57, 'wheat':327, 'cucumber':16}#apply to fruit/vegetable, numeric. missing for cocoa
    relations['happend_in_place']={'cuban_missile_crisis':'cuba', 'oslo_peace_conference':'norway', 'edward_snoden_leak':'u.s.', 'ireland_potato_famine':'ireland', '2014_israel_president_election':'israel','french_revolution':'france','2016_olympics':'brazil', 'cocoa_ban':'china',
                                    'fu':'f','r':'r','b':'b','c':'c','d':'d'}#apply to event(cuba missile crisis)
    #relations['happend_on_date']={'cuban_missile_crisis':1962, 'oslo_peace_conference':1993, 'edward_snoden_leak':2013, 'ireland_potato_famine':1845, '2014_israel_president_election':2014} #apply to event, numeric
    for key in relations.keys():
        new_key= 'reverse_'+key
        relations[new_key]= {}
        for (a,b) in relations[key].items():
            if relations[new_key].has_key(b):
                relations[new_key][b].append(a)
                continue
            relations[new_key][b]= [a]
    
    #now for actual stuff:
#    SPLIT_THRESH=4
#    blah1=TreeRecursiveSRLClassifier(msg_objs, message_labels, relations, [], True)#no recursive!
#    before=time.time()
#    blah1.train()
#    print time.time()-before
#    pred1trn=array([blah1.predict(x) for x in msg_objs])
#    print mean(pred1trn!=message_labels)
#    pred1tst=array([blah1.predict(x) for x in test])
#    print mean(pred1tst!=test_lbl)
#    MAX_DEPTH=0
#    blah2=TreeRecursiveSRLClassifier(msg_objs, message_labels, relations, [])#no recursive but has relation usage...
#    before=time.time()
#    blah2.train()
#    print time.time()-before
#    pred2trn=array([blah2.predict(x) for x in msg_objs])
#    print mean(pred2trn!=message_labels)
#    pred2tst=array([blah2.predict(x) for x in test])
#    print mean(pred2tst!=test_lbl)
    blah3=TreeRecursiveSRLClassifier(msg_objs, message_labels, relations, [], 200, 2, 3)
    before=time.time()
    blah3.train()
    print time.time()-before
    pred3trn=array([blah3.predict(x) for x in msg_objs])
    print mean(pred3trn!=message_labels)
    pred3tst=array([blah3.predict(x) for x in test])
    print mean(pred3tst!=test_lbl)