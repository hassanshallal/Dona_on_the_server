import requests
import os
import spoonacular as sp
import pickle
import random



# Important webhook related tokens and verifications
spoonacular_api = os.environ.get('spoonacular_api')
api = sp.API(spoonacular_api)

FB_API_URL = os.environ.get('FB_API_URL')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
THERMOGENA_ACCESS_TOKEN = os.environ.get('THERMOGENA_ACCESS_TOKEN')

this_image_url = "https://www.algoromida.com/images/Original.png"

# Load any expandable resources
thermogena_exercises = pickle.load( open("thermogena_assets/Thermogena_exercises.pkl", "rb"))
Thermogenic_ingredients = pickle.load( open("thermogena_assets/Thermogenic_ingredients.pkl", "rb"))
thermogena_dict = pickle.load( open("thermogena_assets/thermogena_dict.pkl", "rb"))

# This is where the real development of real value is presented to users
thermogena_specialities = ["Exercises", # serve at d1
                           "Thermogenic ingredients", # serve at d2
                           "Thermogenic recipes", # serve at d2
                           "Find wine for food", # serve at d3
                           "Find food for wine"] # serve at d3

# These are where user makes a choice
thermogena_controllers = ["Start with Thermogena",  # Zero decision against larn more about thermogena and go to dona.
                          "Food & Wine", # d1_ First decision against Exercises 
                          "Wine pairing", # d2_ Second decision against ingredients/recipes
                          "Take me to Dona now"] # This is there all the time, this is how thermogene delegeates back to Dona



zero_controller = thermogena_controllers[0]
first_controller = thermogena_controllers[1]
second_controller = thermogena_controllers[2]
dona_delegate = thermogena_controllers[len(thermogena_controllers) - 1]

zero_serve = thermogena_specialities[0]
first_serve = thermogena_specialities[1]
second_serve = thermogena_specialities[2]
third_serve = thermogena_specialities[3]
fourth_serve = thermogena_specialities[4]


# Define your zero serve
def zero_service(thermogena_exercises):
    # input is a resource that can be extended and improved all the time
    
    thermogenic_exercises_service = []
    for key in thermogena_exercises.keys():
        if key == 'aerobic exercise':
            recs = random.sample(thermogena_exercises[key], 4)
            for n in recs:
                thermogenic_exercises_service.append(n)
        else:
            thermogenic_exercises_service.append(random.choice(thermogena_exercises[key]))
    
    random.shuffle(thermogenic_exercises_service)

    return str(thermogenic_exercises_service).replace('[', '').replace(']', '') # thermogenic_exercises_service


# Define first service
def first_service(Thermogenic_ingredients):
    # input is a resource that can be extended and improved all the time
    Thermogenic_ingredients_service = []
    # We always add fruits or vegetables
    Thermogenic_ingredients_service.append(random.choice(Thermogenic_ingredients['fruits & vegetables']))
    
    # We take one of grains dairy, protein:
    
    main_dish = random.choice(Thermogenic_ingredients[random.choice(['grains', 'protein', 'dairy'])])
    Thermogenic_ingredients_service.append(main_dish)
    extra = random.choice(Thermogenic_ingredients[random.choice(['drinks', 'cooking helpers', 'give me a break!'])])
    Thermogenic_ingredients_service.append(extra)
    Thermogenic_ingredients_service_image_urls = []
    for n in Thermogenic_ingredients_service:
        Thermogenic_ingredients_service_image_urls.append('https://www.algoromida.com/images/' + n + '.jpg')
    message = str(Thermogenic_ingredients_service).replace('[', '').replace(']', '')
    #return str(Thermogenic_ingredients_service).replace('[', '').replace(']', '') # Thermogenic_ingredients_service
    return message, Thermogenic_ingredients_service, Thermogenic_ingredients_service_image_urls


def second_service(Thermogenic_ingredients):
    message, ingreds, ingreds_urls = first_service(Thermogenic_ingredients)
    #print(ingreds)
    response_8 = api.search_recipes_by_ingredients(ingreds, number = 3)
    search_recipes_by_ingredients_example8 = response_8.json()
    #print(search_recipes_by_ingredients_example8)
    #print(len(search_recipes_by_ingredients_example8))
    #print(search_recipes_by_ingredients_example8[0].keys())
    recipes = []
    image_urls = []
    if len(search_recipes_by_ingredients_example8) > 0:
        for n in search_recipes_by_ingredients_example8:
            recipes.append(n['title'])
            image_urls.append(n['image'])
            
    return message, recipes, image_urls
 
