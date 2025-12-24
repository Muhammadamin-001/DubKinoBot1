# serial/serial_handler.py
"""
🎞️ SERIAL ADMIN HANDLER
Serial yuklash, o'chirish, menular va callback handlerlari
"""

from telebot import types
from utils.db_config import bot, state#, serials
from utils.menu_builder import create_inline_buttons
from utils.admin_utils import is_admin
from config.settings import ADMIN_ID
from . serial_db import (
    create_serial, add_season, add_episode, add_full_files,
    get_serial, get_all_serials, get_season, delete_serial,
    delete_season,# delete_episode,
    check_serial_code_exists,
    check_episode_exists
)
from .serial_states import (
    set_serial_state, clear_serial_state, get_serial_state,
    get_serial_code_from_state
    #is_waiting_for
)
#import time

# =================== YORDAMCHI FUNKSIYALAR ===================

def show_serial_menu_after_upload(chat_id, serial):
    """Upload qilingandan keyin serial menyu ko'rsatish"""
    markup = types.InlineKeyboardMarkup()
    
    seasons = serial.get("seasons", [])
    if seasons:
        for season in seasons:   
            season_num = season["season_number"]
            episodes_count = len(season.get("episodes", []))
            full_count = len(season.get("full_files", []))
            count_text = f"{episodes_count} qism" if episodes_count > 0 else f"{full_count} video"
            
            markup.add(types.InlineKeyboardButton(
                f"📺 {season_num}-fasl ({count_text})",
                callback_data=f"season_select_{serial['code']}_{season_num}"
            ))
    
    markup.add(types.InlineKeyboardButton("➕ Fasl qo'shish", callback_data=f"season_add_{serial['code']}"))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_show_existing"))
    
    caption = f"📚 *{serial['name']}*\n\nFasllarni boshqarish:"
    
    bot.send_photo(
        chat_id,
        serial["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )

# def show_serials_or_add(chat_id):
#     """Menyu ko'rsatish"""
#     serials_list = get_all_serials()
    
#     markup = types.InlineKeyboardMarkup()
    
#     for serial in serials_list:  
#         markup.add(types.InlineKeyboardButton(
#             f"📺 {serial['name']}",
#             callback_data=f"serial_select_{serial['code']}"
#         ))
    
#     markup.add(types.InlineKeyboardButton("➕ Yangi Serial", callback_data="serial_add_new"))
#     markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_back_to_admin"))
    
#     bot.send_message(
#         chat_id,
#         "📚 *Mavjud Seriallar*\n\nSerialni tanlang:",
#         reply_markup=markup,
#         parse_mode="Markdown"
#     )

# =================== SERIAL YUKLASH MENYU ===================

#✅ BUNI QO'SHISH KERAK ENDI! 
@bot.message_handler(func=lambda msg: msg.text == "🎞 Serial yuklash")
def upload_serial_menu(msg):
    """Serial yuklash asosiy menyu - AUTO HANDLER"""
    user_id = msg.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    buttons = [
        {"text": "➕ Yangi Serial", "callback":  "serial_add_new"},
        {"text":  "📺 Mavjud Seriallar", "callback": "serial_show_existing"},
        {"text": "🔙 Ortga", "callback": "serial_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        "🎞️ *Serial Yuklash Menyu*\n\nNima qilish?  ",
        reply_markup=markup,
        parse_mode="Markdown"
    )

#=================== YANGI:  CALLBACK dan keladigan SERIAL MENYU ===================

# @bot.callback_query_handler(func=lambda call: call.data == "upload_type_serial")
# def show_serial_menu_from_callback(call):
#     """Callback dan keladigan serial menyu - ✅ YANGI"""
    
#     buttons = [
#         {"text": "➕ Yangi Serial", "callback": "serial_add_new"},
#         {"text": "📺 Mavjud Seriallar", "callback": "serial_show_existing"},
#         {"text": "🔙 Ortga", "callback": "upload_back_to_admin"}
#     ]
#     markup = create_inline_buttons(buttons)
    
#     bot.send_message(
#         call.message.chat.id,
#         "🎞️ *Serial Yuklash Menyu*\n\nNima qilish? ",
#         reply_markup=markup,
#         parse_mode="Markdown"
#     )

#========== Mavjud seriallar =============
@bot.callback_query_handler(func=lambda call: call. data == "serial_show_existing")
def show_serials_or_add(call):
    """Mavjud seriallarni ko'rsatish"""
    serials_list = get_all_serials()
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:  
        markup.add(types.InlineKeyboardButton(
            f"📺 {serial['name']}",
            callback_data=f"serial_select_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("➕ Yangi Serial", callback_data="serial_add_new"))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_back_to_admin"))
    
    if serials_list:
        bot. send_message(
            call. message.chat.id,
            "📚 *Mavjud Seriallar*\n\nSerialni tanlang:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "📺 Hech qanday serial qo'shilmagan.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

# =================== YANGI SERIAL YARATISH ===================

# =================== CALLBACK: YANGI SERIAL QADAMI 1 ===================

@bot.callback_query_handler(func=lambda call: call.data == "serial_add_new")
def add_new_serial_start(call):
    """Yangi serial yaratishni boshlash"""
    user_id = str(call.from_user.id)
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    print(f"🔵 [CALLBACK] serial_add_new - user_id: {user_id}")
    
    bot.send_message(
        call.message.chat.id,
        "🆔 *Serial kodini kiriting*\n\n(Masalan: serial_001)",
        parse_mode="Markdown"
    )
    
    set_serial_state(user_id, ["serial_waiting_code"])
    print(f"🟢 [STATE SET] {user_id}:  {state. get(user_id)}")


# =================== MESSAGE:  QADAMI 2 - KOD SAQLASH ===================

@bot.message_handler(func=lambda msg:  (
    str(msg.from_user.id) in state and 
    state[str(msg.from_user.id)] is not None and
    len(state[str(msg.from_user.id)]) > 0 and
    state[str(msg.from_user.id)][0] == "serial_waiting_code"
))
def save_serial_code(msg):
    """Serial kodi saqlash"""
    user_id = str(msg.from_user.id)
    serial_code = msg.text. strip()
    
    print(f"🔵 [MESSAGE] save_serial_code - user_id: {user_id}, code: {serial_code}")
    
    if not serial_code:
        bot.send_message(msg.chat.id, "❌ Kod bo'sh bo'lmasligi kerak!")
        return
    
    if check_serial_code_exists(serial_code):
        bot.send_message(msg.chat.id, "⚠️ *Bu kod allaqachon mavjud!*\n\nBoshqa kod kiriting:", parse_mode="Markdown")
        return
    
    if len(serial_code) < 2:
        bot.send_message(msg.chat.id, "❌ Kod kamina 2 ta belgi bo'lishi kerak!", parse_mode="Markdown")
        return
    
    set_serial_state(user_id, ["serial_waiting_name", serial_code])
    print(f"🟢 [STATE SET] {user_id}: {state.get(user_id)}")
    
    bot.send_message(msg.chat.id, "📝 *Serial nomini kiriting*\n\n(Masalan:  Mirzabek)", parse_mode="Markdown")


# =================== MESSAGE: QADAMI 3 - NOM SAQLASH ===================

@bot.message_handler(func=lambda msg: (
    str(msg.from_user.id) in state and 
    state[str(msg.from_user.id)] is not None and
    len(set_serial_state[str(msg.from_user.id)]) > 0 and
    state[str(msg.from_user.id)][0] == "serial_waiting_name"
))
def save_serial_name(msg):
    """Serial nomi saqlash"""
    user_id = str(msg.from_user.id)
    state_data = get_serial_state(user_id)
    
    print(f"🔵 [MESSAGE] save_serial_name - user_id: {user_id}, state: {state_data}")
    
    if not state_data or len(state_data) < 2:
        print(f"❌ State xatosi:  {state_data}")
        clear_serial_state(user_id)
        bot.send_message(msg.chat.id, "❌ Xatolik!  Qayta boshlang.")
        return
    
    serial_code = state_data[1]
    serial_name = msg.text.strip()
    
    if not serial_name:
        bot. send_message(msg.chat. id, "❌ Nom bo'sh bo'lmasligi kerak!")
        return
    
    set_serial_state(user_id, ["serial_waiting_image", serial_code, serial_name])
    print(f"🟢 [STATE SET] {user_id}: {state.get(user_id)}")
    
    bot.send_message(msg.chat.id, "🖼️ *Serial uchun rasm yuboring*\n\n(Afisha yoki poster)", parse_mode="Markdown")
    

# =================== MESSAGE:  QADAMI 4 - RASM SAQLASH ===================

@bot.message_handler(func=lambda msg: (
    msg.content_type == 'photo' and
    str(msg.from_user.id) in state and 
    state[str(msg. from_user.id)] is not None and
    len(set_serial_state[str(msg.from_user. id)]) > 0 and
    state[str(msg. from_user.id)][0] == "serial_waiting_image"
), content_types=['photo'])
def save_serial_image(msg):
    """Serial rasmi saqlash"""
    user_id = str(msg.from_user.id)
    state_data = get_serial_state(user_id)
    
    print(f"🔵 [MESSAGE] save_serial_image - user_id: {user_id}, state: {state_data}")
    
    if not state_data or len(state_data) < 3:
        print(f"❌ State xatosi: {state_data}")
        clear_serial_state(user_id)
        bot.send_message(msg.chat.id, "❌ Xatolik!  Qayta boshlang.")
        return
    
    serial_code = state_data[1]
    serial_name = state_data[2]
    image_file_id = msg.photo[-1].file_id
    
    print(f"🟢 Creating serial:  code={serial_code}, name={serial_name}")
    
    if create_serial(serial_code, serial_name, image_file_id):
        bot.send_message(
            msg.chat.id,
            f"✅ *Serial '{serial_name}' yaratildi!*\n\n🆔 Kod: `{serial_code}`\n\n📺 Endi fasl qo'shishingiz mumkin.",
            parse_mode="Markdown"
        )
        print("🟢 Serial created successfully!")
    else:
        bot.send_message(msg.chat.id, "❌ Serial yaratishda xatolik yuz berdi!", parse_mode="Markdown")
        print("❌ Failed to create serial")
    
    clear_serial_state(user_id)
    print(f"🟢 [STATE CLEARED] {user_id}")

# =================== SERIAL TANLASH VA FASLLAR ===================

@bot.callback_query_handler(func=lambda call: call.data. startswith("serial_select_"))
def select_serial(call):
    """Serial tanlash va fasllarni ko'rsatish"""
    user_id = str(call.from_user.id)
    serial_code = call.data.replace("serial_select_", "")
    
    print(f"[CALLBACK] select_serial - serial_code: {serial_code}")
    
    serial = get_serial(serial_code)
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    
    markup = types.InlineKeyboardMarkup()
    
    seasons = serial.get("seasons", [])
    if seasons:
        for season in seasons:   
            season_num = season["season_number"]
            episodes_count = len(season. get("episodes", []))
            full_count = len(season.get("full_files", []))
            count_text = f"{episodes_count} qism" if episodes_count > 0 else f"{full_count} video"
            
            markup.add(types.InlineKeyboardButton(
                f"📺 {season_num}-fasl ({count_text})",
                callback_data=f"season_select_{serial_code}_{season_num}"
            ))
    
    markup.add(types.InlineKeyboardButton("➕ Fasl qo'shish", callback_data=f"season_add_{serial_code}"))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_show_existing"))
    
    caption = f"📚 *{serial['name']}*\n\nFasllarni boshqarish:"
    
    bot.send_photo(
        call.message.chat.id,
        serial["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    set_serial_state(user_id, ["viewing_serial", serial_code])

# =================== FASL QO'SHISH ===================

@bot.callback_query_handler(func=lambda call: call. data.startswith("season_add_"))
def add_season_start(call):
    """Fasl qo'shishni boshlash"""
    user_id = str(call.from_user. id)
    serial_code = call.data.replace("season_add_", "")
    
    print(f"[CALLBACK] add_season_start - serial_code: {serial_code}")
    
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    bot.send_message(
        call.message.chat.id,
        "🔢 *Fasl raqamini kiriting*\n\n(Masalan: 1, 2, 3... )",
        parse_mode="Markdown"
    )
    
    set_serial_state(user_id, ["season_waiting_number", serial_code])
    print(f"[SAVED SEASON] state: {state. get(user_id)}")

# ✅ TUZATILDI: TO'G'RI MESSAGE HANDLER
@bot.message_handler(func=lambda msg: (
    str(msg.from_user.id) in state and 
    state[str(msg.from_user.id)] and 
    state[str(msg.from_user.id)][0] == "season_waiting_number"
))
def save_season_number(msg):
    """Fasl raqami saqlash"""
    user_id = str(msg.from_user.id)
    
    print(f"[MESSAGE] save_season_number - user_id: {user_id}, state: {state.get(user_id)}")
    
    serial_code = get_serial_code_from_state(user_id)
    
    if not serial_code:  
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        clear_serial_state(user_id)
        return
    
    try:
        season_number = int(msg.text.strip())
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Raqam kiriting!")
        return
    
    if season_number < 1:
        bot.send_message(msg.chat.id, "❌ Fasl raqami 1 dan boshlanadi!")
        return
    
    serial = get_serial(serial_code)
    if serial:
        for season in serial.get("seasons", []):
            if season["season_number"] == season_number:    
                bot.send_message(msg.chat.id, f"⚠️ {season_number}-fasl allaqachon mavjud!")
                return
    
    set_serial_state(user_id, ["season_waiting_type", serial_code, season_number])
    print(f"[SAVED SEASON NUMBER] state: {state.get(user_id)}")
    
    buttons = [
        {"text": "📺 To'liq fasl", "callback":  f"season_type_full_{serial_code}_{season_number}"},
        {"text": "🎬 Qism-qism", "callback": f"season_type_episodes_{serial_code}_{season_number}"},
        {"text":  "🔙 Ortga", "callback":  f"serial_select_{serial_code}"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        f"⏳ *{season_number}-faslni qanday yuklaysiz? *",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== TO'LIQ FASL YUKLASH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("season_type_full_"))
def season_type_full(call):
    """To'liq fasl yuklashni boshlash"""
    user_id = str(call.from_user.id)
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    
    print(f"[CALLBACK] season_type_full - serial_code: {serial_code}, season:  {season_number}")
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        f"📹 *{season_number}-faslning videolarini ketma-ket yuboring*\n\n"
        f"Yuborish tugallansa: `TAYYOR` yozing",
        parse_mode="Markdown"
    )
    
    set_serial_state(user_id, ["season_uploading_full", serial_code, season_number, []])
    print(f"[SAVED FULL SEASON] state: {state. get(user_id)}")

# ✅ TUZATILDI: TO'G'RI MESSAGE HANDLER
@bot.message_handler(func=lambda msg: (
    str(msg.from_user.id) in state and 
    state[str(msg.from_user.id)] and 
    state[str(msg.from_user.id)][0] == "season_uploading_full"
),
content_types=['video', 'text'])
def upload_season_full_video(msg):
    """To'liq fasl videolarini saqlash"""
    user_id = str(msg.from_user.id)
    state_data = get_serial_state(user_id)
    
    print(f"[MESSAGE] upload_season_full_video - user_id: {user_id}, content:  {msg.content_type}")
    
    if not state_data or len(state_data) < 4:
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        clear_serial_state(user_id)
        return
    
    serial_code = state_data[1]
    season_number = state_data[2]
    videos = state_data[3]
    
    if msg.content_type == "text" and msg.text.upper() == "TAYYOR":
        if not videos:
            bot.send_message(msg.chat.id, "❌ Kamina bitta video yuboring!")
            return
        
        add_season(serial_code, season_number)
        add_full_files(serial_code, season_number, videos)
        
        bot.send_message(
            msg.chat.id,
            f"✅ *{season_number}-fasl {len(videos)} video bilan qo'shildi!*",
            parse_mode="Markdown"
        )
        
        clear_serial_state(user_id)
        
        serial = get_serial(serial_code)
        show_serial_menu_after_upload(msg. chat.id, serial)
        
    elif msg.content_type == "video": 
        file_id = msg.video.file_id
        videos.append(file_id)
        set_serial_state(user_id, ["season_uploading_full", serial_code, season_number, videos])
        
        bot.send_message(
            msg.chat.id,
            f"✅ {len(videos)}-video qabul qilindi.\n\n"
            f"Davom etish yoki `TAYYOR` yozing"
        )

# =================== QISM-QISM FASL YUKLASH ===================

@bot.callback_query_handler(func=lambda call: call. data.startswith("season_type_episodes_"))
def season_type_episodes(call):
    """Qism-qism fasl yuklashni boshlash"""
    user_id = str(call.from_user.id)
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    
    print(f"[CALLBACK] season_type_episodes - serial_code: {serial_code}, season:  {season_number}")
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    add_season(serial_code, season_number)
    
    bot.send_message(
        call.message.chat.id,
        f"🎬 *{season_number}-faslga qism qo'shish*\n\n"
        f"Qaysi qism raqamini kiriting?  (1, 2, 3... )",
        parse_mode="Markdown"
    )
    
    set_serial_state(user_id, ["episode_waiting_number", serial_code, season_number])
    print(f"[SAVED EPISODE] state: {state.get(user_id)}")

# ✅ TUZATILDI: TO'G'RI MESSAGE HANDLER
@bot.message_handler(func=lambda msg: (
    str(msg.from_user. id) in state and 
    state[str(msg.from_user.id)] and 
    state[str(msg.from_user.id)][0] == "episode_waiting_number"
))
def save_episode_number(msg):
    """Qism raqami saqlash"""
    user_id = str(msg.from_user.id)
    state_data = get_serial_state(user_id)
    
    print(f"[MESSAGE] save_episode_number - user_id: {user_id}, state: {state. get(user_id)}")
    
    if not state_data or len(state_data) < 3:
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        clear_serial_state(user_id)
        return
    
    serial_code = state_data[1]
    season_number = state_data[2]
    
    try:
        episode_number = int(msg.text.strip())
    except ValueError:
        bot. send_message(msg.chat. id, "❌ Raqam kiriting!")
        return
    
    if episode_number < 1:
        bot.send_message(msg.chat.id, "❌ Qism raqami 1 dan boshlanadi!")
        return
    
    if check_episode_exists(serial_code, season_number, episode_number):
        bot.send_message(msg.chat.id, f"⚠️ {episode_number}-qism allaqachon mavjud!   Boshqa raqam kiriting.")
        return
    
    set_serial_state(user_id, ["episode_waiting_video", serial_code, season_number, episode_number])
    print(f"[SAVED EPISODE NUMBER] state: {state.get(user_id)}")
    
    bot.send_message(
        msg.chat.id,
        f"📹 *{episode_number}-qismning videosini yuboring*",
        parse_mode="Markdown"
    )

# ✅ TUZATILDI: TO'G'RI MESSAGE HANDLER
@bot.message_handler(func=lambda msg: (
    str(msg.from_user.id) in state and 
    state[str(msg.from_user. id)] and 
    state[str(msg.from_user. id)][0] == "episode_waiting_video"
),
content_types=['video'])
def save_episode_video(msg):
    """Qism videosini saqlash"""
    user_id = str(msg.from_user.id)
    state_data = get_serial_state(user_id)
    
    print(f"[MESSAGE] save_episode_video - user_id: {user_id}, state: {state.get(user_id)}")
    
    if not state_data or len(state_data) < 4:
        bot.send_message(msg.chat.id, "❌ Xatolik yuz berdi. Qayta urinib ko'ring.")
        clear_serial_state(user_id)
        return
    
    serial_code = state_data[1]
    season_number = state_data[2]
    episode_number = state_data[3]
    file_id = msg.video.file_id
    
    add_episode(serial_code, season_number, episode_number, file_id)
    
    bot.send_message(
        msg.chat.id,
        f"✅ *{episode_number}-qism qo'shildi! *\n\n"
        f"Yana qism qo'shish?  Qism raqamini kiriting yoki /menu yozing.",
        parse_mode="Markdown"
    )
    
    set_serial_state(user_id, ["episode_waiting_number", serial_code, season_number])
    print(f"[RESET TO EPISODE] state: {state.get(user_id)}")
    
    


# =================== SERIAL O'CHIRISH MENYU ===================

# ✅ BUNI QO'SHISH KERAK ENDI!
@bot.message_handler(func=lambda msg: msg.text == "❌ Serial o'chirish")
def delete_serial_menu(msg):
    """Serial o'chirish menyusi - AUTO HANDLER"""
    user_id = msg.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    serials_list = get_all_serials()
    
    if not serials_list:
        bot.send_message(msg. chat.id, "📺 Hech qanday serial qo'shilmagan.")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list: 
        markup.add(types.InlineKeyboardButton(
            f"🎞 {serial['name']}",
            callback_data=f"delete_serial_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_back_to_admin"))
    
    bot.send_message(
        msg.chat.id,
        "🗑️ *Qaysi serialni o'chirish? *",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# @bot.callback_query_handler(func=lambda call: call.data == "delete_type_serial")
# def show_delete_serial_menu_from_callback(call):
#     """Callback dan keladigan serial o'chirish menyu"""
#     from serial.serial_db import get_all_serials
    
#     serials_list = get_all_serials()
    
#     if not serials_list:
#         bot.answer_callback_query(call.id, "📺 Hech qanday serial qo'shilmagan.")
#         return
    
#     markup = types.InlineKeyboardMarkup()
    
#     for serial in serials_list:
#         markup. add(types.InlineKeyboardButton(
#             f"🎞 {serial['name']}",
#             callback_data=f"delete_serial_{serial['code']}"
#         ))
    
#     markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_back_to_admin"))
    
#     bot.send_message(
#         call.message.chat.id,
#         "🗑️ *Qaysi serialni o'chirish?*",
#         reply_markup=markup,
#         parse_mode="Markdown"
#     )

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_serial_"))
def delete_serial_selected(call):
    """Serial tanlandi - ma'lumoti ko'rsatish"""
    user_id = str(call.from_user. id)
    serial_code = call.data.replace("delete_serial_", "")
    
    serial = get_serial(serial_code)
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    bot.delete_message(call. message.chat.id, call. message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        f"🎞 {serial['name']} - Fasllarni boshqarish",
        callback_data=f"delete_serial_seasons_{serial_code}"
    ))
    markup.add(types.InlineKeyboardButton(
        "❌ Butunlay o'chirish",
        callback_data=f"delete_serial_confirm_{serial_code}"
    ))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_serial_menu"))
    
    caption = f"🎞 *{serial['name']}*\n\nNima qilish?"
    
    bot.send_photo(
        call.message.chat.id,
        serial["image"],
        caption=caption,
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    set_serial_state(user_id, ["deleting_serial", serial_code])

@bot.callback_query_handler(func=lambda call: call. data.startswith("delete_serial_confirm_"))
def delete_serial_all(call):
    """Butun serialni o'chirish"""
    serial_code = call.data.replace("delete_serial_confirm_", "")
    
    if delete_serial(serial_code):
        bot.answer_callback_query(call.id, "✅ Serial o'chirildi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Serial muvaffaqiyatli o'chirildi.")
    else:
        bot. answer_callback_query(call. id, "❌ Xatolik yuz berdi!")

@bot.callback_query_handler(func=lambda call: call. data.startswith("delete_serial_seasons_"))
def delete_serial_seasons(call):
    """Serialning fasllarini ko'rsatish (o'chirish uchun)"""
    serial_code = call.data.replace("delete_serial_seasons_", "")
    
    serial = get_serial(serial_code)
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    bot. delete_message(call.message. chat.id, call.message. message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    seasons = serial. get("seasons", [])
    if seasons:
        for season in seasons:   
            season_num = season["season_number"]
            episodes_count = len(season.get("episodes", []))
            full_count = len(season.get("full_files", []))
            count_text = f"{episodes_count} qism" if episodes_count > 0 else f"{full_count} video"
            
            markup.add(types.InlineKeyboardButton(
                f"📺 {season_num}-fasl ({count_text})",
                callback_data=f"delete_season_select_{serial_code}_{season_num}"
            ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_{serial_code}"))
    
    bot.send_message(
        call.message.chat.id,
        f"🎞 *{serial['name']}*\n\nFaslni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call:  call.data.startswith("delete_season_select_"))
def delete_season_or_episode(call):
    """Fasl tanlandi - qismlari yoki butun fasl o'chirish"""
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    
    season = get_season(serial_code, season_number)
    
    if not season:
        bot.answer_callback_query(call.id, "❌ Fasl topilmadi!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    episodes = season.get("episodes", [])
    if episodes:
        for episode in episodes:
            ep_num = episode["episode_number"]
            markup.add(types.InlineKeyboardButton(
                f"🎬 {ep_num}-qism",
                callback_data=f"delete_episode_{serial_code}_{season_number}_{ep_num}"
            ))
    
    markup.add(types.InlineKeyboardButton(
        f"❌ Butun {season_number}-fasl",
        callback_data=f"delete_season_confirm_{serial_code}_{season_number}"
    ))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_seasons_{serial_code}"))
    
    full_count = len(season.get("full_files", []))
    ep_count = len(episodes)
    
    text = f"📺 *{season_number}-fasl*\n\n"
    if ep_count > 0:
        text += f"Qismlari: {ep_count} ta\n\nQismni tanlang yoki butun faslni o'chirish:"
    elif full_count > 0:
        text += f"To'liq fasl: {full_count} ta video\n\nFaslni o'chirish:"
    
    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_season_confirm_"))
def delete_season_all(call):
    """Butun faslni o'chirish"""
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    
    if delete_season(serial_code, season_number):
        bot.answer_callback_query(call.id, f"✅ {season_number}-fasl o'chirildi!")
        bot.delete_message(call.message. chat.id, call.message. message_id)
        
        delete_serial_seasons(call)
    else:
        bot. answer_callback_query(call. id, "❌ Xatolik yuz berdi!")

# =================== BACK BUTTON HANDLERLARI ===================

@bot.callback_query_handler(func=lambda call: call. data == "serial_back_to_admin")
def serial_back_menu(call):
    """Asosiy serial menuyga qaytish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_serial_menu_after_upload(call. message)

@bot.callback_query_handler(func=lambda call: call.data == "delete_back_to_admin")
def delete_back_menu(call):
    """Admin paneliga qaytish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    from utils.admin_utils import admin_panel
    admin_panel(call. message. chat.id)

@bot.callback_query_handler(func=lambda call: call.data == "delete_serial_menu")
def delete_serial_menu_callback(call):
    """O'chirish menyusi"""
    serials_list = get_all_serials()
    
    if not serials_list: 
        bot.answer_callback_query(call.id, "📺 Hech qanday serial qo'shilmagan")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:   
        markup.add(types. InlineKeyboardButton(
            f"🎞 {serial['name']}",
            callback_data=f"delete_serial_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_back_to_admin"))
    
    bot.send_message(
        call.message.chat.id,
        "🗑️ *Qaysi serialni o'chirish? *",
        reply_markup=markup,
        parse_mode="Markdown"
    )