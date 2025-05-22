import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ Telegram Bot Token
BOT_TOKEN = "your_bot_token"

# ✅ Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ✅ Country/Flag/Currency Map
CURRENCIES = {
    "USD": ("🇺🇸", "US Dollar"),
    "EUR": ("🇪🇺", "Euro"),
    "SGD": ("🇸🇬", "Singapore Dollar"),
    "THB": ("🇹🇭", "Thai Baht"),
    "JPY": ("🇯🇵", "Japanese Yen"),
    "CNY": ("🇨🇳", "Chinese Yuan"),
    "KRW": ("🇰🇷", "South Korean Won"),
    "VND": ("🇻🇳", "Vietnamese Dong"),
    "MYR": ("🇲🇾", "Malaysian Ringgit"),
    "LAK": ("🇱🇦", "Lao Kip"),
    "GBP": ("🇬🇧", "British Pound"),
    "AUD": ("🇦🇺", "Australian Dollar"),
    "NZD": ("🇳🇿", "New Zealand Dollar"),
    "INR": ("🇮🇳", "Indian Rupee"),
    "KHR": ("🇰🇭", "Cambodian Riel"),
}

# ✅ Exchange Rate Fetcher
def get_exchange_table():
    url = "https://forex.cbm.gov.mm/api/latest"
    try:
        response = requests.get(url)
        data = response.json()
        rates = data["rates"]
    except Exception:
        return "❌ ဒေတာရယူမှုမအောင်မြင်ပါ။"

    table = "📊 CBM ငွေလဲနှုန်းများ (MMK)\n\n"
    table += f"{'Flag':<3} {'Currency':<20} {'Rate (MMK)':>12}\n"
    table += "─" * 40 + "\n"

    for code, (flag, name) in CURRENCIES.items():
        rate = rates.get(code)
        if rate:
            table += f"{flag} {name:<20} {rate:>10} MMK\n"

    return table

# ✅ /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 မင်္ဂလာပါ! ငွေလဲနှုန်းစစ်ရန် /rate ကို သုံးပါ။")

# ✅ /rate command
async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    table = get_exchange_table()
    await update.message.reply_text(table)

# ✅ Main Bot App
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("rate", rate))

    print("🤖 Telegram CBM Bot is running...")
    app.run_polling()