# third serve
def third_service_list(confirmed_user_input):
    response_5 = api.get_wine_pairing(confirmed_user_input)
    get_wine_pairing_example5 = response_5.json()
    print(get_wine_pairing_example5)
    #print(get_wine_pairing_example5)
    service_list_image_urls = []
    if 'pairedWines' in get_wine_pairing_example5.keys() and len(get_wine_pairing_example5['pairedWines']) > 0:
        for n in get_wine_pairing_example5['pairedWines']:
            service_list_image_urls.append('https://www.algoromida.com/images/' + n + '.jpg')
            
        return get_wine_pairing_example5['pairedWines'], service_list_image_urls
    else:
        return [], service_list_image_urls

# Fourth serve
def fourth_service_list(confirmed_user_input):
    response_3 = api.get_dish_pairing_for_wine(confirmed_user_input)
    get_dish_pairing_for_wine_example3 = response_3.json()
    print(get_dish_pairing_for_wine_example3)
    service_list_image_urls = []
    if 'pairings' in get_dish_pairing_for_wine_example3.keys() and len(get_dish_pairing_for_wine_example3['pairings']) > 0:
        for n in get_dish_pairing_for_wine_example3['pairings']:
            service_list_image_urls.append('https://www.algoromida.com/images/' + n + '.jpg')
    
        return get_dish_pairing_for_wine_example3['pairings'], service_list_image_urls
    else:
        return [], service_list_image_urls

    
def third_service(confirmed_user_input):
    response_5 = api.get_wine_pairing(confirmed_user_input)
    get_wine_pairing_example5 = response_5.json()
    print(get_wine_pairing_example5)
    #print(get_wine_pairing_example5)
    if 'pairedWines' in get_wine_pairing_example5.keys() and len(get_wine_pairing_example5['pairedWines']) > 0:
    
        return "Here we are: " + str(get_wine_pairing_example5['pairedWines']).replace('[', '').replace(']', '')
    else:
        return "Sorry, I can't find wine to pair with " + confirmed_user_input
    
# Fourth serve
def fourth_service(confirmed_user_input):
    response_3 = api.get_dish_pairing_for_wine(confirmed_user_input)
    get_dish_pairing_for_wine_example3 = response_3.json()
    #print(get_dish_pairing_for_wine_example3)
    if 'pairings' in get_dish_pairing_for_wine_example3.keys() and len(get_dish_pairing_for_wine_example3['pairings']) > 0:
        return "Here we are: " + str(get_dish_pairing_for_wine_example3['pairings']).replace('[', '').replace(']', '')
    else:
        return "Sorry, I can't find food to pair with " + confirmed_user_input

    
def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo") and
            not message['message'].get("attachments"))


def is_user_postback(message):
    """Check if the message is a message from the user"""
    return (message.get('postback') and not message.get('message'))

def is_user_attachment(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and message['message'].get("attachments"))

