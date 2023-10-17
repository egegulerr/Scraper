import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError


class ImmoScoutDB:
    def __init__(self):
        self.password = os.environ["DATABASE_PASSWORD"]
        self.username = os.environ["DATABASE_USERNAME"]
        self.uri = f"mongodb+srv://{self.username}:{self.password}@scraper.nas9w9u.mongodb.net/?retryWrites=true&w=majority"
        self.client = None

    def connect(self):
        try:
            self.client = MongoClient(self.uri, tls=True)
            self.client.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except PyMongoError as e:
            print(f"Failed to connect to MongoDB: {str(e)}")

    def close(self):
        if self.client is not None:
            self.client.close()

    def insert_founded_house(self, house):
        db = self.client["ImmoScout"]
        collection = db["foundHouses"]
        collection.insert_one(house)

    def insert_founded_houses(self, houses):
        db = self.client["ImmoScout"]
        collection = db["foundHouses"]
        collection.insert_many(houses)
