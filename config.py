from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    MONGO_URI = os.getenv("MONGO_URI")
    if not MONGO_URI:
        raise EnvironmentError("Please set the MONGO_URI environment variable.")

    DB_NAME = "QAgameDB"
    USER_COLLECTION = "users"
    QUESTION_COLLECTION = "questions"