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


from kik.messages import messages_from_json, TextMessage, SuggestedResponseKeyboard, TextResponse
from kik import KikApi, Configuration
import os
address = "40fd65c8"



kik = KikApi("dona_algoromida", os.environ.get('kik_apikey'))
kik.set_configuration(Configuration(
    webhook="https://" + address + ".ngrok.io/incoming"))


