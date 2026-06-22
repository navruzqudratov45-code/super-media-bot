from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎥 Video yuklash"), KeyboardButton(text="📊 Statistikam")]
    ],
    resize_keyboard=True
)