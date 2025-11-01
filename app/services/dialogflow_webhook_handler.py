import json
from app.agents.communication_agent import CommunicationAgent

def handle_webhook_request(data):
    """
    Processes a webhook request from Dialogflow CX.

    This function's role is to execute business logic and return a response
    for Dialogflow CX to deliver to the user. It does NOT directly send
    the message to the end channel (e.g., SMS, Voice). Dialogflow's own
    integrations handle the final delivery.

    Args:
        data (dict): The parsed JSON data from the Dialogflow CX request.

    Returns:
        dict: A response dictionary formatted for Dialogflow CX.
    """
    intent_name = data.get('fulfillmentInfo', {}).get('tag')
    params = data.get('sessionInfo', {}).get('parameters', {})
    response_text = "I'm sorry, I didn't understand that. Can you please rephrase?"

    if intent_name == 'send_communication_intent':
        channel = params.get('preferred_channel')

        if not channel:
            response_text = "Please specify a communication channel so I can format my response correctly."

        elif channel.lower() == 'email':
            recipient = params.get('recipient')
            subject = params.get('subject')
            body = params.get('body')
            if not all([recipient, subject, body]):
                response_text = "To compose an email, I need a recipient, a subject, and a body."
            else:
                # Integration with the actual CommunicationAgent
                print(f"--- Calling CommunicationAgent for email to {recipient} ---")
                agent = CommunicationAgent()
                agent_response_json = agent.run(recipient=recipient, subject=subject, body=body)
                agent_response = json.loads(agent_response_json)
                response_text = agent_response.get("message", "An error occurred while sending the email.")

        elif channel.lower() in ['voice', 'sms']:
            phone_number = params.get('phone_number')
            message = params.get('message')
            if not all([phone_number, message]):
                response_text = f"For a {channel} message, I need a phone number and a message."
            else:
                response_text = f"Understood. Preparing the following message for {phone_number}: {message}"

        elif channel.lower() == 'webex':
            message = params.get('message')
            if not message:
                response_text = "I need a message to send to the Webex space."
            else:
                response_text = f"Got it. I will post the following to Webex: \"{message}\"."

        else:
            response_text = f"I can customize content for 'email', 'voice', 'sms', or 'Webex', but '{channel}' is not a channel I'm configured to format for."

    response = {
        "fulfillment_response": {
            "messages": [
                {
                    "text": {
                        "text": [response_text]
                    }
                }
            ]
        }
    }
    return response
