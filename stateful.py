import time
from datetime import datetime, timedelta
from timeit import default_timer as timer
import numpy as np
import pandas as pd

from dona_custome_responses import *
from stateful_utils import *

# We need to thinks of how this is going to be implemented
# we want to instantiate one instance of the class for the whole session
# query, response, query_emb, last_response_emb, this_user_info, this_user_last_two_acs


class Statefulness:
    def __init__(self):

        #  This will be needed for class-3
        self.double_query_pronouns = double_query_pronouns
        self.double_query_pronouns_dahsed = double_query_pronouns_dahsed

        # Process some data for statefulness
        self.pronoun_pairs = zip(query_pronouns, response_pronouns)
        self.pronoun_pairs_dict = {}
        for x in self.pronoun_pairs:
            self.pronoun_pairs_dict.setdefault(x[0], []).append(x[1])
        print("pronoun_pairs_dict obtained.")

    def process_stateful_class_1(self, query, response, this_user_interactions):
        # class-1 statefulness:
        # user repeating query
        is_repeated_query = (
            query == this_user_interactions[len(this_user_interactions)-1][1])
        if is_repeated_query:
            if query == this_user_interactions[len(this_user_interactions)-1][1] and this_user_interactions[len(this_user_interactions)-1][1] != this_user_interactions[len(this_user_interactions)-2][1]:
                response = "I repeat the same response: " + \
                    this_user_interactions[len(this_user_interactions)-1][2]
            elif len(this_user_interactions) > 1 and query == this_user_interactions[len(this_user_interactions)-1][1] and this_user_interactions[len(this_user_interactions)-1][1] == this_user_interactions[len(this_user_interactions)-2][1]:
                response = repeated_query[np.random.choice(
                    len(repeated_query))]

        # user repeating Dona's last response
        is_repeated_last_response = (
            query == this_user_interactions[len(this_user_interactions)-1][2])
        if is_repeated_last_response:
            response = repeated_response[np.random.choice(
                len(repeated_response))]

        return response

    def process_stateful_class_3(self, this_user_interactions):
        to_add = ''
        last_query = this_user_interactions[len(
            this_user_interactions)-1][1].lower()

        for n in range(len(self.double_query_pronouns)):
            if self.double_query_pronouns[n] in last_query:
                last_query = last_query.replace(
                    self.double_query_pronouns[n], self.double_query_pronouns_dahsed[n])

        if last_query[len(last_query)-1] == '.' or last_query[len(last_query)-1] == '?':
            to_add = last_query[len(last_query)-1]
            last_query = last_query[0:len(last_query)-1]

        word_list = last_query.split()

        for n in range(len(word_list)):
            if word_list[n] in self.pronoun_pairs_dict.keys() and word_list[n] == 'you':
                if get_object_subject(last_query) == "subject":
                    word_list[n] = 'i'
                elif get_object_subject(last_query) == "object":
                    word_list[n] = 'me'

            elif word_list[n] in self.pronoun_pairs_dict.keys() and word_list[n] != 'you':
                replacmenet = self.pronoun_pairs_dict[word_list[n]][0]
                word_list[n] = replacmenet

        output = ' '.join(word for word in word_list)
        output = output + to_add
        if output[0] == "i" and output[1] != "t":
            output = output.capitalize()
        output = output.replace("i'm", "I'm")
        output = output.replace(" i ", " I ")

        return output

    def determine_stateful_class(self, query, response, this_user_interactions):
        this_stateful_class = -1
        if 'statefulresponse' in response:
            if response == 'statefulresponse2':
                this_stateful_class = 2
            elif response == 'statefulresponse3':
                this_stateful_class = 3
            elif response == 'statefulresponse4':
                this_stateful_class = 4
            elif response == 'statefulresponse5':
                this_stateful_class = 5
        elif 'statefulresponse' not in response:
            # check for class 1:
            if len(this_user_interactions) > 0:
                is_repeated_query = (
                    query == this_user_interactions[len(this_user_interactions)-1][1])
                is_repeated_last_response = (
                    query == this_user_interactions[len(this_user_interactions)-1][2])
                if is_repeated_query or is_repeated_last_response:
                    this_stateful_class = 1
            # Check for ungenerated class 4:
            for n in stateful_class_4_phrases_checks:
                if n in query:
                    this_stateful_class = 4

        return this_stateful_class

    def statefulness(self, query, response, this_user, this_user_info, this_user_interactions):

        this_stateful_class = -1  # to return in case this is the first time user interacts or
        # in case there is no statefulness detected

        if len(this_user_interactions) > 0:
            # class-2, 3, 4, 5 statefulness
            this_stateful_class = self.determine_stateful_class(
                query, response, this_user_interactions)

            if this_stateful_class == 2 or this_stateful_class == 4:  # handle 4 in respond
                response = this_user_interactions[len(
                    this_user_interactions)-1][2]

            elif this_stateful_class == 3:
                last_query = self.process_stateful_class_3(
                    this_user_interactions)
                response = "I thought you just said " + last_query

            elif this_stateful_class == 5:
                response = stateful_class_5_responses[np.random.choice(
                    len(stateful_class_5_responses))]

        # simple replacements
        exempt_class_1 = ('getjoke' in response)
        #print("response before simple replacements is: " + response)
        #print("exempt_class_1 is: " + str(exempt_class_1))
        response = simple_replacements(
            this_user, this_user_info, query, response)
        #print("response after replacements is: " + response)

        # Check class-1
        if this_stateful_class == 1 and exempt_class_1 == False:
            response = self.process_stateful_class_1(
                query, response, this_user_interactions)

        return response, this_stateful_class
