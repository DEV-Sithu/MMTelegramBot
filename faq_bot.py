from telegram import Update, ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup,InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
from telegram.constants import ParseMode
import logging

# Logging စနစ်ကို စတင်ခြင်း
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ဖုန်းဆိုင်အတွက် FAQ အချက်အလက်များ (မေးခွန်း 30ခု)
FAQ = [
    {
        "question": "ဖုန်းပြင်ဆင်ချိန် ဘယ်လောက်ကြာမလဲ?",
        "answer": "ပျမ်းမျှပြင်ဆင်ချိန် ၁နာရီမှ ၃နာရီအတွင်း (ပြဿနာအလိုက် ကွဲပြားမှုရှိနိုင်ပါသည်)"
    },
    {
        "question": "အာမခံသက်တမ်း ဘယ်လောက်ရှိပါသလဲ?",
        "answer": "ပြင်ဆင်မှုအမျိုးအစားအလိုက် ၁၅ရက်မှ ၃လအထိ အာမခံပေးထားပါသည်"
    },
    {
        "question": "ဖုန်းအမျိုးအစားအားလုံးကို ပြင်ပေးပါသလား?",
        "answer": "Android နှင့် iOS ဖုန်းအားလုံးကို ပြင်ဆင်ပေးပါသည်။ တရားဝင်မဟုတ်သော ဖုန်းများအတွက် ဝန်ဆောင်မှုမပေးနိုင်ပါ"
    },
    {
        "question": "ပြင်ဆင်ခကို ဘယ်လိုသိရှိနိုင်မလဲ?",
        "answer": "အခမဲ့ပြဿနာရှာဖွေပေးပြီး ပြင်ဆင်မည့်ကုန်ကျစရိတ်ကို ကြိုတင်တွက်ချက်ပေးပါမည်"
    },
    {
        "question": "ဆက်သွယ်ရန် ဖုန်းနံပါတ်",
        "answer": "၀၉-၉၁၂၃၄၅၆၇၈, ၀၉-၇၆၅၄၃၂၁၀၁ (နေ့စဉ် မနက်၉နာရီမှ ည၈နာရီအထိ)"
    },
    {
        "question": "ဆိုင်ခွဲများ ဘယ်နေရာတွေမှာရှိပါသလဲ?",
        "answer": "ရန်ကုန် - ဗဟန်း၊ မန္တလေး - ၈၀လမ်း၊ မကွေး - ဈေးခြိုက်ဆိုင်လမ်း"
    },
    {
        "question": "အချိန်မှန်ယူချင်ပါတယ်",
        "answer": "ကျေးဇူးပြု၍ ဖုန်းဖြင့်ချိန်းဆိုပါ (သို့) အွန်လိုင်းမှတစ်ဆင့် ရက်ချိန်းယူနိုင်ပါသည် - https://example.com/booking"
    },
    {
        "question": "အစားထိုးပစ္စည်းများ ရှိပါသလား?",
        "answer": "မူရင်းပစ္စည်းများနှင့် အရည်အသွေးမြင့် ပစ္စည်းများကို စတော့အပြည့်ဖြင့် ဝယ်ယူနိုင်ပါသည်"
    },
    {
        "question": "ပြင်ပြီးသား ဖုန်းတွေကို ပြန်ယူနိုင်ချိန်",
        "answer": "တနင်္လာမှ စနေနေ့အထိ မနက်၁၀နာရီမှ ည၇နာရီအထိ ပြန်လည်ရယူနိုင်ပါသည်"
    },
    {
        "question": "အရေးပေါ်ဝန်ဆောင်မှုရှိပါသလား?",
        "answer": "အရေးပေါ်ဝန်ဆောင်မှုအနေဖြင့် ၂၄နာရီ ဖုန်းပြင်ဆင်ဝန်ဆောင်မှုပေးပါသည် (အပိုကုန်ကျစရိတ် ၁၀,000ကျပ် ကျသင့်မည်)"
    },
    {
        "question": "ဖုန်းအပူကြီးနေရင် ပြင်ပေးပါသလား?",
        "answer": "အပူလွန်ကဲမှုပြဿနာများကို ကျွမ်းကျင်နည်းလမ်းဖြင့် စစ်ဆေးပြင်ဆင်ပေးပါသည်"
    },
    {
        "question": "ဖုန်းရေစိုသွားရင် ဘယ်လိုလုပ်ရမလဲ?",
        "answer": "ချက်ချင်းပါဝါပိတ်ပြီး ကျွန်ုပ်တို့ဆိုင်သို့ အမြန်ဆုံးယူလာပါ (ရေစိုပြီး ၂၄နာရီအတွင်း အမြန်ဝန်ဆောင်မှု)"
    },
    {
        "question": "ဘက်ထရီပြဿနာများအတွက် ဝန်ဆောင်မှု",
        "answer": "ဘက်ထရီအစားထိုးခြင်း၊ အားသွင်းမှုပြဿနာများကို ကျွမ်းကျင်စွာဖြေရှင်းပေးပါသည်"
    },
    {
        "question": "ဖုန်းဖန်သားပြင်ပြောင်းဖို့ ကုန်ကျစရိတ်",
        "answer": "ဖန်သားပြင်အရွယ်အစားနှင့် ဖုန်းအမျိုးအစားအလိုက် 50,000ကျပ်မှ 300,000ကျပ်အထိ"
    },
    {
        "question": "ဒေတာများ ပြန်လည်ရယူနိုင်ပါသလား?",
        "answer": "ဖုန်းပျက်စီးမှုအဆင့်ပေါ်မူတည်၍ 80% အထိ ဒေတာများပြန်လည်ရယူနိုင်ပါသည်"
    },
    {
        "question": "ဆော့ဖ်ဝဲပြဿနာများကို ဖြေရှင်းပေးပါသလား?",
        "answer": "အန်းဒရွိုက်ဖ်ြနောင့်ရှင်းခြင်း၊ iOSဗားရှင်းအဆင့်မြှင့်တင်ခြင်းစသည့် ဝန်ဆောင်မှုများပေးပါသည်"
    },
    {
        "question": "ဝယ်ယူထားသော ပစ္စည်းများ ပြန်လည်လဲလှယ်နိုင်ပါသလား?",
        "answer": "အာမခံသက်တမ်းအတွင်း ပစ္စည်းချို့ယွင်းပါက အခမဲ့လဲလှယ်ပေးပါသည်"
    },
    {
        "question": "ဖုန်းအဟောင်းလဲလှယ်ဝန်ဆောင်မှုရှိပါသလား?",
        "answer": "ဖုန်းအဟောင်းများကို ဈေးနှုန်းသတ်မှတ်ချက်ဖြင့် လဲလှယ်ဝယ်ယူပေးပါသည်"
    },
    {
        "question": "ချက်ချင်းပြင်ဆင်နိုင်သော ပြဿနာများ",
        "answer": "ဘက်ထရီပြောင်းခြင်း၊ ဆင်မြူလေတိုက်ခြင်း၊ ဖန်သားပြင်ကွက်ကျားပြဿနာများ စသည်တို့ကို ၁နာရီအတွင်း ပြင်ဆင်ပေးပါသည်"
    },
    {
        "question": "အွန်လိုင်းမှတစ်ဆင့် ငွေပေးချေနိုင်ပါသလား?",
        "answer": "KBZ Pay, Wave Money, CB Pay စသည့် ဒီဂျစ်တယ်ငွေပေးချေမှုစနစ်များဖြင့် လက်ခံပါသည်"
    },
    {
        "question": "အသုံးပြုထားသော ပစ္စည်းများ ရှိပါသလား?",
        "answer": "အရည်အသွေးအာမခံထားသော ပြန်လည်ပြုပြင်ထားသည့် ပစ္စည်းများကို စျေးနှုန်းသက်သာစွာဖြင့် ရရှိနိုင်ပါသည်"
    },
    {
        "question": "ဖုန်းအရောင်းဝန်ဆောင်မှုရှိပါသလား?",
        "answer": "အသစ်နှင့်အသုံးပြုထားသော ဖုန်းများကို အာမခံပါဝင်သည့် စျေးနှုန်းဖြင့် ရောင်းချပေးပါသည်"
    },
    {
        "question": "ဖုန်းသော့ဖွင့်ဝန်ဆောင်မှုပေးပါသလား?",
        "answer": "တရားဝင်ဖုန်းများအတွက် သော့ဖွင့်ဝန်ဆောင်မှုပေးပါသည် (အထောက်အထားလိုအပ်ပါသည်)"
    },
    {
        "question": "ပစ္စည်းမှာယူဝယ်ယူနိုင်ပါသလား?",
        "answer": "အွန်လိုင်းမှတစ်ဆင့် မှာယူနိုင်ပြီး အိမ်အရောက်ပို့ဆောင်ပေးပါသည်"
    },
    {
        "question": "အထူးပရိုမိုရှင်းများရှိပါသလား?",
        "answer": "ပွဲတော်ရက်များတွင် 10% မှ 30% အထိ လျှော့စျေးများ ရရှိနိုင်ပါသည်"
    },
    {
        "question": "ပြင်ဆင်ပြီးဖုန်းများကို အာမခံပေးပါသလား?",
        "answer": "ပြင်ဆင်မှုတိုင်းကို 15 ရက်အာမခံပေးပါသည်"
    },
    {
        "question": "ဖုန်းအတွင်းပိုင်းပြဿနာများကို စစ်ဆေးပေးပါသလား?",
        "answer": "အခမဲ့ဆားကစ်ဘုတ်စစ်ဆေးမှုဝန်ဆောင်မှုပေးပါသည်"
    },
    {
        "question": "ဆက်သွယ်ရန်လိပ်စာ",
        "answer": "အမှတ် ၁၂၃၊ မြို့မလမ်း၊ ရန်ကုန်မြို့။ ဖုန်း - ၀၉ ၇၈၉၀၁၂၃၄၅"
    },
    {
        "question": "အလုပ်လုပ်ချိန်များ",
        "answer": "တနင်္လာ-သောကြာ : ၉:၀၀ - ၂၀:၀၀\nစနေ-တနင်္ဂနွေ : ၉:၀၀ - ၁၇:၀၀"
    }
]


