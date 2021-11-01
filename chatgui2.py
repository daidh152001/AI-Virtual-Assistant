import datetime
import fnmatch
import os
import re
import nltk
import requests
import spacy
import wikipedia
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import webbrowser
from tensorflow.keras.models import load_model
import json
import random
from googlesearch import search
import tensorflow as tf
print(tf.__version__)
model = load_model('chatbot_model.h5')
intents = json.loads(open('data/intents.json').read())
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))

nlp = spacy.load('venv\\Lib\\site-packages\\en_core_web_sm\\en_core_web_sm-3.1.0')

def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
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

    if len(return_list) == 0:
        return_list.append({"intent": classes[7]})

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

def find(pattern, path):
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                if fnmatch.fnmatch(name, pattern):
                    result.append(os.path.join(root, name))
        return result

def openApps(ints, message):
    pattern = '(?:open|launch|run|go to) ([A-Za-z]*)'
    phrase = re.search(pattern, message.lower()).group(1)
    apps = {"photo":"ms-photos:","camera": "microsoft.windows.camera:", "word": "winword", "powerpoint": "powerpnt", "paint":"mspaint", "calculator":"calc"}
    # phrase is name of the app --> run app 'phrase' here
    path = "C:\\"

    if phrase in apps.keys():
        os.system('start {}'.format(apps[phrase]))
        res = getResponse(ints, intents).format(phrase)
        return res

    try:
        os.startfile('{}'.format(phrase))
        res = getResponse(ints, intents).format(phrase)
        return res
    except:
        result = find('{}*.exe'.format(phrase), path)
        print(result)
        if len(result) > 0:
            try:
                os.startfile(result[0])
                res = getResponse(ints, intents).format(phrase)
            except:
                res = "Sorry, I couldn't open the app!"
        else:
            res = "Sorry, I couldn't find the app!"
        return res

def callback(url):
    webbrowser.open_new(url)

def searchInfo(ints, message):
    # search and return summary information

    result = []
    try:
        results = wikipedia.page(message)
        result.append(getResponse(ints, intents) + "\n\n" + wikipedia.summary(message, sentences=3, auto_suggest=True, redirect=True))
        result.append([results.url])
        return result
    except:
        result.append(getResponse(ints, intents))
        res = []
        for link in search(message, start=0, stop=5):
            res.append(link)

        result.append(res)
        return result


def webBrowser(ints, message):
    # just open google
    url = "http://www.google.com.vn"
    webbrowser.open(url)
    res = getResponse(ints, intents)
    return res

def askTime(ints, message):
    # nlp = spacy.load('en_core_web_sm')
    doc = nlp(message)
    for ent in doc.ents:
        location = ent.text
        entity = ent.label_
        if(entity == 'GPE'):
            ow_url = "http://api.openweathermap.org/data/2.5/weather?"
            if not location:
                pass
            api_key = "fe8d8c65cf345889139d8e545f57819a"
            call_url = ow_url + "appid=" + api_key + "&q=" + location + "&units=metric"
            res = requests.get(call_url)
            data = res.json()
            if data["cod"] != "404":
                tz = get_date(data['timezone'])
                content = "{tzone}".format(tzone = tz)
                res = getResponse(ints, intents).format(content)
                return res
    # get time of current location

    now = datetime.datetime.now()
    date_time = now.strftime("%m/%d/%Y, %H:%M:%S")

    res = getResponse(ints, intents).format(date_time)
    return res


def get_date(timezone):
    tz = datetime.timezone(datetime.timedelta(seconds=int(timezone)))
    return datetime.datetime.now(tz = tz).strftime("%m/%d/%Y, %H:%M:%S")

