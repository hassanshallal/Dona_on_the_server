
import wikipedia
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
import numpy as np
import pandas as pd
import requests

import spacy
nlp = spacy.load('en_core_web_md')

from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

tokenizer = RegexpTokenizer(r'\w+')
stop_words = set(stopwords.words('english')) 



# Get a list of jokes without "\'"
jokes_db = pd.read_csv('shortjokes.csv')
jokes_list_unclean = list(jokes_db.Joke)
#jokes_list = [n for n in jokes_list_unclean if "\'" not in n]
jokes_list = [n.lower() for n in jokes_list_unclean]
joke_redundant_set = set(["tell", "joke", "dona", "huh", "ha", "hmm", "hm", "another", "other", "lol", "jokes", 'make me laugh', 'dirty'])


def get_joke_target(query):
    #print(query)
    query_list = tokenizer.tokenize(query)
    #print(query_list)
    query_list = [w for w in query_list if not w in stop_words] 
    query_list = [w for w in query_list if not w in joke_redundant_set]
    return query_list

def get_a_joke(jokes_list, query):
    query_list = get_joke_target(query)
    if len(query_list) == 0:
        return "Here is a joke for you: " + jokes_list[np.random.choice(len(jokes_list))]

    # User wants a joke onsomething specific
    elif len(query_list) == 1:
        target = " " + query_list[0] + " "  # this is to avoid trump in trumpet or train rather than rain
    else:
        target = " " + " ".join(query_list) + " "
    print("target is: " + target)
    # Get indices of jokes on that target
    indices = list()
    for n in range(len(jokes_list)):
        if target in jokes_list[n]:
            indices.append(n)
            #print(indices)
    # If you have it, return it otherwise
    #print(len(indices) > 1)
    if len(indices) > 1:
        return "Here is a joke about" + target + "for you: " + jokes_list[indices[np.random.choice(len(indices))]]
    elif len(indices) == 1:
        return "Here is a joke about" + target + "for you: " + jokes_list[indices[0]]
    elif len(indices) == 0:
        return "Sorry, I don't have a joke about" + target.rstrip() + ", wanna try something else?"
    

def get_object_subject(query):
    parsed_text = nlp(query)
    for text in parsed_text:
        if text.orth_ == 'you':
            if text.dep_ == "nsubj":
                return "subject"
            elif text.dep_ == "dobj":
                return "object"


def get_time(this_user_info):
    if this_user_info[3] == "Undisclosed":
        return "Undisclosed"

    else:
        time_there = datetime.utcnow(
        ) + timedelta(hours=int(this_user_info[3]))
        hour = time_there.hour
        minute = time_there.minute
        period = " AM"

        if hour == 12:
            period = " PM"
        elif hour > 12:
            hour = hour - 12
            period = " PM"

        if minute < 10:
            minute = str(0) + str(minute)
        else:
            minute = str(minute)

        return str(hour) + ":" + minute + period


def get_date(this_user_info):
    if this_user_info[3] == "Undisclosed":
        return "Undisclosed"

    else:
        time_there = datetime.utcnow(
        ) + timedelta(hours=int(this_user_info[3]))
        year = time_there.year
        month = time_there.month
        day = time_there.day
        return str(month) + "/" + str(day) + "/" + str(year)


def search_wikipedia(query):
    query = query.replace("search wikipedia", "")
    query = query.replace("tell me about", "")
    query = query.strip()
    try:
        search_results = wikipedia.search(query)
        if len(search_results) > 0:
            # print(len(search_results))
            for m in range(1):
                return wikipedia.summary(search_results[m], sentences=5)
        else:
            return "I couldn't find results for this search on wikipedia."
    except wikipedia.exceptions.DisambiguationError:
        print("DisambiguationError")
        return "Wikipedia and I are confused Could you ask for a more specific search?"


def simple_replacements(this_user, this_user_info, query, response):
    # Simple replacmenets

    if query == "sure, i'm male.":
        this_user.disclose_gender('male')

    if query == "sure, i'm female.":
        this_user.disclose_gender('female')

    if 'username' in response:
        print("username detected")
        if np.random.uniform() >= 0.5:
            name = this_user_info[1]
        else:
            name = this_user_info[1] + ' ' + this_user_info[2]
        response = response.replace('username', name)

    if 'usergender' in response:
        print("usergender detected")
        response = response.replace(
            'usergender', this_user_info[4])

    if 'gettime' in response:
        print("gettime detected")
        response = response.replace(
            'gettime', get_time(this_user_info))

    if 'getdate' in response:
        print("get_date() detected")
        response = response.replace(
            'getdate', get_date(this_user_info))

    if 'getjoke' in response:
        response = get_a_joke(jokes_list, query)

    # This is to search wikipedia under certain circumstances, raise your world cutoff to 0.9
    if query != "search wikipedia" and "search wikipedia" in query and response != "getgooglesearchsummary":
        print("Prompted wikipedia search")
        response = "I am guessing that the answer is as I found in Wikipedia: " + \
            str(search_wikipedia(query))

    elif (query != "search google" and "search google" in query) or (response == "getgooglesearchsummary"):
        print("prompt get_google_search_summary()")
        response = "initiate google search module."

    return response
