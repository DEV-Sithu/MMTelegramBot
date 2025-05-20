import logging
from telegram import Update ,ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes,MessageHandler, filters

# Logging Setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Season အလိုက် Video File IDs (Array အဖြစ်သိမ်းမည်)
SEASON_DATA = {
    "season1": [
        "BAACAgUAAxkBAAMGaCtas2ETl0llBN08cAGyBI42juAAAuUWAAJ941lVk0ysVUV_LOI2BA",
        "BAACAgUAAxkBAAMHaCtazIYrZK15tgbl-sOHqqlCEAQAAgkXAAJ941lVm7Kbd2QFv1g2BA",
        "BAACAgUAAxkBAAMIaCta-gtuMEmMlSexGQjUjXKsv8gAAtEWAAIlOlFVvy5BCt2OyMY2BA"
    ],
    "season2": [
        "BAACAgUAAxkBAANlaCu0kfS64ldVW5xmhyqCSOWqkmoAAtYXAALEIlFVK2bMQwqBLjQ2BA",
        "BAACAgUAAxkBAANnaCu0tgszo-7F6r6G5E_cXcQBKxUAAmgHAAKkN4hUZyY4I3d5yWo2BA",
        "BAACAgUAAxkBAANpaCu01_cY-MUyiSJhZAFrgakwycoAArYNAAJyCEBX0AmFw77-2Yc2BA",
        "BAACAgUAAxkBAANqaCu0z1a2X3g5v4bq6Qe7m8r9c0AAtYXAALEIlFVK2bMQwqBLjQ2BA",
    ],
    "season3": [
        "VIDEO_FILE_ID_4",
        "VIDEO_FILE_ID_5",
        "VIDEO_FILE_ID_6"
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start command ကိုလက်ခံပြီး ကြိုဆိုစာသားပြမယ်"""
    await update.message.reply_text(
        """
    🎉 မင်္ဂလာပါ!
    ကျေးဇူးပြု၍ ဇာတ်လမ်းတွဲများကို အောက်ပါ Menu မှ ရွေးချယ်ပါ။
    """
    )

 # Main Menu Keyboard
    menu_keyboard = ReplyKeyboardMarkup(
        [["Season 1", "Season 2", "Season 3"]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    # စာသားနှင့် Menu ကို တစ်ပြိုင်နက်ပို့ပါ
    await update.message.reply_text(
        "📺 ဇာတ်လမ်းတွဲများကို ရွေးချယ်ပါ။",
        reply_markup=menu_keyboard
    )


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command ကိုလက်ခံပြီး အကူအညီစာသားပြမယ်"""
    await update.message.reply_text(
        """
    📖 အကူအညီ:
    - /start: Bot ကိုစတင်ပါ
    - /help: အကူအညီစာသားကိုကြည့်ပါ
    """
    )

async def send_season_episodes(update: Update, context: ContextTypes.DEFAULT_TYPE, season: str):
    """Season အလိုက် Video အားလုံးကို အလိုအလျောက်ပို့မည်"""
    episodes = SEASON_DATA.get(season, [])

    if not episodes:
        await update.message.reply_text(f"❌ {season} တွင် Video များမရှိသေးပါ။")
        return

    # Video အားလုံးကို အစဉ်လိုက်ပို့ပါ
    for index, video_id in enumerate(episodes, start=1):
        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_id,
                caption=f"🎥 {season} - Episode {index}"
            )
        except Exception as e:
            logger.error(f"Video ပို့ရာတွင် အမှားဖြစ်နေပါသည်: {e}")

    # ပြီးဆုံးကြောင်းအကြောင်းကြားပါ
    await update.message.reply_text(f"✅ {season} ဇာတ်လမ်းတွဲအားလုံးကို ပို့ပြီးပါပြီ။")

async def handle_season_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menu ကရွေးတဲ့ Season ကို ဖမ်းပြီး Video တွေပို့မယ်"""
    selected_text = update.message.text

    # "Season 1" => "season1" အဖြစ် ပြောင်းမယ်
    season_key = selected_text.lower().replace(" ", "")

    if season_key not in SEASON_DATA:
        await update.message.reply_text("❌ မရှိသော Season ဖြစ်နေပါသည်။")
        return

    # Video အားလုံးပို့မယ်
    episodes = SEASON_DATA[season_key]
    for index, video_id in enumerate(episodes, start=1):
        try:
            await context.bot.send_video(
                chat_id=update.effective_chat.id,
                video=video_id,
                caption=f"🎥 {selected_text} - Episode {index}"
            )
        except Exception as e:
            logger.error(f"Video ပို့ချက်အမှား: {e}")

    await update.message.reply_text(f"✅ {selected_text} ဇာတ်လမ်းတွဲအားလုံး ပို့ပြီးပါပြီ။")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Video ဖိုင်ရဲ့ File ID ကို ရယူပါ
    video_id = update.message.video.file_id
    await update.message.reply_text(f"📁 File ID: {video_id}")



def main():
    # Bot Token ထည့်ပါ
    application = Application.builder().token("7816726849:AAGgO81NBHs-jMyceLne6EPVo0yGswBHXQQ").build()

    # Command Handlers များကို အလိုအလျောက်ဖန်တီးပါ
    for season in SEASON_DATA.keys():
        application.add_handler(
            CommandHandler(
                season,
                lambda update, context, s=season: send_season_episodes(update, context, s)
            )
        )

    # Start Command
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_season_selection))
    application.add_handler(MessageHandler(filters.VIDEO, handle_video))
    application.add_handler(CommandHandler("help", help))
    print(" Bot is running...")
    application.run_polling()

if __name__ == "__main__":
    main()
