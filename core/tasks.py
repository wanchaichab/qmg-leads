import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from core.messaging import sendInitialMessage

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SECRET")
supabase = create_client(url, key)

def process_current_batch(batch_id):
    response = (supabase.table("leads")
        .select("*")
        .eq("batch_id", batch_id)
        .limit(2) # Only process 5 leads at a time for testing
        .execute()
    )
    df = pd.DataFrame(response.data)
    print(f"Processing batch {batch_id} with {len(df)} records.")
    # Check if there are any pending leads
    if not df.empty:
        pending_leads = df[df['status'] == 'pending']
        print(f"Found {len(pending_leads)} pending leads.")
        for lead in pending_leads.itertuples():
            sendInitialMessage(lead)
            #update_lead_status(lead.lead_id, "contacted")
            print(f"Sent message to {lead.phone_number} and updated status of {lead.lead_id} to contacted.")