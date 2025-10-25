import json
from .base_agent import ToolbeltAgent

class BenchmarkingAgent(ToolbeltAgent):
    """Performs competitive benchmarking for a startup based on its internal documents."""
    def __init__(self):
        super().__init__(
            agent_name="Benchmarking Agent",
            tools=[]
        )

    def run(self, startup_data):
        """
        Analyzes the competitive landscape as described in the startup's internal documents.
        """

        prompt = f"""
        You are a market analyst specializing in competitive benchmarking.

        **Instructions:**
        1.  **You have been provided with summaries of key internal documents in the 'Internal Document Summaries' section below. Your analysis MUST be based solely on this information.**
        2.  Identify any competitors mentioned in the provided documents.
        3.  Analyze how the startup positions itself against these competitors based on the text.
        4.  After your review, create a benchmarking report that summarizes the startup's own view of its competition.
        5.  Make sure to include sources or references of the information formatted nicely with each data point picked from these documents. It should contain the document name and page number or numbers.

        **Startup Information:**
        - **Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Description:** {startup_data.get('description')}
        - **Funding Goal:** {startup_data.get('fundingGoal')}
        - **Raised:** {startup_data.get('raised')}

        **Internal Document Summaries:**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        **Report Structure:**
        1.  **Key Competitors Mentioned**: List the main competitors identified in the internal documents.
        2.  **Financial Benchmarking**: Based on the documents, compare the startup's funding situation to any mentioned competitors.
        3.  **Product Benchmarking**: Summarize how the startup's product is described in relation to its competitors' products, according to the documents.
        4.  **Team Benchmarking**: Does the documentation mention any competitive advantages related to the team?
        5.  **Overall Competitive Assessment**: Summarize the startup's competitive position as it is presented in its own internal documents.

        Begin your analysis. Use only the 'Internal Document Summaries' to write your report.
        """

        report = self.generate_text_with_llm(prompt)
        return {"benchmarking_analysis": report}
