import requests
import json
import random
import string
from urllib.parse import quote_plus
from websocket import WebSocketApp
from threading import Thread
import asyncio
import websockets

class BriarHeadlessClient:
    def __init__(self, base_url, auth_token):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        self.ws = None
        self.ws_thread = None
        self.event_handlers = {}
        self.loop = asyncio.get_event_loop()

    def generate_unique_nickname(self, length=12):
        characters = string.ascii_letters  # a-z, A-Z
        while True:
            nickname = ''.join(random.choice(characters) for i in range(length))
            if not self.is_nickname_used(nickname):
                return nickname

    def is_nickname_used(self, nickname):
        # This method should check if the nickname is already used.
        return False

    ### CONTACTS ###
 
    # Getting briar:// link
    def get_add_link(self):
        try:
            response = requests.get(
                f"{self.base_url}/contacts/add/link",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get add link:  {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error getting add link: {e}")

    # Adding a contact
    def add_contact(self, briar_link):
        alias = self.generate_unique_nickname()
        try:
            response = requests.post(
                f"{self.base_url}/contacts/add/pending",
                headers=self.headers,
                json={
                    "link": briar_link,
                    "alias": alias
                }
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to add contact: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error adding contact: {e}")

    # Get a list of all pending contacts
    def get_pending_contacts(self):
        try:
            response = requests.get(
                f"{self.base_url}/contacts/add/pending",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to get pending contacts:  {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error getting pending contacts: {e}")

    # Listing all contacts
    def list_contacts(self):
        try:
            response = requests.get(
                f"{self.base_url}/contacts",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to list contacts: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error listing contacts: {e}")

    def get_contact_id_by_name(self, name):
        try:
            contacts = self.list_contacts()
            for contact in contacts:
                if contact["author"]["name"] == name:
                    return contact["contactId"]
            raise Exception(f"Contact name {name} not found")
        except Exception as e:
            raise Exception(f"Error getting contact ID: {e}")

    # Changing alias of a contact
    def change_contact_alias(self, contact_id, contact_alias):
        try:
            payload = {
                "alias": contact_alias
            }
            response = requests.put(
                f"{self.base_url}/contacts/{contact_id}/alias",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to change contact {contact_id} alias: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error changing contact {contact_id} alias: {e}")

    # Removing a contact
    def remove_contact(self, contact_id):
        try:
            response = requests.delete(
                f"{self.base_url}/contacts/{contact_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to remove contact {contact_id}: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error removing contact {contact_id}: {e}")

    ### PRIVATE MESSAGES ###

    # Listing all private messages
    def list_private_messages(self, contact_id):
        try:
            response = requests.get(
                f"{self.base_url}/messages/{contact_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to list private messages from {contact_id}: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error listing private messages from {contact_id}: {e}")

    # Writing a private message
    def write_private_message(self, contact_id, message_text):
        try:
            payload = {
                "text": message_text
            }
            response = requests.post(
                f"{self.base_url}/messages/{contact_id}",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to sent private message to {contact_id}: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error sending private message to {contact_id}: {e}")

    # Marking private messages as read
    def mark_private_message_read(self, contact_id, message_id):
        try:
            payload = {
                "messageId": message_id
            }
            response = requests.post(
                f"{self.base_url}/messages/{contact_id}/read",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to mark private message {message_id} from {contact_id} as read: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error marking private message {message_id} from {contact_id} as read: {e}")
    
    # Deleting all private messages
    def delete_private_messages(self, contact_id):
        try:
            response = requests.delete(
                f"{self.base_url}/messages/{contact_id}/all",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to delete privates message from {contact_id}: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error deleting messages from {contact_id}: {e}")

    ### FORUMS ###

    def share_forums(self, contact_id, forum_ids, text):
        for forum_id in forum_ids:
            try:
                payload = {
                    "forumId": forum_id,
                    "contactId": str(contact_id),
                    "text": text
                }
                url = f"{self.base_url}/forums/add/pending"
                print("Making request to URL:", url)
                print("Headers:", self.headers)
                print("Payload:", payload)
                response = requests.post(
                    f"{self.base_url}/forums/add/pending",
                    headers=self.headers,
                    json=payload
                )
                if response.status_code != 204:
                    raise Exception(f"Failed to share forum {forum_id}: {response.status_code} {response.text}")
                else:
                    print(f"Successfully shared forum {forum_id} for contact ID: {contact_id}.")
            except Exception as e:
                print(f"Error sharing forum {forum_id} for contact ID {contact_id}: {e}")

    # Listing blog posts
    def list_forums(self):
        try:
            response = requests.get(
                f"{self.base_url}/forums",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to list forums: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error listing forums: {e}")

    def get_forum_id_by_name(self, forum_name):
        try:
            forums = self.list_forums()
            for forum in forums:
                if forum["name"] == forum_name:
                    return forum["id"]
            raise Exception(f"Forum name {forum_name} not found")
        except Exception as e:
            raise Exception(f"Error getting forum ID: {e}")

    ### BLOGS ###

    # Listing blog posts
    def list_blog_posts(self):
        try:
            response = requests.get(
                f"{self.base_url}/blogs/posts",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to list blog posts: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error listing blog posts: {e}")

    # Writing a blog post
    def write_blog_post(self, message_text):
        try:
            payload = {
                "text": message_text
            }
            response = requests.post(
                f"{self.base_url}/blogs/posts",
                headers=self.headers,
                json=payload
            )
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Failed to write blog post: {response.status_code} {response.text}")
        except Exception as e:
            raise Exception(f"Error writing blog post: {e}")

    ### WEBSOCKET ###

    async def on_message(self, message):
        print("Received message:", message)
        try:
            data = json.loads(message)
            # Dispatch the message to the appropriate handler based on type
            if data["type"] == "event" and data["name"] in self.event_handlers:
                for handler in self.event_handlers[data["name"]]:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data["data"])
                    else:
                        handler(data["data"])
        except:
            print("On message error")

    async def on_error(self, error):
        print("WebSocket error:", error)

    async def on_close(self, close_status_code, close_msg):
        print(f"WebSocket connection closed: status_code={close_status_code}, message={close_msg}")

    async def on_open(self, ws):
        print("WebSocket connection opened")
        await ws.send(self.auth_token)

    async def start_websocket(self, ws_url):
        async with websockets.connect(ws_url) as ws:
            self.ws = ws
            await self.on_open(ws)
            try:
                async for message in ws:
                    await self.on_message(message)
            except websockets.ConnectionClosed as e:
                await self.on_close(e.code, e.reason)
            except Exception as e:
                await self.on_error(e) 

    def start_websocket_thread(self, ws_url):
        self.loop.run_until_complete(self.start_websocket(ws_url))

    def stop_websocket(self):
        if self.ws:
            asyncio.run(self.ws.close())
        self.loop.stop()

    def register_event_handler(self, event_name, handler):
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

