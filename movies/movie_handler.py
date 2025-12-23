# movies/movie_handler.py
from telebot import types
from utils.db_config import bot, movies, state

@bot.message_handler(func=lambda msg: msg.text == "🎬 Kino yuklash")
def upload_movie(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    bot.send_message(msg.chat.id, "🎬 Video yuboring (video fayl ko'rinishida).")
    state[str(msg.from_user.id)] = ["waiting_for_video"]

# ...  qolgan kino kodi ... 