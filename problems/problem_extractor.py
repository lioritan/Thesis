
import os


def binary_bow_feature(message):    
    import nltk
    return set(nltk.word_tokenize(message.lower())) 
    
def parse_reuters_message(fptr):
    '''parses one message(reuters to /reuters) from the file.
    returns tuple (type, content, categories)
    type->'train','test' or 'skip', uses ModApte
    content->text
    categories->list of categories
    '''
    header=fptr.readline()
    if len(header)==0:
        return None #reached EOF
    is_train= header[rfind(header_split, 'LEWISSPLIT="'):].split('"')[0] 
    message_type= 'train' if is_train=='TRAIN' else 'test' if is_train=='TEST' else 'skip'
    
    header=fptr.readline()#skip dateline
    header=fptr.readline() #Topic line. TODO:extract topics. if none relevant, return None?
    tags=[]#TODO
    
    while find(header, 'BODY')==-1 and find(header, 'REUTERS')==-1:
        header=fptr.readline() #skip lines
        
    if find(header, 'REUTERS')!=-1:
        header=fptr.readline() #go to next message
        return None  #no body=worthless
        
    #Now we have the body of the text. 
    #TODO: handle first line:
    pass
    content=''#TODO
    
    header=fptr.readline()
    while find(header, '/BODY')==-1: #not done with content yet
        content=content+header
        header=fptr.readline()
        
    header=fptr.readline() #read the </REUTERS> line
    header=fptr.readline() #go to next message!
    return (message_type, content, tags)

PATH=r'C:\Users\liorf\Desktop\thesis code\problems\reuters21578\'
categories= ['acq','corn', 'crude', 'earn', 'grain', 'interest', 'money-fx', 'ship', 'trade', 'wheat']
    
if __name__=='__main__':
    data_train = []
    tags_train = []
    data_test = []
    tags_test = []
    for _,_,filenames in os.walk(PATH):
        for filename in filenames:
            fptr=open(PATH+filename, 'r')
            fptr.readline() #skip first line
            fptr.read()
            message= parse_reuters_message(fptr)
            while message is not None:
                if message[0]=='train':
                    data_train.append(message[1])
                    tags_train.append(message[2])
                elif message[0]=='test':
                    data_test.append(message[1])
                    tags_test.append(message[2])
                message= parse_reuters_message(fptr)
            fptr.close()
            