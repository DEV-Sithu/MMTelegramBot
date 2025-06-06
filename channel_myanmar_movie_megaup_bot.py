import os
import asyncio
from dotenv import load_dotenv
from contextlib import asynccontextmanager
import re
from fastapi import FastAPI, Request
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters
import httpx
import time
import uuid
import asyncio
from typing import Dict
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO  # Or DEBUG for more detail
)
logger = logging.getLogger(__name__)

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")
webhook_url = os.getenv("WEBHOOK_URL")
port = int(os.getenv("PORT", 8080))

bot = Client("cm_bypass_bot", api_id=api_id,
             api_hash=api_hash, bot_token=bot_token)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.start()
    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"https://api.telegram.org/bot{bot_token}/setWebhook",
            data={"url": webhook_url},
        )
        print("Webhook set:", res.json())
    yield
    await bot.stop()
    print("Bot stopped.")

app = FastAPI(lifespan=lifespan)

# In-memory token store
token_store: Dict[str, Dict] = {}

# --- UTIL FUNCTION ---


def generate_token(chat_id: int, url: str) -> str:
    token = str(uuid.uuid4())
    token_store[token] = {
        "chat_id": chat_id,
        "url": url,
        "verified": False,
        "created_at": time.time()
    }
    return token


@app.get("/")
async def root():
    return {"message": "App running with Playwright + Xvfb on Render!"}
# --- Step 1: Extract download options from CM post ---


async def get_download_options(movie_url):
    async with httpx.AsyncClient() as client:
        r = await client.get(movie_url)
        soup = BeautifulSoup(r.text, "html.parser")
        domains = [
            "megaup.net",
        ]
        options = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if any(domain in href for domain in domains):
                text = a.get_text(strip=True)
                domain = next((d for d in domains if d in href), None)
                resolution = ""
                parent_text = a.find_parent().get_text(" ", strip=True)
                match = re.search(r"(480p|720p|1080p|2160p)",
                                  parent_text, re.IGNORECASE)
                if match:
                    resolution = match.group(1).upper()
                clean_name = f"{domain.replace('.com', '').replace('.net', '').capitalize()} {resolution}".strip(
                )
                options.append({"name": clean_name, "url": href})
        return options

# --- Step 2: Telegram Handlers ---
user_download_cache = {}


@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("🌐 Channel Myanmar Website ဖွင့်ရန်", url="https://www.channelmyanmar.to")
        ]]
    )
    await message.reply(
        "👋 ကြိုဆိုပါတယ်!\n\n"
        "ChannelMyanmar movie download link bypass bot ပါ။\n"
        "🎬 /download movie_url လို့ ရိုက်ထည့်ပါ။\n",
         reply_markup=keyboard
    )


@bot.on_message(filters.command("download"))
async def download_options(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply("❗️ Movie link URL ကို /download <movie_url> နဲ့ထည့်ပါ။")
    movie_url = message.command[1]

    options = await get_download_options(movie_url)

    if not options:
        return await message.reply("❌ Download options မတွေ့ပါ။")

    user_download_cache[message.chat.id] = options
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton(opt["name"], callback_data=f"dlopt_{i}")]
         for i, opt in enumerate(options)]
    )
    await message.reply("📥 Download options များ ", reply_markup=keyboard)


@bot.on_callback_query(filters.regex(r"^dlopt_(\d+)"))
async def download_option_handler(client: Client, callback_query: CallbackQuery):
    index = int(callback_query.matches[0].group(1))
    chat_id = callback_query.message.chat.id

    options = user_download_cache.get(chat_id)
    if not options or index >= len(options):
        return await callback_query.answer("❌ Link မရှိတော့ပါ", show_alert=True)

    url = options[index]['url']
    await callback_query.answer("⏳ Download link ကို ပြင်ဆင်နေပါသည်...")
    await callback_query.message.edit_text(f"⏳ Download link ကို ပြင်ဆင်နေပါသည်...ခဏစောင့်ဆိုင်းပေးပါ။\n\n")

    # Start progress bar update concurrently while automate_download_flow runs
    # progress_task = asyncio.create_task(wait_with_progress(callback_query, total_seconds=300))

    try:
        final_link = await automate_download_flow(url, callback_query, chat_id)
    except Exception as e:
        # progress_task.cancel()
        await callback_query.message.edit_text(f"❌ Error: {e}\n\n🔗 Original CM Link:\n{url}\n\n")
        return

   #  progress_task.cancel()  # Stop progress bar updates after done

    await callback_query.message.edit_text(
        f"✅ ‌ဒေါင်းလော့လင့်ရယူရန်ရန် :\n{final_link}\n\n"
    )


