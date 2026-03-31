import requests
import json
import datetime
import time
from urllib.parse import quote_plus
from briar_headless import BriarHeadlessClient

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

base_url = config['base_url']
auth_token = config['auth_token']

headers = {
    "Authorization": f"Bearer {auth_token}",
    "Content-Type": "application/json"
}

file_path = config['file_path']

briar_client = BriarHeadlessClient(
    base_url=config['base_url'], 
    auth_token=config['auth_token']
    )

def read_forums_data():
    with open(file_path, "r") as file:
        return json.load(file)

def write_forums_data(forums_data):
    with open(file_path, "w") as file:
        json.dump(forums_data, file, indent=4)

def get_forum_post_count_and_last_post_date(forum_id):
    try:
        print(f"Fetching post count and last post date for forum {forum_id}...")
        encoded_forum_id = quote_plus(forum_id)  # URL-encode the forum ID
        response = requests.get(f"{base_url}/forums/{encoded_forum_id}/posts/count", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"Forum {forum_id} has {data['postCount']} posts. Last post date: {data['lastPostDate']}")
            return data
        else:
            raise Exception(f"Failed to get post count for forum {forum_id}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Error fetching post count for forum {forum_id}: {e}")
        return None

def get_pending_forums():
    print("Checking for pending forum invitations...")
    response = requests.get(f"{base_url}/forums/add/pending", headers=headers)
    if response.status_code == 200:
        pending_forums = response.json()
        print(f"Found {len(pending_forums)} pending forums.")
        return pending_forums
    else:
        raise Exception(f"Failed to get pending forums: {response.status_code} {response.text}")

def accept_pending_forum(forum_id, contact_id):
    try:
        print(f"Accepting forum invitation for forum {forum_id} and contact {contact_id}...")
        payload = {
            "forumId": forum_id,
            "contactId": contact_id
        }
        response = requests.post(f"{base_url}/forums/accept", headers=headers, data=json.dumps(payload))
        if response.status_code == 204:
            print(f"Successfully accepted forum invitation for forum {forum_id} and contact {contact_id}.")
            return True
        else:
            print(f"Failed to accept forum invitation: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"Error accepting forum invitation for forum {forum_id} and contact {contact_id}: {e}")
        return False

def get_all_contacts():
    print("Retrieving all contacts...")
    response = requests.get(f"{base_url}/contacts", headers=headers)
    if response.status_code == 200:
        contacts = response.json()
        print(f"Found {len(contacts)} contacts.")
        return contacts
    else:
        raise Exception(f"Failed to get contacts: {response.status_code} {response.text}")

def update_forums_data(forums_data, new_forum_data):
    next_id = max(forum["id"] for forum in forums_data["forums"]) + 1 if forums_data["forums"] else 1
    for new_forum in new_forum_data:
        existing_forum = next((forum for forum in forums_data["forums"] if forum["name"] == new_forum["forumName"]), None)
        try:
            last_post_date = datetime.datetime.fromtimestamp(int(new_forum["lastPostDate"]) / 1000).strftime('%Y-%m-%d') if new_forum["lastPostDate"] != "No posts yet" else "Unknown"
            first_post_date = datetime.datetime.fromtimestamp(int(new_forum["firstPostDate"]) / 1000).strftime('%Y-%m-%d') if new_forum["firstPostDate"] != "No posts yet" else "Unknown"
        except (ValueError, TypeError, KeyError) as e:
            print(f"Error parsing last post date for forum {new_forum['forumName']}: {e}")
            print(f"Raw data: {new_forum}")
            last_post_date = "Unknown"
            first_post_date = "Unknown"
        if existing_forum:
            existing_forum["total_posts"] = new_forum["postCount"]
            existing_forum["last_post_date"] = last_post_date
            existing_forum["first_post_date"] = first_post_date
        else:
            forums_data["forums"].append({
                "id": next_id,
                "name": new_forum["forumName"],
                "total_posts": new_forum["postCount"],
                "last_post_date": last_post_date,
                "first_post_date": first_post_date
            })
            next_id += 1
    return forums_data

def main():
    try:
        # Check for pending forums and accept them
        pending_forums = get_pending_forums()
        print(pending_forums)
        
        # Get all contacts
        contacts = get_all_contacts()

        for pending_forum in pending_forums:
            forum_id = pending_forum["forumId"].split("(")[1].strip(")")
            for contact in contacts:
                contact_id = contact["contactId"]
                accepted = accept_pending_forum(forum_id, contact_id)
                if accepted:
                    break  # Stop trying other contacts if accepted

        #pending_contacts = get_pending_contacts()
        #print(pending_contacts)

        # After accepting pending forums, list all forums and their details
        print(briar_client.list_contacts())
        forums = briar_client.list_forums()
        forum_details = []

        for forum in forums:
            forum_id = forum["id"]
            forum_name = forum["name"]

            post_data = get_forum_post_count_and_last_post_date(forum_id)
            if post_data:
                post_count = post_data["postCount"]
                last_post_date = post_data["lastPostDate"]
                first_post_date = post_data["firstPostDate"]
            else:
                post_count = 0
                last_post_date = "Unknown"
                first_post_date = "Unknown"

            forum_details.append({
                "forumId": forum_id,
                "forumName": forum_name,
                "postCount": post_count,
                "lastPostDate": last_post_date,
                "firstPostDate": first_post_date
            })
            time.sleep(1)

        # Read existing forums data from file
        forums_data = read_forums_data()

        # Update forums data with the new information
        updated_forums_data = update_forums_data(forums_data, forum_details)

        # Write updated forums data back to file
        write_forums_data(updated_forums_data)

        print("Forums data updated successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
