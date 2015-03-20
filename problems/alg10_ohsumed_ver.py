# -*- coding: utf-8 -*-
"""
Created on Sun Jan 18 16:46:57 2015

@author: liorf
"""

from numpy import *
from matplotlib.mlab import find
from scipy.stats import mode, chisquare

import time


def clean_tree_for_pickle(tree_node):
#    tree_node.relations=None
    if tree_node.chosen_query is None:
        return
    try:
        clean_tree_for_pickle(tree_node.justify)
    except:
        pass
    #for (tree_root,_,_) in tree_node.cool_things:
    #    clean_tree_for_pickle(tree_root)
    tree_node.chosen_query=None
    for son in tree_node.sons.values():
        clean_tree_for_pickle(son)
    return tree_node
        
def entropy(tags): #this is 0 if all same tag, 1 if uniform, lower=better
    '''computes entropy on tags. Assumes binary 0-1 tagging only.(not +-1 !!!)
    entropy= sum(-f*log2(f)) where f are the frequencies of each value'''
    length=len(tags)*1.0
    value_list=frozenset(tags)
    ent=0.0
    for val in value_list:
        count=count_nonzero(tags==val)/length
        ent-=count*log2(count)
    return ent 
 
def statistic_test(tagging, feature_values):
    '''need to compare the two sides I split (how many of each label in each one)'''
    return 0.0,0.0
#    if len(frozenset(feature_values))>2:
#        return 0.0,0.0 #only works for 2 values
#    locs= find(feature_values==1)
#    locs2= find(feature_values!=1)
#    observed= array([len(find(tagging[locs]==1)),len(find(tagging[locs]!=1))])
#    expected= array([len(find(tagging[locs2]==1)),len(find(tagging[locs2]!=1))])
#    if any(expected==0):
#        if any(observed==0):
#            return inf, 0.0 #this is good for us
#        return chisquare(expected, observed)
#    return chisquare(observed, expected) #high stat+low p->good
    
def info_gain(curr_node_tags, feature_values): #0 if same divide, 1 if perfect
    '''computes simple info-gain for a split. '''

    curr_ent = entropy(curr_node_tags) #current entropy H(T)
    #sum over all values: #elements with this value/#total elements * entropy(elements with this value)
    cond_ent = 0.0
    total_elem_sz = 1.0*len(feature_values)
    
    for value in frozenset(feature_values):
        locs= find(feature_values == value)
        value_prob = len(locs)/total_elem_sz
        cond_ent += value_prob*entropy(curr_node_tags[locs])
    return curr_ent- cond_ent
    
def ig_ratio(curr_node_tags, feature_values, discard_na=False):
    intrinsic_val= 0.0
    if discard_na is True:
        inds= find(feature_values!=-1)
        if len(inds)==0:
            print 'something has gone horribly wrong!'
            return 0.0
        feature_values= feature_values[inds]
        curr_node_tags= curr_node_tags[inds]
    
    total_elem_sz = 1.0*len(feature_values)
    
    for value in frozenset(feature_values):
        locs= find(feature_values == value)
        value_prob = len(locs)/total_elem_sz
        intrinsic_val += value_prob*log2(value_prob)
    if intrinsic_val==0.0: #labels are all the same! can just return ig(thing) (which is 0)
        return info_gain(curr_node_tags, feature_values)
    return -1*info_gain(curr_node_tags, feature_values)/intrinsic_val
    
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
    
