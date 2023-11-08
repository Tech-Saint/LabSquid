import sqlite3,os
from sqlite3 import Error



class SQL_DB:
    def __init__(self) -> None:
        self.dir_path = os.path.join(os.path.dirname(__file__))
        self.dbpath = os.path.join(self.dir_path,'Users.db')
        self.create_connection()
        self.execute_query(
            """CREATE TABLE IF NOT EXISTS users (
                ID INTEGER PRIMARY KEY,
                Username TEXT NOT NULL,
                Email TEXT UNIQUE NOT NULL,
                Password TEXT NOT NULL
            );

            """
        )
    def create_connection(self):
        self.connection = None
        try:
            self.connection = sqlite3.connect(self.dbpath,check_same_thread=False)
            print("Connection to SQLite DB successful")
        except Error as e:
            print(f"The error '{e}' occurred")

    
    def execute_query(self, query):
        cursor = self.connection.cursor()
        result = None
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            print(f"The error '{e}' occurred")
