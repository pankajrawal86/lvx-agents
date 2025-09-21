
from app.services.google_services import vector_db

def vector_search(query: str, num_neighbors: int = 5) -> dict:
    """
    Performs a vector search on the knowledge base and returns the top results.

    Args:
        query: The query to search for.
        num_neighbors: The number of results to return.

    Returns:
        A dictionary containing the search results.
    """
    print(f"--- Calling Vector Search Tool with query: {query} ---")
    
    # Call the actual vector search service
    search_results = vector_db.search(query=query, num_neighbors=num_neighbors)
    
    print(f"--- Raw results from vector_db.search: {search_results} ---")

    # The vector search service returns a list of lists of objects.
    # We need to parse these results and format them into a list of dictionaries.
    formatted_results = []
    if search_results:
        for result in search_results[0]:
            formatted_results.append({
                "id": result.id,
                "distance": result.distance,
                # The datapoint field is not always present, so we need to check for it
                "data": result.datapoint if hasattr(result, 'datapoint') else None
            })

    return {
        "search_results": formatted_results
    }
