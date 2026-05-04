import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from core.messaging import sendInitialMessage
from core.data_processing import update_lead_status, increment_batch_id

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SECRET")
processing_batch_size = int(os.environ.get("PROCESSING_BATCH_SIZE", 50))
supabase = create_client(url, key)

def process_current_batch(batch_id):
    response = (supabase.table("leads")
        .select("*")
        .eq("batch_id", batch_id)
        .eq("status", "pending")
        .limit(processing_batch_size)
        .execute()
    )
    leads = response.data or []
    print(f"Processing batch {batch_id} with {len(leads)} records.")

    for lead in leads:
        sendInitialMessage(lead)
        update_lead_status(lead["lead_id"], "message_sent")
        print(f"Sent message to {lead['phone_number']} and updated status of {lead['lead_id']} to message_sent.")
    print(f"Processed #{len(leads)} leads in batch {batch_id}.")
    increment_batch_id()
