import logging
import os
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError
from bson.objectid import ObjectId


class ImmoScoutDB:
    def __init__(self):
        self.password = os.environ["DATABASE_PASSWORD"]
        self.username = os.environ["DATABASE_USERNAME"]
        self.uri = f"mongodb+srv://{self.username}:{self.password}@scraper.nas9w9u.mongodb.net/?retryWrites=true&w=majority"
        self.client: MongoClient = None
        self.founded_collection: Collection = None
        self.contacted_collection: Collection = None
        self.db = None

    @staticmethod
    def convert_to_object_id(id):
        return ObjectId(id)

    def connect(self):
        try:
            self.client = MongoClient(self.uri, tls=True)
            self.client.admin.command("ping")
            self.db = self.client["ImmoScout"]
            self.founded_collection = self.db["foundHouses"]
            self.contacted_collection = self.db["contactedHouses"]
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except PyMongoError as e:
            print(f"Failed to connect to MongoDB: {str(e)}")

    def close(self):
        logging.info("Closing db connection")
        if self.client is not None:
            self.client.close()

    def insert_founded_house(self, house):
        logging.info(
            f"Inserting house with address {house['Address']} to founded collection"
        )
        self.founded_collection.insert_one(house)

    def insert_founded_houses(self, houses):
        logging.info(f"Inserting houses to founded collection")

        self.founded_collection.insert_many(houses)

    def insert_contacted_houses(self, houses):
        logging.info(f"Inserting houses to contacted collection")
        self.contacted_collection.insert_many(houses)

    def insert_contacted_house(self, house):
        # TODO Better loging
        logging.info(f"Inserting a house to contacted collection")
        self.contacted_collection.insert_one(house)

    def get_founded_houses(self):
        return [house for house in self.founded_collection.find()]

    def delete_founded_houses(self, houses):
        logging.info(f"Deleting contacted houses from founded collection")
        house_links = [house["link"] for house in houses]
        self.founded_collection.delete_many({"link": {"$in": house_links}})

    def delete_founded_house(self, house):
        logging.info(
            f"Deleting house with address {house['Address']} from founded collection"
        )
        self.founded_collection.delete_one({"link": house["link"]})
