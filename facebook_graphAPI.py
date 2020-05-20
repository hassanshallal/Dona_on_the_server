import requests
import os

# Important webhook related tokens and verifications
FB_API_URL = os.environ.get('FB_API_URL')
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')
thermogena_image_url = "https://www.algoromida.com/images/Original.png"


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"


def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("attachments") and
            not message['message'].get("is_echo"))  # No response to links or attachments


def typing_bubble_on(recipient_id):
    """Simulate a typing bubble"""
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'sender_action': 'typing_on'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result


def typing_bubble_off(recipient_id):
    """Simulate a typing bubble"""
    payload = {
        'recipient': {
            'id': recipient_id
        },
        'sender_action': 'typing_off'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result


def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'messaging_type': "RESPONSE",
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }
    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    return result


def send_thermogena_link_from_dona(recipient_id, thermogena_image_url):
    print("inside send_thermogena_link function")
    payload = {
        'messaging_type': "RESPONSE",
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "Stop by anytime 🙂",
                                     "image_url": thermogena_image_url,
                                     "buttons": [
                                         {
                                             "type": "web_url",
                                             "url": "m.me/thermogena",
                                             "title": "Have fun with Thermogena!",
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
        'access_token': PAGE_ACCESS_TOKEN
    }
    # The issue is in the next line!
    # response = requests.post(FB_API_URL, params=auth, data=payload)
    print("payload is: ", str(payload))
    response = requests.post(FB_API_URL, params=auth, json=payload)
    result = response.json()
    print(result)
    return result
