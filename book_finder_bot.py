from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext  import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
from google.oauth2.service_account import Credentials
import gspread
from telegram import Update
import re
import traceback

# Google Sheets setup
SCOPES = [ 'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file("creds.json", scopes=SCOPES)
client = gspread.authorize(creds)
sheet_id = 'your sheet id'
sheet = client.open_by_key(sheet_id).worksheet("Books")
books = sheet.get_all_records()

# Telegram bot setup
BOT_TOKEN = "bot api token"
CHANNEL_USERNAME = "your channel id"  # Channel ID မှန်ကန်ပါစေ

async def post_init(application):

    """Send initial message to channel when bot starts"""
    try:
        # Button ကို URL နဲ့ပြောင်းသုံးထားပါတယ်
        keyboard = [
            [InlineKeyboardButton("🔍 စာအုပ်ရှာဖွေရန်...", url="https://t.me/yourBot?start=search")],
            [InlineKeyboardButton("📚 စာအုပ်အမျိုးအစားများကြည့်ရန်....", url="https://t.me/yourBot?start=booklist")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await application.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text="👋နည်းပညာစာအုပ်များစွာရှိပါသည် \n စာအုပ်များအားရှာ‌ရလွယ်အောင် အကူဘော့လေးအား အသုံးနိုင်ပါသည်",
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Channel message error: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Start command ကို deep linking အတွက် update
    args = context.args
    if args and args[0] == "search":
        await update.message.reply_text("ရှာဖွေလိုသော စာအုပ်အမည်ကို ရိုက်ထည့်ပါ။\nဥပမာ: /search programming")
    elif args[0] == "booklist":
            await book_list(update, context)  # စာအုပ်စာရင်းပြသည့် function ကိုခေါ်
    else:
        await update.message.reply_text(
            "မဂ်လာပါ ကျွန်တော်က တော့ စာအုပ်လေးတွေရှာရလွယ်အောင် ကူညီပေးမဲ့ စက်ရုပ်လေးပါ ။ လူကြီးမင်းတို့ ရှာချင်တဲ့စာအုပ်အမည်ကိူ (/search စာအုပ်အမည်) ပုံစံဖြင့် ပြောပေးပါ မြန်မြန်ဆန်ဆန်ရှာပေးပါမည်" )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🤖 **စာအုပ်ရှာဖွေရန် Bot အသုံးပြုနည်း**\n\n"
        "အောက်ပါ command များကို အသုံးပြုနိုင်ပါတယ် -\n\n"
        "🔹 /start - Bot ကို စတင်အသုံးပြုရန်\n"
        "🔹 /help - ဤအကူအညီစာမျက်နှာကို ပြသရန်\n"
        "🔹 /search <စာအုပ်အမည်> - စာအုပ်ရှာရန်\n"
        "   ဥပမာ - `/search Python` သို့မဟုတ် `/search ကွန်ပျူတာ`\n\n"
        "🔹 /booklist - စာအုပ်အမျိုးအစားများ ကြည့်ရန်\n"
        "   (အမျိုးအစားရွေးပြီး စာအုပ်စာရင်းကြည့်နိုင်ပါတယ်)\n\n"
       
    )
    
    await update.message.reply_text(
        text=help_text,
        parse_mode='Markdown'  # Markdown formatting ကိုဖွင့်ထားပါ
    )

def search_books(query):
    query_lower = query.lower()
    return [book for book in books
            if query_lower in book['title'].lower() or
            query_lower in book['author'].lower() or
            query_lower in book['category'].lower()]
            

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = ' '.join(context.args)
    if not query:
        await update.message.reply_text("ရှာဖွေရန် စာအုပ်အမည် သို့မဟုတ် အမျိုးအစား ရိုက်ထည့်ပါ။")
        return

    results = search_books(query)

    if not results:
        await update.message.reply_text("ရှာဖွေမှုအတွက် မတွေ့ပါ။")
        return

    response = "စာအုပ်တွေကို ရှာတွေ့ပါပြီ:\n\n"
    for book in results:
        response += (
            f"📚 စာအုပ်အမည်: {book['title']}\n"
            f"👤 စာရေးသူ: {book['author']}\n"
            f"🏷️ အမျိုးအစား: {book['category']}\n"
            f"🔗 လင့်ခ်: {book['link']}\n\n"
        )

    # စာတိုလွှာမဖြစ်အောင် split လုပ်ပေးခြင်း
    if len(response) > 4096:
        for x in range(0, len(response), 4096):
            await update.message.reply_text(response[x:x+4096])
    else:
        await update.message.reply_text(response)
 

# Conversation states
TITLE, AUTHOR, CATEGORY, LINK = range(4)

async def add_book(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("စာအုပ်အမည်ရိုက်ထည့်ပါ:")
    return TITLE

async def title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("စာရေးသူအမည်ရိုက်ထည့်ပါ:")
    return AUTHOR

async def author(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['author'] = update.message.text
    await update.message.reply_text("အမျိုးအစားရိုက်ထည့်ပါ:")
    return CATEGORY

async def category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['category'] = update.message.text
    await update.message.reply_text("လင့်ခ်ရိုက်ထည့်ပါ:")
    return LINK

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['link'] = update.message.text

    # Google Sheet ထဲထည့်ခြင်း
    new_row = [
        context.user_data['title'],
        context.user_data['author'],
        context.user_data['category'],
        context.user_data['link']
    ]
    sheet.append_row(new_row)

    await update.message.reply_text("စာအုပ်အသစ်ထည့်သွင်းပြီးပါပြီ!")
    return ConversationHandler.END

# Cancel handler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("စာအုပ်ထည့်သွင်းမှုကို ပယ်ဖျက်လိုက်ပါပြီ။")
    return ConversationHandler.END
# Add conversation handler
conv_handler = ConversationHandler(
    entry_points=[CommandHandler('addbook', add_book)],
    states={
        TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, title)],
        AUTHOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, author)],
        CATEGORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, category)],
        LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, link)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        post = update.channel_post

        # Message ID ရယူပါ
        message_id = post.message_id

        # Caption မှ အချက်အလက်များဖတ်ပါ
        caption = post.caption or ""
        match = re.search(
            r"စာအုပ်အမည်[=:]?\s*(.+?)\s*"
            r"စာရေးသူ[=:]?\s*(.+?)\s*"
            r"အမျိုးအစား[=:]?\s*(.+)",
            caption,
            re.DOTALL
        )

        if not match:
            print("❌ Caption Format မှားနေပါတယ်")
            return

        title, author, category = match.groups()
        title = title.strip()
        author = author.strip()
        category = category.strip()

        # PDF Link ရယူပါ
        file_id = post.document.file_id
        file = await context.bot.get_file(file_id)
        link = f"https://t.me/yourchannel/{message_id}"

        # Google Sheet သို့ Message ID နှင့်တကွ သိမ်းပါ
        sheet.append_row([message_id, title, author, category, link])
        print(f"✅ သိမ်းဆည်းပြီး | ID: {message_id}")

    except Exception as e:
        print(f"🔥 အမှား: {str(e)}")
