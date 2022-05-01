import nltk
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy as np
import tflearn
#import tensorflow as tf
from tensorflow.python.framework import ops
#import random
import json
import pickle

with open ("intents_en.json") as file:
    data = json.load(file)
    
#with open ("recognition_names.json") as file:
#    data_names = json.load(file)

#print(data["intents"])
#print(data_names["recognition_names"])

try:
    with open("data.pickle", "rb") as f:
        words, labels, training, output = pickle.load(f)
except:
    words = []
    labels = []
    docs_x = []
    docs_y = []
    
    for intent in data["intents"]:
        for pattern in intent["patterns"]:
            wrds = nltk.word_tokenize(pattern)
            words.extend(wrds)
            docs_x.append(wrds)
            docs_y.append(intent["tag"])
            
        if intent["tag"] not in labels:
            labels.append(intent["tag"])
    
    words = [stemmer.stem(w.lower()) for w in words if w != "?"] #bot nie bierze pod uwage znakow zapytania
    words = sorted(list(set(words)))
    
    labels = sorted(labels)
    
    training = [] #list of 0 and 1
    output = [] #list of 0 and 1
    
    out_empty = [0 for _ in range(len(labels))]
    
    for x, doc in enumerate(docs_x):
        bag = []
        
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1) #this word is found so im putting the one
            else:
                bag.append(0) #this word is not here so im putting the zero
    
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        
        training.append(bag)
        output.append(output_row)
        
    training = np.array(training) #konwertujemy do np array dla tflearn
    output = np.array(output)
    
    #save
    with open("data.pickle", "wb") as f:
        pickle.dump((words, labels, training, output), f)

#neurony
ops.reset_default_graph()
#neuron odpowiadajacy za input
net = tflearn.input_data(shape=[None, len(training[0])])
#8 neuronow w pelni polaczonych
net = tflearn.fully_connected(net, 8)
#8 neuronow w pelni polaczonych
net = tflearn.fully_connected(net, 8)
#neuron odpowiadajacy za klasy w intents i output
net = tflearn.fully_connected(net, len(output[0]), activation="softmax") #daje prawdopodobienstwa na kazdy output
net = tflearn.regression(net)

model = tflearn.DNN(net)
try:
    model.load("model.tflearn")
except:
    model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
    model.save("model.tflearn")
    
def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]
    
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    
    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1
                
    return np.array(bag)