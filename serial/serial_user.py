# serial/serial_user.py
"""
👤 SERIAL USER VIEW
Foydalanuvchi uchun serialni ko'rish
"""

from utils.db_config import bot, serials

def show_serial_for_user(chat_id, serial_code):
    """Serialni ko'rsatish"""
    serial = serials.find_one({"code":  serial_code})
    if serial:
        bot.send_message(chat_id, f"🎞 {serial['name']}")