# From here to the end is mainly for thermogena, we can continue build this up.
def send_button_postback(recipient_id, this_text, service_introduction):  # comes postback of Wine pairing
    """Send a button to a Facebook user"""
    #print('a')
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": service_introduction,
                    "buttons": [
                        {
                            "type": "postback",
                                    "title": this_text,
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    #print('b')
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    #print('c')
    result = response.json()
    #print(result)
    return result

def send_info_call(recipient_id, this_text, service_introduction):  # comes postback of Wine pairing
    """Send a button to a Facebook user"""
    #print('a')
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": service_introduction + this_text,
                    "buttons": [
                                 {
                                     "type":"phone_number",
                                     "title":"Call Algoromida!",
                                     "payload":"+12092787142"
                                     #"type": "web_url",
                                     #"url": "https://en.wikipedia.org/wiki/" + this_text,
                                     #"title": this_text 
                                }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    #print('b')
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    #print('c')
    result = response.json()
    #print(result)
    return result

def send_recipe_image(recipient_id, recipe, image_url):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": recipe,
                            "image_url": image_url
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result



def send_button_url(recipient_id, this_text, service_introduction):  # comes postback of Wine pairing
    """Send a button to a Facebook user"""
    #print('a')
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": service_introduction + this_text,
                    "buttons": [
                                 {
                                     #"type":"phone_number",
                                     #"title":"Call Algoromida!",
                                     #"payload":"+12092787142"
                                     "type": "web_url",
                                     "url": "https://en.wikipedia.org/wiki/" + this_text,
                                     "title": this_text 
                                }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    #print('b')
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    #print('c')
    result = response.json()
    #print(result)
    return result


def send_image(recipient_id, image_url):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                                     "title": "Welcome to Algoromida!",
                                     "image_url": image_url
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result


def send_image_link(recipient_id, image_url):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Welcome to Algoromida!",
                            "image_url": image_url,
                                     "buttons": [
                                         {
                                             "type": "web_url",
                                             "url": "https://www.algoromida.com",
                                             "title": "View Website",
                                         }
                                     ]
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result


def send_dona_link(recipient_id, image_url):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Thanks for stopping by 🙂",
                                     "image_url": image_url,
                                     "buttons": [
                                         {
                                             "type": "web_url",
                                             "url": "m.me/algoromida",
                                             "title": "To Dona!",
                                         }
                                     ]
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result

# m.me/algoromida

# functional
# https://developers.facebook.com/docs/messenger-platform/send-messages/template/generic


def send_general_template(recipient_id, zero_controller = zero_controller, dona_delegate = dona_delegate):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                                     "title": "Welcome!",
                                     "image_url": "https://www.algoromida.com/images/Original.png",
                                     "subtitle": "Welcome to Algoromida!",
                                     "default_action": {
                                         "type": "web_url",
                                         "url": "https://www.algoromida.com",
                                         "webview_height_ratio": "tall",
                                     },
                            "buttons": [{
                                "type": "postback",
                                "title": zero_controller, 
                                "payload": "DEVELOPER_DEFINED_PAYLOAD"
                            },
                                         {
                                             "type": "web_url",
                                             "url": "https://www.algoromida.com/thermogena.html",
                                             "title": "Learn about Thermogena!"
                            }, {
                                             "type": "postback",
                                             "title": dona_delegate,
                                             "payload": "DEVELOPER_DEFINED_PAYLOAD"
                            }
                                     ]
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result

def send_thermogena_link(recipient_id, image_url):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Read more about Thermogena 🙂",
                                     "image_url": image_url,
                                     "buttons": [
                                         {
                                             "type": "web_url",
                                             "url": "https://www.algoromida.com/thermogena.html",
                                             "title": "To Thermogena @algoFit",
                                         }
                                     ]
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result


def send_help_template(recipient_id):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                                     "title": "Welcome!",
                                     "image_url": "https://www.algoromida.com/images/Original.png",
                                     "subtitle": "Welcome to Algoromida!",
                                     "default_action": {
                                         "type": "web_url",
                                         "url": "https://www.algoromida.com",
                                         "webview_height_ratio": "tall",
                                     },
                            "buttons": [
                                        {
                                            "type": "web_url",
                                             "url": "https://www.algoromida.com/thermogena.html",
                                             "title": "To Thermogena @algoFit",
                                        },
                                        {
                                            "type": "postback",
                                             "title": "Take me to Dona now!",
                                             "payload": "DEVELOPER_DEFINED_PAYLOAD"
                                        }
                                      ]
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result


# functional
def send_postback_button_d1(recipient_id, first_controller = first_controller, zero_serve = zero_serve):
    print(first_controller)
    print(zero_serve)
    """Send a button to a Facebook user"""
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Tell me what you want :)",
                    "buttons": [ 
                        {
                            "type": "postback",
                            "title": zero_serve,
                            "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        },
                        {
                            "type": "postback", #reward by an instant serve
                            "title": first_controller,
                            "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    print(payload)
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    
    result = response.json()
    print(result)
    return result

# comes postback of Thermogenic food & wine
def send_postback_button_d2(recipient_id, first_serve = first_serve, second_serve = second_serve, second_controller = second_controller):
    """Send a button to a Facebook user"""
    
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Tell me what you want :)",
                    "buttons": [
                        {
                            "type": "postback",
                                    "title": first_serve,
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        },
                        {
                            "type": "postback",
                                    "title": second_serve,
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        },
                        {
                            "type": "postback",
                                    "title": second_controller,
                                    "payload": "DEVELOPER_DEFINED_PAYLOAD"
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    
    response = requests.post(FB_API_URL, params=auth, json=payload)

    result = response.json()

    return result


def send_postback_button_d3(recipient_id, third_serve = third_serve, fourth_serve = fourth_serve):  # comes postback of Wine pairing
    """Send a button to a Facebook user"""
    #print('a')
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": "Tell me what you want :)",
                    "buttons": [
                        {
                            "type": "postback",
                                    "title": third_serve,
                                    "payload": "Please type or enter the food, you'll get the wine back :)"
                        },
                        {
                            "type": "postback",
                                    "title": fourth_serve,
                                    "payload": "Please type or enter the wine, you'll get the food back :)"
                        }
                    ]
                }
            }
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': THERMOGENA_ACCESS_TOKEN
    }
    #print('b')
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    #print('c')
    result = response.json()
    #print(result)
    return result