def askWeather(ints, message):
    # nlp = en_core_web_sm.load()
    doc = nlp(message)
    for ent in doc.ents:
        location = ent.text
        entity = ent.label_
        if (entity == 'GPE'):
            ow_url = "http://api.openweathermap.org/data/2.5/weather?"
            if not location:
                pass
            api_key = "fe8d8c65cf345889139d8e545f57819a"
            call_url = ow_url + "appid=" + api_key + "&q=" + location + "&units=metric"
            res = requests.get(call_url)
            data = res.json()
            if data["cod"] != "404":
                    city_res = data["main"]
                    current_temperature = city_res["temp"]
                    feels_like = city_res["feels_like"]
                    min_temp = city_res["temp_min"]
                    max_temp = city_res["temp_max"]
                    current_humidity = city_res["humidity"]
                    wthr = data["weather"]
                    weather_description = wthr[0]["description"]
                    now = datetime.datetime.now()
                    content = "Today is {day}th, {month}, {year}  \nAverage temperature is {temp}°C\nFeels like {feelslike}°C\nMin temperature is {min}°C\nMax temperature is {max}°C\nHumidity is {humidity}%\nDiscription: {des}".format(day = now.day,month = now.month, year= now.year,
                                                                                    temp = current_temperature, feelslike=feels_like, min = min_temp, max = max_temp, humidity = current_humidity, des = weather_description)
                    return getResponse(ints, intents) + "\n\n" + content

    url = "https://www.google.com/search?q=weather"
    webbrowser.open(url)
    res = getResponse(ints, intents)
    return res

def chatbot_response(msg):
    ints = predict_class(msg, model)
    if ints[0]['intent'] in ['greeting', 'name', 'tasks', 'good_bye', 'thank_you']:
        res = getResponse(ints, intents)
    elif ints[0]['intent'] == 'open_apps':
        res = openApps(ints, msg)
    elif ints[0]['intent'] == 'web_browser':
        res = webBrowser(ints, msg)
    elif ints[0]['intent'] == 'time_asking':
        res = askTime(ints, msg)
    elif ints[0]['intent'] == 'weather_asking':
        res = askWeather(ints, msg)
    elif ints[0]['intent'] == 'search_info':
        res = searchInfo(ints, msg)
    return res


# Creating GUI with tkinter
from tkinter import *

def send():
    msg = EntryBox.get("1.0", 'end-1c').strip()
    EntryBox.delete("0.0", END)

    if msg != '':
        ChatLog.config(state=NORMAL)
        ChatLog.insert(END, "You: " + msg + '\n\n')
        ChatLog.config(foreground="#442265", font=("Verdana", 12))

        res = chatbot_response(msg)
        if type(res) is not list:
            ChatLog.insert(END, "Bot: " + res + '\n\n')
        else:
            ChatLog.insert(END, "Bot: " + res[0] + "\n\n")

            for res_link in res[1]:
                link=res_link
                ChatLog.insert(END, res_link + "\n\n", link)
                ChatLog.tag_config(link, foreground="blue",underline=1)
                ChatLog.tag_bind(link, "<Button-1>", lambda e,res_link=res_link : callback(res_link))
        ChatLog.config(state=DISABLED)
        ChatLog.yview(END)


base = Tk()
base.title("Chatbot")
base.geometry("600x600")
base.resizable(width=FALSE, height=FALSE)

# Create Chat window
ChatLog = Text(base, bd=0, bg="white", height="20", width="100", font="Arial",wrap='word')
ChatLog.config(state=DISABLED)

# Bind scrollbar to Chat window
scrollbar = Scrollbar(base, command=ChatLog.yview, cursor="arrow")
ChatLog['yscrollcommand'] = scrollbar.set

# Create Button to send message
SendButton = Button(base, font=("Verdana", 12, 'bold'), text="Send", width="12", height=5,
                    bd=0, bg="#32de97", activebackground="#3c9d9b", fg='#ffffff',
                    command=send)
# Create the box to enter message
EntryBox = Text(base, bd=0, bg="white", width="29", height="5", font="Arial")

EntryBox.bind("<Return>", lambda e: send())


# Place all components on the screen
scrollbar.place(x=580, y=6, height=510)
ChatLog.place(x=6, y=6, height=500, width=574)
EntryBox.place(x=6, y=510, height=90, width=440)
SendButton.place(x=450, y=510, height=90)

base.mainloop()



