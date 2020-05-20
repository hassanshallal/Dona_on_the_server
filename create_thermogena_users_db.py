import sqlite3

connection = sqlite3.connect('thermogena_users.db')
cursor = connection.cursor()

# Creating a table
create_table1 = "CREATE TABLE users (ID text, first_name text, last_name text, gender text, Platform text)"
cursor.execute(create_table1)

create_table2 = "CREATE TABLE userInteractions (ID text, query text, is_postback text, response text, dateTime text)"
cursor.execute(create_table2)

connection.commit()
connection.close()
