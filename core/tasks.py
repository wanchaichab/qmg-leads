import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from core.messaging import sendInitialMessage
from core.data_processing import update_lead_status, increment_batch_id, get_current_batch_id

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SECRET")
processing_batch_size = int(os.environ.get("PROCESSING_BATCH_SIZE", 50))
supabase = create_client(url, key)
max_leads = int(os.environ.get("MAX_LEADS"))

def process_current_batch():
    total_processed = 0
    batches = []

    while total_processed < max_leads:
        batch_id = get_current_batch_id()
        batches.append(batch_id)

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
            #print(f"Sent message to {lead['phone_number']} and updated status of {lead['lead_id']} to message_sent.")
        total_processed += len(leads)
        print(f"Processed #{len(leads)} leads in batch {batch_id}.")

        increment_batch_id()
    
    return (f"Processed {total_processed} leads across batches: {batches}")
