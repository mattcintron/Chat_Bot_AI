import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow as tf
import random
import json
from pathlib import Path
import time


with open(str(Path(__file__).absolute().parent /'json_files'/'intents.json')) as file:
    data = json.load(file)

# use to make sure only relivent words are matching-
stop_words=["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", 
 "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", 
 "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", 
 "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and",
 "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between",
 "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on",
 "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all",
 "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same",
 "so", "than", "too", "very", "can", "will", "just", "don't", "should", "now","·",]


#extract data
words = []
labels = []
docs_x = []
docs_y = []




for intent in data['intents']:
    for pattern in intent['patterns']:
        wrds = nltk.word_tokenize(pattern)
        words.extend(wrds)
        docs_x.append(wrds)
        docs_y.append(intent["tag"])
        
    if intent['tag'] not in labels:
        labels.append(intent['tag'])
        

#stem words
words = [stemmer.stem(w.lower()) for w in words if w != "?"]
words = sorted(list(set(words)))

labels = sorted(labels)

training = []
output = []

out_empty = [0 for _ in range(len(labels))]

for x, doc in enumerate(docs_x):
    bag = []

    wrds = [stemmer.stem(w.lower()) for w in doc]

    for w in words:
        if w in wrds:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1

    training.append(bag)
    output.append(output_row)


training = numpy.array(training)
output = numpy.array(output)


#set up model
tf.compat.v1.reset_default_graph()
net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)

try:
    model.load(str(Path(__file__).absolute().parent /'notebooks'/'model_data'/'model.tflearn'))
    print('model loaded')
except:
    print('no model to load')


def retrain_model():
    #set globals
    global data
    global words
    global docs_x
    global docs_y
    global training
    global output
    global out_empty
    global model
    global labels

    print('training model')
    with open(str(Path(__file__).absolute().parent /'json_files'/'intents.json')) as file:
        data = json.load(file)

    #extract data
    words = []
    labels = []
    docs_x = []
    docs_y = []

    for intent in data['intents']:
        for pattern in intent['patterns']:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
            
        if intent['tag'] not in labels:
            labels.append(intent['tag'])
            
    #stem words
    words = [stemmer.stem(w.lower()) for w in words if w != "?"]
    words = sorted(list(set(words)))

    labels = sorted(labels)

    training = []
    output = []

    out_empty = [0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)

        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    #set up model structure
    tf.compat.v1.reset_default_graph()
    net = tflearn.input_data(shape=[None, len(training[0])])
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, 8)
    net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
    net = tflearn.regression(net)

    #set model training
    model = tflearn.DNN(net)
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save(str(Path(__file__).absolute().parent /'notebooks'/'model_data'/'model.tflearn'))
    model.load(str(Path(__file__).absolute().parent /'notebooks'/'model_data'/'model.tflearn'))

def text_count(s0, s1):
    s0 = s0.lower()
    s1 = s1.lower()
    s0List = s0.split(" ")
    s1List = s1.split(" ")
    return len(list(set(s0List)&set(s1List)))

def give_sugestion(text):
    # Opening JSON file
    f = open(str(Path(__file__).absolute().parent /'json_files'/'intents.json'))
    
    # returns JSON object as dic
    data = json.load(f)
    f.close()

    questions =[]
    answers = []

    #build out data into lists 
    for i in data['intents']:
        questions.append(i['patterns'])
        answers.append(i['responses'][0])

    #run sugestion layer 
    text = text.lower()
    
    #clean text before use
    for word in stop_words:
        text = text.replace(' '+word+' ',' ')
    
    index =0
    count =0
    target = []
    for x in questions:
        for y in x:
            countz = text_count(text, y.lower())
            if(countz >= count and countz >0):
                count = countz
                target.append(index)
        index +=1
    
    target.reverse()
    if(len(target) >1 and count >1):
        res ='Sorry i do not understand please ask again. I think your question might have somthing to do with this -      '
        index =0
        for x in target:
            res += str(questions[x][0])+'-            -'
            res += str(answers[x])+'-           -'
            if(index<2 and index != len(target)-1):
                res += 'or perhaps this -          -'
            index +=1
            if(index >2):
                break
            
        return res
    else:
        return 'Sorry I do not understand the question please ask again.'
      

def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
            
    return numpy.array(bag)


def chat():
    print("Start talking with the bot (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])
        results_index = numpy.argmax(results)
        tag = labels[results_index]

        for tg in data["intents"]:
            if tg['tag'] == tag:
                responses = tg['responses']

        print(random.choice(responses))


def respond(text:str):

    ts = time.time()
    acc = 0.99
    answer =''

    text = text.lower()
    if(('hello' in text or 'hi' in text or 'good day' in text or 'hey' in text) and len(text)<12):
        answer = 'Hello there what can i help you with today?'
        res = {'time stamp':ts, 'question': text, 'answer':answer, 'accuracy':acc}
        return res
    if(('what are you' in text or 'what is this' in text or 'how do i use' in text or
        'help' in text or 'whats this' in text)and len(text)< 15):
        answer = 'I am an QA AI assistant for Maximus ask your work related question and I will do my best to help.'
        res = {'time stamp':ts, 'question': text, 'answer':answer, 'accuracy':acc}
        return res
    
    results = model.predict([bag_of_words(text, words)])
    results_index = numpy.argmax(results)
    results_score = numpy.amax(results)
    tag = labels[results_index]

    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']

    answer = (random.choice(responses))
    if(results_score> 0.95):
        res = {'time stamp':ts, 'question': text, 'answer':answer, 'accuracy':str(results_score)}
        return res
    else:
        answer = give_sugestion(text)
        res = {'time stamp':ts, 'question': text, 'answer':answer, 'accuracy':str(results_score)}
        return res

