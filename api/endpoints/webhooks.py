
from fastapi import FastAPI, Request, Response, HTTPException
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse
import os
from dotenv import load_dotenv
from core.messaging import handleInbound


load_dotenv()

app = FastAPI()
validator = RequestValidator(os.environ.get('TWILIO_AUTH_TOKEN'))
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL")

@app.post("/qmg/inbound")
async def inbound(request: Request):
    form_data = await request.form()
    
    params = dict(form_data)

    twiml = handleInbound(params)

    return Response(content=str(twiml), media_type="application/xml")