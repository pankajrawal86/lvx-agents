from .base_agent import ToolbeltAgent

class UserPreferencesAgent(ToolbeltAgent):
    """Handles user preferences for deal notes."""
    def __init__(self):
        super().__init__(
            agent_name="User Preferences Agent",
            tools=[]
        )

    def run(self, user_query):
        """
        Acknowledges the user's request to save their preferences for deal notes.
        """
        # In a real application, this would save the user's preferences to a database.
        # For now, it just returns a confirmation message.
        return {"status": "Acknowledged. I will remember this for future deals."}
