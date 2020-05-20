import time
import signal
from contextlib import contextmanager

from facebook_graphAPI import *
from kik_graphAPI import *
from news_assist import *

# Control execution time under facebook pressure


class TimeoutException(Exception):
    pass


@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


ask_kik_gender = 20  # Ask kikuser to share their gender every 20 messages.


# A function to report awareness and statefulness
def report_aware_stateful(this_awareness, this_statefulness):
    # This is for illustration purposes only. We can
    # have a video on youtube and take it from there.
    aware_description = ' '
    if this_awareness == 'g':
        aware_description = "Dona assumes that your message is about a general topic."
    elif this_awareness == 's':
        aware_description = 'Dona assumes that your message is about Dona.'
    elif this_awareness == 'u':
        aware_description = 'Dona assumes that your message is about yourself.'
    elif this_awareness == 'us':
        aware_description = 'Dona assumes that your message is about both Dona and yourself.'
    elif this_awareness == 'w':
        aware_description = 'Dona assumes that your message is about the world.'

    stateful_descriptios = ' '
    if this_statefulness == 1:
        stateful_descriptios = 'Dona thinks that you are repeating your input.'
    elif this_statefulness == 2:
        stateful_descriptios = 'Dona thinks that you want Dona to repeat its last response!'
    elif this_statefulness == 3:
        stateful_descriptios = "Dona thinks you're asking it by referring  to your eralier input!."
    elif this_statefulness == 4:
        stateful_descriptios = "Dona thinks you're asking about its take on something you both are discussing."
    elif this_statefulness == 5:
        stateful_descriptios = 'Dona thinks you asked it to stop chatting or stop communicating.'

    return aware_description + ' ' + stateful_descriptios

# View function


def view(report_awareness_statefulness, this_user, this_awareness, this_statefulness, this_response, platform, kik_message=None):
    if "initiate google search module" in this_response:
        this_response = " "
    # Basic responding
    if platform == "Facebook":
        send_message(this_user.ID, this_response)
    elif platform == "Kik":
        kik.send_messages([
            TextMessage(
                to=kik_message.from_user,
                chat_id=kik_message.chat_id,
                body=this_response
            )
        ])
        # First example of proactivity implemented on kik and accomodated by statefulness and the data
        if this_user.is_undisclosed_gender() and (this_user.get_num_messages_by_id() - 1) % ask_kik_gender == 0:
            kik.send_messages([
                TextMessage(
                    to=kik_message.from_user,
                    chat_id=kik_message.chat_id,
                    body="Hey {}, Thanks a lot for chatting with me. I wonder whether you could share your gender with me.".format(
                        kik_message.from_user),
                    # keyboards are a great way to provide a menu of options for a user to respond with!
                    keyboards=[SuggestedResponseKeyboard(responses=[TextResponse("Sure, I'm male."), TextResponse("Sure, I'm female."), TextResponse("I prefer not to disclose my gender.")])])])

    # send extra details
    if report_awareness_statefulness:
        extra_details = report_aware_stateful(
            this_awareness, this_statefulness)
        if platform == "Facebook":
            send_message(this_user.ID, extra_details)
        elif platform == "Kik":
            kik.send_messages([
                TextMessage(
                    to=kik_message.from_user,
                    chat_id=kik_message.chat_id,
                    body=extra_details
                )
            ])
    return "ok"


def view_google_search(query, report_awareness_statefulness, this_user, this_awareness, this_statefulness, this_response, platform, kik_message=None):
    print("a")
    this_response = "I will search this and get back to you very soon, thanks for your patience."
    if kik_message == None:
        view(False, this_user, this_awareness,
             this_statefulness, this_response, "Facebook")
    else:
        view(False, this_user, this_awareness,
             this_statefulness, this_response, "Kik", kik_message=kik_message)

    print("b")

    # search_result = get_google_search(query)
    try:
        with time_limit(5):
            search_result = search_google(query)
    except TimeoutException as e:
        print("Timed out!")
        search_result = []
    print(search_result)

    print("c")

    if len(search_result) == 0:
        print("d")
        this_response = "I am sorry I couldn't " + query
        if kik_message == None:
            view(False, this_user, this_awareness,
                 this_statefulness, this_response, "Facebook")
        else:
            view(False, this_user, this_awareness,
                 this_statefulness, this_response, "Kik", kik_message=kik_message)

    else:
        all_summaries = {}
        print("e")
        for n in search_result:
            print("f")
            if kik_message != None:
                try:
                    with time_limit(3):
                        all_summaries[n] = get_summary(n, 3)
                except TimeoutException as e:
                    print("Timed out!")
            else:
                all_summaries[n] = ""

        print("f")
        for n in all_summaries.keys():
            if all_summaries[n] != "Sorry, I couldn't summarize this link." and all_summaries[n] != "":
                try:
                    if kik_message == None:
                        view(False, this_user, this_awareness,
                             this_statefulness, "For this link: " + n, "Facebook")
                        time.sleep(1)
                        view(False, this_user, this_awareness,
                             this_statefulness, "I suggest this summary: " + all_summaries[n], "Facebook")
                    else:
                        view(False, this_user, this_awareness,
                             this_statefulness, "For this link: " + n, "Kik", kik_message=kik_message)
                        time.sleep(1)
                        view(False, this_user, this_awareness, this_statefulness,
                             "I suggest this summary: " + all_summaries[n], "Kik", kik_message=kik_message)
                except:
                    pass
            else:
                if kik_message == None:
                    view(False, this_user,
                         this_awareness, this_statefulness, n, "Facebook")
                else:
                    view(False, this_user, this_awareness,
                         this_statefulness, n, "Kik", kik_message=kik_message)
