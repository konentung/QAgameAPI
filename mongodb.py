from pymongo import MongoClient
from config import Config
from pymongo.errors import ConnectionFailure

class MongoDB:
    def __init__(self):
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.DB_NAME]
            print("✅ MongoDB connection successful")
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")

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