# Bot စတင်တဲ့အခါ Background Task ကို စတင်ပါ
    try:
        # (1) Edited Post နှင့် PDF ဖိုင်စစ်ပါ
        edited_post = update.edited_channel_post
        if not edited_post or not edited_post.document:
            print("❌ Edited Post သို့မဟုတ် PDF မရှိပါ")
            return

        # (2) MIME Type စစ်ပါ
        if edited_post.document.mime_type != "application/pdf":
            return

        # (3) Message ID ရယူပါ
        message_id = edited_post.message_id
        print(f"✏️ Edit တွေ့ရှိ: {message_id}")

        # (4) Caption မှအချက်အလက်ဖတ်ပါ
        caption = edited_post.caption or ""
        match = re.search(
            r"📚 စာအုပ်အမည်:\s*(.+?)\s*"
            r"✍️ စာရေးသူ:\s*(.+?)\s*"
            r"📖 အမျိုးအစာ:\s*(.+?)\s*",
            caption,
            re.DOTALL
        )
        if not match:
            print("❌ Caption Format မှားနေပါတယ်")
            return

        title, author, category = match.groups()
        title = title.strip()
        author = author.strip()
        category = category.strip()

        # (5) PDF Link ရယူပါ
        file_id = edited_post.document.file_id
        file = await context.bot.get_file(file_id)
        link = f"https://t.me/yourchannel/{message_id}"

        # (6) Google Sheet Update
        cell = sheet.find(str(message_id))
        if cell:
            row = cell.row
            sheet.update(f"B{row}", title)    # Title
            sheet.update(f"C{row}", author)   # Author
            sheet.update(f"D{row}", category) # Category
            sheet.update(f"E{row}", link) # Link
            print(f"✅ Update ပြီးပါပြီ | ID: {message_id}")
    except Exception as e:
       # print(f"🔥 အမှား: {str(e)}")
        print(f"Full Error: {traceback.format_exc()}")  # Debug အတွက်


async def handle_edited_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        edited_post = update.edited_channel_post
        if not edited_post or not edited_post.document:
            return

        # Message ID ရယူပါ
        message_id = edited_post.message_id

        # Sheet မှာ Message ID ရှာပါ
        cell = sheet.find(str(message_id))
        if not cell:
            print(f"❌ Message ID {message_id} ကို Sheet မှာမတွေ့ပါ")
            return

        row = cell.row

        # Caption မှအချက်အလက်ဖတ်ပါ
        caption = edited_post.caption or ""
        match = re.search(
            r"စာအုပ်အမည်[=:]?\s*(.+?)\s*"
            r"စာရေးသူ[=:]?\s*(.+?)\s*"
            r"အမျိုးအစား[=:]?\s*(.+)",
            caption,
            re.DOTALL
        )
        if not match:
            return

        title, author, category = match.groups()
        title = title.strip()
        author = author.strip()
        category = category.strip()

        # PDF Link ရယူပါ
        file_id = edited_post.document.file_id
        file = await context.bot.get_file(file_id)
        link = f"https://t.me/yourchannel/{message_id}"

        # တစ်ခုချင်းစီ Update လုပ်ပါ
        sheet.update_cell(row, 2, title)    # Column B
        sheet.update_cell(row, 3, author)   # Column C
        sheet.update_cell(row, 4, category) # Column D
        sheet.update_cell(row, 5, link) # Column E
        print(f"✅ Updated: {message_id}")

    except Exception as e:
        print(f"🔥 အမှား: {str(e)}")
        import traceback  # ဒါကို ဖိုင်အစမှာ import လုပ်ပါ
        print(f"Full Traceback: {traceback.format_exc()}")


