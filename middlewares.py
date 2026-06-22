from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.enums import ChatMemberStatus


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        # Faqat username ishlatamiz, raqamli ID kerak emas!
        CHANNEL_USERNAME = "@F218G"

        # /start komandasi o'tkazib yuboriladi
        if event.text and event.text.startswith('/start'):
            return await handler(event, data)

        try:
            # To'g'ridan-to'g'ri username bilan tekshiramiz
            member = await event.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=event.from_user.id)

            # Agar a'zo bo'lmasa yoki haydalgan bo'lsa
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                await event.answer(f"❌ Botdan foydalanish uchun kanalimizga obuna bo'ling!\n👉 {CHANNEL_USERNAME}")
                return

        except Exception as e:
            print(f"XATOLIK: {e}")
            await event.answer(
                "⚠️ Bot kanal a'zolarini ko'ra olmayapti. Iltimos, botni @F218G kanaliga Administrator qilib qo'shing.")
            return

        return await handler(event, data)