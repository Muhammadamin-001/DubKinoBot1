# movies/movie_handler.py
"""
🎬 KINO ADMIN HANDLER
Kino yuklash, o'chirish va boshqarish
"""

from telebot import types
from utils.db_config import bot, state, movies
from utils.admin_utils import is_admin
from config.settings import ADMIN_ID
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

from utils.menu_builder import code_exists
#import time

kanal_link = "https://t.me/DubHDkinolar"

# =================== KINO YUKLASH ===================

@bot.message_handler(func=lambda msg: msg.text == "🎬 Kino yuklash")
def upload_movie(msg):
    """Kino yuklashni boshlash"""
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⛔️ Exit", callback_data="exit_upload_movie")
    )
    bot.send_message(msg.chat.id, 
                     "🎬 *Video yuboring (video fayl ko'rinishida)*",
                     parse_mode="Markdown",
                     reply_markup=markup
                     )
    state[str(msg.from_user.id)] = ["waiting_for_video"]
    
    
    
    
#======*** kino yuklashni to'xtatish ****==========

@bot.message_handler(func=lambda msg:
    str(msg.from_user.id) in state
    and msg.text
    and msg.text.lower() in ["stop", "exit", "bekor"]
)
def exit_process(msg):
    user_id = str(msg.from_user.id)
    del state[user_id]
    
    bot.send_message(msg.chat.id, "✅ Jarayon yakunlandi")

@bot.callback_query_handler(func=lambda call: call.data == "exit_upload_movie")
def exit_by_button(call):
    user_id = str(call.from_user.id)

    if user_id in state:
        del state[user_id]

    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=None
    )
    bot.send_message(
        call.message.chat.id,
        "✅ Jarayon bekor qilindi",
        parse_mode="Markdown",
    )





#===========*********************=============================



@bot.message_handler(func=lambda m: str(m.from_user.id) in state 
                     and state[str(m.from_user.id)][0] == "waiting_for_video",
                     content_types=['video'])
def catch_video(msg):
    """Videoni qabul qilish"""
    user = str(msg.from_user.id)
    file_id = msg.video. file_id
    state[user] = ["waiting_for_code", file_id]
    bot.send_message(msg.chat.id, "🆔 Kino uchun kod kiriting:")
    
@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user.id)][0] == "waiting_for_code")
def movie_code(msg):
    """Kino kodini qabul qilish"""
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = msg.text. strip()
    
    # Kod bormi tekshirish
    if code_exists(code):
        bot.send_message(
            msg.chat.id,
            f"⚠️ *Bu kod allaqachon mavjud!* #{code}\nBoshqa kod kiriting:",
            parse_mode="Markdown"
        )
        return

    state[user] = ["waiting_for_name", file_id, code]
    bot.send_message(msg.chat.id, "🎬 Kino nomini kiriting:")

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user. id)][0] == "waiting_for_name")
def movie_name(msg):
    """Kino nomini qabul qilish"""
    user = str(msg. from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = msg.text.strip()

    state[user] = ["waiting_for_genre", file_id, code, name]
    bot.send_message(msg.chat.id, "📚 Kino janrini kiriting:")

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user. id)][0] == "waiting_for_genre")
def movie_genre(msg):
    """Kino janrini qabul qilish"""
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = state[user][3]
    genre = msg.text.strip()

    state[user] = ["waiting_for_format", file_id, code, name, genre]
    bot.send_message(msg.chat.id, "💽 Kino formatini kiriting:")

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user. id)][0] == "waiting_for_format")
def movie_url(msg):
    """Kino formatini qabul qilish"""
    user = str(msg. from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = state[user][3]
    genre = state[user][4]
    formati = msg.text.strip()

    # MongoDB-ga saqlash
    movies.update_one(
        {"code": code},
        {"$set": {
            "file_id": file_id,
            "name": name,       
            "formati": formati,    
            "genre": genre,      
            "url": "@DubHDkinolar",
            "urlbot": "@DubKinoBot"
        }},
        upsert=True
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("⛔️ Exit", callback_data="exit_upload_movie")
    )

    bot.send_message(
        msg.chat.id,
        "✅ *Kino muvaffaqiyatli qo'shildi!*\n\n"
        "🎬 Yana video yuborishingiz mumkin\n"
        "⛔️ Tugatish uchun `stop` yozing yoki Exit tugmasini bosing",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    state[user] = ["waiting_for_video"]



def send_movie_info(chat_id, kino_kodi):
    """Kino ma'lumotini yuborish"""
    movie = movies.find_one({"code": kino_kodi})
    if movie:
        file_id = movie["file_id"]
        code = movie["code"]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎬 Kanalimiz", url=kanal_link))
        markup.add(types.InlineKeyboardButton("❌", callback_data="delete_movie"))
        
        caption_text = (
            f"🎬 {movie['name']} \n"
            f"{'─' * 15}\n"
            f"💽 Formati: {movie['formati']}\n"
            f"🎞 Janri: {movie['genre']}\n"
            f"🆔 Kod: {code}\n\n"
            f"🤖 Botimiz: {movie['urlbot']}"
        )
        bot.send_video(
            chat_id,
            file_id,
            caption=caption_text,
            reply_markup=markup
        )
    else:
        bot.send_message(chat_id, "❌ Bunday kod bo'yicha kino topilmadi.")
        

@bot.callback_query_handler(func=lambda call: call.data == "delete_movie")
def delete_movie_warning(call):
    """Kino o'chirish ogohlantirish"""
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("❌ O'chirish", callback_data="delete_movie_confirm")
    )

    bot.answer_callback_query(
        call.id,
        "⚠️ Rostdan ham kinoni o'chirmoqchimisiz?\n\nYana bir marta bosing ... ❌",
        show_alert=True
    )

    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )
    
@bot.callback_query_handler(func=lambda call: call.data == "delete_movie_confirm")
def delete_movie_confirm(call):
    """Kino o'chirish tasdiqlash"""
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Kino o'chirildi")
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")