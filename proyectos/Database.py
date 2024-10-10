import pyodbc

class DatabaseManager:
    @staticmethod
    def connect_to_database():
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=your_server_name;"
            "DATABASE=your_database_name;"
            "UID=your_username;"
            "PWD=your_password;"
        )
        connection = pyodbc.connect(connection_string)
        return connection

    @staticmethod
    def execute_query_on_database(query):
        connection = DatabaseManager.connect_to_database()
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()
        return result

