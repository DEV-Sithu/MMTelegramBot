from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from dotenv import load_dotenv
import os
# Load .env configuration
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

BOT_TOKEN =os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")

app = Client("github_webapp_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(client, message):
    
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Open GitHub Web App 🌐",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    await message.reply(
        "👇 GitHub-hosted Web App ကိုဖွင့်ရန် Button ကိုနှိပ်ပါ။",
        reply_markup=keyboard
    )

print("Bot is running...")
app.run()
