import json
import asyncio
from briar_headless import BriarHeadlessClient

def load_forums():
    with open('forums.json', 'r') as file:
        data = json.load(file)
    return data

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

forums_data = load_forums()
config_data = load_config()
briar_client = BriarHeadlessClient(base_url=config_data['base_url'], auth_token=config_data['auth_token'])

def get_forum_name_by_id(forum_id):
    print(f"Getting forum name for ID: {forum_id}")
    for forum in forums_data['forums']:
        if int(forum['id']) == int(forum_id):
            print(f"Found forum name: {forum['name']}")
            return forum['name']
    print("Forum name not found")
    return None

async def handle_private_message(data):
    print("Custom handler: New private message received:", data)
    
    # Extract message text and contact ID
    message_text = data.get("text", "")
    contact_id = data.get("contactId")
    
    # Check if the message is a command
    if message_text.startswith("/"):
        command, *args = message_text[1:].split()
        print(f"Command received: {command}, args: {args}")
        if command == "echo":
            response = " ".join(args)
            print(f"Sending echo response: {response}")
            await send_command_response(contact_id, response)

        elif command == "list":
            response = ""
            for forum in forums_data["forums"]:
                response += str(forum['id']) + " - " + forum['name'] + "\n"
            print(f"Sending list response: {response}")
            await send_command_response(contact_id, response)

        elif command == "join":
            print(f"Join command with args: {args}")
            forum_id = args[0]
            forum_name = get_forum_name_by_id(forum_id)
            forum_id = briar_client.get_forum_id_by_name(forum_name)
            print(f"Sharing forum {forum_name} with ID {forum_id}")
            await briar_client.share_forums(contact_id, [forum_id], f"Invitation to join a {forum_name} from briar.retiolus.net")

        elif command == "help":
            response = (
                "Available commands:\n"
                "/echo <message> - Replies with the same message.\n"
                "/list - Lists all available forums.\n"
                "/join <forum_id> - Sends an invitation to join the specified forum.\n"
                "/help - Displays this help message.\n\n"
                "Note: The bot may know about forums without having access to them. "
                "Forums must be shared at least once by users for the bot to be able to share them.\n\n"
                "Check https://briar.retiolus.net/request to add the bot to your contacts."
            )
            print("Sending help response")
            await send_command_response(contact_id, response)

async def send_command_response(contact_id, response):
    try:
        print(f"Preparing to send command response to contact {contact_id}: {response}")
        await client.write_private_message(contact_id, response)
        print(f"Response sent to contact {contact_id}")
    except Exception as e:
        print(f"Error in send_command_response: {e}")

async def handle_new_contact(data):
    print("Custom handler: New contact added:", data)
    # Add your custom logic here

async def handle_contact_connected(data):
    print("Contact connected:", data)

async def handle_contact_disconnected(data):
    print("Contact disconnected:", data)

async def main():
    ws_url = "ws://localhost:7000/v1/ws"

    global client
    client = BriarHeadlessClient(base_url=config_data['base_url'], auth_token=config_data['auth_token'])

    # Register event handlers
    client.register_event_handler("ConversationMessageReceivedEvent", handle_private_message)
    client.register_event_handler("ContactAddedEvent", handle_new_contact)
    client.register_event_handler("ContactConnectedEvent", handle_contact_connected)
    client.register_event_handler("ContactDisconnectedEvent", handle_contact_disconnected)

    await client.start_websocket(ws_url)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        client.stop_websocket()
