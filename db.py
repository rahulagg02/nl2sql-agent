import sqlite3


class Database:
    def __init__(self, db_path="employees.db"):
        self.db_path = db_path

    def execute_query(self, sql):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            return columns, rows