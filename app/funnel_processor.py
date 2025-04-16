import os
import csv
import sys
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from db import SessionLocal, init_db
from models import Room

load_dotenv()

QISCUS_BASE = os.getenv("QISCUS_BASE_URL")
APP_ID = os.getenv("QISCUS_APP_ID")
SECRET_KEY = os.getenv("QISCUS_SECRET_KEY")


url = "https://sdksample.qiscus.com/api/v2.1/rest/get_rooms_info?room_ids[]=1375619"
HEADERS = {
    "QISCUS-SDK-APP-ID": 'sdksample',
    "Content-Type": 'application/json',
    "QISCUS-SDK-SECRET": SECRET_KEY
}

response = requests.get(url, headers=HEADERS)
# print(response.status_code)
# print(response.json())


KEYWORDS_FILE = "keywords.csv"
OUTPUT_FILE = "funnel_output.csv"

def load_keywords():
    df = pd.read_csv(KEYWORDS_FILE)
    grouped = df.groupby("type")["keyword"].apply(list).to_dict()
    return grouped

def fetch_room_info(room_id):
    url = f"{QISCUS_BASE}/get_rooms_info?room_ids[]={room_id}"
    res = requests.get(url, headers=HEADERS).json()

    rooms_info = res.get("results", {}).get("rooms_info", [])
    if not rooms_info:
        raise ValueError(f"Room ID {room_id} not found or access denied.")

    room_data = rooms_info[0]
    return {
        "channel": room_data.get("channel_id", "unknown"),
        "phone": room_data.get("user_ids", ["unknown"])[0]
    }

def fetch_all_messages(room_id, limit=3):
    messages = []
    page = 1
    while page < 3:
        url = f"{QISCUS_BASE}/load_comments?room_id={room_id}&page={page}&limit={limit}"
        res = requests.get(url, headers=HEADERS).json()
        comments = res.get("results", {}).get("comments", [])
        if not comments:
            break
        messages.extend(comments)
        if len(comments) < limit:
            break
        page += 1
    return messages

def find_value_in_text(text):
    import re
    match = re.search(r'(?:Rp\s*)?([\d.,]{3,})', text)
    if match:
        val = match.group(1).replace('.', '').replace(',', '')
        return int(val)
    return None

def extract_funnel(room_id, keywords):
    meta = fetch_room_info(room_id)
    messages = fetch_all_messages(room_id)
    
    lead_date = booking_date = trx_date = None
    trx_value = None

    for msg in messages:
        text = msg["message"].lower()
        timestamp = datetime.fromtimestamp(msg["timestamp"] / 1000)

        if not lead_date and any(k in text for k in keywords.get("lead", [])):
            lead_date = timestamp
        if not booking_date and any(k in text for k in keywords.get("booking", [])):
            booking_date = timestamp
        if not trx_date and any(k in text for k in keywords.get("transaction", [])):
            trx_date = timestamp
            trx_value = find_value_in_text(text)

    if lead_date:
        return {
            "room_id": room_id,
            "leads_date": lead_date.date(),
            "channel": meta.get("channel"),
            "phone": meta.get("phone"),
            "booking_date": booking_date.date() if booking_date else None,
            "transaction_date": trx_date.date() if trx_date else None,
            "transaction_value": trx_value
        }
    return None

def main():
    print("🔍 Starting funnel processor from Qiscus API...")
    # init_db()
    db = SessionLocal()

    keywords = load_keywords()
    rooms = db.query(Room).all()

    results = []
    for room in rooms:
        try:
            funnel = extract_funnel(room.id, keywords)
            if funnel:
                results.append(funnel)
        except Exception as e:
            print(f"Error processing room {room.id}: {e}")

    if results:
        keys = results[0].keys()
        with open(OUTPUT_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)

    print(f"✅ Done. Extracted {len(results)} funnel rows.")
    db.close()

if __name__ == "__main__":
    room_ids = sys.argv[1:]  # get room IDs from command-line arguments

    if not room_ids:
        print("⚠️  Please provide at least one room_id")
        sys.exit(1)

    print(f"🔍 Starting funnel processor for rooms: {room_ids}")
    init_db()
    db = SessionLocal()
    keywords = load_keywords()

    results = []
    for room_id in room_ids:
        try:
            funnel = extract_funnel(room_id, keywords)
            if funnel:
                results.append(funnel)
        except Exception as e:
            print(f"❌ Error processing room {room_id}: {e}")
        # print(room_id)
        

    if results:
        keys = results[0].keys()
        with open(OUTPUT_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        

    print(f"✅ Done. Extracted {len(results)} funnel rows.")
    db.close()
    # print(fetch_all_messages(room_id, 3))
    # main()