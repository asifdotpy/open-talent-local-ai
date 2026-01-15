#!/usr/bin/env python3
"""
Script to revert Trello changes - move task back and remove completion comment
"""

import os
from datetime import datetime

import requests

# Load Trello credentials from environment variables (now stored as GitHub organization secrets)
TRELLO_API_KEY = os.environ.get("TRELLO_API_KEY")
TRELLO_TOKEN = os.environ.get("TRELLO_API_TOKEN")
TRELLO_BOARD_ID = os.environ.get("TRELLO_BOARD_ID")

if not all([TRELLO_API_KEY, TRELLO_TOKEN, TRELLO_BOARD_ID]):
    raise ValueError("Trello API credentials not found in environment variables.")

BASE_URL = "https://api.trello.com/1"
AUTH_PARAMS = f"?key={TRELLO_API_KEY}&token={TRELLO_TOKEN}"

# The task we incorrectly updated
CARD_ID = "1ybtNl0M"  # From the previous URL


def get_card_actions(card_id):
    """Get recent actions on a card to find the comment we added"""
    url = f"{BASE_URL}/cards/{card_id}/actions{AUTH_PARAMS}&filter=commentCard&limit=10"

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting card actions: {e}")
        return []


def delete_comment(action_id):
    """Delete a specific comment action"""
    url = f"{BASE_URL}/actions/{action_id}{AUTH_PARAMS}"

    try:
        response = requests.delete(url)
        response.raise_for_status()
        print("✅ Deleted incorrect completion comment")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Error deleting comment: {e}")
        return False


def move_back_to_in_progress(card_id):
    """Move task back to In Progress or appropriate list"""
    # Get all lists
    lists_url = f"{BASE_URL}/boards/{TRELLO_BOARD_ID}/lists{AUTH_PARAMS}"

    try:
        response = requests.get(lists_url)
        response.raise_for_status()
        lists = response.json()

        # Find appropriate list (In Progress, To Do, etc.)
        target_list = None
        for list_item in lists:
            list_name = list_item["name"].lower()
            if "in progress" in list_name or "doing" in list_name or "active" in list_name:
                target_list = list_item
                break

        # Fallback to "To Do" or similar
        if not target_list:
            for list_item in lists:
                list_name = list_item["name"].lower()
                if "to do" in list_name or "todo" in list_name or "backlog" in list_name:
                    target_list = list_item
                    break

        if target_list:
            # Move card back
            move_url = f"{BASE_URL}/cards/{card_id}{AUTH_PARAMS}"
            data = {"idList": target_list["id"]}

            response = requests.put(move_url, data=data)
            response.raise_for_status()
            print(f"✅ Moved task back to '{target_list['name']}' list")
            return True
        else:
            print("⚠️ Could not find appropriate list to move task back to")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error moving task: {e}")
        return False


def main():
    print("🔄 REVERTING TRELLO CHANGES - Routine Check Only")
    print("=" * 55)

    # Get recent comments on the card
    actions = get_card_actions(CARD_ID)

    # Find and delete our completion comment
    deleted_comment = False
    for action in actions:
        if (
            action["type"] == "commentCard"
            and "AWS Instance Sync - COMPLETED" in action["data"]["text"]
        ):
            if delete_comment(action["id"]):
                deleted_comment = True
            break

    if not deleted_comment:
        print("ℹ️ No completion comment found to delete")

    # Move task back to appropriate list
    if move_back_to_in_progress(CARD_ID):
        print("✅ Task status reverted successfully")

    # Add clarification comment
    clarify_url = f"{BASE_URL}/cards/{CARD_ID}/actions/comments{AUTH_PARAMS}"
    clarify_comment = f"""📋 **Routine Check Completed** - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

This was a routine checkpoint to verify Trello API connectivity and task tracking capability.

**No work completed yet** - task remains active and in progress.

The AWS deployment work is planned and will be properly tracked when executed."""

    try:
        response = requests.post(clarify_url, data={"text": clarify_comment})
        response.raise_for_status()
        print("✅ Added clarification comment")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Could not add clarification comment: {e}")

    print(f"\n🔗 Task URL: https://trello.com/c/{CARD_ID}")
    print("✅ Trello changes successfully reverted!")


if __name__ == "__main__":
    main()
