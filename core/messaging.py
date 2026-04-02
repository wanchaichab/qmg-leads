import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
twilio_test_phone_number = os.environ.get('TWILIO_TEST_PHONE_NUMBER')

client = Client(account_sid, auth_token)

def send_initial_message(lead):
    message = client.api.account.messages.create(
        to=twilio_test_phone_number,
        from_=twilio_phone_number,
        body=f"Hi {lead.phone_number}, this is QMG. Just wanted to follow up.")

