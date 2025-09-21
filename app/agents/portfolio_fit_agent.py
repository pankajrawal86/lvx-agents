import json
from .base_agent import ToolbeltAgent

class PortfolioFitAgent(ToolbeltAgent):
    """Analyzes how well a startup fits into an investment portfolio based on internal documents."""
    def __init__(self):
        super().__init__(
            agent_name="Portfolio Fit Agent",
            tools=[]
        )

    def run(self, startup_data):
        """
        Analyzes how well the startup aligns with a specific investment portfolio, based on its own documents.
        """
        prompt = f"""        You are a portfolio analyst for a venture capital firm.

        **Instructions:**
        1.  **Your analysis MUST be based solely on the provided information: our firm's stated investment focus and the startup's internal document summaries.**
        2.  Compare the startup's characteristics to our firm's investment thesis.
        3.  Do not use any external tools or data.

        **Our Portfolio Focus:**
        - **Industries:** FinTech, HealthTech, and B2B SaaS.
        - **Business Model:** Strong preference for B2B models.
        - **Stage:** Early-stage (Seed, Series A).

        **Startup Information:**
        - **Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Description:** {startup_data.get('description')}
        - **Stage:** {startup_data.get('stage')}

        **Internal Document Summaries (from the Startup):**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        **Report Structure:**
        1.  **Industry Fit**: Does the startup's self-reported sector align with our target industries?
        2.  **Business Model Fit**: Based on the documents, does the startup have a B2B model?
        3.  **Synergy with Portfolio**: Based on the description, are there any obvious synergies or conflicts with a portfolio focused on FinTech, HealthTech, and B2B SaaS?
        4.  **Risk Alignment**: Does the startup's risk profile, as suggested by its own documents, seem appropriate for an early-stage investor?
        5.  **Exit Potential**: Do the internal documents suggest a particular exit strategy that aligns with our goals?

        Begin your analysis. Use only the provided information to write your report.

        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """

        report = self.generate_text_with_llm(prompt)
        return { "portfolio_fit_analysis": report }