def relabel(complex_objs, old_tagging, majority=True):
    '''flatten+label(majority or consistent)'''
    val_map={}
    for i,obj in enumerate(complex_objs):
        tag= old_tagging[i]
        for item in obj: #each entity
            if not val_map.has_key(item):
                val_map[item]={}
            if not val_map[item].has_key(tag):
                val_map[item][tag]=0
            val_map[item][tag]+=1
    blorf= [[a] for a,counts in val_map.items() if len(counts.values())==1 or #it is not the case that there is full equality for all tags, so it's 1-1-1 or 2-2-2
        sum(counts.values()) % len(counts.values()) != 0]
    items= array(blorf, dtype=object)
    
    tags=[]
    for i,item in enumerate(items):
        label_counts=val_map[item[0]]
        #label counts is mapping of tag->apperances
        if majority:
            tags.append(label_counts.keys()[argmax(label_counts.values())])
        else:
            vals=array(label_counts.values())
            inds= find(vals>0)
            if len(inds) == 1: #exactly one class
                tags.append(array(label_counts.keys())[inds])
            else:
                tags.append(-1)
    tags=array(tags)
    if majority:
        return items,tags
    idxs=find(tags>=0)
    return items[idxs], tags[idxs]

def apply_transforms_other(relations, transforms, objects):
    '''transforms is list of relation+direction pairs.
    objects is set of objects(set of sets'''
    curr_objs=objects
    for relation in transforms:
        curr_objs= [is_in_relation(obj, relations[relation], relation) for obj in curr_objs]
    return curr_objs
    
def apply_transforms(relations, transforms, objects):
    '''transforms is list of relation+direction pairs.
    objects is set of objects(set of sets'''
    if len(transforms)==0:
        return objects
    curr_objs=[is_relation_key(x, relations[transforms[0]]) for x in objects]
    return apply_transforms_other(relations, transforms[1:], curr_objs)
    for relation in transforms[1:]:
        curr_objs= [is_in_relation(obj, relations[relation], relation) for obj in curr_objs]
    return curr_objs

def split_and_subtree(query_chosen, recursive_step_obj):
    query_results=array([query_chosen(x) for x in recursive_step_obj.objects])
    for val in frozenset(query_results):
        inds=find(query_results==val)
        ents_son= [] if len(recursive_step_obj.entities)==0 else recursive_step_obj.entities[inds]
        recursive_step_obj.sons[val]= TreeRecursiveSRLStep(recursive_step_obj.objects[inds],ents_son, recursive_step_obj.tagging[inds], recursive_step_obj.relations, 
                                        recursive_step_obj.transforms, recursive_step_obj.n, recursive_step_obj.MAX_DEPTH, 
                                        recursive_step_obj.SPLIT_THRESH, recursive_step_obj.logfile, recursive_step_obj.stopthresh, recursive_step_obj.cond)
    return query_chosen,recursive_step_obj.sons, recursive_step_obj.good_recs, recursive_step_obj.good_recs_justify, recursive_step_obj.good_recs_trees
def ig_from_one_retag(tagging): 
    curr_max= -1.0
    for value in frozenset(tagging):
        ind= find(tagging==value)[0]
        tag_pos= zeros(len(tagging))
        tag_pos[ind]= 1
        curr_max= max(curr_max, ig_ratio(tagging, tag_pos))
    return curr_max
        
