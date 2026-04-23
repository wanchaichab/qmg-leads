import os
from numpy import select
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv
from core.messaging import sendInitialMessage
from core.data_processing import update_lead_status, getRecentMessages

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_PUBLISHABLE_KEY")
supabase = create_client(url, key)

def get_current_batch_id():
    response = (supabase.table("system_config")
        .select("value")
        .eq("key", "current_batch")
        .execute()
    )
    if response.data:
        return response.data[0]["value"]
    else:
        return 0
    
    
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
    

if __name__ == "__main__":
    active_batch_id = get_current_batch_id()
    print(f"Current active batch ID: {active_batch_id}")
    process_current_batch(active_batch_id)