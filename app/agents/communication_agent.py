import os
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from app.agents.base_agent import ToolbeltAgent

class CommunicationAgent(ToolbeltAgent):
    def __init__(self):
        super().__init__(agent_name="Communication Agent")
        # In the future, we can add tools for other communication channels like SMS, Slack, etc.
        self.tools = []

    def run(self, recipient, subject, body):
        """
        Sends an email to the specified recipient using SendGrid if the API key is available,
        otherwise, it mocks the email by printing it to the console.
        """
        sendgrid_api_key = os.environ.get("SENDGRID_API_KEY")
        email_draft = {
            "recipient": recipient,
            "subject": subject,
            "body": body
        }

        if sendgrid_api_key:
            # Use SendGrid to send the email
            print(f"--- Sending email to {recipient} via SendGrid ---")
            sender_email = os.environ.get("SENDER_EMAIL")
            if not sender_email:
                return json.dumps({"status": "error", "message": "SENDER_EMAIL environment variable not set for SendGrid."})

            message = Mail(
                from_email=sender_email,
                to_emails=recipient,
                subject=subject,
                html_content=body
            )

            try:
                sg = SendGridAPIClient(sendgrid_api_key)
                response = sg.send(message)
                print(f"--- Email sent with status code: {response.status_code} ---")
                return json.dumps({"status": "success", "message": "The email has been sent successfully. I will monitor for a reply and let you know when a response is received with any updated documents or information.", "email_draft": email_draft})
            except Exception as e:
                print(f"--- Error sending email via SendGrid: {e} ---")
                return json.dumps({"status": "error", "message": f"Error sending email via SendGrid: {e}"})
        else:
            # Mock the email by printing to the console
            print("--- MOCKING EMAIL (SENDGRID_API_KEY not found) ---")
            email_content = (
                "--------------------------------------------------\n"
                f"TO: {recipient}\n"
f"SUBJECT: {subject}\n"
                "--------------------------------------------------\n"
                f"BODY:\n{body}\n"
                "--------------------------------------------------"
            )
            print(email_content)
            return json.dumps({"status": "success", "message": "An email draft has been generated and printed to the console because no email provider is configured. Once an email provider is set up, I will send the email and notify you when a response is received with any updated documents or information.", "email_draft": email_draft})
