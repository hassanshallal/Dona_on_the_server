import pickle
from spellchecker import SpellChecker
from user import User

spell = SpellChecker()
# make sure you don't correct spelling for any word in actions or reactions
bag_of_words = pickle.load(open("bag_of_words.pkl", "rb"))

interrogative_starters = ['which', 'what', 'whose', 'who', 'whom', 'where', 'when', 'how', 'why', 'are', 'is', 'am', 'do', 'does', 'was', 'were', 'can', 'may', 'will',
                          'would', 'should', 'shall', "who's", "where's", "when's", "how's", "how're", "isn't", "aren't", "don't", "doesn't", "shouldn't", 'have', 'has', "haven't", "hasn't"]

# Updata database function


def update_database(this_user, text, this_response, this_awareness, this_statefulness, best_match):
    update_info = {}
    update_info['query'] = text.lower()
    update_info['response'] = this_response
    update_info['aware'] = this_awareness
    update_info['stateful'] = this_statefulness
    update_info['bestMatch'] = best_match
    this_user.update_user_info_by_id(update_info)
    return "ok"

# correct spelling


def correct_spelling(query, ask_for_permission = False):
    # print(query)
    word_list = query.split()
    misspelled = spell.unknown(word_list)
    changes = {}
    if len(misspelled) > 0:
        for word in misspelled:
            if '.' in word:
                word = word.replace('.', '')
            if '?' in word:
                word = word.replace('?', '')
            if '!' in word:
                word = word.replace('!', '')
            if ',' in word:
                word = word.replace(',', '')
            if word not in bag_of_words:
                if ask_for_permission:
                    print("do you want to spell correct " + word + " ?")
                    if input() == "":
                        changes[word] = spell.correction(word)
                else:
                    changes[word] = spell.correction(word)
    # print(changes)
    for n in changes.keys():
        print(n + " is corrected to: " + changes[n])
        query = query.replace(n, changes[n])

    return query

# Process query


def process_query(text, ask_for_permission = False):
    text = text.replace('’', "'")
    text = text.replace("'s ", " is ")
    text = text.replace("n't ", " not ")
    text = text.lstrip()
    text = text.rstrip()
    text = text.lower()
    text = correct_spelling(text, ask_for_permission)

    isnt_punctuated = (text[-1] != "." and text[-1] != "!" and text[-1] != "?")
    if isnt_punctuated:
        if text.split()[0] in interrogative_starters:
            text = text + '?'
        else:
            text = text + '.'

    return text

# remove repetitive words in response


def remove_consecutive_repetitions(response):

    response_list = response.split()
    if len(response_list) < 2:
        return response_list

    new_list = []

    for n in range(len(response_list)-1):
        if response_list[n] != response_list[n+1]:
            new_list.append(response_list[n])

    if(response_list[len(response_list) - 1] != response_list[len(response_list) - 2]):
        new_list.append(response_list[len(response_list) - 1])

    return ' '.join(new_list)

# Process response


def process_response(text):
    text = remove_consecutive_repetitions(text)
    if type(text) == list:
        if len(text) == 1:
            text = text[0]
        elif len(text) == 0:
            text = ""
    text = text.capitalize()
    text = text.replace(' i ', ' I ')
    text = text.replace(" i'm ", " I'm ")
    text = text.replace(" dona ", " Dona ")
    return text
