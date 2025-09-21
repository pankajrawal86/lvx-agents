import json
from .base_agent import ToolbeltAgent

class RiskAndComplianceAgent(ToolbeltAgent):
    """Analyzes potential risks and compliance issues for a startup based on internal documents."""
    def __init__(self):
        super().__init__(
            agent_name="Risk and Compliance Agent",
            tools=[]
        )

    def run(self, startup_data):
        """
        Analyzes potential risks and compliance requirements for the given startup
        based on its internal document summaries.
        """
        prompt = f"""
        You are a specialist in risk and compliance for venture capital.

        **Instructions:**
        1.  **Your analysis MUST be based solely on the 'Internal Document Summaries' provided below.**
        2.  Focus your analysis on the following areas as described in the documents: Intellectual Property (IP), competition, financial stability, key-person dependencies, and regulatory hurdles.
        3.  Do not use any external tools or data.
        4.  After your review, compile a detailed report for an investment committee with a moderate risk tolerance.

        **Startup Information:**
        - **Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Description:** {startup_data.get('description')}
        - **Location:** {startup_data.get('location')}

        **Internal Document Summaries:**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        **Report Structure:**
        1.  **Intellectual Property (IP) Risks:** Are there any patent or trademark risks mentioned in the documents?
        2.  **Competitive Risks:** Who are the main competitors identified in the documents?
        3.  **Financial Risks:** Analyze burn rate, runway, and financial projections based only on the data in the summaries.
        4.  **Key-Person Dependencies:** Is the startup overly reliant on key individuals, based on the provided info?
        5.  **Regulatory & Compliance Risks**: What regulatory hurdles or compliance efforts are mentioned in the documents for the {startup_data.get('sector')} sector in {startup_data.get('location')}?

        Begin your analysis. Use only the 'Internal Document Summaries' to write your report.
        
        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """

        report = self.generate_text_with_llm(prompt)
        return {{"risk_and_compliance_analysis": report}}
