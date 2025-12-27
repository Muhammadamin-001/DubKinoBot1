# serial/serial_user.py
"""
👤 SERIAL USER VIEW
Foydalanuvchi uchun serialni ko'rish, qismlar, playback
"""

from telebot import types
from utils.db_config import bot
from .serial_db import get_serial, get_season#, get_episode, get_all_serials

# =================== FOYDALANUVCHI UCHUN SERIAL KO'RISH ===================

def show_serial_for_user(chat_id, serial_code):
    """Serialni ko'rsatish (rasm + nomi + tavsif + fasllar)"""
    serial = get_serial(serial_code)
    
    if not serial: 
        bot.send_message(chat_id, "❌ Serial topilmadi!")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    seasons = serial.get("seasons", [])
    if seasons:
        for season in seasons:
            season_num = season["season_number"]
            markup.add(types.InlineKeyboardButton(
                f"📺 {season_num}-fasl",
                callback_data=f"user_season_{serial_code}_{season_num}"
            ))
    
    markup.add(types.InlineKeyboardButton("🔙", callback_data="user_back"))
    
    caption = f"🎞 *{serial['name']}*\n{serial['description']}\n\nFaslni tanlang:"
    
    bot.send_photo(
        chat_id,
        serial["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data. startswith("user_season_"))
def show_episodes_for_user(call):
    """Qismlarni ko'rsatish"""
    parts = call.data.split("_")
    serial_code = parts[2]
    season_number = int(parts[3])
    
    serial = get_serial(serial_code)
    season = get_season(serial_code, season_number)
    
    if not season:
        bot.answer_callback_query(call.id, "❌ Fasl topilmadi!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    # Qismlar
    episodes = season.get("episodes", [])
    full_files = season.get("full_files", [])
    
    if episodes:
        for episode in episodes:
            ep_num = episode["episode_number"]
            markup.add(types.InlineKeyboardButton(
                f"{ep_num}",
                callback_data=f"user_episode_{serial_code}_{season_number}_{ep_num}"
            ))
    elif full_files:
        for i, _ in enumerate(full_files, 1):
            markup.add(types.InlineKeyboardButton(
                f"{i}",
                callback_data=f"user_episode_{serial_code}_{season_number}_{i}"
            ))
    
    # Fasllar o'rtasida navigatsiya
    prev_button = None
    next_button = None
    
    all_seasons = serial.get("seasons", [])
    season_numbers = [s["season_number"] for s in all_seasons]
    
    if season_number > min(season_numbers):
        prev_season = season_number - 1
        prev_button = types.InlineKeyboardButton(
            "⬅️ Oldingi fasl",
            callback_data=f"user_season_{serial_code}_{prev_season}"
        )
    
    if season_number < max(season_numbers):
        next_season = season_number + 1
        next_button = types. InlineKeyboardButton(
            "Keyingi fasl ➡️",
            callback_data=f"user_season_{serial_code}_{next_season}"
        )
    
    if prev_button and next_button:
        markup. row(prev_button, next_button)
    elif prev_button:
        markup. add(prev_button)
    elif next_button:
        markup.add(next_button)
    
    markup.add(types.InlineKeyboardButton("🔙", callback_data=f"user_serial_{serial_code}"))
    
    text = f"📺 *{serial['name']} - {season_number}-fasl*\n\n"
    text += f"Qismlari: {len(episodes) or len(full_files)}\n\n"
    text += "Qismni tanlang:"
    
    bot.send_message(
        call.message. chat.id,
        text,
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("user_episode_"))
def send_episode_to_user(call):
    """Qismning videosini yuborish"""
    parts = call. data.split("_")
    serial_code = parts[2]
    season_number = int(parts[3])
    episode_number = int(parts[4])
    
    season = get_season(serial_code, season_number)
    
    if not season:
        bot.answer_callback_query(call.id, "❌ Fasl topilmadi!")
        return
    
    # Qismni topish
    episode = None
    episodes = season.get("episodes", [])
    
    for ep in episodes:
        if ep["episode_number"] == episode_number: 
            episode = ep
            break
    
    # Agar episode yo'q bo'lsa, full_files'dan olish
    if not episode: 
        full_files = season.get("full_files", [])
        if episode_number <= len(full_files):
            episode = {
                "episode_number": episode_number,
                "file_id": full_files[episode_number - 1]
            }
    
    if not episode:
        bot.answer_callback_query(call.id, "❌ Qism topilmadi!")
        return
    
    serial = get_serial(serial_code)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_seria"))
    
    caption = f"🎞 *{serial['name']}*\n{season_number}-fasl, {episode_number}-qism\n\n🤖 Bot manzili: @DubKinoBot"
    
    bot.send_video(
        call.message.chat.id,
        episode["file_id"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    

#======== Foydalanuvchi kinoni O'chirib yuborsa======
@bot.callback_query_handler(func=lambda call: call.data == "delete_seria")
def delete_movie_warning(call):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("❌ O'chirish", callback_data="delete_movie_confirm")
    )

    bot.answer_callback_query(
        call.id,
        "⚠️ Rostdan ham kinoni o‘chirmoqchimisiz?\n\nYana bir marta bosing ...❌",
        show_alert=True
    )

    # ❗ XABAR O‘CHMAYDI
    # faqat tugma o‘zgaradi
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )
    
@bot.callback_query_handler(func=lambda call: call.data == "delete_movie_confirm")
def delete_movie_confirm(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Kino o‘chirildi")
    except Exception as e:
        print(e)
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")




@bot.callback_query_handler(func=lambda call: call.data.startswith("user_serial_"))
def user_serial_back(call):
    """Serial menuyga qaytish"""
    serial_code = call.data.replace("user_serial_", "")
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_serial_for_user(call.message.chat.id, serial_code)

@bot.callback_query_handler(func=lambda call: call.data == "user_back")
def user_back(call):
    """Ortga (asosiy menyu)"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        "🆔 Film kodini kiriting:\n\t(🔍 Yoki kino/serial nomini: )"
    )

def search_serial_results(chat_id, search_results):
    """Qidirish natijalarida seriallar"""
    # Agar qidirish natijasida serial topilsa
    markup = types.InlineKeyboardMarkup()
    
    for item in search_results:
        if "seasons" in item:  # Bu serial
            markup.add(types.InlineKeyboardButton(
                f"🎞 {item['name']}",
                callback_data=f"user_serial_{item['code']}"
            ))
    
    if not markup.keyboard:
        return None
    
    markup.add(types.InlineKeyboardButton("🔙", callback_data="user_back"))
    return markup