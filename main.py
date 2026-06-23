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
from shazamio import Shazam
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

# O'zingiz yozgan fayllar
from database import init_db, save_video, get_video, save_user, count_users
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
    keyboard=[[KeyboardButton(text="📹 Video yuklash"), KeyboardButton(text="📊 Statistikam")]],
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
    save_user(message.from_user.id, message.from_user.first_name)
    await message.answer("Salom! Super Media Bot ishga tushdi. Quyidagilardan birini tanlang:", reply_markup=main_menu)

@dp.message(F.text == "📹 Video yuklash")
async def ask_for_link(message: Message):
    await message.answer("Video linkini yuboring (YouTube yoki Instagram):")

@dp.message(F.text == "📊 Statistikam")
async def show_stats(message: Message):
    ADMIN_ID = 7788049741 
    
    if message.from_user.id == ADMIN_ID:
        users_count = count_users()
        await message.answer(f"📊 *Bot statistikasi:*\n\nJami foydalanuvchilar: {users_count} ta odam", parse_mode="Markdown")
    else:
        await message.answer("Kechirasiz, statistika faqat admin uchun yopiq! 🔒")

# YANGILANGAN SHAZAM FUNKSIYASI (Endi videolarni ham oladi)
@dp.message(F.audio | F.voice | F.video)
async def handle_media_for_shazam(message: Message):
    wait_msg = await message.answer("🎵 Musiqa qidirilmoqda (Shazam)...")
    try:
        # Fayl turini aniqlaymiz va olamiz
        if message.voice:
            file_id = message.voice.file_id
            file_extension = ".ogg"
        elif message.audio:
            file_id = message.audio.file_id
            file_extension = ".mp3"
        else:
            file_id = message.video.file_id
            file_extension = ".mp4"
            
        file = await bot.get_file(file_id)
        file_path = f"temp_media_{file_id}{file_extension}"
        
        # Faylni vaqtincha serverga yuklab olamiz
        await bot.download_file(file.file_path, file_path)

        # Shazam orqali aniqlash
        shazam = Shazam()
        out = await shazam.recognize(file_path)

        if 'track' in out:
            title = out['track']['title']
            artist = out['track']['subtitle']
            text = f"🎧 *Musiqa topildi!*\n\n👤 *Qo'shiqchi:* {artist}\n🎵 *Nomi:* {title}"
            await wait_msg.edit_text(text, parse_mode="Markdown")
        else:
            await wait_msg.edit_text("🤷‍♂️ Afsuski, bu musiqani topa olmadim yoki ovoz aniq emas.")

        # Vaqtinchalik faylni o'chirib tashlash
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        await wait_msg.edit_text("❌ Xatolik yuz berdi yoki fayl hajmi juda katta (Telegram chegarasi: 20MB).")
        print(f"Shazam xatosi: {e}")

@dp.message(F.text.regexp(r'(https?://)?(www\.)?(youtube\.com|youtu\.?be|instagram\.com)/.+'))
async def handle_media_link(message: Message):
    url = message.text
    cached_file_id = get_video(url)

    if cached_file_id:
        try:
            await message.answer_video(cached_file_id, caption="Mana videongiz! ⚡")
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
