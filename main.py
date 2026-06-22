import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

def dummy_server():
    port = int(os.environ.get("PORT", 10000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Bot 24/7 ishlamoqda!")
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()

threading.Thread(target=dummy_server, daemon=True).start()
import yt_dlp
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ChatMemberStatus
from dotenv import load_dotenv

# O'zingiz yozgan fayllar
from database import init_db, save_video, get_video
from middlewares import SubscriptionMiddleware

load_dotenv()

# Bot va Dispatcher
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

# Middleware va Baza
dp.message.middleware(SubscriptionMiddleware())
init_db()

# Tugmalar
main_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="🎥 Video yuklash"), KeyboardButton(text="📊 Statistikam")]],
    resize_keyboard=True
)


def download_media(url):
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'outtmpl': 'temp_video.%(ext)s',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Salom! Super Media Bot ishga tushdi. Quyidagilardan birini tanlang:", reply_markup=main_menu)


@dp.message(F.text == "🎥 Video yuklash")
async def ask_for_link(message: Message):
    await message.answer("Video linkini yuboring (YouTube yoki Instagram):")


@dp.message(F.text == "📊 Statistikam")
async def show_stats(message: Message):
    await message.answer("Botimiz hozirda sinov rejimida. 🚀")


@dp.message(F.text.regexp(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be|instagram\.com)/.+'))
async def handle_media_link(message: Message):
    url = message.text
    cached_file_id = get_video(url)

    if cached_file_id:
        try:
            await message.answer_video(cached_file_id, caption="Mana videongiz! ⚡️")
            return
        except:
            pass

    wait_msg = await message.answer("⏳ Video yuklanmoqda...")
    try:
        file_path = await asyncio.to_thread(download_media, url)
        sent = await message.answer_video(FSInputFile(file_path))
        save_video(url, sent.video.file_id)
        if os.path.exists(file_path):
            os.remove(file_path)
        await wait_msg.delete()
    except Exception as e:
        await wait_msg.edit_text(f"❌ Yuklab bo'lmadi. Linkni tekshiring.")
        print(f"Xato: {e}")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
