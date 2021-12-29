import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import tflearn
import tensorflow as tf
import random
import json
from pathlib import Path
import os, shutil


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

    #clean old models
    folder = str(Path(__file__).absolute().parent /'notebooks'/'model_data')
    clean_folder(folder)

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
    if(text ==None):
        return
        
    text = text.lower()
    if(('hello' in text or 'hi' in text or 'good day' in text or 'hey' in text) and len(text)<12):
        return 'Hello there what can i help you with today?'
    if(('what are you' in text or 'what is this' in text or 'how do i use' in text or
        'help' in text or 'whats this' in text)and len(text)< 20):
        return 'I am an QA AI assistant for Maximus ask your work related question and I will do my best to help.'
    
    results = model.predict([bag_of_words(text, words)])
    results_index = numpy.argmax(results)
    results_score = numpy.amax(results)
    tag = labels[results_index]

    for tg in data["intents"]:
        if tg['tag'] == tag:
            responses = tg['responses']

    result = (random.choice(responses))
    if(results_score> 0.95):
        return(result)
    else:
        return('Sorry I do not understand the question, can you please try asking again.')


def clean_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))