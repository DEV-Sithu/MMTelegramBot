import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuration
TELEGRAM_BOT_TOKEN = 'your_telegram_bot_token'  # Telegram Bot Token
OPENROUTER_API_KEY = 'your open router api key for deepseek'  # OpenRouter API Key
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# System Prompt for Translation
TRANSLATION_PROMPT = """
ကျေးဇူးပြု၍ ဘာသာပြန်ဆိုသူအဖြစ်လုပ်ဆောင်ပါ။ မြန်မာဘာသာစကားမှ အင်္ဂလိပ်ဘာသာသို့ (သို့မဟုတ်) အင်္ဂလိပ်ဘာသာမှ မြန်မာဘာသာသို့ အလိုအလျောက်ပြန်ဆိုပေးပါ။
ဘာသာပြန်ခြင်းများကို သဘာဝကျပြီး နားလည်လွယ်အောင်ပြန်ဆိုပေးပါ။
Please act as a translator between Myanmar (Burmese) and English. Automatically detect the input language and translate to the other language.
"""

# Telegram Bot Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ဘာသာပြန်ဘော့ကို အသုံးပြုရန်ကြိုဆိုပါသည်။\n"
        "မြန်မာစာ သို့မဟုတ် အင်္ဂလိပ်စာပို့ပါ၊ အလိုအလျောက်ပြန်ဆိုပေးပါမည်။\n"
        "Welcome! Send me text in Myanmar or English for auto-translation."
    )

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ဘာသာပြန်ဘော့ကို အသုံးပြုရန်ကြိုဆိုပါသည်။\n"
        "မြန်မာစာ သို့မဟုတ် အင်္ဂလိပ်စာပို့ပါ၊ အလိုအလျောက်ပြန်ဆိုပေးပါမည်။\n"
        "Welcome! Send me text in Myanmar or English for auto-translation."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    if not user_text.strip():
        await update.message.reply_text("ကျေးဇူးပြု၍ စာသားတစ်ခုခုပို့ပါ။\nPlease send some text.")
        return
    
    try:
        # OpenRouter API အတွက် ပြင်ဆင်ခြင်း
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://dev-sithu.github.io/skybit_studio_17", # မရှိမဖြစ်လိုအပ်သည်
            "X-Title": "Myanmar Translator Bot" # ရွေးချယ်နိုင်သော header
        }

     # ပြင်ဆင်ပြီး payload
        payload = {
       "model": "deepseek/deepseek-chat-v3-0324:free",
        "messages": [
         {"role": "system", "content": "You are a professional translator between Myanmar (Burmese) and English. Accurately detect input language and translate naturally."},
         {"role": "user", "content": user_text}  # "Translate this:" ကိုဖြုတ်
          ],
           "temperature": 0.3
         }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        
        # HTTP Error များအတွက် စစ်ဆေးခြင်း
        if response.status_code != 200:
            error_detail = response.json().get('error', {}).get('message', 'Unknown error')
            raise Exception(f"API Error ({response.status_code}): {error_detail}")

        # Response ကို စစ်ဆေးခြင်း
        result = response.json()
        if not result.get('choices'):
            raise Exception("No translation found in response")
        
        translated_text = result['choices'][0]['message']['content']
        await update.message.reply_text(f"Translation:\n{translated_text}")

    except Exception as e:
        error_msg = f"⚠️ ဘာသာပြန်မှုမအောင်မြင်ပါ\nError: {str(e)}"
        await update.message.reply_text(error_msg)
        print(f"API Error: {e}\nFull Response: {response.text if 'response' in locals() else ''}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Command Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))  # Same as start
    
    # Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot running...")
    app.run_polling()

if __name__ == "__main__":
    main()

