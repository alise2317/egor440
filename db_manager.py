import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'DataBs', 'textlatordb.db')

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def check_user_credentials(self, username, password):
        query = "SELECT * FROM User WHERE username = ? AND password = ?"
        self.cursor.execute(query, (username, password))
        result = self.cursor.fetchone()
        return result is not None

    def add_user(self, username, password):
        try:
            query = "INSERT INTO User (username, password) VALUES (?, ?)"
            self.cursor.execute(query, (username, password))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
    # хз зачем
    def execute(self, query, params=()):
        """Выполняет запрос без возврата результата."""
        self.cursor.execute(query, params)
        self.conn.commit()

    def execute_query(self, query, params=None):
        self.cursor.execute(query, params or ())
        self.conn.commit()

    def fetch_one(self, query, params=()):
        """Выполняет запрос и возвращает одну строку результата."""
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetch_all(self, query, params=()):
        """Выполняет запрос и возвращает все строки результата."""
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def get_last_inserted_id(self):
        """Возвращает ID последней вставленной записи."""
        return self.cursor.lastrowid
    # конец хз зачем

    def close(self):
        self.conn.close()