MAX_SIZE= 1500 #TODO: change this in future(needed to make it run fast)
IGTHRESH=0.01
P_THRESH=0.001
#BAD_RELATION=False
class TreeRecursiveSRLStep(object):
    def __init__(self, objects, entities, tagging, relations, steps_to_curr, n, MAX_DEPTH, SPLIT_THRESH, logfile, stopthresh, cond=False):
        self.relations= relations
        self.objects =array(objects)
        self.tagging=tagging
        self.entities= entities
        if len(objects) > 0:
            self.chosen_tag= mode(tagging)[0] 
        else:
            self.chosen_query=None
            self.justify='no objects'
            self.chosen_tag=None
        self.transforms= steps_to_curr        
        self.ig = None
        self.chosen_query=None
        self.cond=cond
        self.n=n
        self.MAX_DEPTH=MAX_DEPTH
        self.SPLIT_THRESH=SPLIT_THRESH
        self.logfile= logfile
        self.sons= {}
        
        self.cool_things=[]
        self.is_rec= False
        self.good_recs= []
        self.good_recs_justify= []
        self.good_recs_trees= []
        self.stopthresh= stopthresh
        self.logfile.write(' '*len(self.transforms)+'Created node. Num objects: '+str(len(self.tagging))+': '+str(len(find(self.tagging==1)))+' positive, '+str(len(find(self.tagging!=1)))+' negative.\n' )#'Positive: '+str(self.objects[find(self.tagging==1)])+' \n Negative: '+str(self.objects[find(self.tagging!=1)])+'\n')

    def pick_split_query(self):
        '''pick one query(if simple query on objects give high IG, do that, otherwise go recursive and build tree as query'''
        '''never have to worry about len(transforms)>0'''
        avg_word_ig=0.0
        all_words=set()
        for words in self.objects:
            all_words.update(words)
        max_ig,best_word=-1.0,''
        for word in all_words:
            word_ig= ig_ratio(self.tagging, array([1 if (word in obj) else 0 for obj in self.objects]))
            avg_word_ig+=word_ig
            if word_ig>max_ig:
                max_ig,best_word=word_ig,word
        self.chosen_query, self.ig, self.justify=lambda x: 1 if (best_word in x) else 0, max_ig, 'hasword:'+str(best_word)
        avg_word_ig=avg_word_ig/len(all_words)
        if self.cond is True or self.MAX_DEPTH==0 or len(self.objects)< self.stopthresh:
            if self.ig <= ig_from_one_retag(self.tagging): #no query is useful enough
                self.chosen_query=None
                self.justify='nothing useful for tagging'
                return None,self.sons, [], [], []
            self.logfile.write('chose query: '+self.justify+'. ig is '+str(self.ig)+'\n')
            return split_and_subtree(self.chosen_query, self)
        
        #Build relation-based features(super table) for objects, see if any query good enough
        relevant_features= [] #list of relation,direction pairs that are relevant(to pick from)
        for relation in self.relations.keys():    
            feature_vals=[is_relation_key(ents, self.relations[relation]) for ents in self.entities] 
            val_lens=[len(val) for val in feature_vals]
            if sum(val_lens)==0 : #no objects have relevant values. This may leave us with objects whose feature values are [], which means any query will return false...
                continue #not relevant
            relevant_features.append(relation)
        
        min_ig_required= ig_from_one_retag(self.tagging)
        if self.ig <= min_ig_required: #was IGTHRESH
            self.chosen_query=None
            self.justify='not good enough'
            return None,self.sons, [], [], []
        if len(relevant_features)==0:
            print 'no relations can be used on this problem!'
            self.logfile.write('chose query: '+self.justify+'. ig is '+str(self.ig)+'\n')
            return split_and_subtree(self.chosen_query, self)
        
        #sample relevent features n times(with replacement, so recursive n is the amount chosen)
        choices=random.choice(relevant_features, self.n, True)
        
        temp={}
        for relation in choices:
            if temp.has_key(relation):
                temp[relation]+=1
                continue
            temp[relation]=1
        
        worthy_relations= temp.items()
        self.bttoo=worthy_relations
        tree_ig=0.0
        best_ig= self.ig
        before_all= time.time()
        for relation_used_for_recursive,rel_n in worthy_relations:  
            
            feature_vals=[is_relation_key(ents, self.relations[relation_used_for_recursive]) for ents in self.entities]
            new_objs, new_tagging= relabel(feature_vals, self.tagging) #flatten+relabel
            #3)call TreeRecursiveSRLClassifier
            classifier_chosen= TreeRecursiveSRLClassifier(new_objs, [], new_tagging, self.relations, self.transforms+[relation_used_for_recursive], rel_n, self.MAX_DEPTH,self.SPLIT_THRESH, self.logfile, self.cond)
            inds= [i for i,v in enumerate(feature_vals) if len(v)>0]
            def rep_zero(x):
                if x==0:
                    return 1
                return x
            blop=0.
            if len(new_tagging)!=0:
                blop=len(find(new_tagging!=mode(new_tagging)[0]))*1.0/len(new_tagging)
            self.logfile.write('trying out tree with transform:'+str(self.transforms+[relation_used_for_recursive])+'. Number of N/A:'+str(len([p for p in feature_vals if len(p)==0]))+'. Ratio of new/old misclass ratios: '+str( 
            (blop)/rep_zero(len(find(self.tagging[inds]!=self.chosen_tag))*1.0/len(inds)) ) +'\n')
            before=time.time()
            classifier_chosen.train_vld_local()
            self.logfile.write('tree tried! Time: '+str(time.time()-before)+'\n')
            
            #TODO: FIXME!!!!!! predict shouldn't work on x but rather do something smart...
            clf_labels=array([classifier_chosen.predict(x) for x in self.entities])
            tree_ig=ig_ratio(self.tagging, clf_labels)
            tree_ig_penalty=1 #TODO? something to do with tree size and depth?
                    
            self.cool_things.append((classifier_chosen.transforms,tree_ig,self.ig))
            if tree_ig/tree_ig_penalty >= best_ig: #any better than non-rec
                self.good_recs.append(lambda x,c=classifier_chosen: c.predict(x))
                self.good_recs_justify.append(str(classifier_chosen.transforms))
                self.good_recs_trees.append((relation_used_for_recursive,classifier_chosen))
            
            if tree_ig/tree_ig_penalty >= self.ig: #if tree is better, it's the new classifier                
                test_statistic, p_val= statistic_test(self.tagging, clf_labels) #high stat+low p->good
                if p_val > P_THRESH: #1% confidence level
                    continue
                self.is_rec= True
                self.logfile.write('chose tree with: '+str(self.transforms+[relation_used_for_recursive])+'. ig is '+str(tree_ig)+'\n')
                self.chosen_query= lambda x, b=classifier_chosen: b.predict(x)
                self.ig, self.justify= tree_ig, classifier_chosen.query_tree
            else:
                del classifier_chosen
        self.logfile.write('finished recursive part for node. Time: '+str(time.time()-before_all)+'\n')
        
        if self.ig <= 0: #no query is useful
            self.chosen_query=None
            self.justify='nothing useful for tagging'
            return None,self.sons, [],[], []
        self.logfile.write('chose query: '+str(self.justify)+'. ig is '+str(self.ig)+'\n')
        return split_and_subtree(self.chosen_query, self)
    
    def filter_bad_rels(self, relations, value_things):
        #filter transforms+non-relevant since doesn't apply
        #relations-relations I consider moving to
        new_rel_fet=[]
        new_avg_ig=[]
        for i,relation in enumerate(relations):
            if len(self.transforms)>1 and (relation=='reverse_'+self.transforms[-1] or (relation==self.transforms[-1].replace('reverse_','') and relation!=self.transforms[-1]) or (len(self.transforms)>1 and relation==self.transforms[-1])) :
                continue #no using the relation you came with on the way back...
            if value_things[i]<=0.0:
                continue #ig is 0->no point            
            barf=False
            new_objs=apply_transforms_other(self.relations, [relation], self.objects)
            if sum([len(obj) for obj in new_objs])==0:#all objects are []
                continue
            for other_rel in self.relations.keys():
                if other_rel==relation or other_rel=='reverse_'+relation or other_rel==relation.replace('reverse_',''):
                    continue
                feature_vals= [is_in_relation(obj, self.relations[other_rel],other_rel) for obj in new_objs]#apply_transforms_other(self.relations, [other_rel],new_objs)# 
                val_lens=[len(val) for val in feature_vals]
                if sum(val_lens)>0 :
                    barf=True
                    break
            if barf:   
                new_rel_fet.append(relation)
                new_avg_ig.append(value_things[i]) 
        return new_rel_fet, array(new_avg_ig)
                   
                
    def pick_split_vld_local(self):
        '''never have to worry about len(transforms==0)'''
        relevant_features= [] #list of relation,direction pairs that are relevant(to pick from)
        relation_avg_igs= [] #in alg 3 we only 
        self.chosen_query=None 
        
        self.ig= -1.0#best known error: treat me as leaf
        best_ig, relation_used, constant= self.ig,None,''
        for relation in self.relations.keys():
            if relation=='reverse_'+self.transforms[-1] or (relation==self.transforms[-1].replace('reverse_','') and relation!=self.transforms[-1]) or (len(self.transforms)>1 and relation==self.transforms[-1]) :
                continue #no using the relation you came with on the way back...
            feature_vals=[is_in_relation(obj, self.relations[relation],relation) for obj in self.objects] #apply_transforms_other(self.relations, [relation], self.objects) #
            val_lens=[len(val) for val in feature_vals]
            if sum(val_lens)==0 : #no objects have relevant values. This may leave us with objects whose feature values are [], which means any query will return false...
                continue #not relevant
            
            relation_constants= set()
            for obj in feature_vals:
                for const in obj:
                    relation_constants.add(const)            
            sz=len(relation_constants)
            if sz>=MAX_SIZE:
                continue #For now, skip. 
            relation_constants.add(None)
            
            avg_for_rel=0.0                        
            for const in relation_constants:
                if const is None:
                    query= lambda x: 1 if len(is_in_relation(x, self.relations[relation],relation))==0 else 0
                else:
                    query= lambda x: 1 if is_in_relation(x, self.relations[relation],relation,const) else 0
                
                ig_for_const= ig_ratio(self.tagging, array([query(x) for x in self.objects]))

                avg_for_rel+=ig_for_const
                if ig_for_const>best_ig:
                    best_ig, relation_used, constant= ig_for_const, relation,const            
            
            relevant_features.append(relation)
            relation_avg_igs.append(avg_for_rel/len(relation_constants))
            
        #1)pick some relation from relevant_features(how?) 
        if len(relevant_features)==0:
            self.chosen_query=None
            self.justify='no features'
            return None,self.sons, [],[], []
        if constant is None:
            self.chosen_query= lambda x: 1 if len(is_in_relation(x, self.relations[relation_used],relation_used))==0 else 0
        else:
            self.chosen_query= lambda x: 1 if is_in_relation(x, self.relations[relation_used],relation_used,constant) else 0
        self.ig, self.justify= best_ig, 'hasword(X),X in relation: %s with %s'%(relation_used, constant)
        
        min_ig_required= ig_from_one_retag(self.tagging)
        if self.ig<= min_ig_required:
            self.chosen_query=None
            self.justify='not good enough'
            return None,self.sons, [],[], []
        
        clf_tagging= array([self.chosen_query(x) for x in self.objects])
        test_val, p_val= statistic_test(self.tagging, clf_tagging) #high stat+low p->good
        if p_val > P_THRESH: #10% confidence level
            self.chosen_query=None
            self.justify='not good enough'
            return None,self.sons, [],[], []     
            
        if len(self.transforms)>= self.MAX_DEPTH: 
            self.justify=self.justify+' and max depth reached'
            self.logfile.write(' '*len(self.transforms)+'chose query: '+self.justify+'. ig is '+str(self.ig)+'\n')
            return split_and_subtree(self.chosen_query, self)
        
        relevant_features, relation_avg_igs =self.filter_bad_rels(relevant_features, relation_avg_igs)
        if len(relevant_features)==0: #had feature, now I don't
            self.justify=self.justify+' also cannot recurse'
            self.logfile.write(' '*len(self.transforms)+'chose query: '+self.justify+'. ig is '+str(self.ig)+'\n')
            return split_and_subtree(self.chosen_query, self)
            
        #sample relevent features n times(with replacement, so recursive n is the amount chosen)
        choices=random.choice(relevant_features, self.n, True, relation_avg_igs/sum(relation_avg_igs))
        temp={}
        for relation in choices:
            if temp.has_key(relation):
                temp[relation]+=1
                continue
            temp[relation]=1
        
        worthy_relations= temp.items()
        self.bttoo=worthy_relations
    
        tree_ig=0.0
        before_all= time.time()
        for relation_used_for_recursive,new_n in worthy_relations:  
            feature_vals=[is_in_relation(obj, self.relations[relation_used_for_recursive],relation_used_for_recursive) for obj in self.objects]#apply_transforms_other(self.relations, [relation_used_for_recursive], self.objects) #
            new_objs, new_tagging= relabel(feature_vals, self.tagging) #flatten+relabel
            #3)call TreeRecursiveSRLClassifier
            classifier_chosen= TreeRecursiveSRLClassifier(new_objs, [], new_tagging, self.relations, self.transforms+[relation_used_for_recursive], new_n ,self.MAX_DEPTH, self.SPLIT_THRESH,self.logfile, self.cond)
            inds= [i for i,v in enumerate(feature_vals) if len(v)>0]
            def rep_zero(x):
                if x==0:
                    return 1
                return x
            blop=0.
            if len(new_tagging)!=0:
                blop=len(find(new_tagging!=mode(new_tagging)[0]))*1.0/len(new_tagging)
            self.logfile.write(' '*len(self.transforms+['a'])+'trying out tree with transform:'+str(self.transforms+[relation_used_for_recursive])+'. Number of N/A:'+str(len([p for p in feature_vals if len(p)==0]))+'. Ratio of new/old misclass ratios: '+str( 
            (blop)/rep_zero(len(find(self.tagging[inds]!=self.chosen_tag))*1.0/len(inds)) ) +'\n')
            before= time.time()
            classifier_chosen.train_vld_local()
            self.logfile.write(' '*len(self.transforms)+'tree tried! Time: '+str(time.time()-before)+'\n')
            
            query=lambda x, b=classifier_chosen: b.predict(x, True)
            clf_tagging= array([query(x) for x in self.objects])
            tree_ig=ig_ratio(self.tagging, clf_tagging)
            tree_ig_penalty=1.0 #TODO? something to do with tree size and depth?
            
            self.cool_things.append((classifier_chosen.transforms,tree_ig,self.ig))
            if tree_ig/tree_ig_penalty >= self.ig: #if tree is better, it's the new classifier
                test_val, p_val= statistic_test(self.tagging, clf_tagging) #high stat+low p->good
                if p_val > P_THRESH: #1% confidence level
                    continue #tree not good enough!
                self.is_rec= True
                self.logfile.write(' '*len(self.transforms)+'chose tree with: '+str(self.transforms+[relation_used_for_recursive])+'. ig is '+str(tree_ig)+'\n')
                self.chosen_query= lambda x, b=classifier_chosen: b.predict(x, True)
                self.ig, self.justify= tree_ig, classifier_chosen.query_tree
            else:
                del classifier_chosen
        self.logfile.write(' '*len(self.transforms)+'finished recursive part for node. Time: '+str(time.time()-before_all)+'\n')
        
        if self.ig <= 0 : #no query is useful
            self.justify='nothing useful for tagging'
            return None,self.sons, [],[], []         
        self.logfile.write(' '*len(self.transforms)+'chose query: '+str(self.justify)+'. ig is '+str(self.ig)+'\n')
        return split_and_subtree(self.chosen_query, self)
        
