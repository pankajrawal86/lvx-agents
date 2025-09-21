import uuid

# Simple in-memory cache for conversation histories.
# In a production environment, this would be replaced with a more robust
# solution like Redis, a database, or a dedicated caching service.
conversation_cache = {}

def get_conversation_history(conversation_id=None):
    """
    Retrieves the history for a given conversation_id.
    If no id is provided, it starts a new conversation.
    """
    if conversation_id and conversation_id in conversation_cache:
        return conversation_cache[conversation_id]
    return [] # Return an empty history for a new conversation

def save_conversation_history(conversation_id, history):
    """
    Saves the updated history for a conversation.
    """
    if not conversation_id:
        conversation_id = str(uuid.uuid4())
    conversation_cache[conversation_id] = history
    return conversation_id

