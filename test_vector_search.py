import os
# This is a workaround to load the environment variables from the .env file
# The main application uses python-dotenv, but this script can be run standalone.
from dotenv import load_dotenv
load_dotenv()

from app.tools.vector_search import vector_search

def test_vector_search_connectivity():
    """
    Tests the connectivity to the vector search service and prints the results.
    """
    print("--- Testing Vector Search Connectivity ---")
    
    # Check if the required environment variables are set
    required_vars = [
        "GOOGLE_CLOUD_PROJECT",
        "VECTOR_SEARCH_REGION",
        "VECTOR_SEARCH_INDEX_ID",
        "VECTOR_SEARCH_ENDPOINT_ID"
    ]
    
    if not all(os.getenv(var) for var in required_vars):
        print("\n--- VECTOR SEARCH TEST FAILED ---")
        print("One or more required environment variables are not set.")
        print("Please ensure the following are set in your .env file:")
        for var in required_vars:
            print(f"- {var}")
        return

    # Use a simple query to test the connection
    test_query = "What does the fox do?"
    print(f"\n--- Running vector_search with query: '{test_query}' ---")
    
    try:
        results = vector_search(query=test_query)
        
        print("\n--- VECTOR SEARCH TEST RESULTS ---")
        if results and results["search_results"]:
            print("Successfully received results from the vector search service:")
            for result in results["search_results"]:
                print(f"- ID: {result.get('id')}, Distance: {result.get('distance')}, Data: {result.get('data')}")
        else:
            print("The vector search service returned no results.")
            print("This could be due to an empty index or a problem with the service.")

    except Exception as e:
        print(f"\n--- An error occurred during the vector search test: {e} ---")
        print("Please check your environment variables and service configuration.")

if __name__ == "__main__":
    test_vector_search_connectivity()