# /booklist command ကို process လုပ်မယ့် function
async def book_list(update: Update, context: CallbackContext):
    # Google Sheet မှ စာအုပ်စာရင်းအားလုံးကို အသစ်ပြန်ဖတ်ပါ
    sheet = client.open_by_key(sheet_id).worksheet("Books")
    books = sheet.get_all_records()

    # Category များကို အလိုအလျောက်ထုတ်ယူပါ (ထပ်နေလျှင် ၁ခါသာ ပြပါ)
    categories = list({book['category'] for book in books})

    # Category ခလုတ်များ ဖန်တီးခြင်း
    buttons = [
        [InlineKeyboardButton(category, callback_data=f"category_{category}")]
        for category in categories
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    # Message ပို့ပါ
    await update.message.reply_text("📚 စာအုပ်အမျိုးအစားရွေးပါ:", reply_markup=reply_markup)


async def handle_category_click(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("category_"):
        try:
            category = data.split("_", 1)[1]
            results = search_books(category)
            if not results:
                await query.edit_message_text("⚠️ ရှာဖွေမှုအတွက် မတွေ့ပါ။")
                return


            response = "စာအုပ်တွေကို ရှာတွေ့ပါပြီ:\n\n"
            for book in results:
             response += (
             f"📚 စာအုပ်အမည်: {book['title']}\n"
             f"👤 စာရေးသူ: {book['author']}\n"
             f"🏷️ အမျိုးအစား: {book['category']}\n"
             f"🔗 လင့်ခ်: {book['link']}\n\n"  )

            # နောက်ပြန်ခလုတ်နဲ့အတူ ပြပါ
             back_button = [[InlineKeyboardButton("🔙 နောက်သို့", callback_data="back_to_categories")]]
             reply_markup = InlineKeyboardMarkup(back_button)

             await query.edit_message_text(
                f"🔍 ရှာဖွေမှု: {category}\n\n{response}",
                reply_markup=reply_markup
             )

        except Exception as e:
            await query.edit_message_text(f"⚠️ အမှားတစ်ခုဖြစ်နေပါတယ်: {str(e)}")


# နောက်ပြန်ခလုတ်ကို စီမံမယ့် function
async def handle_back_button(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()  # Loading indicator ပိတ်ရန်

    try:
        # Google Sheet မှ အသစ်ပြန်ဖတ်ပါ
        sheet = client.open_by_key(sheet_id).worksheet("Books")
        books = sheet.get_all_records()

        # Category များကို အလိုအလျောက်ထုတ်ယူပါ (ထပ်နေလျှင် ၁ခါသာ ပြပါ)
        categories = list({book['category'] for book in books})

        # Category ခလုတ်များ ဖန်တီးခြင်း
        buttons = [
            [InlineKeyboardButton(category, callback_data=f"category_{category}")]
            for category in categories
        ]
        reply_markup = InlineKeyboardMarkup(buttons)

        # လက်ရှိ message ကို edit လုပ်ပါ
        await query.edit_message_text(
            text="📚 စာအုပ်အမျိုးအစားရွေးပါ:",
            reply_markup=reply_markup
        )
    except Exception as e:
        await query.edit_message_text("⚠️ အမှားတစ်ခုဖြစ်နေပါတယ်။ နောက်မှပြန်ကြိုးစားပါ။")
        print(f"Error in back button: {str(e)}")

# Build and configure application
app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("booklist", book_list))

app.add_handler(conv_handler)
# (1) အသစ်တင်သော PDF Post များအတွက် Handler
app.add_handler(
    MessageHandler(
        filters.ChatType.CHANNEL &
        filters.UpdateType.CHANNEL_POST &  # CHANNEL_POST (အများကိန်း မဟုတ်)
        filters.Document.PDF,
        handle_channel_post
    )
)

# (2) Edit လုပ်ထားသော PDF Post များအတွက် Handler
app.add_handler(
    MessageHandler(
        filters.ChatType.CHANNEL &
        filters.UpdateType.EDITED_CHANNEL_POST &
        filters.Document.PDF,
        handle_edited_post
    )
)
app.add_handler(CallbackQueryHandler(handle_category_click, pattern="^category_"))
app.add_handler(CallbackQueryHandler(handle_back_button, pattern="^back_to_categories"))

# Start polling
print("🤖 Bot running...")
app.run_polling()