BOT_USERNAME = "MK_FaqBot"  # Don't include @



async def send_bot_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = f"https://t.me/{BOT_USERNAME}?start"
    keyboard = [
        [InlineKeyboardButton("🤖 Bot သို့သွားရန်", url=url)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "FAQ များအတွက် Bot နှင့်ဆက်သွယ်ပါ:",
        reply_markup=reply_markup
    )

def private_keyboard():
    """Private Chat အတွက် Reply Keyboard"""
    buttons = [KeyboardButton(q["question"]) for q in FAQ]
    keyboard = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )


# Keyboard Generators
def channel_keyboard():
    """Channel အတွက် Inline Keyboard"""
    buttons = [
        InlineKeyboardButton(q["question"], callback_data=f"faq_{idx}")  # "q" ကို "question" အဖြစ်ပြင်ဆင်
        for idx, q in enumerate(FAQ)
    ]
    return InlineKeyboardMarkup([buttons[i:i+2] for i in range(0, len(buttons), 2)])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start command handler"""
    # Group သို့မဟုတ် Supergroup ဖြစ်လျှင် Bot Link ပေးမည်
    chat_type = update.message.chat.type
    if chat_type in ['group', 'supergroup']:
        await send_bot_link(update, context)
        return  # ဆက်လက်လုပ်ဆောင်ခြင်းကို ရပ်တန့်ရန်

    # Private Chat အတွက် ပုံမှန်စနစ်
    reply_markup = private_keyboard()
    
    welcome_text = (
        "📱 **ဖုန်းဆိုင်ဝန်ဆောင်မှုသို့ ကြိုဆိုပါသည်**\n\n"
        "အောက်ပါမေးခွန်းများထဲမှ ရွေးချယ်နိုင်ပါသည်။"
    )
  
    await update.message.reply_text(
        text=welcome_text,
        reply_markup=reply_markup,
        parse_mode="MarkdownV2"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inline Keyboard အတွက် Response"""
    query = update.callback_query
    idx = int(query.data.split("_")[1])
    
    await query.answer()
    await query.edit_message_text(
        text=f"❓ **မေးခွန်း:** {FAQ[idx]['question']}\n\n💡 **အဖြေ:** {FAQ[idx]['answer']}",  # Keys ပြင်ဆင်
        parse_mode=ParseMode.MARKDOWN_V2
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle private chat messages"""
    user_msg = update.message.text
    for entry in FAQ:
        if user_msg == entry["question"]:  # Fixed key
            await update.message.reply_text(
                f"**{entry['question']}**\n\n{entry['answer']}",  # Fixed keys
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
    
    await update.message.reply_text("ကျေးဇူးပြု၍ ပေးထားသောစာရင်းမှ ရွေးချယ်ပါ။")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 *Bot Command List*\n\n"
        "/start - Bot ကိုစဖွင့်ပါ\n"
        "/faq - မေးလေ့ရှိတဲ့မေးခွန်းများကိုကြည့်ရန်\n"
        "/help - ဤ command list ကိုပြရန်\n"
        "/contact - Admin ကိုဆက်သွယ်ရန်\n"
        "/about - Bot ၏အကြောင်းအရာ\n"
    )

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def contact_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "📞 *Admin Contact*\n\n"
        "ဖုန်း - ၀၉-၇၈၉၀၁၂၃၄၅\n"
        "အီးမေးလ် - mmm@gmail.com\n"
        "Facebook - [MK Phone Service](https://www.facebook.com/MKPhoneService)\n"  
        "Instagram - [MK Phone Service](https://www.instagram.com/MKPhoneService)\n"
        "Website - [MK Phone Service](https://www.mkphoneservice.com)\n"
        "Telegram - [MK Phone Service](https://t.me/MKPhoneService)\n"
        "YouTube - [MK Phone Service](https://www.youtube.com/MKPhoneService)\n"
        "Twitter - [MK Phone Service](https://twitter.com/MKPhoneService)\n"
        "LinkedIn - [MK Phone Service](https://www.linkedin.com/company/mkphoneservice)\n"
    )
    await update.message.reply_text(contact_text, parse_mode="Markdown")
    

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    about_text = (
        "🤖 *About This Bot*\n\n"
        "ဤ Bot သည် ဖုန်းပြင်ဆင်ခြင်းနှင့် ဆိုင်ခွဲများအကြောင်း အထောက်အကူပြုရန် ဖန်တီးထားသည်။\n"
        "ဖုန်းပြင်ဆင်ခြင်း၊ အစားထိုးပစ္စည်းများ၊ ဝန်ဆောင်မှုများနှင့် ပတ်သက်၍ မေးခွန်းများကို ရှာဖွေရန် အသုံးပြုနိုင်ပါသည်။\n"
        "Bot ကို အသုံးပြုရန် အထောက်အကူပြုပါသည်။"
    )
    await update.message.reply_text(about_text, parse_mode="Markdown")      


def main() -> None:
    """Bot ကို စတင်အလုပ်လုပ်မည့် function"""
    # Bot Token ထည့်ပါ
    application = Application.builder().token("bot api token").build()
    
    # Handlers များ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("faq", send_bot_link))
    application.add_handler(CommandHandler("contact", contact_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,handle_message))
      # Add callback handler
    application.add_handler(CallbackQueryHandler(handle_callback))
    # Bot ကို Run ပါ
    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
