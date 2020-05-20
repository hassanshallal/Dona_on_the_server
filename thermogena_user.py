import os
import sqlite3
import requests
from datetime import datetime, timedelta

THERMOGENA_ACCESS_TOKEN = os.environ.get('THERMOGENA_ACCESS_TOKEN')


class Thermogena_user:
    # Initializer / Instance Attributes
    def __init__(self, ID, kikuser, kikuser_data=None):
        self.ID = ID
        self.kikuser = kikuser
        if self.find_by_id(ID) == False and kikuser == False:
            target_link = 'https://graph.facebook.com/v3.3/' + ID
            params = (('fields', 'first_name, last_name, gender'),
                      ('access_token', THERMOGENA_ACCESS_TOKEN))
            response = requests.get(target_link, params=params)
            user_info = response.text
            print(user_info)
            user_info = user_info[1:len(user_info)-1]
            user_info = user_info.replace('"', '')
            user_info = user_info.replace(',', ', ')
            self.user_info = [x.strip() for x in user_info.split(',')]
            print(self.user_info)
            if self.user_info[0].split(":")[0] != "error":
                connection = sqlite3.connect('thermogena_users.db')
                cursor = connection.cursor()
                # Inserting one user
                insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?)"
                this_user = (ID,
                             self.user_info[0].split(":")[1],
                             self.user_info[1].split(":")[1],
                             self.user_info[2].split(":")[1],
                             "Facebook")

                cursor.execute(insert_query, this_user)
                connection.commit()
                connection.close()
            else:
                print("User " + str(ID) + " information can't be retrieved")

        elif self.find_by_id(ID) == False and kikuser == True:
            if kikuser_data != None:
                connection = sqlite3.connect('thermogena_users.db')
                cursor = connection.cursor()
                # Inserting one user
                insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?)"
                this_user = (ID,
                             kikuser_data[0],
                             kikuser_data[1],
                             "Undisclosed",
                             "Kik")
                cursor.execute(insert_query, this_user)
                connection.commit()
                connection.close()
            else:
                print("User " + str(ID) + " information can't be retrieved")

    def find_by_id(self, ID):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (ID,))
        row = result.fetchone()
        connection.close()
        if row:
            return True
        else:
            return False


    def is_undisclosed_gender(self):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        row = result.fetchone()
        connection.close()
        if row[3] == "Undisclosed":
            return True
        else:
            return False

    def disclose_gender(self, user_gender):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        row = result.fetchone()

        delete_query = "DELETE FROM users WHERE ID = ?"
        cursor.execute(delete_query, (self.ID,))
        connection.commit()

        insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)"
        this_user = (self.ID,
                     row[1],
                     row[2],
                user_gender,
                     row[4])
        cursor.execute(insert_query, this_user)
        connection.commit()
        connection.close()

        return True

    def get_user_info_by_id(self):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        row = result.fetchone()

        query = "SELECT * FROM userInteractions WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        all_records = result.fetchall()

        connection.close()

        return row, all_records

    def get_num_messages_by_id(self):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM userInteractions WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        all_records = result.fetchall()

        connection.close()

        return len(all_records)

    def update_user_info_by_id(self, update_info):
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()
        # create_table2 = "CREATE TABLE userInteractions (ID text, query text, is_postback text, response text, dateTime text)"
        insert_query = "INSERT INTO userInteractions VALUES (?, ?, ?, ?, ?)"
        this_interaction = (self.ID,
                            update_info['query'],
                            update_info['is_postback'],
                            update_info['response'],
                            str(datetime.now()))
        cursor.execute(insert_query, this_interaction)
        connection.commit()
        connection.close()
    
    # return third or fourth or none
    def to_invoke_service(self): 
        connection = sqlite3.connect('thermogena_users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM userInteractions WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        all_records = result.fetchall()
        connection.close()
        if len(all_records) > 0:
            last_response = all_records[len(all_records)-1][3]
            if "Please type or enter the food, you'll get the wine back :)" in last_response:
                return 'third'
            elif "Please type or enter the wine, you'll get the food back :)" in last_response:
                return 'fourth'
            else:
                return 'recurse'
        else:
            return 'recurse'
              
        
        
        
        
        
