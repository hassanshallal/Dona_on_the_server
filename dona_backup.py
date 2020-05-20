
# In this system, we implemented MVC for the UI and a Facade for the model of the MVC.

# Import modules
from flask import Flask
from flask import request
from flask import render_template
from flask import Response
from flask import redirect
import requests
import pickle
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
import os
from os import system
import string
import numpy as np
import nltk
from nltk import sent_tokenize

# This is the controller here, import model (respond) and view
from dona_utils import *
from respond import *
from view import *

# autopep8 -i dona.py
# parameters
dona = Flask(__name__)


report_awareness_statefulness = False
# This is the model (implemented as a Facade pattern) supposed to
# return this_response, this_awareness, this_statefulness, best_match to
# the controller with access to the database via the user class
respond_inst = Respond()


# Model function
def model(this_user, query, platform):
    this_user_info, this_user_interactions = this_user.get_user_info_by_id()
    num_records = len(this_user_interactions)

    print(this_user_info)
    print("This user has " + str(num_records) + " previous interactions.")

    if this_user_info == None and platform == "Facebook":
        return None, None, None

    elif this_user_info != None:
        # send and receive from the model
        this_response, this_awareness, this_statefulness, best_match = respond_inst.cognify(query,
                                                                                            this_user, this_user_info, this_user_interactions)
    print("awareness is: " + this_awareness + ", statefulness is: " + str(this_statefulness) +
          ", response is: " + this_response + ", best match is: " + str(best_match))
    return this_awareness, this_statefulness, this_response, best_match


# This is the controller of the MVC pattern. Use it to access user info
# send it to the model and recieve the awareness, statefulness, response
# /webhook is for Facebook chatbot messenger
@dona.route("/webhook", methods=['GET', 'POST'])
def listen():
    """This is the main function flask uses to listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        print(payload)
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                query = process_query(x['message']['text'])
                sender_id = x['sender']['id']

                # Get user data from the database
                this_user = User(sender_id, False)
                texts = sent_tokenize(query)

                for text in texts:
                    # Use model
                    this_awareness, this_statefulness, this_response, best_match = model(
                        this_user, text, "Facebook")
                    print(best_match)
                    # decide how to view your output
                    if this_response == "initiate google search module.":
                        view_google_search(text, report_awareness_statefulness, this_user,
                                           this_awareness, this_statefulness, this_response, "Facebook")
                        update_database(this_user, text, this_response,
                                        this_awareness, this_statefulness, best_match)

                    elif this_response != "initiate google search module." and this_response != None:
                        # Text bubble effect in Facebook
                        if this_statefulness != 5:
                            typing_bubble_on(this_user.ID)
                            time.sleep(2)
                            typing_bubble_off(this_user.ID)

                        view(report_awareness_statefulness, this_user, this_awareness,
                             this_statefulness, process_response(this_response), "Facebook")
                        update_database(this_user, text, this_response,
                                        this_awareness, this_statefulness, best_match)
                    elif this_response == None:
                        send_message(
                            this_user.ID, "Hi, I am Dona from the algoChat cluster @algoromida. Please make sure your facebook account is active and retry again.")

    return "ok"

# /incoming is for Kik
@dona.route('/incoming', methods=['POST'])
def incoming():
    if not kik.verify_signature(request.headers.get('X-Kik-Signature'), request.get_data()):
        return Response(status=403)

    messages = messages_from_json(request.json['messages'])
    now = datetime.now()
    for message in messages:
        if isinstance(message, TextMessage):
            query = process_query(message.body)
            message_timestamp = str(message.timestamp)
            print("this is timestamp from kik " + message_timestamp)
            message_timestamp = float(
                message_timestamp[0:10] + '.' + message_timestamp[10:len(message_timestamp)])
            this_message_time = datetime.fromtimestamp(message_timestamp)
            print("this meesage time " + str(this_message_time))
            print("time now is " + str(now))
            print("the difference is " +
                  str((now - this_message_time).seconds//3600))

            sender_id = message.from_user
            kikuser = kik.get_user(message.from_user)
            kikuser_data = list()
            kikuser_data.append(kikuser.first_name)
            kikuser_data.append(kikuser.last_name)

            # Get user data from the database
            this_user = User(sender_id, True, kikuser_data)

            texts = sent_tokenize(query)

            for text in texts:
                # Use model
                this_awareness, this_statefulness, this_response, best_match = model(
                    this_user, text, "Kik")

                # View & update
                if this_response == "initiate google search module.":
                    view_google_search(text, report_awareness_statefulness, this_user, this_awareness,
                                       this_statefulness, this_response, "Kik", kik_message=message)
                    update_database(this_user, text, this_response,
                                    this_awareness, this_statefulness, best_match)
                elif this_response != None and this_response != "initiate google search module.":

                    view(report_awareness_statefulness, this_user, this_awareness,
                         this_statefulness, process_response(this_response), "Kik", kik_message=message)
                    update_database(this_user, text, this_response,
                                    this_awareness, this_statefulness, best_match)
                elif this_response == None:
                    this_response = "Hi, I am Dona from the algoChat cluster @algoromida. I am encoutering some difficulties, will be back soon."
                    view(report_awareness_statefulness, this_user, this_awareness,
                         this_statefulness, this_response, "Kik", kik_message=message)

    return Response(status=200)


if __name__ == "__main__":
    dona.run()
