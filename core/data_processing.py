import os
import pandas as pd
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

raw_file_path = "data/raw"


batch_size = 50

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

for file in os.listdir(raw_file_path):
    if file.endswith(".csv"):
        file_path = os.path.join(raw_file_path, file)
        df = pd.read_csv(file_path)
        df_pr = process_data(df)
        print(df_pr.head())
        insert_data(df_pr)
        move_file(file_path, "data/processed")

        
