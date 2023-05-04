import os
from dotenv import load_dotenv
from pymongo import MongoClient
# import certifi

load_dotenv()

MONGODB_USERNAME = os.environ.get('MONGODB_USERNAME')
MONGODB_PW = os.environ.get('MONGODB_PASSWORD')

CONNECTION_STRING = f"mongodb+srv://{MONGODB_USERNAME}:{MONGODB_PW}@cluster0.xza4gbz.mongodb.net/?retryWrites=true&w=majority"

class DB:
    def __init__(self, db):
        self.db_name = db
        self.db = MongoClient(CONNECTION_STRING)[db]
    def get_collection(self, collection):
        return self.db[collection]

        
def get_db(name):
    client = MongoClient(CONNECTION_STRING)
    
    # Create the database for our example (we will use the same database throughout the tutorial
    return client[name]

def get_collection(db, name):
    return db[name]