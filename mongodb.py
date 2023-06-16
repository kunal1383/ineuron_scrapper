import pymongo
import json
from application_logger.app_logger import Logger

class MongoDBHandler:
    def __init__(self, username, password, db_name):
        self.client = pymongo.MongoClient(f"mongodb+srv://{username}:{password}@cluster0.thebkor.mongodb.net/")
        self.db = self.client[db_name]
        self.log_writer = Logger()
        self.file_object = open("Mongodb_Logs/mongodb_log.txt", 'a+') 
        

    def insert_courses_into_collection(self, collection_name, courses_json):
        self.log_writer(self.file_object ,'connecting to mongodb')
        try:
            if collection_name in self.db.list_collection_names():
                collection = self.db[collection_name]
            else:
                collection = self.db.create_collection(collection_name)
                
            self.log_writer(self.file_object ,'Inserting into collection')
            courses = json.loads(courses_json)
            collection.insert_many(courses)
            self.log_writer(self.file_object ,f"Inserted {len(courses)} courses into the collection '{collection_name}'")
            self.file_object.close()   
        except Exception as e:
            self.log_writer(self.file_object ,f"An error occurred: {str(e)}")
            raise Exception