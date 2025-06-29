import os
import asyncio
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from dotenv import load_dotenv
from datetime import datetime

# Load .env
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
string_session = os.getenv("STRING_SESSION")
source_channel = os.getenv("SOURCE_CHANNEL")
target_channel = os.getenv("TARGET_CHANNEL")

# Inisialisasi client pakai StringSession
client = TelegramClient(StringSession(string_session), api_id, api_hash)

def format_message_with_time(message):
    text = message.message or ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\n🕒 Forwarded at: {timestamp}"

# Forward semua pesan lama dari awal
async def forward_all_history():
    print("📤 Forwarding semua pesan dari awal...")
    async for message in client.iter_messages(source_channel, reverse=True):
        try:
            if message.text:
                msg = format_message_with_time(message)
                await client.send_message(target_channel, msg)
            elif message.media:
                await client.send_file(target_channel, message.media, caption=message.text or "")
            print(f"✅ Forwarded message ID: {message.id}")
        except FloodWaitError as e:
            print(f"⏳ FloodWait: Harus tunggu {e.seconds} detik...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error message {message.id}: {e}")

# Real-time forward
@client.on(events.NewMessage(chats=source_channel))
async def realtime_forward(event):
    try:
        if event.message.text:
            msg = format_message_with_time(event.message)
            await client.send_message(target_channel, msg)
        elif event.message.media:
            await client.send_file(target_channel, event.message.media, caption=event.message.text or "")
        print(f"🆕 Real-time forward: {event.message.id}")
    except FloodWaitError as e:
        print(f"⚠️ Real-time FloodWait: Harus tunggu {e.seconds} detik...")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"❌ Error real-time: {e}")

async def main():
    await forward_all_history()
    print("🚀 Listening for new messages...")

with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
