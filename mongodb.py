from pymongo import MongoClient
from config import Config

class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client[Config.DB_NAME]

    def get_user_collection(self):
        return self.db[Config.USER_COLLECTION]

    def get_question_collection(self):
        return self.db[Config.QUESTION_COLLECTION]
    
    def insert_user(self, user_data):
        return self.get_user_collection().insert_one(user_data)

    def insert_question(self, question_data):
        return self.get_question_collection().insert_one(question_data)

    def insert_many_questions(self, question_list):
        return self.get_question_collection().insert_many(question_list)

    def find_user_by_username(self, username):
        return self.get_user_collection().find_one({"username": username})