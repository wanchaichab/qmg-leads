import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SECRET")
supabase = create_client(url, key)

raw_file_path = "data/raw"


batch_size = 50

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

def process_data(df):
    current_batch = 1
    count = 0
    # Add columns
    df['status'] = "pending"
    df['updated_at'] = pd.Timestamp.now()
    # Convert types
    df["lead_date"] = df["lead_date"].astype(str)
    df['updated_at'] = df['updated_at'].dt.strftime("%Y-%m-%d %H:%M:%S")
    # Drop columns and duplicates
    df.drop(columns=['call_duration', 'Unnamed: 0'], inplace=True)
    df = df.drop_duplicates(subset=["phone_number"])
    # Add batch number
    for index, row in df.iterrows():
        if count >= batch_size:
            current_batch += 1
            count = 0
        df.at[index, 'batch_id'] = current_batch
        count += 1
    return df

def insert_data(df):
    data = df.to_dict(orient="records")
    supabase.table("leads").insert(data).execute()
    print(f"Inserted {len(data)} records into the database.")

def move_file(file_path, destination_folder):
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    file_name = os.path.basename(file_path)
    destination_path = os.path.join(destination_folder, file_name)
    os.rename(file_path, destination_path)
    print(f"Moved {file_name} to {destination_path}")

def update_lead_status(lead_id, new_status):
    result = (supabase.table("leads")
     .update({"status": new_status, "updated_at": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")})
     .eq("id", lead_id)
     .execute()
    )
    
    return result.data

def logMessageToDB(from_number, direction, message_body, message_id, fk_lead_id):
    data = {
        "phone_number": from_number,
        "direction": direction,
        "content": message_body,
        "message_id": message_id,
        "created_at" : pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d %H:%M:%S %Z",),
        "lead_id": fk_lead_id

    }
    supabase.table("messages").insert(data).execute()
    if direction == "inbound":
        print(f"Logged message from {from_number} to the database.")
    else:
        print(f"Logged message to {from_number} to the database.")

def getLeadIdByPhoneNumber(phone_number):
    response = (supabase.table("leads")
        .select("lead_id")
        .eq("phone_number", phone_number)
        .execute()
    )
    if response.data:
        return response.data[0]["lead_id"]
    else:
        return None

def getLeadStatus(lead_id):
    response = (supabase.table("leads")
        .select("status")
        .eq("lead_id", lead_id)
        .execute()
    )
    if response.data:
        return response.data[0]["status"]
    else:
        return None
    
def getRecentMessages(lead_id, limit=3):
    response = (supabase.table("messages")
        .select("direction, content, created_at")
        .eq("lead_id", lead_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    if response.data:
        rows = response.data
        rows = list(reversed(rows))

        messages = []
        for row in rows:
            role = "user" if row["direction"] == "inbound" else "assistant"
            messages.append({
                "role": role,
                "content": row["content"]
            })
        return messages
    else:
        return []

for file in os.listdir(raw_file_path):
    if file.endswith(".csv"):
        file_path = os.path.join(raw_file_path, file)
        df = pd.read_csv(file_path)
        df_pr = process_data(df)
        print(df_pr.head())
        insert_data(df_pr)
        move_file(file_path, "data/processed")

        
