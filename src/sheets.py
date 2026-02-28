import os
from dotenv import load_dotenv
from datetime import datetime
import json
from pathlib import Path
import logging

import gspread
from google.oauth2.service_account import Credentials

from instagrapi import Client

from src.images import handle_user_images
from src.insta import post_album

load_dotenv()

logger = logging.getLogger()

# gets credentials from the json file and authorizes the client to interact with Google Sheets API using those credentials.
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("utils\\credentials.json", scopes=scopes)
google_client = gspread.authorize(creds)

sheet_id = os.getenv("SHEET_ID")
STATE_PATH = "utils\\state.json"

workbook = google_client.open_by_key(sheet_id)


def validate_timestamp(row_timestamp: datetime) -> bool:
    """
    Validates if a post timestamp has been seen before.

    Args:
        row_timestamp: The timestamp from the form response

    Returns:
        bool: True if timestamp is new (haven't posted yet), False if already posted
    """
    last_timestamp = get_last_timestamp()

    if not last_timestamp:
        return True  # No previous posts, timestamp is valid

    if row_timestamp <= last_timestamp:
        logger.info(f"Skipping post - timestamp {row_timestamp} already processed")
        return False  # Already posted this timestamp

    return True  # New timestamp, valid to post


def process_form_row(row_dict: dict, client: Client) -> bool:
    """
    Processes a single form response row from Google Sheets.
    Parses fields, downloads/edits images, and posts to Instagram.

    Args:
        row_dict: Dictionary containing form fields for a user
        client: Instagram API client

    Returns:
        bool: True if post was successful, False otherwise
    """
    try:
        # Parse timestamp first for validation
        row_timestamp = datetime.strptime(row_dict["Timestamp"], "%d/%m/%Y %H:%M:%S")

        # Validate that we haven't posted this timestamp before
        if not validate_timestamp(row_timestamp):
            return False

        # Extract and parse user fields
        full_name = row_dict["Full_name"]
        first_name = full_name.split(" ")[0]
        username = row_dict.get("Instagram_username", "")
        location = row_dict["Country"]
        caption = row_dict.get("Caption", "")

        logger.info(f"Processing post for: {full_name} (@{username})")
        print(f"\n{'='*50}")
        print(f"Processing: {full_name}")
        print(f"Username: @{username}")
        print(f"City: {location}")

        # Get edited images and return paths
        baby_edited_img, recent_edited_img = handle_user_images(row_dict)
        print(f"✓ Image editing successful")

        # Post to Instagram with location tag
        image_paths = [Path(baby_edited_img), Path(recent_edited_img)]

        if post_album(client, image_paths, caption, username, location):
            print(f"✓ {first_name}'s post created at {row_timestamp}")
            print(f"{'='*50}\n")

            # Save the timestamp as processed (only if post was successful)
            save_last_timestamp(row_timestamp)

            return True
        else:
            logger.error(f"Failed to post album for {full_name}")
            print(f"✗ Instagram posting failed")
            print(f"{'='*50}\n")
            return False

    except Exception as e:
        logger.error(
            f"Error processing row for {row_dict.get('Full_name', 'Unknown')}: {str(e)}"
        )
        print(f"✗ Error processing post: {str(e)}")
        return False


def fetch_rows():
    """Fetches all rows from the Google Sheet."""
    all_rows = workbook.sheet1.get_all_values()
    return all_rows


def get_last_timestamp():
    """Gets the last processed timestamp from state file."""
    if not Path(STATE_PATH).exists():
        return None

    with open(STATE_PATH, "r") as f:
        return datetime.fromisoformat(json.load(f)["last_timestamp"])


def save_last_timestamp(ts: datetime):
    """Saves the last processed timestamp to state file."""
    with open(STATE_PATH, "w") as f:
        json.dump({"last_timestamp": ts.isoformat()}, f)
