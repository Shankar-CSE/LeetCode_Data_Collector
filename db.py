import os
import requests
from dotenv import load_dotenv

load_dotenv()

mongodb_uri = os.getenv("MONGODB_URI")
headers = {"Content-Type": "application/json"}
url = "https://mongodbproxyapi.vercel.app"


def check_mongodb_connection():
    try:
        print("MongoDB URI:", mongodb_uri)
        response = requests.post(url+"/connect-check", json={"uri": mongodb_uri}, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("success", False)
        else:
            print(f"Error: Received status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False


def insert_data(db_name,collection_name, data):
    try:
        drop_collection(db_name,collection_name)
        payload = {
    "uri": mongodb_uri,
    "db": db_name,
    "collection": collection_name,
    "operation": "insertMany",
    "params": [data]
}
        response = requests.post(url+"/execute", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Data inserted successfully into {collection_name}")
        else:            
            print(f"Error: Received status code {response.status_code} while inserting data into {collection_name}")
    except Exception as e:
        print(f"Error inserting data into {collection_name}: {e}")


def drop_collection(db_name, collection_name):
    try:
        payload = {
            "uri": mongodb_uri,
            "db": db_name,
            "collection": collection_name,
            "operation": "drop",
            "params": []
        }
        response = requests.post(url+"/execute", json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Collection {collection_name} dropped successfully")
        else:
            print(f"Error: Received status code {response.status_code} while dropping collection {collection_name}")
    except Exception as e:
        print(f"Error dropping collection {collection_name}: {e}")