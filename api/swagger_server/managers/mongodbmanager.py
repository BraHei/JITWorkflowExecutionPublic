import os
from pymongo import MongoClient
from .awssecretsmanager import get_aws_secret  # Import AWS Secrets Manager function

class MongoDBManager:
    def __init__(self, db_name=None, collection_name=None):
        """
        Initializes MongoDB connection using credentials from AWS Secrets Manager.
        """
        try:
            # Fetch credentials from AWS Secrets Manager
            secret_data = get_aws_secret("replicationDB_secret")  # Replace with your AWS secret name

            # Construct MongoDB connection URI
            mongo_uri = f"mongodb://{secret_data['username']}:{secret_data['password']}@{secret_data['host']}:27017/?tls=true&tlsCAFile=global-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

            # Establish connection
            self.client = MongoClient(mongo_uri, tls=True, retryWrites=False)
            self.db = self.client[db_name or secret_data.get("database", "replicationDB")]
            self.collection = self.db[collection_name or "cacheState"]

            print("Successfully connected to AWS DocumentDB!")
            print("Databases:", self.client.list_database_names())

        except Exception as e:
            print("Connection failed:", e)
            raise

    def insert_event(self, event_data):
        """
        Inserts a new event into the collection.
        """
        if not isinstance(event_data, dict):
            raise ValueError("Event data must be a dictionary.")
        result = self.collection.insert_one(event_data)
        return result.inserted_id

    def get_event(self, unique_id):
        """
        Retrieves an event based on unique_id.
        """
        return self.collection.find_one({"unique_id": unique_id})

    def delete_event(self, unique_id):
        """
        Deletes an event based on unique_id.
        """
        result = self.collection.delete_one({"unique_id": unique_id})
        return result.deleted_count > 0

    def close_connection(self):
        """
        Closes the MongoDB connection.
        """
        self.client.close()