class TreeRecursiveSRLClassifier(object):
    def __init__(self, objects, entities, tagging, relations, transforms, n, MAX_DEPTH, SPLIT_THRESH, logfile, cond=False):
        self.relations= relations
        self.objects =objects
        self.entities= entities
        self.tagging=tagging
        self.transforms=transforms
        self.cond=cond
        self.n=n
        self.MAX_DEPTH=MAX_DEPTH
        self.SPLIT_THRESH=SPLIT_THRESH
        self.logfile= logfile
        self.logfile.write(' '*len(self.transforms)+'Created tree with transforms: '+str(self.transforms)+'\n')
        
        self.recursive_features=[] #the important thing in the end!
        self.feature_justify= [] #the relation used for tree?
        self.feature_trees= []
        
    def train(self, stopthresh):
        num_nodes= 0
        depth= 0
        self.tree_sets= [TreeRecursiveSRLStep(self.objects, self.entities, self.tagging, self.relations, self.transforms, self.n, self.MAX_DEPTH, self.SPLIT_THRESH, self.logfile, stopthresh, self.cond)] #initally all in same node
        self.tree_sets[0].depth= 1
        for node in self.tree_sets:
            if len(node.objects)<=self.SPLIT_THRESH or all(node.tagging==node.chosen_tag):#consistent/too small to split 
                node.justify='leafed(thresh/constistant)'
                node.chosen_query=None
                self.logfile.write('node became leaf\n')
                continue #leaf
            _,sons, rec_feature, justify, trees =node.pick_split_query()
            if len(sons.keys())==0:
                node.justify='leafed(weird stuff)'
                node.chosen_query=None
                self.logfile.write('node became leaf\n')
                continue#another leaf case...
            num_nodes+=1
            self.recursive_features.extend(rec_feature)
            self.feature_justify.extend(justify)
            self.feature_trees.extend(trees)
            depth= max(depth, node.depth)
            for son in sons.values():
                son.depth= node.depth+1
            self.tree_sets.extend(sons.values()) 
        self.query_tree=self.tree_sets[0] #root
        self.logfile.write('training done. num_nodes: '+str(num_nodes)+'. depth: '+str(depth)+'\n')
        
    def train_vld_local(self):
        num_nodes= 0
        depth= 0
        self.tree_sets=[TreeRecursiveSRLStep(self.objects, self.entities, self.tagging, self.relations, self.transforms,self.n,  self.MAX_DEPTH, self.SPLIT_THRESH,self.logfile, inf, self.cond)] #initally all in same node
        self.tree_sets[0].depth= 1
        self.query_tree=self.tree_sets[0] #root
        for node in self.tree_sets:
            if (len(node.objects)<self.SPLIT_THRESH or all(node.tagging==node.chosen_tag)):#consistent/too small to split 
                node.justify='leafed(thresh/constistant)'
                node.chosen_query=None
                self.logfile.write(' '*len(self.transforms)+'node became leaf\n')
                continue #leaf            
            _,sons,_,_,_ =node.pick_split_vld_local()
            if len(sons.keys())==0:
                node.justify='leafed(weird stuff)'
                node.chosen_query=None
                self.logfile.write(' '*len(self.transforms)+'node became leaf\n')
                continue#another leaf case...
            num_nodes+=1
            depth= max(depth, node.depth)
            for son in sons.values():
                son.depth= node.depth+1
            self.tree_sets.extend(sons.values())
        self.query_tree=self.tree_sets[0] #root
        self.logfile.write(' '*len(self.transforms)+'training done. num_nodes: '+str(num_nodes)+'. depth: '+str(depth)+'\n')
    
    def predict(self, entities, flag=False):  
        #if depth > 0, object is an entity list. otherwise, problem!!!!
        NA_VAL= -100
        curr_node= self.query_tree
        if curr_node.chosen_tag is None:#edge case in the case of consistent
            return 0#some arbitrary rule
        while curr_node.chosen_query is not None:            
            if len(curr_node.sons.keys())==1: #only one son
                curr_node=curr_node.sons[curr_node.sons.keys()[0]]
                continue
            
            transformed_obj= apply_transforms(curr_node.relations, curr_node.transforms, [entities]) 
            if flag:
                transformed_obj= apply_transforms_other(curr_node.relations, curr_node.transforms[-1:], [entities])
            query_val= None
            #print transformed_obj

            if len(transformed_obj[0])==0: #no entities
                query_val= NA_VAL
                if len(self.transforms)>0:
                    return NA_VAL
                #if not lvl0, return -1 for this
            elif not curr_node.is_rec:
                query_val= curr_node.chosen_query(transformed_obj[0])
            else: 
                vals=[]
                if len(self.transforms)==0: #need apply trans
                    vals= [curr_node.chosen_query([x]) for x in transformed_obj[0] if len(apply_transforms(curr_node.relations, curr_node.justify.transforms, [x])[0])>0]
                else:
                    vals= [curr_node.chosen_query([x]) for x in transformed_obj[0] if len(apply_transforms_other(curr_node.relations, curr_node.justify.transforms[-1:], [x])[0])>0]
                if len(vals)>0:
                    query_val= int(mode(vals)[0][0]) #ISSUE: mode is problem if equal...
                else:
                    query_val= NA_VAL #query for tree is -1
            
            tmp= curr_node.chosen_tag
            curr_node=curr_node.sons.get(query_val)
            if curr_node is None: #tried tree that has no N/A in train, but does in test/ example was []
                return tmp #best possible guess
        return int(curr_node.chosen_tag)
        
