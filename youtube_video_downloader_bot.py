from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from pyrogram.enums import ParseMode
from yt_dlp import YoutubeDL
import os
import time
from dotenv import load_dotenv
import re
import asyncio
import requests

load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client("yt_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
video_options = {}

def sanitize_filename(name):
    return re.sub(r'[\\/*?"<>|]', "_", name)

def get_visual_bar(percentage):
    filled_length = int(percentage // 10)
    bar = "🟩" * filled_length + "⬜" * (10 - filled_length)
    return f"{bar} {int(percentage)}%"

def create_upload_progress_hook(message: Message, start_time):
    async def hook(current, total):
        percentage = current * 100 / total
        now = time.time()
        elapsed = now - start_time
        speed = current / elapsed if elapsed > 0 else 0
        eta = (total - current) / speed if speed > 0 else 0

        progress_str = get_visual_bar(percentage)
        size_str = f"{round(current / 1024 / 1024, 2)}MB / {round(total / 1024 / 1024, 2)}MB"
        speed_str = f"{round(speed / 1024 / 1024, 2)} MB/s"
        eta_str = f"ETA: {int(eta)}s"

        text = f"📤 Uploading...\n{progress_str}\n📦 {size_str}\n⚡ {speed_str}\n⏳ {eta_str}"
        try:
            await message.edit_text(text)
        except:
            pass
    return hook

def get_format_options(url):
    ydl_opts = {'quiet': True, 'dump_single_json': True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get('formats', [])
        video_formats = []
        audio_format = None
        seen_resolutions = set()

        for fmt in formats:
            if fmt.get('vcodec') != 'none':
                height = fmt.get('height')
                if not height or height in seen_resolutions:
                    continue
                seen_resolutions.add(height)
                fmt_id = fmt['format_id']
                res = f"{height}p"
                size = fmt.get('filesize') or fmt.get('filesize_approx')
                size_str = f"{round(size / 1024 / 1024, 2)}MB" if size else "Unknown size"
                label = f"🎞 {res} - {size_str}"
                video_formats.append((fmt_id, label))
            elif not audio_format and fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':
                audio_format = fmt['format_id']

        video_formats.sort(key=lambda x: int(x[1].split(' ')[1].replace('p', '')))
        return video_formats, audio_format, info['title'], info.get('thumbnail')

@bot.on_message(filters.command("start"))
async def start(_, message):
    await message.reply("🎬 YouTube Link ပေးပါ။")

@bot.on_message(filters.text & ~filters.command("start"))
async def handle_video(_, message):
    url = message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await message.reply("❌ YouTube link တင်ပါ။")
        return

    await message.reply("🔍 Format ရွေးချယ်မှုများ ရယူနေသည်...")

    try:
        formats, audio_format, title, thumb = get_format_options(url)
        chat_id = message.chat.id
        video_options[chat_id] = {
            "url": url,
            "formats": formats,
            "audio_format": audio_format,
            "title": title,
            "thumb": thumb
        }

        buttons = [
            [InlineKeyboardButton(text=label, callback_data=f"video|{chat_id}|{fmt_id}")]
            for fmt_id, label in formats[:10]
        ]
        if audio_format:
            buttons.append([InlineKeyboardButton(text="🎧 MP3 Only", callback_data=f"audio|{chat_id}|{audio_format}")])

        await message.reply(
            f"📺 *{title}*\n\nResolution/Size ရွေးပါ:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@bot.on_callback_query()
async def download_callback(client, callback_query: CallbackQuery):
    await callback_query.answer()
    try:
        ftype, chat_id_str, fmt_id = callback_query.data.split("|")
        chat_id = int(chat_id_str)
        info = video_options.get(chat_id)

        if not info:
            await callback_query.message.edit("Session expired.")
            return

        url = info["url"]
        title = sanitize_filename(info["title"])
        audio_format = info["audio_format"]
        thumb_url = info.get("thumb")
        out_ext = "mp3" if ftype == "audio" else "mp4"
        filename = f"downloads/{title}-{fmt_id}.{out_ext}"
        thumbnail_path = None

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

        if thumb_url:
            thumb_data = requests.get(thumb_url).content
            thumbnail_path = f"downloads/{title}_thumb.jpg"
            with open(thumbnail_path, "wb") as f:
                f.write(thumb_data)

        await callback_query.message.reply("📥 Downloading...")
        
      
        ydl_opts = {
            'format': fmt_id if ftype == 'audio' else f"{fmt_id}+bestaudio/best",
            'outtmpl': filename,
            'quiet': True,
            'noplaylist': True,
            'merge_output_format': 'mp4' if ftype == 'video' else 'mp3',
            'verbose': True
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        progress_msg = await callback_query.message.reply("📤 Uploading...")
        start_time = time.time()
        hook = create_upload_progress_hook(progress_msg, start_time)

        async def progress_wrapper(file_path):
            total = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                sent = 0
                while chunk := f.read(1024 * 64):
                    sent += len(chunk)
                    await hook(sent, total)

        if ftype == 'video':
            await progress_wrapper(filename)
            await client.send_video(
                chat_id,
                video=filename,
                caption=f"✅ Downloaded: {info['title']}",
                parse_mode=ParseMode.MARKDOWN,
                thumb=thumbnail_path if thumbnail_path else None
            )
        else:
            await progress_wrapper(filename)
            await client.send_audio(
                chat_id,
                audio=filename,
                caption=f"✅ MP3 Downloaded: {info['title']}",
                parse_mode=ParseMode.MARKDOWN,
                thumb=thumbnail_path if thumbnail_path else None
            )

        os.remove(filename)
        if thumbnail_path and os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)

    except Exception as e:
        await callback_query.message.edit(f"❌ Upload error: {str(e)}")

if __name__ == "__main__":
    print("✅ Bot is running...")
    bot.run()
