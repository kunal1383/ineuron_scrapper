import mysql.connector
from application_logger.app_logger import Logger


class MySQHandler:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.log_writer = Logger()
        self.file_object = open("Sql_Logs/sql_log.txt", 'a+')
        self.connection = None
        self.cursor = None

    def connect(self):
        self.log_writer.log(self.file_object, 'Creating connection to MySQL database')
        try:
            self.connection = mysql.connector.connect(host=self.host, user=self.username, password=self.password)
            self.cursor = self.connection.cursor()
        except Exception as e:
            self.log_writer.log(self.file_object, f'Unsuccessful connection to MySQL database due to {e}')
            raise Exception

    def create_database(self, db_name):
        self.log_writer.log(self.file_object, 'Creating database')
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        except Exception as e:
            self.log_writer.log(self.file_object, f"Error occurred while creating database: {e}")

    def create_table(self,course):
        self.log_writer.log(self.file_object, 'Creating table')
        try:
            
            self.cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {course} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title TEXT,
                    instructors TEXT,
                    curriculum TEXT
                )
            ''')
        except Exception as e:
            self.log_writer.log(self.file_object, f"Failed to create table due to: {e}")    

    def insert_course(self, title, instructors, curriculum ,course):
        self.log_writer.log(self.file_object, 'Inserting into the table')
        try:
            query = f'INSERT INTO {course} (title, instructors, curriculum) VALUES (%s, %s, %s)'
            values = (title, instructors, curriculum)
            self.cursor.execute(query, values)
        except Exception as e:
            self.log_writer.log(self.file_object, f"Failed to insert in table table due to: {e}")     

    def commit(self):
        self.log_writer.log(self.file_object, 'Commiting changes')
        try:
            self.connection.commit()
        except Exception as e:
            self.log_writer.log(self.file_object, f"Failed to commit : {e}")     

    def close(self):
        self.log_writer.log(self.file_object, 'closing conection')
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.file_object.close()
        except Exception as e:
            self.log_writer.log(self.file_object, f"Failed to close connection: {e}")     