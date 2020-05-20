import sqlite3

connection = sqlite3.connect('thermogena_users.db')
cursor = connection.cursor()

query = "SELECT * FROM users"
result = cursor.execute(query)
row = result.fetchall()
for n in range(len(row)):
    print(row[n])
print('Number of users is: ', str(len(row)))
#print('==========')
#query = "SELECT * FROM userInteractions"
#result = cursor.execute(query)
#row = result.fetchall()
#for n in range(len(row)):
#    print(row[n])

connection.close()

