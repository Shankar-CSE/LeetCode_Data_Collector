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
            print(f"MongoDB connection successful: {data.get('message', 'N/A')}")
            return data.get("success", False)
        else:
            print(f"Error: Received status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return False


def insert_data(db_name, collection_name, data, batch_size=200):
    """
    Inserts data into MongoDB in batches to avoid 413 errors.
    """
    try:
        drop_collection(db_name, collection_name)
        total_records = len(data)
        print(f"Inserting {total_records} records into {collection_name} in batches of {batch_size}...")

        for start_idx in range(0, total_records, batch_size):
            batch = data[start_idx : start_idx + batch_size]
            payload = {
                "uri": mongodb_uri,
                "db": db_name,
                "collection": collection_name,
                "operation": "insertMany",
                "params": [batch],
            }
            response = requests.post(url + "/execute", json=payload, headers=headers, timeout=30)
            if response.status_code != 200:
                print(f"Error inserting batch starting at index {start_idx}: status {response.status_code}")
            else:
                print(f"Batch {start_idx}-{start_idx + len(batch)-1} inserted successfully")

        print(f"All records inserted into {collection_name} successfully.")
        create_indexes(db_name, collection_name)

    except Exception as e:
        print(f"Error inserting data into {collection_name}: {e}")

def create_indexes(db_name, collection_name):
    indexes = ["DEPT", "GENDER", "BATCH", "Problem Count", "Contest Rating"]
    for field in indexes:
        try:
            payload = {
                "uri": mongodb_uri,
                "db": db_name,
                "collection": collection_name,
                "operation": "createIndex",
                "params": [{field: 1}],
            }
            response = requests.post(url + "/execute", json=payload, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"Index on '{field}' created successfully")
            else:
                print(f"Error creating index on '{field}': status {response.status_code}")
        except Exception as e:
            print(f"Error creating index on '{field}': {e}")


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