
import json
import re
from .base_agent import ToolbeltAgent
from .deal_memo_agent import DealMemoAgent
from .risk_and_compliance_agent import RiskAndComplianceAgent
from .benchmarking_agent import BenchmarkingAgent
from .market_research_agent import MarketResearchAgent
from .portfolio_fit_agent import PortfolioFitAgent
from .digital_footprint_analysis_agent import DigitalFootprintAnalysisAgent
from .communication_agent import CommunicationAgent
from .user_preferences_agent import UserPreferencesAgent
from app.services.conversation_manager import get_conversation_history, save_conversation_history
from app.services.google_services import realtime_db

class AIStartupAnalysisAgent(ToolbeltAgent):
    """Orchestrates a team of AI agents to perform a comprehensive analysis of a startup."""
    def __init__(self):
        super().__init__("AI Startup Analysis Agent")
        self.agent_team = {
            "deal_memo": DealMemoAgent(),
            "risk_and_compliance": RiskAndComplianceAgent(),
            "benchmarking": BenchmarkingAgent(),
            "market_research": MarketResearchAgent(),
            "portfolio_fit": PortfolioFitAgent(),
            "digital_footprint": DigitalFootprintAnalysisAgent(),
            "communication": CommunicationAgent(),
            "user_preferences": UserPreferencesAgent(),
        }

    def _get_startup_data(self, deal_id):
        """
        Retrieves startup data from Firebase, including deal, startup, and key metrics.
        """
        print(f"--- Fetching data for deal_id: {deal_id} from Firebase ---")

        # 1. Query for deal information
        deal_info_dict = realtime_db.query('deals', 'id', deal_id)
        if not deal_info_dict:
            print(f"--- No deal info found for deal_id: {deal_id} ---")
            return { "name": "Unknown Startup" }
        deal_info = next(iter(deal_info_dict.values()), {})
        print(f"--- Deal Info: {deal_info} ---")

        # 2. Get startupId from deal and query for startup details
        startup_id = deal_info.get('startupId')
        if startup_id:
            startup_info_dict = realtime_db.query('startups', 'id', startup_id)
            if startup_info_dict:
                startup_info = next(iter(startup_info_dict.values()), {})
                print(f"--- Startup Info: {startup_info} ---")
                # Map 'company' to 'name' for consistency with other agents.
                if 'company' in startup_info:
                    startup_info['name'] = startup_info['company']
                if 'companyDetails' in startup_info:
                    print(f"--- Company Details: {startup_info['companyDetails']} ---")
                deal_info.update( startup_info)

        # 3. Query for key metrics
        key_metrics_dict = realtime_db.query('keyMetrics', 'dealId', deal_id)
        if key_metrics_dict:
            key_metrics = next(iter(key_metrics_dict.values()), {})
            print(f"--- Key Metrics: {key_metrics} ---")
            deal_info.update(key_metrics)
            
        return deal_info

    def _run_all_agents_and_synthesize(self, startup_data):
        """
        Runs all agents and synthesizes their findings into a final report.
        """
        analysis_results = {}
        for agent_name, agent_instance in self.agent_team.items():
            print(f"--- Running {agent_instance.agent_name} ---")
            result = agent_instance.run(startup_data)
            print(f"--- Result from {agent_instance.agent_name}: {result} ---")
            analysis_results.update(result)

        print("--- Synthesizing Final Report ---")
        final_summary_prompt = f'''
        You are a Chief Investment Officer reviewing the analysis from your team of specialist agents.
        Based on the following reports, generate a final, comprehensive summary and recommendation for the startup: {startup_data.get('company')}.
        
        **Team's Analysis:**
        {json.dumps(analysis_results, indent=2)}

        **Final Report:**
        Provide a final summary that synthesizes these findings. Structure your report as follows:
        1. Overall Investment Recommendation.
        2. Key Strengths.
        3. Key Weaknesses & Risks.
        4. Final Verdict.
        
        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        '''
        final_summary = self.generate_text_with_llm(final_summary_prompt)
        analysis_results['final_summary'] = final_summary
        return analysis_results

    def _intelligent_route_query(self, query, history, startup_data):
        """Determines the best course of action using an LLM."""
        print("--- Using LLM to route query... ---")

        formatted_history = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in history])
        available_agents = list(self.agent_team.keys())

        # Check if the last interaction was an email confirmation prompt
        if history and "I have drafted the following email" in history[-1].get('ai', ''):
            if query.lower() in ['yes', 'y', 'confirm', 'send it']:
                return "execute_email"
            else:
                # If the user provides changes, treat it as a new email request
                return "send_email" 

        prompt = f'''
        You are an intelligent routing agent. Your job is to determine the best course of action based on a user's query.

        Here are the available options:
        1.  **direct_answer**: If the query can be answered directly from the provided 'Startup Data', especially from the 'companyDetails'.
        2.  **chat**: If the query is a follow-up or conversational in nature.
        3.  **run_specific_agent**: If the query maps to one of the specialist agents.
        4.  **run_all_agents**: For broad, comprehensive analysis queries.
        5.  **send_email**: If the user wants to send an email.
        6.  **save_deal_note_preferences**: If the user wants to make changes to the deal notes.

        **User Query:** "{query}"

        **Conversation History:**
        {formatted_history}

        **Available Specialist Agents:** {available_agents}

        **Startup Data (for context):**
        ```json
        {json.dumps(startup_data, indent=2)}
        ```

        **Decision Logic:**
        - If the user's query is about changing or saving preferences for deal notes, choose `save_deal_note_preferences`.
        - If the query is specific and the answer is likely within the 'Startup Data' (e.g., asking for ARR, company name, or details from the document summaries), choose `direct_answer`.
        - If the user is asking a follow-up question, choose `chat`.
        - If the user asks to send an email or implies a need to get information *from* the founder (e.g., 'need more info from founder', 'ask the founder about...'), choose `send_email`.
        - If the query clearly aligns with a specialist agent (e.g., "analyze competitors" -> "benchmarking"), return `run_specific_agent:<agent_name>`.
        - If the query is general (e.g., "give me a full analysis"), choose `run_all_agents`.

        **Return only the chosen action as a single string.** For example: `direct_answer`, `chat`, `run_specific_agent:deal_memo`, `run_all_agents`, `send_email`, `save_deal_note_preferences`.
        '''
        
        decision = self.generate_text_with_llm(prompt).strip()
        print(f"--- LLM Router Decision: {decision} ---")
        return decision

    def _run_direct_answer(self, query, startup_data):
        """Generates a direct answer from the startup data."""
        print("--- Generating direct answer... ---")
        prompt = f'''
        You are an expert investment analyst. Answer the user's query directly using the provided data, paying special attention to the `companyDetails` field which contains summaries of internal documents.
        
        **User Query:** "{query}"

        **Startup Data:**
        {json.dumps(startup_data, indent=2)}

        **Your Answer:**
        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        '''
        return self.generate_text_with_llm(prompt)

    def _run_chat(self, query, history, startup_data):
        """Handles a conversational turn."""
        print("--- Handling follow-up query... ---")
        formatted_history = "\n".join([f"User: {h['user']}\nAI: {h['ai']}" for h in history])
        prompt = f"""You are an investment analyst continuing a conversation about the startup '{startup_data.get('name')}'.
        
        **Previous Conversation:**
        {formatted_history}
        **Startup Context (including internal document summaries):**
        {json.dumps(startup_data, indent=2)}
        **User's New Query:** "{query}"
        Please provide a direct answer to the user's new query based on the context and history.
        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """
        response = self.generate_text_with_llm(prompt)
        return {{ "chat_response": response }}

    def _format_single_agent_response(self, agent_name, agent_result, startup_name):
        """
        Formats the JSON output of a single agent into a natural, user-friendly response.
        """
        print(f"--- Formatting response from {agent_name} ---")
        if not agent_result or not isinstance(agent_result, dict):
             return "The agent did not provide a valid response."
        result_key = list(agent_result.keys())[0]
        result_content = agent_result[result_key]
        prompt = f"""You are an expert investment analyst. Your specialist agent, the '{agent_name}', has just completed its analysis for the startup '{startup_name}'.
        The agent provided the following data:
        **Agent's Data:**
        ```json
        {result_content}
        ```
        Your task is to present this information to the user in a clear, natural, and easy-to-read narrative.
        Synthesize it into a coherent summary as if you were presenting the findings.
        Do NOT include inline citations. Instead, list all sources in a separate "References" section at the end of your response. 
        The references should be formatted in italics and include the document name and page number.
        """
        return self.generate_text_with_llm(prompt)

    def _compose_and_confirm_email(self, query, startup_data):
        """
        Composes a well-formatted email and asks the user for confirmation before sending.
        """
        print("--- Composing email draft... ---")
        investor_name = startup_data.get('investor_name', 'a potential investor')
        recipient_email = startup_data.get('email')

        # If there's no email in the startup data, ask the user for it.
        if not recipient_email:
            return "I can help with that. Who should I address the email to? Please provide the recipient's email address."


        # Use an LLM to compose the email
        prompt = f'''
        You are an intelligent assistant that composes a polite and professional email to a startup founder.

        **Startup Data (including internal document summaries):**
        ```json
        {json.dumps(startup_data, indent=2)}
        ```

        **Instructions:**
        1.  The user wants to send an email based on the following query: "{query}"
        2.  The email should be addressed to the founder of the startup, using the company name from the 'Startup Data' provided above.
        3.  The email must mention that the request is on behalf of '{investor_name}'.
        4.  The email must clearly instruct the founder to upload any requested documents to the "LVX platform".
        5.  The tone should be professional, polite, and encouraging.
        6.  Use the startup's actual name in the subject and body of the email.
        7.  Extract a suitable subject line, and the email body from the user's query and the instructions. The recipient is already known.
        
        **Return the details in a JSON format with the following keys:**
        - "subject"
        - "body"

        **Example Query:** "Send an email to founder@example.com to request their pitch deck."

        **Example JSON Output:**
        {{
            "subject": "Request for Pitch Deck for [Startup Name] from {investor_name}",
            "body": "Dear Founder of [Startup Name],\\n\\nMy name is {investor_name}, and I am a potential investor who is very interested in learning more about your startup. To proceed with our evaluation, could you please upload your pitch deck to the LVX platform at your earliest convenience?\\n\\nThank you for your time and cooperation.\\n\\nBest regards,\\n{investor_name}"
        }}
        '''
        
        email_details_str = self.generate_text_with_llm(prompt)
        
        try:
            # Use regex to find the JSON object within the response string
            json_match = re.search(r'\{.*\}', email_details_str, re.DOTALL)
            if not json_match:
                raise json.JSONDecodeError("No JSON object found in the response.", email_details_str, 0)
            
            email_details = json.loads(json_match.group(0))
            subject = email_details.get("subject")
            body = email_details.get("body")

            if not all([subject, body]):
                return "I'm sorry, I couldn't generate a complete email draft. Please try again with more specific details."

            # Format the confirmation message for the user
            confirmation_message = f"""
            I have drafted the following email for you:

            **To:** {recipient_email}
            **Subject:** {subject}
            **Body:**
            {body}

            Do you approve of sending this email? Please respond with 'yes' to send, or provide any changes you'd like to make.
            """
            return confirmation_message

        except json.JSONDecodeError:
            return "I'm sorry, I had trouble drafting the email. Please try rephrasing your request."

    def _execute_email(self, history):
        """
        Executes the sending of an email after user confirmation.
        """
        print("--- Executing email send... ---")
        # Extract the email details from the last AI response in the history
        last_ai_response = history[-2].get('ai', '') # The confirmation message

        try:
            lines = [line.strip() for line in last_ai_response.split('\n')]
            to_line = [line for line in lines if line.startswith('**To:**')][0]
            subject_line = [line for line in lines if line.startswith('**Subject:**')][0]
            
            body_start_index = last_ai_response.find('**Body:**') + len('**Body:**')
            body_end_index = last_ai_response.find("Do you approve")

            recipient = to_line.split('**To:**')[1].strip()
            subject = subject_line.split('**Subject:**')[1].strip()
            body = last_ai_response[body_start_index:body_end_index].strip()

            # Format body for HTML
            body_html = body.replace("\n", "<br>")

            communication_agent = self.agent_team["communication"]
            # The communication agent now returns a JSON string, so we need to parse it.
            response_str = communication_agent.run(recipient, subject, body_html)
            response_json = json.loads(response_str)
            return response_json.get("message", "Email sending status unknown.")

        except (IndexError, AttributeError, json.JSONDecodeError) as e:
            print(f"--- Error parsing email from history or sending email: {e} ---")
            return "I'm sorry, I couldn't retrieve the email details to send. Please try the request again."

    def run(self, deal_id, query, conversation_id=None):
        """
        Orchestrates the analysis based on the user's query and conversation history.
        """
        print(f"--- STARTING ANALYSIS FOR DEAL ID: {deal_id} (Conv ID: {conversation_id}) ---")
        history = get_conversation_history(conversation_id)
        startup_data = self._get_startup_data(deal_id)
        
        if startup_data.get("name") == "Unknown Startup":
            return { "error": f"No data found for deal ID: {deal_id}" }

        action = None
        # Check if the last AI response was a request for an email address.
        if (history and 
            history[-1].get("ai") == "I can help with that. Who should I address the email to? Please provide the recipient's email address."):
            
            # The new query is the email address. Let's validate it simply.
            new_email = query.strip()
            if "@" in new_email and "." in new_email: # Simple email validation
                print(f"--- Email address provided: {new_email}. Proceeding with email composition. ---")
                # The original query is the one before the AI asked for the email
                original_query = history[-1].get("user")
                
                # Update startup_data with the new email.
                startup_data['email'] = new_email
                
                # Set the action directly to send_email and use the original query
                action = "send_email"
                query = original_query 
            
        if not action:
            # If the special email handling case wasn't met, run the normal router.
            startup_data['query'] = query
            action = self._intelligent_route_query(query, history, startup_data)

        print(f"--- Action from router: {action} ---")

        analysis_results = {}
        ai_response_for_history = ""

        if action == "direct_answer":
            direct_answer = self._run_direct_answer(query, startup_data)
            analysis_results = { "response": direct_answer }
            ai_response_for_history = direct_answer
        elif action == "chat":
            chat_response = self._run_chat(query, history, startup_data)
            analysis_results = { "response": chat_response.get('chat_response') }
            ai_response_for_history = chat_response.get('chat_response')
        elif action.startswith("run_specific_agent:"):
            agent_name = action.split(":")[1]
            agent_instance = self.agent_team.get(agent_name)
            if agent_instance:
                print(f"--- Running specific agent: {agent_instance.agent_name} ---")
                raw_agent_result = agent_instance.run(startup_data)
                print(f"--- Raw agent result: {raw_agent_result} ---")
                formatted_response = self._format_single_agent_response(
                    agent_name=agent_instance.agent_name,
                    agent_result=raw_agent_result,
                    startup_name=startup_data.get('name')
                )
                analysis_results = { "response": formatted_response }
                ai_response_for_history = formatted_response
            else:
                print(f"--- WARNING: Router returned unknown agent '{agent_name}'. ---")
                action = "run_all_agents"
        
        if action == "run_all_agents":
            print("--- Running comprehensive analysis... ---")
            full_analysis_dict = self._run_all_agents_and_synthesize(startup_data)
            final_summary = full_analysis_dict.get('final_summary', "Analysis failed to generate a summary.")
            analysis_results = { "response": final_summary }
            ai_response_for_history = final_summary
            
        elif action == "send_email":
            email_response = self._compose_and_confirm_email(query, startup_data)
            analysis_results = { "response": email_response }
            ai_response_for_history = email_response

        elif action == "execute_email":
            # The history already includes the user's 'yes' and the prior AI prompt
            email_result = self._execute_email(history + [{"user": query, "ai": ""}])
            analysis_results = { "response": email_result }
            ai_response_for_history = email_result
        elif action == "save_deal_note_preferences":
            user_preferences_agent = self.agent_team["user_preferences"]
            response = user_preferences_agent.run(query)
            analysis_results = { "response": response.get('status') }
            ai_response_for_history = response.get('status')

        # Save the state before the final response is formulated
        if action != "execute_email":
            history.append({"user": query, "ai": ai_response_for_history})
        else: # for execute_email we need to update the last placeholder
            history[-1]["ai"] = ai_response_for_history
            
        new_conversation_id = save_conversation_history(conversation_id, history)

        print(f"--- ANALYSIS COMPLETE FOR DEAL ID: {deal_id} (Conv ID: {new_conversation_id}) ---")
        return {
            "conversation_id": new_conversation_id,
            "analysis": analysis_results
        }
