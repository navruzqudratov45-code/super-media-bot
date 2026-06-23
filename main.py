import asyncio
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import pylast
from acrcloud.recognizer import ACRCloudRecognizer
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

load_dotenv()

# RENDER KUTAYOTGAN "PORT" UCHUN 1 SONIYADA ISHLAYDIGAN YECHIM
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot 100% is alive!")

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), DummyHandler)
    server.serve_forever()

# Portni fonda (alohida) darhol ishga tushiramiz
threading.Thread(target=keep_alive, daemon=True).start()

# --- ASOSIY BOT KODI ---
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

config = {
    'host': os.getenv('ACR_HOST'),
    'access_key': os.getenv('ACR_ACCESS_KEY'),
    'access_secret': os.getenv('ACR_ACCESS_SECRET'),
    'timeout': 10
}
lastfm = pylast.LastFMNetwork(api_key=os.getenv('LASTFM_API_KEY'))

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Salom! Musiqa aniqlash botiga xush kelibsiz. Musiqa yoki audio yuboring!")

@dp.message(F.video | F.audio | F.voice)
async def handle_media(message: Message):
    wait_msg = await message.answer("🔍 Musiqa tahlil qilinmoqda...")
    try:
        file_id = message.video.file_id if message.video else (message.audio.file_id if message.audio else message.voice.file_id)
        file = await bot.get_file(file_id)
        file_path = f"temp_{file_id}.mp3"
        await bot.download_file(file.file_path, file_path)
        
        re = ACRCloudRecognizer(config)
        result = re.recognize_by_file(file_path, 0)
        
        if 'metadata' in result:
            track = result['metadata']['music'][0]
            title = track['title']
            artist = track['artists'][0]['name']
            
            try:
                track_info = lastfm.get_track(artist, title)
                cover_url = track_info.get_cover_image()
                if cover_url:
                    await message.answer_photo(photo=cover_url, caption=f"🎧 *{title}*\n👤 *{artist}*\n\nTopildi!")
                else:
                    await message.answer(f"🎧 *{title}*\n👤 *{artist}*\n\n(Rasm topilmadi)")
            except:
                await message.answer(f"🎧 {title} - {artist}")
        else:
            await wait_msg.edit_text("🤷‍♂️ Kechirasiz, bu musiqani aniqlay olmadim.")
        
        if os.path.exists(file_path): os.remove(file_path)
    except Exception as e:
        await wait_msg.edit_text("❌ Xatolik yuz berdi.")
        if os.path.exists(file_path): os.remove(file_path)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
