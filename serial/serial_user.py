# serial/serial_user.py
"""
👤 SERIAL USER VIEW
Foydalanuvchi uchun serialni ko'rish, qismlar, playback
"""

from telebot import types
from utils.db_config import bot
from .serial_db import get_serial, get_season#, get_episode, get_all_serials

kanal_link = "https://t.me/Saboq_kinolar"

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
    markup.add(types.InlineKeyboardButton("🎬 Kanalimiz", url=kanal_link))
    markup.add(types.InlineKeyboardButton("🔙", callback_data="user_back"))
    
    caption = f"🎞 *{serial['name']}*\n\n🆔 Serial kodi: `{serial_code}`\n{serial['description']}\n\nFaslni tanlang:"
    
    bot.send_photo(
        chat_id,
        serial["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )


#===== *** Qismlar xabari =======

@bot.callback_query_handler(func=lambda call: call.data.startswith("user_season_"))
def show_episodes_for_user(call):
    parts = call.data.split("_")
    serial_code = parts[2]
    season_number = int(parts[3])
    page = int(parts[5]) if "page" in call.data else 0

    serial = get_serial(serial_code)
    season = get_season(serial_code, season_number)

    if not season:
        bot.answer_callback_query(call.id, "❌ Fasl topilmadi!")
        return

    bot.delete_message(call.message.chat.id, call.message.message_id)

    episodes = season.get("episodes", [])
    full_files = season.get("full_files", [])
    total = episodes or list(range(1, len(full_files) + 1))

    PER_PAGE = 25
    PER_ROW = 5

    start = page * PER_PAGE
    end = start + PER_PAGE
    page_items = total[start:end]

    markup = types.InlineKeyboardMarkup()

    # 🔢 QISMLAR (5 tadan qatorda)
    row = []
    for item in page_items:
        ep_num = item["episode_number"] if isinstance(item, dict) else item
        row.append(
            types.InlineKeyboardButton(
                str(ep_num),
                callback_data=f"user_episode_{serial_code}_{season_number}_{ep_num}"
            )
        )
        if len(row) == PER_ROW:
            markup.row(*row)
            row = []

    if row:
        markup.row(*row)

    # 🔁 PAGINATION
    nav = []
    if page > 0:
        nav.append(
            types.InlineKeyboardButton(
                "⬅️ Oldingi",
                callback_data=f"user_season_{serial_code}_{season_number}_page_{page-1}"
            )
        )
    if end < len(total):
        nav.append(
            types.InlineKeyboardButton(
                "Keyingi ➡️",
                callback_data=f"user_season_{serial_code}_{season_number}_page_{page+1}"
            )
        )

    if nav:
        markup.row(*nav)

    markup.add(
        types.InlineKeyboardButton("🔙 Ortga", callback_data=f"user_serial_{serial_code}")
    )

    text = (
        f"\t\t\t\t📺 *{serial['name']} — {season_number}-fasl*\n\n"
        f"Qismlar: {len(total)}\t\t||\t\t"
        f"Sahifa: {page + 1}/{(len(total) + PER_PAGE - 1)//PER_PAGE}\n\n"
        "Qismni tanlang:"
    )

    bot.send_message(
        call.message.chat.id,
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
    
    caption = f"🎞 *{serial['name']}*\n\t\t\t\t{season_number}-fasl, {episode_number}-qism\n\n🤖 *Yuklovchi*: @Saboq_kinolar_bot"
    
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
        "⚠️ Rostdan ham videoni o‘chirmoqchimisiz?\n\nYana bir marta bosing ...❌",
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
        bot.answer_callback_query(call.id, "✅ Video o‘chirildi")
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