import os
from dotenv import load_dotenv
from app.agents.ai_startup_analysis_agent import AIStartupAnalysisAgent

# Load environment variables from .env file
load_dotenv()

# Check if the API key is set
if not os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY") == "your_api_key_here":
    print("ERROR: GOOGLE_API_KEY is not set.")
    print("Please set your API key in the .env file.")
else:
    # Initialize and run the agent
    agent = AIStartupAnalysisAgent()
    # You can change the deal_id and query here to test different scenarios
    result = agent.run(deal_id="1", query="Give me a full analysis of this startup.")

    # Pretty print the results
    print("\n--- AGENT RUN RESULTS ---")
    import json
    print(json.dumps(result, indent=2))
