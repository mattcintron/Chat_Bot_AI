from flask import Flask
from flask import request
import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
import matplotlib.pyplot as plt
import scipy.cluster.hierarchy as shc
import pandas as pd
import numpy as np
from sklearn.cluster import AgglomerativeClustering

import tflearn
import tensorflow as tf
import random

import json

import nltk
from nltk.corpus import stopwords

stopwords = ["'re", "'ve","'s","a","about","above","after","again","against","all","am","an","and","any","are","aren't","as","at","be","because","been","before","being","below","between","both","but","by","can't","cannot","could","couldn't","did","didn't","do","does","doesn't","doing","don't","down","during","each","few","for","from","further","had","hadn't","has","hasn't","have","haven't","having","he","he'd","he'll","he's","her","here","here's","hers","herself","him","himself","his","how","how's","i","i'd","i'll","i'm","i've","if","in","into","is","isn't","it","it's","its","itself","let's","me","more","most","mustn't","my","myself","no","nor","not","of","off","on","once","only","or","other","ought","our","ours","ourselves","out","over","own","same","shan't","she","she'd","she'll","she's","should","shouldn't","so","some","such","than","that","that's","the","their","theirs","them","themselves","then","there","there's","these","they","they'd","they'll","they're","they've","this","those","through","to","too","under","until","up","very","was","wasn't","we","we'd","we'll","we're","we've","were","weren't","what","what's","when","when's","where","where's","which","while","who","who's","whom","why","why's","with","won't","would","wouldn't","you","you'd","you'll","you're","you've","your","yours","yourself","yourselves"]

failedThreshold = .85
intentCounts={}
allInputs = {}
failedInputs = {}
labeledClusters = {}

def loadData():
    global intentCounts
    global allInputs
    global labeledClusters
    global failedInputs
    
    try:
        with open('data/intentCounts.json') as infile:
            intentCounts = json.load(infile)
    except:
        pass

    try:
        with open('data/inputs.json') as infile:
            allInputs = json.load(infile)
            for input in allInputs:
                if allInputs[input]["score"] < failedThreshold:
                    failedInputs[input] = allInputs[input]["count"]
            
    except:
        pass

    try:
        with open('data/labeledClusters.json') as infile:
            labeledClusters = json.load(infile)
    except:
        pass

def create_app():
    app = Flask(__name__)
    loadData()
    return app

app = create_app()

@app.route("/")
def displayCounts():
    print (labeledClusters)
    page = "<h>Intent Counts</h>\n<ul>"
    for intent in sorted(intentCounts):
        page += "<li>" + intent +": " + str(intentCounts[intent]['count']) + " " + str(intentCounts[intent]['score']/intentCounts[intent]['count']) +"</li>"        
    page += "</ul>"

    page += "<h>Clustered Inputs</h>\n<ol type='I'>"
    for key, cluster in sorted(labeledClusters.items(),
                        key=lambda item: item[1]["count"],
                               reverse=True):
        page += "<li>" + str(cluster["count"]) +" queries with " + str(len(cluster["sentences"])) + " unique sentences<ul>"
        for sentence in cluster["sentences"]:
            page += "<li>" + sentence + "</li>"
        page += "</ul></li>"
    page += "</ol>"
    return page

@app.route("/record", methods=["POST"])
def record():
    requestJson=request.get_json()
    print(requestJson)
    intent = requestJson["intent"]
    count = requestJson["count"]
    score = float(requestJson["score"])
    input = requestJson["input"]
    addIntent(intent, count, score)
    addInput(input, count, score)

    with open('intentCounts.json', 'w') as f:
        json.dump(intentCounts, f)

    with open('inputs.json', 'w') as f:
        json.dump(allInputs, f)
    
    return "received"

def addIntent(intent, count, score):
   if intent in intentCounts:
        intentCounts[intent]['count'] = intentCounts[intent]['count'] + count
        intentCounts[intent]['score'] = intentCounts[intent]['score'] + count*score
   else:
       intentCounts[intent] = {'count': count, 'score':count*score}

def addInput(input, count, score):
    if input in allInputs:
        allInputs[input]["count"] = allInputs[input]["count"] + count
        allInputs[input]["score"] = score
    else:
       allInputs[input] = {"count": count, "score": score}

    if (score < failedThreshold):
        if input in failedInputs:
            failedInputs[input]  = failedInputs[input] + count
        else:
            failedInputs[input] = count

@app.route("/cluster")
def labelClusters():
    words = []
    docs_x = []
    inputDecoder = []
    countDecoder = []
    if(len(failedInputs) < 2):
        return "not enough data: " + str(len(failedInputs))
    for input in failedInputs:
        wrds = nltk.word_tokenize(input)
        
        words.extend(wrds)
        docs_x.append(wrds)
        inputDecoder.append(input)
        countDecoder.append(failedInputs[input])
    words = [stemmer.stem(w.lower()) for w in words if (w != "?" and w.lower() not in stopwords)]
    words = sorted(list(set(words)))
    bags = []
    for x, doc in enumerate(docs_x):
        bag = []

        wrds = [stemmer.stem(w.lower()) for w in doc]

        for w in words:
            if w in wrds:
                print(w)
                bag.append(1)
            else:
                bag.append(0)
        bags.append(bag)

   
    clusters = shc.fcluster(shc.linkage(bags, method='ward'), .75)
    global labeledClusters
    labeledClusters = {}
    for idx, value in enumerate(clusters):
       val = str(value)
       if val in labeledClusters:
           labeledClusters[val]['sentences'].append(inputDecoder[idx])
           labeledClusters[val]['count'] = labeledClusters[val]['count'] + countDecoder[idx]
       else:
           labeledClusters[val] = {'sentences': [inputDecoder[idx]], 'count': countDecoder[idx]}

    with open('data/labeledClusters.json', 'w') as f:
        json.dump(labeledClusters, f)
    return str(len(labeledClusters)) + " clusters formed"



       
        