async def wait_with_progress(callback_query, total_seconds):
    for elapsed in range(1, total_seconds + 1):
        minutes, seconds = divmod(elapsed, 60)
        elapsed_text = (
            f"{minutes} မိနစ် {seconds} စက္ကန့်ကြာခဲ့ပြီ" if minutes else f"{seconds} စက္ကန့်ကြာခဲ့ပြီ"
        )

        progress = int(elapsed / total_seconds * 10)
        bar = "█" * progress + "░" * (10 - progress)

        text = (
            f"⏳ စောင့်နေသည်... {elapsed_text}\n"
            f"[{bar}]"
        )

        try:
           # await callback_query.message.edit_text(text)
            logger.info(f"⏳ [{bar}] {minutes}m {seconds}s")
        except Exception:
            pass  # Error တက်လျှင် မပြောပဲ ကျော်သွားမယ်

        await asyncio.sleep(1)

# --- Step 3: Bypass Logic with Playwright ---


async def automate_download_flow(start_url: str, callback_query: CallbackQuery, chatID: int) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox"])
        context = await browser.new_context()
        page = await context.new_page()
        await stealth_async(page)

        # 🛑 Block ad requests

        async def handle_route(route):
            if any(ad in route.request.url for ad in ["doubleclick", "ads", "pop", "googlesyndication"]):
                await route.abort()
            else:
                await route.continue_()
        await context.route("**/*", handle_route)
        await page.goto(start_url, timeout=60000)

        try:
            await callback_query.message.edit_text(f"⏳ ကြော်ငြာစာမျက်နှာသို့ရောက်ရှိနေပါပြီ...")
            await page.wait_for_selector("#lite-single-sora-button", timeout=15000)

            await page.click("#lite-single-sora-button")

        except Exception:
            try:
                await callback_query.message.edit_text(f"⏳ လင့်ရရှိရန် ခလုတ်လေး‌ ပေါ် လာဖို့ ခဏစောင့်နေပါပြီ...")
                await page.wait_for_selector(
                    "img[src='https://channelmyanmar.to/wp-content/uploads/2023/09/get-link.png']", timeout=30000
                )
                await asyncio.sleep(6)
                await callback_query.message.edit_text(f"⏳ လင့်ရရှိရန် ခလုတ်လေးနိုပ်လိုက်ပါပြီ ....")
                await page.evaluate("""() => {
                    document.querySelector("img[src='https://channelmyanmar.to/wp-content/uploads/2023/09/get-link.png']").click();
                }""")
            except:
                pass

        await page.wait_for_load_state("networkidle", timeout=150000)
        url = page.url
        await callback_query.message.edit_text("⏳ ဒေါင်းလော့ဖိုင်တင်ထားသော စာမျက်နှာအားရှာဖွေနေပါပြီပြီ...ခဏစောင့်ပေးပါ")
        # === Megaup ===
        if "megaup" in url:
            try:
                await callback_query.message.edit_text(f"⏳ Megaup စာမျက်နှာသို့ ရောက်ရှိနေပါပြီ.....")
                # stealth mode ဆိုတာ Cloudflare bot detection ကိုလှည့်ဖို့

                await page.wait_for_selector("div.btn-free-element a.btn.btn--primary", state="attached", timeout=30000)
                await page.evaluate("""() => {
                  const btn = document.querySelector("div.btn-free-element a.btn.btn--primary");
                  if (btn) btn.click();
                  }""")

            
                await callback_query.message.edit_text(f"⏳ ပထမအဆင့် ဒေါင်းလော့ခလုတ် ရှာဖွေနေပါသည်...")
                await asyncio.sleep(6)

                await callback_query.message.edit_text(f"⏳ ဒုတိယအဆင့် ဒေါင်းလော့ခလုတ် အားတွေ့ပါပြီပြီ..")

                download_button_selector = "div.download-timer a.btn.btn--primary"
                await page.wait_for_selector(download_button_selector, timeout=30000)
                while True:
                    try:
                        btn_text = await page.inner_text(download_button_selector)
                        if "DOWNLOAD / VIEW NOW" in btn_text:
                            break
                        await asyncio.sleep(1)
                    except:
                        break
                
                await callback_query.message.edit_text(f"⏳ ဒေါင်းလော့ခလုတ်ကို နှိပ်နေပါပြီ...နောက်အဆင့်ဖစ်သော Cloud fare စာမျက်နှာကိုခေါနေပါပြီ ...")

                ads_skipped = 0
                while True:
                    try:
                        async with context.expect_page(timeout=8000) as new_page_info:
                            await page.click(download_button_selector)
                        new_page = await new_page_info.value
                        # Wait for page to fully load
                        await new_page.wait_for_load_state("load")
                        final_url = new_page.url
                        if not any(x in final_url for x in ["megaup.net", "megadl.boats", "megadl.site"]):
                            await new_page.close()
                            ads_skipped += 1
                            logger.warning(
                                f"❌ Detected ad page instead of Megaup: {final_url}")

                            await callback_query.message.edit_text(f"❌ ကြော်ငြာစာမျက်နှာကို တွေ့ရှိခဲ့ပါသည် ကြော်ငြာအား ကျော်ပါမည် အရေတွက် {ads_skipped} ကြိမ်ရှိပါပြီ.. ")
                        else:
                            await callback_query.message.edit_text(f"⏳ Mega စာမျက်နှာ သို့ရောက်ရှိပါပြီ video ဖိုင်တင်ထားသော စာမျက်နှာ ဖစ်ပါသည် ...:\n")
                            return final_url
                    except Exception as e:
                        content = await page.content()
                        await callback_query.message.edit_text(f"⚠️ Mega စာမျက်နှာအားမတွေ့ပါ {content[:1000]}  ....\n\n")
                        await asyncio.sleep(10)
                        break

                # await callback_query.message.edit_text("⏳ Cloudflare challenge ကို ကျော်ဖို့ စောင့်နေပါသည်...")
                # try:
                manual_browser_url = page.url
                await callback_query.message.edit_text(f"{manual_browser_url}")
                await asyncio.sleep(10)
                # page.goto(url, wait_until="networkidle", timeout=40000)
                # Cloudflare challenge check
                for i in range(10):
                    html = await page.content()
                    # if "Download Now" in html:
                    #     await callback_query.message.edit_text(f"[*] ✅ Button is now available.")
                    #     page.click("#btndownload")
                    #     page.wait_for_load_state("load")
                    #     final_url = page.url
                    #     return final_url
                    if "Just a moment" in html:
                        await callback_query.message.edit_text(f"[*] Cloudflare challenge... {i+1}s")
                    else:
                        await callback_query.message.edit_text(f"[*] Waiting... {i+1}s")

                    await asyncio.sleep(1)
                else:

                    try:
                        
                        await callback_query.message.edit_text("❌ Cloudflare challenge ကို auto bypass မဖြစ်နိုင်တော့ပါ။")
                        await asyncio.sleep(5)
                        await page.expose_function("notifyPassComplete", lambda: print("✅ User passed Cloudflare."))
                        url = page.url
                        token = generate_token(chatID, manual_browser_url)
                        verify_url = f"{webhook_url}/verify?token={token}"

                        keyboard = InlineKeyboardMarkup(
                            [[InlineKeyboardButton("🌐 Browser မှာဖွင့်ရန်", url=verify_url)]])
                        
                        await callback_query.message.edit_text(
                            f"⚠️ Cloudflare challenge ကို auto bypass မဖြစ်နိုင်တော့ပါ။\n\n"
                            f"🧑‍💻 ကျေးဇူးပြု၍ ဒီ link ကို browser မှဖွင့်ပြီး 'Download Now' button ပေါ်လာအောင် ဖြတ်ပါ။\n\n"
                            f"✅ ဖြတ်ပြီးသွားရင် download button ကို detect လုပ်မယ်။ ",
                            reply_markup=keyboard
                        )
                        await asyncio.sleep(30)  # 30 sec စောင့်မယ်
                        # Loop until user solves manually
                        for i in range(120):  # wait up to 2 mins
                            info = token_store.get(token)
                            if info and info.get("verified"):
                                html = await page.content()
                                if "Download Now" in html:
                                    await page.click("#btndownload")
                                    await page.wait_for_load_state("load")
                                    final_url = page.url
                                    await callback_query.message.edit_text("✅ Manual ဖြတ်ပြီးပြီးပါပြီ။ Download URL ရရှိပါပြီ။")
                                    await browser.close()
                                    dl_link = final_url
                                    return dl_link

                            else:
                                await callback_query.message.edit_text("❌ Manual ဖြတ်မှု မအောင်မြင်ပါ။ အချိ္္န်ကုန်သွားပါပြီ။")
                                await browser.close()
                                dl_link = None
                                return dl_link
                            await asyncio.sleep(2)
                    except Exception:
                        content = await page.content()
                        await callback_query.message.edit_text(f"❌ Download button မတက်သေးပါ။{content[:1000]}")
                        await asyncio.sleep(10)
                        await browser.close()
                        dl_link = None
                        return

                await browser.close()
                return dl_link or url
            except Exception as e:
                error_url = page.url
                await page.screenshot(path="error.png", full_page=True)
                await browser.close()
                raise Exception(
                    f"❌ Error fetching Megaup link at URL: {error_url}\n"
                    f"Reason: {str(e)}")

        await browser.close()
        return url

# --- Step 4: FastAPI webhook endpoint ---


@app.post("/")
async def telegram_webhook(req: Request):
    update = await req.json()
    logger.info("Incoming Telegram webhook: %s", update.get("update_id"))
    await bot.process_update(update)
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port,
                log_level="info", reload=True)
