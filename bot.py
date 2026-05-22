import os
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ForceReply

# ==================== CONFIGURATION ====================
API_ID = 35394497         # Votre API_ID (sans guillemets)
API_HASH = "890bcd6bb51422b9bdce8aa65566889e"  # Votre API_HASH (avec guillemets)
BOT_TOKEN = "8937126319:AAGOCmCpLstnI0o7FzbVg5TUA61sq2ohrf8" # Votre Token de @BotFather
# =======================================================

# Configuration des logs pour suivre les actions du bot
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Client("my_rename_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Dictionnaires temporaires pour stocker les choix des utilisateurs
user_files = {}
user_thumbs = {}

START_TEXT = """
ᴄᴇᴄɪ ᴇsᴛ ᴜɴ ʙᴏᴛ ᴘᴜɪssᴀɴᴛ ᴅᴇ ʀᴇɴᴏᴍᴍᴀɢᴇ.

    ➻ ᴜᴛɪʟɪsᴇz ᴄᴇ ʙᴏᴛ ᴘᴏᴜʀ ʀᴇɴᴏᴍᴍᴇʀ ᴇᴛ ᴍᴏᴅɪғɪᴇʀ ʟᴀ ᴠɪɢɴᴇᴛᴛᴇ ᴅᴇ ᴠᴏs ғɪᴄʜɪᴇʀs.

    ➻ ᴠᴏᴜs ᴘᴏᴜᴠᴇᴢ ᴇ́ɢᴀʟᴇᴍᴇɴᴛ ᴄᴏɴᴠᴇʀᴛɪʀ ᴜɴᴇ ᴠɪᴅᴇ́ᴏ ᴇɴ ғɪᴄʜɪᴇʀ ᴇᴛ ᴠɪᴄᴇ ᴠᴇʀsᴀ.

    ➻ ᴄᴇ ʙᴏᴛ ᴘʀᴇɴᴅ ᴇɴ ᴄʜᴀʀɢᴇ ʟᴇs ᴠɪɢɴᴇᴛᴛᴇs ᴇᴛ ʟᴇs ʟᴇ́ɢᴇɴᴅᴇs ᴘᴇʀsᴏɴɴᴀʟɪsᴇ́ᴇs.
 ʙᴏᴛ ᴄʀᴇ́ᴇ́ ᴘᴀʀ @sperot228<
    
"""

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    await message.reply_text(text=START_TEXT)

# Étape A : Détection de la vignette (Si l'utilisateur envoie une photo)
@app.on_message(filters.photo & filters.private)
async def save_thumb(client, message):
    user_id = message.from_user.id
    thumb_path = await message.download()
    user_thumbs[user_id] = thumb_path
    await message.reply_text("✅ **Vignette enregistrée avec succès !** Elle sera appliquée aux prochains fichiers.")

# Étape B : Détection d'un média à renommer
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
        text=f"📂 **Fichier reçu** : `{file.file_name}`\n\nChoisissez une action ci-dessous :",
        reply_markup=InlineKeyboardMarkup(buttons),
        reply_to_message_id=message.id
    )

# Étape C : Gestion des clics sur les boutons
@app.on_callback_query()
async def callback_handler(client, query):
    user_id = query.from_user.id
    
    if user_id not in user_files:
        await query.answer("❌ Erreur : Fichier introuvable. Renvoyez le fichier.", show_alert=True)
        return

    if query.data == "rename":
        await query.message.delete()
        await query.message.reply_text(
            "✍️ Entrez le **nouveau nom** du fichier avec son extension (ex: `video.mp4`) :",
            reply_markup=ForceReply(True)
        )
        
    elif query.data == "type_video":
        user_files[user_id]["type"] = "video"
        await query.answer("Conversion configurée : Mode Vidéo 🎬")
        
    elif query.data == "type_doc":
        user_files[user_id]["type"] = "document"
        await query.answer("Conversion configurée : Mode Document 📁")

# Étape D : Réception du nouveau nom et traitement final
@app.on_message(filters.reply & filters.private)
async def rename_process(client, message):
    user_id = message.from_user.id
    
    if user_id not in user_files or not message.reply_to_message:
        return
        
    new_name = message.text
    file_info = user_files[user_id]
    
    status_msg = await message.reply_text("⚡ **Traitement en cours...** Téléchargement depuis Telegram...")
    
    file_path = await client.download_media(file_info["file_id"])
    
    directory = os.path.dirname(file_path)
    new_file_path = os.path.join(directory, new_name)
    os.rename(file_path, new_file_path)
    
    await status_msg.edit("⬆️ **Envoi en cours vers Telegram...** Veuillez patienter.")
    
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

# --- AJOUT POUR COMPATIBILITÉ RENDER GRATUIT ---
from flask import Flask
import threading

flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot en ligne !"

def run_flask():
    flask_app.run(host='0.0.0.0', port=10000)

# Lance le serveur web en arrière-plan
threading.Thread(target=run_flask).start()
# -----------------------------------------------

print("🚀 Bot Pyrogram connecté et prêt à l'action !")
app.run()

