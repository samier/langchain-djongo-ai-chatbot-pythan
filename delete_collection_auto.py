"""Delete Milvus collection automatically to fix schema mismatch"""
import sys

try:
    from pymilvus import connections, utility
    
    # Connect to Milvus
    print("Connecting to Milvus...")
    connections.connect(
        alias="default",
        host="localhost",
        port="19530"
    )
    print("Connected!")
    
    collection_name = "classcare_documents"
    collections = utility.list_collections()
    print(f"Available collections: {collections}")
    
    if collection_name in collections:
        print(f"\nDeleting collection '{collection_name}'...")
        utility.drop_collection(collection_name)
        print(f"✅ Collection '{collection_name}' deleted successfully!")
        print("\nYou can now upload documents - the collection will be recreated with correct schema.")
    else:
        print(f"\n✅ Collection '{collection_name}' does not exist.")
        print("You can upload documents now - the collection will be created automatically.")
    
    connections.disconnect("default")
    print("\nDone!")
    
except ImportError as e:
    print(f"❌ Error: pymilvus is not installed!")
    print("Install it with: pip install pymilvus==2.3.4")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

