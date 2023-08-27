import pymongo

class MongoDBConnector:

    def __init__(self, db_host):
        self.client = pymongo.MongoClient(db_host)
        self.database = self.client["praktikum"]
        self.collection_forums = self.database["forums"]
        self.collection_users = self.database["users"]

    def push_data_forums(self, forums_data):
        return self.collection_forums.insert_many(forums_data)
    
    def push_data_users(self, users_data):
        return self.collection_users.insert_many(users_data)
    
    def push_single_user(self, user_data):
        return self.collection_users.insert_one(user_data)