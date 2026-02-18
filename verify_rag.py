try:
    print("Importing rag_engine...")
    import rag_engine
    print("rag_engine imported successfully.")
    
    print("Trying to add a document...")
    rag_engine.add_response_to_rag("test_id", "This is a test document.", {"name": "Tester"})
    print("Document added.")
    
    print("Trying to query...")
    res = rag_engine.query_rag("test")
    print("Query result:", res)
    
except Exception as e:
    import traceback
    traceback.print_exc()
