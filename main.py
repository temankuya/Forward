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

# Format pesan dengan waktu forward
def format_message_with_time(message):
    text = message.message or ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"{text}\n\n🕒 Forwarded at: {timestamp}"

# Simpan dan ambil ID terakhir
def save_last_id(message_id, filename="last_id.txt"):
    with open(filename, "w") as f:
        f.write(str(message_id))

def get_last_id(filename="last_id.txt"):
    try:
        with open(filename, "r") as f:
            return int(f.read())
    except FileNotFoundError:
        return None

# Forward semua pesan lama
async def forward_all_history():
    print("📤 Forwarding semua pesan dari awal (atau lanjutan)...")
    last_id = get_last_id()

    async for message in client.iter_messages(source_channel, reverse=True, min_id=last_id or 0):
        try:
            if message.text:
                msg = format_message_with_time(message)
                await client.send_message(target_channel, msg)
            elif message.media:
                await client.send_file(target_channel, message.media, caption=message.text or "")
            print(f"✅ Forwarded message ID: {message.id}")
            save_last_id(message.id)
        except FloodWaitError as e:
            print(f"⏳ FloodWait: Harus tunggu {e.seconds} detik...")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"❌ Error message {message.id}: {e}")

# Forward real-time
@client.on(events.NewMessage(chats=source_channel))
async def realtime_forward(event):
    try:
        if event.message.text:
            msg = format_message_with_time(event.message)
            await client.send_message(target_channel, msg)
        elif event.message.media:
            await client.send_file(target_channel, event.message.media, caption=event.message.text or "")
        print(f"🆕 Real-time forward: {event.message.id}")
        save_last_id(event.message.id)
    except FloodWaitError as e:
        print(f"⚠️ Real-time FloodWait: Harus tunggu {e.seconds} detik...")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"❌ Error real-time: {e}")

# Main function
async def main():
    await forward_all_history()
    print("🚀 Listening for new messages...")

# Jalankan client
with client:
    client.loop.run_until_complete(main())
    client.run_until_disconnected()
