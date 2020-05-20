import time
from datetime import datetime, timedelta
from timeit import default_timer as timer


from thermogena_user import Thermogena_user
from facebook_graphAPI_thermogena import * # this is including custome Thermogena specific methods

'''
    
def get_time(this_user_info):
    if this_user_info[3] == "Undisclosed":
        return "Undisclosed"

    else:
        time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[3]))
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
        time_there = datetime.utcnow() + timedelta(hours=int(this_user_info[3]))
        year = time_there.year
        month = time_there.month
        day = time_there.day
        return str(month) + "/" + str(day) + "/" + str(year)

'''

def simple_thermogena_replacements(this_user, this_user_info, response):
    # Simple replacmenets

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
            'usergender', this_user_info[3])
    if 'gettime' in response:
        print("gettime detected")
        response = "I am sorry but Facebook did not approve Thermogena to access your timezone."

    if 'getdate' in response:
        print("get_date() detected")
        response = "I am sorry but Facebook did not approve Thermogena to access your timezone."

    return response
'''
if 'gettime' in response:
    print("gettime detected")
    response = response.replace('gettime', get_time(this_user_info))
    
if 'getdate' in response:
    print("get_date() detected")
    response = response.replace('getdate',
    get_date(this_user_info))
'''


# Updata database function
def update_thermogena_database(this_user, text, is_postback, this_response):
    update_info = {}
    update_info['query'] = text.lower()
    update_info['is_postback'] = is_postback
    update_info['response'] = this_response
    this_user.update_user_info_by_id(update_info)
    return "ok"

