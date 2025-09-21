import json
from .base_agent import ToolbeltAgent
from app.tools.vector_search import vector_search

class DealMemoAgent(ToolbeltAgent):
    """Generates a deal memo for a startup."""
    def __init__(self):
        super().__init__(
            agent_name="Deal Memo Agent",
            tools=[vector_search]
        )

    def run(self, startup_data):
        """
        Generates a comprehensive deal memo based on the startup's data.
        """
        
        prompt = f"""
        You are a world-class investment analyst, and your task is to generate a detailed investment deal memo.

        **Instructions:**
        1.  You have access to a `vector_search` tool that can search through a knowledge base of internal documents, such as pitch decks, call transcripts, and market research reports.
        2.  **Crucially, you have also been provided with summaries of key internal documents in the 'Internal Document Summaries' section below. You MUST use this information as a primary source for your analysis.**
        3.  Use the `vector_search` tool to supplement the provided summaries and gather any additional information needed about the startup\'s market, team, product, financials, and competition.
        4.  Once you have gathered all the necessary information, synthesize it into a comprehensive deal memo.
        5.  The memo should be structured for an investment committee and cover the following sections in detail:
            -   Executive Summary
            -   Market Opportunity
            -   Founding Team Background
            -   Product/Service
            -   Competitive Landscape
            -   Financials
            -   Use of Funds
            -   Investment Thesis
            -   Risks
        
        **Startup Information:**
        - **Company Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Description:** {startup_data.get('description')}
        - **Location:** {startup_data.get('location')}
        - **Stage:** {startup_data.get('stage')}
        - **Funding Goal:** {startup_data.get('fundingGoal')}
        - **Raised so far:** {startup_data.get('raised')}

        **Internal Document Summaries:**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        Now, begin your work. Remember to prioritize the 'Internal Document Summaries' and supplement with `vector_search` to gather information before writing the memo.

        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """

        deal_memo = self.generate_text_with_llm(prompt)
        return {{"deal_memo": deal_memo}}
