import json
from .base_agent import ToolbeltAgent

class DigitalFootprintAnalysisAgent(ToolbeltAgent):
    """Analyzes a startup's digital footprint, including its founders' presence."""
    def __init__(self):
        super().__init__(
            agent_name="Digital Footprint Analysis Agent",
            tools=[]
        )

    def run(self, startup_data):
        """
        Analyzes the startup's and its founders' digital presence.
        """
        founders = startup_data.get('Founders', [])
        founder_names = ", ".join(founders) if founders else "No founders listed"

        prompt = f"""
        You are a digital marketing and branding analyst with built-in web search capabilities. Your task is to conduct a thorough analysis of a startup's digital footprint, including the online presence of its founders.

        **Instructions:**
        1.  **Analyze the Startup's Digital Presence:**
            - Review the internal document summaries to understand the company's intended image.
            - Use your web search capabilities to find the startup's website, social media profiles, and any news or articles.
            - Analyze the external messaging. Does it align with the internal documents? Is it consistent?

        2.  **Analyze the Founders' Digital Presence:**
            - The founders are: **{founder_names}**.
            - Use your web search capabilities to search for each founder on professional networks (like LinkedIn) and social media (like Twitter/X).
            - Analyze their professional background, thought leadership, and public statements.
            - Is their online persona consistent with the startup's brand and goals?

        3.  **Synthesize and Report:**
            - Combine your findings into a single, comprehensive report.
            - Highlight strengths, weaknesses, and any inconsistencies between the company's intended image and its actual online presence (including its founders').

        **Startup Information:**
        - **Name:** {startup_data.get('company')}
        - **Industry/Sector:** {startup_data.get('sector')}
        - **Founders:** {founder_names}

        **Internal Document Summaries:**
        ```json
        {json.dumps(startup_data.get('companyDetails', 'No document summaries available.'), indent=2)}
        ```

        **Report Structure:**
        1.  **Overall Digital Presence Summary:** A high-level overview of the startup's and founders' digital footprint.
        2.  **Startup Digital Channel Analysis:** Evaluation of the company's website, social media, and other online channels.
        3.  **Founder Presence Analysis:** An individual analysis of each founder's digital presence and its impact on the company brand.
        4.  **Brand Alignment Analysis:** A critical assessment of the consistency and alignment between the startup's internal goals and its external-facing brand, including the founders' personas.
        5.  **Recommendations:** Actionable advice for improving the startup's digital footprint.

        Begin your analysis. Use your internal web search capabilities to gather external data on both the company and its founders.

        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """

        report = self.generate_text_with_llm(prompt)
        return {{"digital_footprint_analysis": report}}
