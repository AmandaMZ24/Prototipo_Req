import mysql.connector
from flask import g

def get_db():
    if 'db' not in g:
        g.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="rfmmsoeu2412##",
            database="petlink"
        )
    return g.db
