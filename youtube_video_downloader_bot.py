import os
from pyrogram import Client, filters
from yt_dlp import YoutubeDL

# ================== Configuration ==================
# ================== Configuration ==================
API_ID = 12345678  # telegram api_id (get from https://my.telegram.org)
API_HASH = "your_api_hash"
BOT_TOKEN = "your_bot_token"
# ===================================================
# ===================================================

# Create bot client
bot = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# YouTube download function
def download_youtube_video(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename, info.get('title', 'Unknown Title')

# Start command
@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply_text("👋 မင်္ဂလာပါ။ YouTube Video Downloader Bot ဖြစ်ပါတယ်။\n\n🔗 YouTube Link တစ်ခု ပေးလိုက်ပါ။")

# Message handler for links
@bot.on_message(filters.text & ~filters.command("start"))
async def download(_, message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await message.reply_text("❌ YouTube link တင်ပေးပါ။")
        return

    msg = await message.reply_text("📥 Downloading... ကျေးဇူးပြု၍ စောင့်ပါ။")

    try:
        filepath, title = download_youtube_video(url)
        await bot.send_video(
            chat_id=message.chat.id,
            video=filepath,
            caption=f"✅ Downloaded: {title}",
        )
        await msg.delete()
        os.remove(filepath)
    except Exception as e:
        await msg.edit(f"❌ Download မဖြစ်ပါ။\nError: {str(e)}")

# Run the bot
if __name__ == "__main__":
    if not os.path.exists("downloads"):
        os.makedirs("downloads")
    print("✅ Bot is running...")
    bot.run()
