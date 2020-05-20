
# This is the extra refactored and object-oriented version of the system to be deployed on 04/02/2019
from flask import Flask
from flask import request
from flask import render_template

import requests

import pickle
import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
from os import system
import numpy as np

from thermogena_utils import *
#dona = Flask(__name__)

#@dona.route("/thermogena", methods=['GET', 'POST'])
def thermogena():
    # This is the main function flask uses to listen at the `/thermogena` endpoint
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        print(payload)
        event = payload['entry'][0]['messaging']
        for x in event:

            # Get sender_id and the user object
            sender_id = x['sender']['id']
            print(sender_id)
            this_user = Thermogena_user(sender_id, False)
            this_user_info, this_user_interactions = this_user.get_user_info_by_id()
            
            is_postback = ''
            text = ''
            # Decide is_postback and get text
            if is_user_attachment(x):
                    payload = "Hi, I am Thermogena from the algoFit cluster @algoromida. As of now, I can handle only text messages with no links or attachments. Thanks for understanding."
                    send_info_call(sender_id, payload, "Instruction: ")
                    update_thermogena_database(this_user, "attachment", 'False', payload)
                    return 'ok'
            elif is_user_postback(x):
                is_postback = True
                text = x['postback']['title'].lower()
                payload = x['postback']['payload']
            elif is_user_message(x):
                is_postback = False
                text = x['message']['text'].lower()
            print('is_postback ' , is_postback)
            print('text ' , text)


            # check services and guess based on thermogena_dict
            is_service = this_user.to_invoke_service()
            print('is_service ' , is_service)
            if text in thermogena_dict.keys():
                this_guess = thermogena_dict[text]
            else:
                this_guess = 'no clue'
            print('this_guess ' , this_guess)
            # Start executing
            
            if is_service  == 'third' and this_guess == 'no clue':
                #service_list = third_service(text)
                #send_info_call(sender_id, service_list, '')
                service_list, images = third_service_list(text)
                if len(service_list) > 0:
                    for n in range(len(service_list)):
                        send_recipe_image(sender_id, service_list[n], images[n])
                else:
                    send_info_call(sender_id, text, "Sorry, I can't find wine to pair with ")
                #send_info_call(sender_id, service_list, '')
                update_thermogena_database(this_user, text, is_postback, str(service_list))
                
            elif is_service  == 'fourth'and this_guess == 'no clue':
                #service_list = fourth_service(text)
                #send_info_call(sender_id, service_list, '')
                service_list, images = fourth_service_list(text)
                #print(service_list)
                #print(images)
                if len(service_list) > 0:
                    for n in range(len(service_list)):
                        send_recipe_image(sender_id, service_list[n], images[n])
                else:
                    send_info_call(sender_id, text, "Sorry, I can't find food to pair with ")                                    
                update_thermogena_database(this_user, text, is_postback, str(service_list))
            else:
                if this_guess == 'no clue': # we limited the user inputs in the thermogena_dict
                    send_general_template(sender_id)
                elif this_guess == thermogena_controllers[0]:
                    print('thermogena_controllers[0]')
                    send_postback_button_d1(sender_id)
                    update_thermogena_database(this_user, text, is_postback, 'send_postback_button_d1')
                elif this_guess == thermogena_controllers[1]:
                    print('thermogena_controllers[1]')
                    send_postback_button_d2(sender_id)
                    update_thermogena_database(this_user, text, is_postback, 'send_postback_button_d2')
                elif this_guess == thermogena_controllers[2]:
                    print('thermogena_controllers[2]')
                    send_postback_button_d3(sender_id)
                    update_thermogena_database(this_user, text, is_postback, 'send_postback_button_d3')
                elif this_guess == thermogena_controllers[len(thermogena_controllers) - 1]:
                    print('thermogena_controllers[3]')
                    send_dona_link(sender_id, this_image_url)
                    update_thermogena_database(this_user, text, is_postback, 'send_dona_link')
                elif this_guess == thermogena_specialities[0]:
                    print('thermogena_specialities[0]')
                    service_list = zero_service(thermogena_exercises)
                    send_info_call(sender_id, service_list, "A fat-burner workout for you: ")
                    update_thermogena_database(this_user, text, is_postback, service_list)
                elif this_guess == thermogena_specialities[1]:
                    print('thermogena_specialities[1]')
                    message, ingreds, images = first_service(Thermogenic_ingredients)
                    send_info_call(sender_id, message, "Fat-burner ingredients: ")
                    for n in range(len(ingreds)):
                        send_recipe_image(sender_id, ingreds[n], images[n])
                    update_thermogena_database(this_user, text, is_postback, str(ingreds))
                elif this_guess == thermogena_specialities[2]:
                    print('thermogena_specialities[2]')
                    ingreds, recipes, image_urls = second_service(Thermogenic_ingredients)
                    send_info_call(sender_id, ingreds, "Fat-burner ingredients: ")
                    for n in range(len(recipes)):
                        send_recipe_image(sender_id, recipes[n], image_urls[n])
                    update_thermogena_database(this_user, text, is_postback, ingreds)
                elif this_guess == thermogena_specialities[3] or this_guess == thermogena_specialities[4]:
                    print('thermogena_specialities[3] or thermogena_specialities[4]')
                    if not is_postback and this_guess == thermogena_specialities[3]:
                        payload = "Please type or enter the food, you'll get the wine back :)"
                    elif not is_postback and this_guess == thermogena_specialities[4]:
                        payload = "Please type or enter the wine, you'll get the food back :)"

                    send_info_call(sender_id, payload, "Instruction: ")
                    update_thermogena_database(this_user, text, is_postback, payload)
                elif this_guess == 'Help':
                    send_thermogena_link(sender_id, this_image_url)
                    update_thermogena_database(this_user, text, is_postback, 'Help')
                else:
                # Get your simple replacements here: Removed time and date awaeness because Thermogena wasn't approved for pages_user_timezone. Can you call Themogena from Dona or another health related bot
                    this_guess = simple_thermogena_replacements(this_user, this_user_info, this_guess)
                    send_info_call(sender_id, this_guess, "")
                    update_thermogena_database(this_user, text, is_postback, this_guess)
                #else:
                    #print('something escaped from thermogena')
                    #payload = "Hi, I am Thermogena from the algoFit cluster @algoromida. Please make sure your facebook account is active and retry again."
                    #payload = "Please type start or help or go to Dona."
                    #send_info_call(sender_id, payload, "Instruction: ")
                    #update_thermogena_database(this_user, text, is_postback, payload)

        return "ok"

#if __name__ == "__main__":
#    dona.run(port=5050)
