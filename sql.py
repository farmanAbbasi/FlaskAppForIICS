# sql.py - Create a SQLite3 table and populate it with data
import sqlite3
# create a new database if the database doesn't already exist
with sqlite3.connect('sample.db') as connection:

    # get a cursor object used to execute SQL commands
    c = connection.cursor()
    # drop the existing one
    c.execute('Drop table posts')
    # create the table
    c.execute('CREATE TABLE posts(title TEXT, details TEXT)')

    # insert dummy data into the table
    c.execute('INSERT INTO posts VALUES("Good", "I\'m good.")')
    c.execute('INSERT INTO posts VALUES("Well", "I\'m well.")')
    c.execute('INSERT INTO posts VALUES("Excellent", "I\'m excellent.")')
    c.execute('INSERT INTO posts VALUES("Okay", "I\'m okay.")')


with sqlite3.connect('usersDB.db') as connection2:
    c2=connection2.cursor()
    c2.execute('CREATE TABLE users(username TEXT, password TEXT,email TEXT)')

