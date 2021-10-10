import nltk
nltk.download("stopwords")
nltk.download('punkt')
nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import json
import pickle
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
import random
import spacy

# load data
lemmatizer = WordNetLemmatizer()
words = []
classes = []
documents = []
ignore_word = ['?', '!', '.', '*']
stop_words = set(stopwords.words("english"))
data_file = open('data/intents.json').read()
intents = json.loads(data_file)

# Tokenize words into word_list (from patterns), classes

for intent in intents['intents']:
    for pattern in intent['patterns']:
        # w = [word.lemma_ for word in nlp(pattern.lower())]
        # words.extend(w)
        # documents.append((w, intent['tag']))
        #
        # if intent['tag'] not in classes:
        #     classes.append(intent['tag'])

        # tokenize each word
        w = [lemmatizer.lemmatize((word)) for word in nltk.word_tokenize(pattern.lower())]
        words.extend(w)
        # add documents in the corpus
        documents.append((w, intent['tag']))

        # add to our classes list
        if intent['tag'] not in classes:
            classes.append(intent['tag'])


# lower case words and remove duplicates
words = [w for w in words if w not in ignore_word and w not in stop_words]
words = sorted(list(set(words)))


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

random.shuffle(training)
training = np.array(training)
train_x = list(training[:, 0])
train_y = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(train_y[0]), activation='softmax'))

sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
model.save('chatbot_model.h5', hist)

print("model created")