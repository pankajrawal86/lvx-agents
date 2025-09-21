import json
from .base_agent import ToolbeltAgent

class MarketResearchAgent(ToolbeltAgent):
    """Conducts market research for a startup using internal documents and web search."""
    def __init__(self):
        super().__init__(
            agent_name="Market Research Agent",
            tools=[]
        )

    def run(self, startup_data):
        """
        Conducts market research by combining the startup's internal document summaries
        with real-time external market data from the web.
        """
        prompt = f"""
        You are a market research analyst with built-in web search capabilities. Your task is to conduct a thorough market analysis for a startup, combining insights from its internal documents with real-time external market data.

        **Instructions:**
        1.  **Internal Data Review:**
            - You have been provided with summaries of key internal documents. Review these to understand the startup's own view of the market, its niche, and target customers.

        2.  **External Market Research:**
            - Use your web search capabilities to find the latest information on the startup's market: **{startup_data.get('sector')}**.
            - Research the current market size, growth rate, key trends, and overall industry outlook.
            - Identify the main competitors and analyze their strengths and weaknesses.
            - Investigate the target customer demographics and their behaviors.

        3.  **Synthesize and Report:**
            - Combine your findings from both internal and external sources into a single, comprehensive report.
            - Compare the startup's internal perceptions with the external reality. Highlight any gaps or misalignments.
            - Provide a clear and data-driven assessment of the market opportunity.

        **Startup Information:**
        - **Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Description:** {startup_data.get('description')}

        **Internal Document Summaries:**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        **Report Structure:**
        1.  **Executive Summary:** A high-level overview of the market and the startup's position within it.
        2.  **Market Overview:** Analysis of the market size, growth projections (including TAM, SAM, SOM if possible), and key trends based on both internal and external data.
        3.  **Competitive Landscape:** Identification and analysis of key competitors, their market share, and strategies.
        4.  **Target Audience Analysis:** A detailed profile of the target customers, their needs, and behaviors.
        5.  **Market Opportunity & Risks:** An assessment of the startup's opportunity, including potential risks and barriers to entry.
        6.  **Strategic Recommendations:** Actionable advice on how the startup can best position itself to succeed in the current market.

        Begin your analysis. Use your internal web search capabilities to gather external data and combine it with the provided internal summaries.

        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """

        report = self.generate_text_with_llm(prompt)
        return {{"market_research_analysis": report}}
