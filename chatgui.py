import os
import re
from time import ctime

import nltk
import spacy
import wikipedia
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import webbrowser
from selenium import webdriver
from keras.models import load_model

model = load_model('chatbot_model.h5')
import json
import random



intents = json.loads(open('data/intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    stop_words = set(stopwords.words("english"))
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

    # sentence_words = [word.lemma_ for word in nlp(sentence.lower()) if word not in stop_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return (np.array(bag))


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.6
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    print(return_list)
    return return_list



def getResponse(ints, intents_json):
    try:
        tag = ints[0]['intent']
        list_of_intents = intents_json['intents']

        for i in list_of_intents:
            if (i['tag'] == tag):
                result = random.choice(i['responses'])
                break
    except:
        result = random.choice(intents_json['intents'][7]['responses'])
    return result


def openApps(ints, message):
    pattern = '(?:open|launch|run|go to) ([A-Za-z]*)'
    phrase = re.search(pattern, message).group(1)
    # phrase is name of the app --> run app 'phrase' here
    # if found app, open app and res = getResponse(ints,intents)
    if  
    # if not found, res = "Sorry, I can't find {} app.".format(phrase)
    res = os.startfile('"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"')
    return res

 def searchInfo(ints, message):
    # search and return summary information
    # if found then res = getResponse(ints,intents)
    # if not found then res = "Im sorry, but I can't help with that."
    # search_term =

    res = getResponse(ints,intents)
    content = wikipedia.summary().split('\n')
    search_for = message.split("find", 1)[1]
    driver = webdriver.Chrome("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")
    driver.get("http://google.com.vn")
    que = driver.find_element_by_xpath("//input[@name ='q']")
    return res

def webBrowser(ints, message):
    # just open google
    search_for = message.split("find", 1)[1]
    res = getResponse(ints,intents)
    url = "http://www.google.com.vn"
    res = webbrowser.open(url)
    return res

def askTime(ints, message):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(message)
    for ent in doc.ents:
        location = ent.text
        entity = ent.label_
    if(entity == 'GPE'):
        print()
    else: # get time of current location
        time = ctime().split(" ")[3].split(":")[0:2]
        if time[0] == "00":
            hours = '12'
        else:
            hours = time[0]
        minutes = time[1]
        time = hours + " hours and " + minutes + "minutes"

    time = getResponse(ints, intents)
    return time

def askWeather(ints, message):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(message)
    for ent in doc.ents:
        location = ent.text
        entity = ent.label_
    if (entity == 'GPE'):
        print()
    else: # current location
        # url = "https://www.google.com/search?sxsrf=ACYBGNSQwMLDByBwdVFIUCbQqya-ET7AAA%3A1578847393212&ei=oUwbXtbXDN-C4-EP-5u82AE&q=weather&oq=weather&gs_l=psy-ab.3..35i39i285i70i256j0i67l4j0i131i67j0i131j0i67l2j0.1630.4591..5475...1.2..2.322.1659.9j5j0j1......0....1..gws-wiz.....10..0i71j35i39j35i362i39._5eSPD47bv8&ved=0ahUKEwiWrJvwwP7mAhVfwTgGHfsNDxsQ4dUDCAs&uact=5"
        print()

    res = getResponse(ints, intents)
    return res

def chatbot_response(msg):
    ints = predict_class(msg, model)
    if ints[0]['intent'] in ['greeting', 'name', 'tasks', 'good_bye', 'thank_you']:
        res = getResponse(ints, intents)
    elif ints[0]['intent'] == 'open_apps':
        res = openApps()
    elif ints[0]['intent'] == 'web_browser':
        res = webBrowser()
        # viet tiep ho t nhe
    elif ints[0]['intent'] == 'time_asking':
        res = askTime()
    return res


# Creating GUI with tkinter
import tkinter
from tkinter import *


def send():
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12))

        res = chatbot_response(msg)
        ChatLog.insert(END, "Bot: " + res + '\n\n')

        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


base = Tk()
base.title("Chatbot")
base.geometry("400x500")
base.resizable(width=FALSE, height=FALSE)

# Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="8", width="50", font="Arial", )

ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="heart")
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message
SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                    command=send)

# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")
# EntryBox.bind("<Return>", send)


# Place all components on the screen
scrollbar.place(x=376, y=6, height=386)
ChatLog.place(x=6, y=6, height=386, width=370)
EntryBox.place(x=128, y=401, height=90, width=265)
SendButton.place(x=6, y=401, height=90)

base.mainloop()