class FeatureGenerationFromRDF(object):
    def __init__(self, objects, entities, tagging, relations):
        self.objects= objects
        self.entities= entities
        self.tagging= tagging
        self.relations= relations
        
        self.new_features= []
        self.new_justify= []
        self.feature_trees= []
    
    def generate_features(self, n, max_depth, split_thresh, logfile, STOPTHRESH= 10, version=1):
        if version==1: #first version: stop-thresh+take all better.
            tree= TreeRecursiveSRLClassifier(self.objects, self.entities, self.tagging, self.relations, [], n, max_depth, split_thresh, logfile)
            tree.train(STOPTHRESH) #minimum number of objects!
        
            self.new_features= list(tree.recursive_features)
            self.new_justify= list(tree.feature_justify)
            self.feature_trees= list(tree.feature_trees)
            return
        elif version==2: #second version will be the stochastic thing on examples
            for i in xrange(10):
                inds= random.choice(len(self.objects), len(self.objects)/2, replace=False)
                tree= TreeRecursiveSRLClassifier(self.objects[inds], self.entities[inds], self.tagging[inds], self.relations, [], n, max_depth, split_thresh, logfile)
                tree.train(STOPTHRESH)
                
                self.new_features.extend(tree.recursive_features)
                self.new_justify.extend(tree.feature_justify)
                self.feature_trees.extend(tree.feature_trees)
                return
        
    
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
        return self.table, self.tagging, self.test, self.feature_names, self.feature_trees
                    
    
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
            
    logfile= open('run_log.txt','w')
    blor= FeatureGenerationFromRDF(msg_objs,msg_entities,  message_labels, relations)
    before=time.time()
    blor.generate_features(200, 2, 3, logfile, 1, 1)    
    #blah3=TreeRecursiveSRLClassifier(msg_objs, message_labels, relations, [], 200, 2, 3, logfile)    
    #blah3.train(1)
    print time.time()-before
    logfile.close()
    trn, trn_lbl, tst, feature_names, floo= blor.get_new_table(test, tst_ents)
    
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.feature_selection import SelectKBest

#    feature_selector= SelectKBest(chi2, k=100)
#    filtered_trn= feature_selector.fit_transform(trn, trn_lbl)
#    filtered_tst= feature_selector.transform(tst)
    blah3= SVC(kernel='linear', C=inf)
#    blah3= KNeighborsClassifier(n_neighbors=5)
#    blah3= DecisionTreeClassifier(criterion='entropy', min_samples_split=2)
    blah3.fit(trn, trn_lbl)
    
    pred3trn=blah3.predict(trn)
    print mean(pred3trn!=trn_lbl)
    pred3tst=blah3.predict(tst)
    print mean(pred3tst!=test_lbl)
    print len(blor.new_features)
    
