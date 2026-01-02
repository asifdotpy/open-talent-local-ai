#!/usr/bin/env python3
"""
Script to check Trello board for AWS instance sync task and update it
"""

import os

import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load Trello credentials from environment variables (now stored as GitHub organization secrets)
TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
TRELLO_TOKEN = os.environ.get("TRELLO_API_TOKEN")
TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID")

if not all([TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
    raise ValueError("Trello API credentials not found in environment variables.")

BASE_URL = "https://api.trello.com/1"
AUTH_PARAMS = f"?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"


def get_all_cards():
    """Fetches all cards from the Trello board"""
    url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/cards{AUTH_PARAMS}"

    try:
        response = requests.get(url)
        response.raise_for_status()
        cards = response.json()

        print(f"🔍 Found {len(cards)} cards on the Trello board.")
        return cards

    except requests.exceptions.RequestException as e:
        print(f"❌ Error searching tasks: {e}")
        return []


def get_list_names_map():
    """Fetches all lists on the board and returns a dictionary mapping list IDs to names."""
    lists_url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/lists{AUTH_PARAMS}"
    try:
        response = requests.get(lists_url)
        response.raise_for_status()
        lists = response.json()
        return {lst["id"]: lst["name"] for lst in lists}
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching lists: {e}")
        return {}


def update_task_with_completion(card_id, completion_comment):
    """Add completion comment to a task"""
    url = f"{BASE_URL}/cards/{card_id}/actions/comments{AUTH_PARAMS}"

    data = {"text": completion_comment}

    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        print("✅ Added completion comment to task")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error updating task: {e}")
        return False


def move_to_done_list(card_id):
    """Move task to Done list"""
    # First get all lists to find the "Done" list
    lists_url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/lists{AUTH_PARAMS}"

    try:
        response = requests.get(lists_url)
        response.raise_for_status()
        lists = response.json()

        done_list = None
        for list_item in lists:
            if "done" in list_item["name"].lower() or "complete" in list_item["name"].lower():
                done_list = list_item
                break

        if done_list:
            # Move card to done list
            move_url = f"{BASE_URL}/cards/{card_id}{AUTH_PARAMS}"
            data = {"idList": done_list["id"]}

            response = requests.put(move_url, data=data)
            response.raise_for_status()
            print(f"✅ Moved task to '{done_list['name']}' list")
            return True
        else:
            print("⚠️ No 'Done' list found on board")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error moving task: {e}")
        return False


def main():
    print("🚀 TRELLO CARD LISTER")
    print("=" * 60)

    all_cards = get_all_cards()

    if not all_cards:
        print("❌ No cards found on Trello board")
        return

    print(f"\n📋 Listing {len(all_cards)} cards:")
    print("-" * 50)

    list_names_map = get_list_names_map()

    for i, card in enumerate(all_cards, 1):
        print(f"{i}. **{card['name']}**")
        print(f"   URL: {card['shortUrl']}")
        list_name = list_names_map.get(card.get("idList"), "Unknown")
        print(f"   List: {list_name}")
        if card.get("desc"):
            print(f"   Description: {card['desc'][:100]}...")
        print()


if __name__ == "__main__":
    main()
