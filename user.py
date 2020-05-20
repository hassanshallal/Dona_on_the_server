import os
import sqlite3
import requests
from datetime import datetime, timedelta

PAGE_ACCESS_TOKEN = os.environ.get('PAGE_ACCESS_TOKEN')


class User:
    # Initializer / Instance Attributes
    def __init__(self, ID, kikuser, kikuser_data=None):
        self.ID = ID
        self.kikuser = kikuser
        if self.find_by_id(ID) == False and kikuser == False:
            target_link = 'https://graph.facebook.com/v3.3/' + ID
            params = (('fields', 'first_name, last_name, timezone, gender'),
                      ('access_token', PAGE_ACCESS_TOKEN))
            response = requests.get(target_link, params=params)
            user_info = response.text
            print(user_info)
            user_info = user_info[1:len(user_info)-1]
            user_info = user_info.replace('"', '')
            user_info = user_info.replace(',', ', ')
            self.user_info = [x.strip() for x in user_info.split(',')]
            print(self.user_info)
            if self.user_info[0].split(":")[0] != "error":
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()
                # Inserting one user
                insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)"
                this_user = (ID,
                             self.user_info[0].split(":")[1],
                             self.user_info[1].split(":")[1],
                             self.user_info[2].split(":")[1],
                             self.user_info[3].split(":")[1],
                             "Facebook")

                cursor.execute(insert_query, this_user)
                connection.commit()
                connection.close()
            else:
                print("User " + str(ID) + " information can't be retrieved")

        elif self.find_by_id(ID) == False and kikuser == True:
            if kikuser_data != None:
                connection = sqlite3.connect('users.db')
                cursor = connection.cursor()
                # Inserting one user
                insert_query = "INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)"
                this_user = (ID,
                             kikuser_data[0],
                             kikuser_data[1],
                             "Undisclosed",
                             "Undisclosed",
                             "Kik")
                cursor.execute(insert_query, this_user)
                connection.commit()
                connection.close()
            else:
                print("User " + str(ID) + " information can't be retrieved")

    def find_by_id(self, ID):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (ID,))
        row = result.fetchone()
        connection.close()
        if row:
            return True
        else:
            return False

    def is_undisclosed_timezone(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        row = result.fetchone()
        connection.close()
        if row[3] == "Undisclosed":
            return True
        else:
            return False

    def is_undisclosed_gender(self):
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM users WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        row = result.fetchone()
        connection.close()
        if row[4] == "Undisclosed":
            return True
        else:
            return False

    def disclose_timezone(self, user_tz):
        connection = sqlite3.connect('users.db')
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
                     user_tz,
                     row[4],
                     row[5])
        cursor.execute(insert_query, this_user)
        connection.commit()
        connection.close()

        return True

    def disclose_gender(self, user_gender):
        connection = sqlite3.connect('users.db')
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
                     row[3],
                     user_gender,
                     row[5])
        cursor.execute(insert_query, this_user)
        connection.commit()
        connection.close()

        return True

    def get_user_info_by_id(self):
        connection = sqlite3.connect('users.db')
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
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()

        query = "SELECT * FROM userInteractions WHERE ID = ?"
        result = cursor.execute(query, (self.ID,))
        all_records = result.fetchall()

        connection.close()

        return len(all_records)

    def update_user_info_by_id(self, update_info):
        print(update_info['bestMatch'])
        connection = sqlite3.connect('users.db')
        cursor = connection.cursor()
        insert_query = "INSERT INTO userInteractions VALUES (?, ?, ?, ?, ?, ?, ?)"
        this_interaction = (self.ID,
                            update_info['query'],
                            update_info['response'],
                            str(datetime.now()),
                            update_info['aware'],
                            update_info['stateful'],
                            update_info['bestMatch'])
        cursor.execute(insert_query, this_interaction)
        connection.commit()
        connection.close()
