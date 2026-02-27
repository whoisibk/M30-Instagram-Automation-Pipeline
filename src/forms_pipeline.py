import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path


import gspread
from google.oauth2.service_account import Credentials

from src.images import handle_user_images

load_dotenv()

# gets credentials from the json file and authorizes the client to interact with Google Sheets API using those credentials.
scopes = [
    "https://www.googleapis.com/auth/spreadsheets"
]
creds = Credentials.from_service_account_file("utils\\credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = os.getenv("SHEET_ID")
STATE_PATH = "utils\\state.json"

workbook = client.open_by_key(sheet_id)



def forms_pipeline():
    """Main pipeline function that fetches new form responses, processes user images, and updates the last processed timestamp."""
    last_timestamp = get_last_timestamp()
    all_rows = fetch_rows()

    headers = all_rows[0]
    data_rows = all_rows[1:]

    newest_ts_seen = last_timestamp

    # loop over responses made by users and parses into dict
    for row in data_rows:
        row_dict = dict(zip(headers, row))

        row_timestamp = datetime.strptime(row_dict["Timestamp"], "%d/%m/%Y %H:%M:%S")

        if last_timestamp and row_timestamp <= last_timestamp:
            continue

        # FUNCTION FOR THE ACTUAL WORK WILL BE INVOKED HERE!
        handle_user_images(row_dict)

        if not newest_ts_seen or row_timestamp > newest_ts_seen:
            newest_ts_seen = row_timestamp

    if newest_ts_seen:
        save_last_timestamp(newest_ts_seen)


# values_list = workbook.sheet1.get_all_values() # gets the first response from Sheet1 in a list
#
# sheet = workbook.worksheet("Form responses 1") # gets the worksheet by its name
# value =  sheet.acell("B2").value # gets value inputted in cell B2
#
# print(values_list)


def fetch_rows():
    all_rows = workbook.sheet1.get_all_values()
    return all_rows

def get_last_timestamp():
    if not Path(STATE_PATH).exists():
        return None

    with open(STATE_PATH, "r") as f:
        return datetime.fromisoformat(json.load(f)["last_timestamp"])


def save_last_timestamp(ts: datetime):
    with open(STATE_PATH, "w") as f:
        json.dump({"last_timestamp": ts.isoformat()}, f)



if __name__ == "__main__":
    forms_pipeline()
