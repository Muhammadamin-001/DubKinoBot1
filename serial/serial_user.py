# serial/serial_user.py
from telebot import types
from utils. db_config import bot, serials

def show_serial_for_user(chat_id, serial_code):
    """Foydalanuvchi uchun serial ko'rsatish"""
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.send_message(chat_id, "❌ Serial topilmadi")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for season in serial. get("seasons", []):
        markup.add(types.InlineKeyboardButton(
            f"📺 {season['season_number']}-fasl",
            callback_data=f"user_season_{serial_code}_{season['season_number']}"
        ))
    
    caption = f"🎞 *{serial['name']}*\n\nFaslni tanlang:"
    bot.send_photo(chat_id, serial["image"], caption=caption, parse_mode="Markdown", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("user_season_"))
def show_episodes_for_user(call):
    """Qismlarni ko'rsatish"""
    # ...  qism ko'rsatish kodi ...
    pass

# ...  qolgan user view kodi ...