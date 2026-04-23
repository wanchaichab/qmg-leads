import os
from twilio.rest import Client
from dotenv import load_dotenv
from celery import Celery
from core.data_processing import logMessageToDB, getLeadIdByPhoneNumber, getLeadStatus, update_lead_status, getRecentMessages
from twilio.twiml.messaging_response import MessagingResponse
from fastapi import Response
from openai import OpenAI
import json

load_dotenv()

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
twilio_toll_free_number = os.environ.get('TWILIO_TOLL_FREE_NUMBER')
twilio_test_phone_number = os.environ.get('TWILIO_TEST_PHONE_NUMBER')
openai_api_key = os.environ.get("OPENAI_API_KEY")
openai_prompt_id = os.environ.get("OPENAI_PROMPT_ID")

client = Client(account_sid, auth_token)

openai_client = OpenAI()

def sendInitialMessage(lead):
    message = client.api.account.messages.create(
        to=twilio_test_phone_number,
        from_=twilio_toll_free_number,
        body=f"Hi {lead.phone_number}, this is QMG toll free. Test #2")
    
    logMessageToDB(lead.phone_number, "outbound", message.body, message.sid, lead.lead_id)

    #update_lead_status(lead.lead_id, "message sent")

def generateResponseMessage(recent_messages: list[dict]):
    # Qualify lead based on recent messages and create response
    response = openai_client.responses.create(
        model="gpt-5-mini",
        prompt={
            "id": openai_prompt_id,
            "version": "2",
        },
        input=recent_messages,
        text={
            "format": {
                "type": "json_schema",
                "name": "lead_reply_and_status",
                "schema": {
                    "type": "object",
                        "properties": {
                            "reply_message": {"type": "string"},
                            "new_status": {
                                "type": "string",
                                "enum": [
                                    "qualified", 
                                    "transfer_ready",
                                    "uninterested",
                                    "needs_follow_up",
                                    "wrong_number",
                                    "opt_out"
                                ]
                            },
                        },
                    "required": ["reply_message", "new_status"],
                    "additionalProperties": False
                }
            }
        }
    )

    data = json.loads(response.output_text)

    return data["reply_message"], data["new_status"]

def handleInbound(params: dict):
    from_number = params.get("From").replace("+1", "")
    message_body = params.get("Body")
    message_id = params.get("MessageSid")

    twiml = MessagingResponse()

    print(f"Received message from {from_number}: {message_body}")

    # Retrieve lead ID from the database
    lead_id = getLeadIdByPhoneNumber(from_number)

    # Log the message to the database
    logMessageToDB(from_number, "inbound", message_body, message_id, lead_id)


    # Handle STOP messages
    stop_words = {"STOP", "CANCEL", "UNSUBSCRIBE", "END", "QUIT"}

    if message_body.strip().upper() in stop_words:
        print("STOP detected")
        if lead_id:
            #update_lead_status(lead_id, "opted out")
            print(f"Updated lead {lead_id} status to opted out.")
        else:
            print(f"No lead found for phone number {from_number}.")
    
    # Update lead status to contacted if it's currently pending
    if lead_id:
        current_status = getLeadStatus(lead_id)
        if current_status == "message sent" or current_status == "pending":
            #update_lead_status(lead_id, "responded")
            print(f"Updated lead {lead_id} status to responded.")
        else:
            print(f"Lead {lead_id} has status {current_status}, not updating to responded.")

    # Get recent lead messages for context
    recent_messages = getRecentMessages(lead_id, 3)

    reply_message, new_status = generateResponseMessage(recent_messages)
    print(f"Generated response message: {reply_message}, new status: {new_status}")
    #update_lead_status(lead_id, new_status)
    twiml.message(reply_message)
    logMessageToDB(from_number, "outbound", reply_message, message_id, lead_id)
    return twiml
    
    
