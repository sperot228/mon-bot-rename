import os
import time
import sys
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

# ==================== CONFIGURATION  ====================
     API_ID = 2847104 # 
API_HASH = "8f4be8c8651a2d592471b01c43b8a1a3" # 
BOT_TOKEN = "7492018402:AAH_jK9xLLpW-m1N7UzOQ2pX4b_v4M1" # 
# ====================================================================================

app = Client("my_rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

user_files = {}
user_thumbs = {}

START_TEXT = """
ᴄᴇᴄɪ ᴇsᴛ ᴜɴ ʙᴏᴛ ᴘᴜɪssᴀɴᴛ ᴅᴇ ʀᴇɴᴏᴍᴍᴀɢᴇ.
 
    ➻ ᴜᴛɪʟɪsᴇz ᴄᴇ ʙᴏᴛ ᴘᴏᴜʀ ʀᴇɴᴏᴍᴍᴇʀ ᴇᴛ ᴍᴏᴅɪғɪᴇʀ ʟᴀ ᴠɪɢɴᴇᴛᴛᴇ ᴅᴇ ᴠᴏs ғɪᴄʜɪᴇʀs.

    ➻ ᴠᴏᴜs ᴘᴏᴜᴠᴇᴢ ᴇ́ɢᴀʟᴇᴍᴇɴᴛ ᴄᴏɴᴠᴇʀᴛɪʀ ᴜɴᴇ ᴠɪᴅᴇ́ᴏ ᴇɴ ғɪᴄʜɪᴇʀ ᴇᴛ ᴠɪᴄᴇ ᴠᴇʀsᴀ.

    ➻ ᴄᴇ ʙᴏᴛ ᴘʀᴇɴᴅ ᴇɴ ᴄʜᴀʀɢᴇ ʟᴇs ᴠɪɢɴᴇᴛᴛᴇs ᴇᴛ ʟᴇs ʟᴇ́ɢᴇɴᴅᴇs ᴘᴇʀsᴏɴɴᴀʟɪsᴇ́ᴇs.
    ʙᴏᴛ ᴄʀᴇ́ᴇ́ ᴘᴀʀ @sperot228
"""

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(text=START_TEXT)

@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    thumb_path = await message.download()
    user_thumbs[user_id] = thumb_path
    await message.reply_text("✅ **Vignette enregistrée !**")

@app.on_message((filters.document | filters.video | filters.audio) & filters.private)
async def file_handler(client, message):
    file = message.document or message.video or message.audio
    user_id = message.from_user.id
    
    user_files[user_id] = {
        "file_id": file.file_id,
        "file_name": file.file_name,
        "type": "video" if message.video else ("audio" if message.audio else "document")
    }

    buttons = [
        [InlineKeyboardButton("✏️ Renommer le fichier", callback_data="rename")],
        [InlineKeyboardButton("🎬 Mode Vidéo", callback_data="type_video"),
         InlineKeyboardButton("📁 Mode Document", callback_data="type_doc")]
    ]
    await message.reply_text(
        text=f"📂 **Fichier reçu** : `{file.file_name}`",
        reply_markup=InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id
    )

@app.on_callback_query()
async def callback_handler(client, query):
    user_id = query.from_user.id
    if user_id not in user_files:
        await query.answer("❌ Erreur. Renvoyez le fichier.", show_alert=True)
        return

    if query.data == "rename":
        await query.message.delete()
        await query.message.reply_text(
            "✍️ Entrez le **nouveau nom** avec l'extension (ex: `video.mp4`) :",
            reply_markup=ForceReply(True)
        )
    elif query.data == "type_video":
        user_files[user_id]["type"] = "video"
        await query.answer("Mode Vidéo 🎬")
    elif query.data == "type_doc":
        user_files[user_id]["type"] = "document"
        await query.answer("Mode Document 📁")

@app.on_message(filters.reply & filters.private)
async def rename_process(client, message):
    user_id = message.from_user.id
    if user_id not in user_files or not message.reply_to_message:
        return
        
    new_name = message.text
    file_info = user_files[user_id]
    status_msg = await message.reply_text("⚡ **Téléchargement en cours...**")
    
    file_path = await client.download_media(file_info["file_id"])
    directory = os.path.dirname(file_path)
    new_file_path = os.path.join(directory, new_name)
    os.rename(file_path, new_file_path)
    
    await status_msg.edit("⬆️ **Envoi en cours vers Telegram...**")
    thumb = user_thumbs.get(user_id, None)
    
    if file_info["type"] == "video":
        await client.send_video(chat_id=message.chat.id, video=new_file_path, caption=f"✅ `{new_name}`", thumb=thumb)
    else:
        await client.send_document(chat_id=message.chat.id, document=new_file_path, caption=f"✅ `{new_name}`", thumb=thumb)
        
    try:
        os.remove(new_file_path)
    except:
        pass
    await status_msg.delete()
    del user_files[user_id]

# --- LOGIQUE SERVEUR COMPATIBILITÉ RENDER ---
from flask import Flask
import threading

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot actif !"

def run_flask():
    try:
        flask_app.run(host='0.0.0.0', port=10000)
    except Exception as e:
        print(f"Flask Error: {e}")

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    time.sleep(1)
    app.run()
