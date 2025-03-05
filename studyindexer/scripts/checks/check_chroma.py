import requests
import json
import time

def check_chroma_connection():
    """Check if ChromaDB is accessible and functioning properly"""
    print("Checking ChromaDB connection...")
    
    # Check heartbeat endpoint
    try:
        response = requests.get("http://localhost:8000/api/v1/heartbeat")
        print(f"Heartbeat status: {response.status_code}")
        print(f"Heartbeat response: {response.text}")
    except Exception as e:
        print(f"Error connecting to ChromaDB heartbeat: {str(e)}")
    
    # Try to list collections
    try:
        response = requests.get("http://localhost:8000/api/v1/collections")
        print(f"Collections status: {response.status_code}")
        if response.status_code == 200:
            collections = response.json()
            print(f"Collections: {json.dumps(collections, indent=2)}")
        else:
            print(f"Collections response: {response.text}")
    except Exception as e:
        print(f"Error listing collections: {str(e)}")
    
    # Try to check if the general collection exists
    try:
        response = requests.get("http://localhost:8000/api/v1/collections/general")
        print(f"General collection status: {response.status_code}")
        if response.status_code == 200:
            collection = response.json()
            print(f"General collection: {json.dumps(collection, indent=2)}")
        else:
            print(f"General collection response: {response.text}")
    except Exception as e:
        print(f"Error checking general collection: {str(e)}")

if __name__ == "__main__":
    check_chroma_connection() 