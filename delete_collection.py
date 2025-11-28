"""Delete Milvus collection to fix schema mismatch"""
from pymilvus import connections, utility

try:
    # Connect to Milvus
    print("🔌 Connecting to Milvus...")
    connections.connect(
        alias="default",
        host="localhost",
        port="19530"
    )
    print("✅ Connected to Milvus")
    
    collection_name = "classcare_documents"
    
    # List collections
    collections = utility.list_collections()
    print(f"\n📋 Available collections: {collections}")
    
    if collection_name in collections:
        print(f"\n⚠️  Found collection '{collection_name}'")
        print(f"   This collection has a schema mismatch and needs to be deleted.")
        
        response = input(f"\n   Delete collection '{collection_name}'? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            try:
                utility.drop_collection(collection_name)
                print(f"\n✅ Successfully deleted collection '{collection_name}'")
                print(f"\n   Now you can upload documents again.")
                print(f"   The collection will be recreated with the correct schema (auto_id=True).")
            except Exception as e:
                print(f"\n❌ Error deleting collection: {e}")
        else:
            print("\n❌ Deletion cancelled.")
    else:
        print(f"\n✅ Collection '{collection_name}' does not exist.")
        print("   You can upload documents now - the collection will be created automatically.")
    
    # Disconnect
    connections.disconnect("default")
    print("\n✅ Done!")
    
except ImportError:
    print("❌ pymilvus is not installed!")
    print("   Install it with: pip install pymilvus==2.3.4")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Make sure Milvus Docker container is running:")
    print("     docker ps")
    print("  2. Check Milvus health:")
    print("     curl http://localhost:9091/healthz")

