from telethon.sessions import StringSession
from telethon.sync import TelegramClient

print(
    """Please go-to my.telegram.org
Login using your Telegram account
Click on API Development Tools
Create a new application, by entering the required details
Using the received data, get a session for your bot / account."""
)
API_KEY = int(input("Enter APP_ID (the shorter one): "))
API_HASH = input("Enter API_HASH (the longer one): ")

with TelegramClient(StringSession(), API_KEY, API_HASH) as client:
    string_session = client.session.save()
    message = f"String_Session: {string_session}" \
    "\n" \
    "Put this variable to environment.py and run module. " \
    "Do NOT send this to anyone else!"
    print(message)