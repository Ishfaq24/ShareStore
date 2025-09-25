# drive/discord_integration.py
import os
import json
import requests
from django.core.files.uploadedfile import UploadedFile
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # default webhook
P_USERNAME = os.getenv("P_USERNAME")

# Load channel mapping safely
try:
    CHANNEL_MAPPINGS = json.loads(os.getenv("CHANNEL_MAPPINGS", "{}"))
except json.JSONDecodeError:
    CHANNEL_MAPPINGS = {}


def send_file_to_discord(file_p: UploadedFile, uploader_username: str):
    """
    Sends a file to Discord using webhooks.
    Uses keyword mapping if available, otherwise uses default webhook.

    Args:
        file_p (UploadedFile): File from Django upload.
        uploader_username (str): Username of the uploader.
    """
    if uploader_username != P_USERNAME:
        # Only send files from the specified username
        return

    sent = False

    # Check each keyword in CHANNEL_MAPPINGS
    for keyword, webhook_url in CHANNEL_MAPPINGS.items():
        if keyword.lower() in file_p.name.lower():
            _send_file(file_p, webhook_url)
            sent = True

    # If no keyword matched, use default webhook
    if not sent and DISCORD_WEBHOOK_URL:
        _send_file(file_p, DISCORD_WEBHOOK_URL)


def _send_file(file_p: UploadedFile, webhook_url: str):
    """Helper function to send file to a given webhook URL."""
    try:
        files = {'file': (file_p.name, file_p.read())}
        response = requests.post(webhook_url, files=files)
        response.raise_for_status()
        print(f"✅ File {file_p.name} sent to Discord webhook!")
    except Exception as e:
        print(f"❌ Failed to send {file_p.name} to Discord: {e}")
