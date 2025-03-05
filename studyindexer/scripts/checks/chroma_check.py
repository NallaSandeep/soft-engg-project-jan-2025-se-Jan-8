import sys
import chromadb
from chromadb.config import Settings

def check_chroma():
    """Check ChromaDB collections with the Python client"""
    print("Initializing ChromaDB client...")
    
    try:
        client = chromadb.HttpClient(
            host="chromadb",
            port=8000,
            settings=Settings(
                anonymized_telemetry=False,
            )
        )
        
        print("Getting client info:")
        print(client.get_version())
        
        print("Listing collections:")
        collections = client.list_collections()
        for collection in collections:
            print(f"Collection: {collection}")
            
        # Try to create the general collection
        try:
            print("Attempting to create general collection...")
            metadata = {
                "description": "General collection for all documents",
                "created_by": "StudyIndexer",
                "version": "0.1.0",
                "collection_type": "general"
            }
            client.create_collection(name="general", metadata=metadata)
            print("General collection created successfully")
        except Exception as e:
            print(f"Error creating general collection: {str(e)}")
            print("Attempting to get general collection...")
            try:
                general_collection = client.get_collection(name="general")
                print("General collection already exists")
            except Exception as inner_e:
                print(f"Error getting general collection: {str(inner_e)}")
            
    except Exception as e:
        print(f"Error connecting to ChromaDB: {str(e)}")
        
if __name__ == "__main__":
    check_chroma() 