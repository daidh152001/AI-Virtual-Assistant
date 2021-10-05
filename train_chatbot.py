import nltk
from nltk.stem import WordNetLemmatizer
import json
import pickle
# import numpy as np
# from keras.models import Sequential
# from keras.layers import Dense, Activation, Dropout
# from tensorflow.keras.optimizers import SGD
import random
import spacy

# load data
lemmatizer = WordNetLemmatizer()
words = []
classes = []
documents = []
ignore_word = ['?', '!', '.', '*']
data_file = open('data/intents.json').read()
intents = json.loads(data_file)

# Tokenize words into word_list (from patterns), classes
# Documents include [(word_in_pattern, tag)]
nlp = spacy.load("en_core_web_sm", disable=['parser', 'ner'])

for intent in intents['intents']:
    for pattern in intent['patterns']:
        w = [word.lemma_ for word in nlp(pattern.lower())]
        words.extend(w)
        documents.append((w, intent['tag']))

        if intent['tag'] not in classes:
            classes.append(intent['tag'])


# lower case words and remove duplicates
words = [w for w in words if w not in ignore_word]
words = sorted(list(set(words)))
# print(words)
# print(len(documents), "documents", documents)
# print(len(classes), "classes", classes)
# print(len(words), "unique lemmatized words", words)

# create a pickle file to store Python objects for later prediction purpose
pickle.dump(words, open('words.pkl', 'wb'))
pickle.dump(classes, open('classes.pkl', 'wb'))

# create training data
training = []
output = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    for word in words:
        bag.append(1) if word in pattern_words else bag.append(0)

    # output_row returns 0 vector except for index of current tag (1)
    output_row = list(output)
    output_row[classes.index(doc[1])] = 1

    # training holds vector bag of words and associated output_row vector
    training.append([bag, output_row])
# print(training)