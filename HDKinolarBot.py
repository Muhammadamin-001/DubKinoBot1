# ============================================
# HDKinolarBot.py - ASOSIY BOT FAYLI
# ============================================

# 📦 Standart kutubxonalar
import os
import time
from flask import Flask, request
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# from utils.admin_utils import is_admin
# from config.settings import ADMIN_ID
# ⚙️ Konfiguratsiya
from config.settings import TOKEN, ADMIN_ID #, WEBHOOK_URL, MONGO_URI

# 🛠️ Utilities
from utils.db_config import (
    bot, state, users_collection, movies, serials, 
    admins_collection, channels_collection
)
from utils.admin_utils import (
    admin_panel, super_admin_panel, user_panel, 
    check_sub, upload_mdb, is_admin, save_user
)
from utils.menu_builder import create_inline_buttons

# 🎞️ Serial va Kino modullar
# from serial.serial_handler import (
#     delete_serial_menu #upload_serial_menu
#     # serial_back_menu
# )

# import serial.serial_handler
from serial.serial_user import show_serial_for_user
from movies.movie_handler import send_movie_info #, upload_movie, catch_video, movie_code, movie_name, movie_genre, movie_url
#from movies.movie_db import get_movie, get_all_movies

#from utils.db_config import bot, state, serials  # ✅ TUZATILGAN
#from utils.menu_builder import create_inline_buttons
# from utils.admin_utils import is_admin
# from config.settings import ADMIN_ID
from serial.serial_db import (get_all_serials)
#     create_serial, add_season, add_episode, add_full_files,
#     get_serial, # get_season, delete_serial,
#     #delete_season, delete_episode,  # ✅ QOSHILDI
#     check_serial_code_exists,
#     check_episode_exists
# )
# from serial.serial_states import (
#     set_serial_state, clear_serial_state, get_serial_state,
#     get_serial_code_from_state,
#     is_waiting_for
# )



# Flask setup
app = Flask(__name__)

#kanal_link = "https://t.me/DubHDkinolar"

# =================== STATE (HOLAT) - ✅ TUZATILGAN ===================

#state = {}  # ✅ UNCOMMENTED

user_clicks = {}
album_buffer = {}  # ✅ UNCOMMENTED
album_sending = {}  # ✅ UNCOMMENTED

movie_pages = {}
user_pages = {}
search_cache = {}  # ✅ UNCOMMENTED

# ...  QOLGAN KOD ... 



    



# =================== QIDIRISH (Kino va Serial) - ✅ YANGILANGAN ===================

def search_content_by_code_or_name(query):
    """Kino yoki serialni qidirish"""
    query = query.strip()
    
    # 1️⃣ Kinoni kod bilan qidirish
    movie_by_code = movies.find_one({"code":  query})
    if movie_by_code:
        return "movie_code_found", [movie_by_code], 1
    
    # 2️⃣ Serialni kod bilan qidirish - ✅ YANGI
    serial_by_code = serials.find_one({"code": query})
    if serial_by_code:
        return "serial_code_found", [serial_by_code], 1
    
    # 3️⃣ Kam belgi bo'lsa
    if len(query) < 3:
        return "too_short", None, 0
    
    # 4️⃣ Nomi bilan qidirish
    search_name = query.lower()
    
    # Kinolarda
    all_movies = list(movies.find({}, {"_id": 0}))
    filtered_movies = [m for m in all_movies if search_name in m['name'].lower()]
    
    # Seriallarda - ✅ YANGI
    all_serials = list(serials.find({}, {"_id": 0}))
    filtered_serials = [s for s in all_serials if search_name in s['name'].lower()]
    
    # Barcha natijalar
    combined = filtered_movies + filtered_serials
    
    if combined:
        total = len(combined)
        pages = (total - 1) // 5 + 1
        return "found", combined, pages, total
    
    return "not_found", None, 0




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
            
            markup.add(types.  InlineKeyboardButton(
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

def show_serials_or_add_temp(chat_id):
    """Menyu ko'rsatish (inline callback o'rniga)"""
    serials_list = get_all_serials()
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:
        markup.add(types.InlineKeyboardButton(
            f"📺 {serial['name']}",
            callback_data=f"serial_select_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("➕ Yangi Serial", callback_data="serial_add_new"))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_back_to_admin"))
    
    bot.send_message(
        chat_id,
        "📚 *Mavjud Seriallar*\n\nSerialni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )





        

# =================== EKSPORT UCHUN ===================






#===== START UCHUN =======
@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if check_sub(user_id):
        # ✅ OBUNA BO'LSA
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        
        bot.send_message(
            chat_id, 
            "✔ Obuna tasdiqlandi! ✅\n\n🎬 Kino kodini yuboring:\n\t(🔍 Yoki kino nomini:)"
        )
        bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
    
    else:
        # ❌ OBUNA BO'LMAGAN BO'LSA
        try:
            bot.delete_message(chat_id, message_id)
        except:
            pass
        
        # ✅ YANA OBUNA XABARI JO'NATISH (faqat obuna bo'lmagan kanallar bilan)
        send_subscription_request(call.message, user_id)
        
        bot.answer_callback_query(
            call.id, 
            "❗ Obuna bo'lmagansiz! ",
            show_alert=True
        )

def send_subscription_request(msg, user_id):
    """
    Obuna so'rash xabari - faqat obuna bo'lmagan kanallarni ko'rsatish
    """
    channels = list(channels_collection.find({}, {"_id": 0, "id": 1, "link": 1}))
    
    if not channels:
        return
    
    btn = types.InlineKeyboardMarkup()
    
    # ✅ FAQAT OBUNA BO'LMAGAN KANALLARNI TOPISH
    for channel in channels: 
        try:
            member = bot.get_chat_member(channel["id"], user_id)
            # Agar obuna bo'lmagan bo'lsa → tugma qo'shish
            if member.status not in ["member", "administrator", "creator"]:
                btn.add(
                    types.InlineKeyboardButton(
                        f"📌 Kanalga obuna bo'lish - {channel['link']}", 
                        url=channel["link"]
                    )
                )
        except:
            # Kanal tekshirish qila olmasa → tugma qo'shish (xavfsizlik uchun)
            btn.add(
                types.InlineKeyboardButton(
                    "📌 Kanalga obuna bo'lish", 
                    url=channel["link"]
                )
            )
    
    # ✅ TEKSHIRISH TUGMASI
    btn.add(
        types.InlineKeyboardButton(
            "♻️ Tekshirish", 
            callback_data="check"
        )
    )
    
    # ✅ XABAR JO'NATISH
    bot.send_message(
        msg.chat.id,
        "❗ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!\n\n"
        "⏳ Obuna bo'lgandan keyin 'Tekshirish' tugmasini bosing.",
        reply_markup=btn
    )
        
        

#======== Foydalanuvchi kinoni O'chirib yuborsa======
@bot.callback_query_handler(func=lambda call: call.data == "delete_movie")
def delete_movie_warning(call):
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("❌ O'chirish", callback_data="delete_movie_confirm")
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

    
    
        




# =================== PAGE HANDLER - ✅ QOSHILDI ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("page_"))
def page_switch(call):
    """Film kodlari sahifalarini o'tish"""
    try:
        page = int(call.data.split("_")[1])
        all_movies = list(movies.find({}, {"_id": 0}))
        total = len(all_movies)
        per_page = 5
        pages = (total - 1) // per_page + 1
        
        boshlash = (page - 1) * per_page
        end = boshlash + per_page
        page_movies = all_movies[boshlash:end]
        
        text = "*🎬 Kinolar ro'yxati*\n\n"
        text += f"📊 Topildi: {total} ta kino | Sahifa: {page}/{pages}\n\n"
        
        c = boshlash + 1
        for m in page_movies:
            code = m['code']
            text += f"{c}.   {m['name']}\n"
            text += f"🆔 Kod: `{code}`\n"
            text += f"[▶️ Kinoni yuklash](https://t.me/DubKinoBot?start={code})\n"
            text += f"*{'─' * 10}*\n"
            c += 1
        
        markup = types.InlineKeyboardMarkup()
        btns = []
        
        if page > 1:
            btns.append(types.InlineKeyboardButton("⬅️ orqaga", callback_data=f"page_{page-1}"))
        
        if page > 1 and page < pages:
            btns.append(types.InlineKeyboardButton("📌 oxirgi", callback_data=f"page_{pages}"))
            
        if page < pages:
            btns.append(types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"page_{page+1}"))
        
        btns.append(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
        
        if btns:
            markup.row(*btns)
        
        bot.  edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Xatolik: {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi.")

# =================== CALLBACK HANDLERS - QIDIRUSH SAHIFALAR ===================

@bot.callback_query_handler(func=lambda c: c.data.startswith("search_"))
def search_page_switch(call):
    """Qidirush natijalari sahifalarini chiqarish - ✅ YANGILANGAN"""
    try:
        parts = call.data.split("_page_")
        user_id = int(parts[0].replace("search_", ""))
        page = int(parts[1])
        
        if user_id not in search_cache: 
            bot.answer_callback_query(call.id, "❌ Qidirush natijalari o'chirib yuborildi.")
            return
        
        cached = search_cache[user_id]
        filtered_items = cached["items"]
        pages = cached["pages"]
        total = cached["total"]
        search_query = cached["query"]
        
        # Sahifa ma'lumotlari
        boshlash = (page - 1) * 5
        end = boshlash + 5
        page_items = filtered_items[boshlash:end]
        
        # Matn
        text = f"🎬 **Qidirush natijalari:  '{search_query}'**\n\n"
        text += f"📊 Topildi: {total} ta | Sahifa: {page}/{pages}\n\n"
        
        c = boshlash + 1
        for item in page_items:
            if "seasons" in item:  # Serial
                text += f"{c}.  🎞 {item['name']}\n"
                text += f"🆔 Kod: `{item['code']}`\n"
                text += f"[▶️ Serial](https://t.me/DubKinoBot?start={item['code']})\n"
            else:  # Kino
                text += f"{c}. 🎬 {item['name']}\n"
                text += f"🆔 Kod: `{item['code']}`\n"
                text += f"[▶️ Yulab olish](https://t.me/DubKinoBot?start={item['code']})\n"
            
            text += f"*{'─' * 30}*\n"
            c += 1
        
        # Tugmalar
        markup = types.InlineKeyboardMarkup()
        btns = []
        
        if page > 1:
            btns.append(types.InlineKeyboardButton("⬅️ Orqaga", callback_data=f"search_{user_id}_page_{page-1}"))
        
        if page < pages:
            btns. append(types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"search_{user_id}_page_{page+1}"))
        
        btns.append(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
        
        if btns:
            markup.row(*btns)
        
        bot.edit_message_text(
            text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
        
    except Exception as e:
        print(f"Xatolik: {e}")
        bot.answer_callback_query(call. id, "❌ Xatolik yuz berdi.")




# O'chirish tugmasi uchun callback handler
@bot.callback_query_handler(func=lambda call: call.data == "delete_msg_list")
def delete_movies_list(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Ro'yxat o'chirildi!")
    except Exception as e:
        print(f"Xatolik:  {e}")
        bot.answer_callback_query(call.id, "❌ Ro'yxat o'chirilmadi.")
        

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_channel_"))
def delete_channel(call):
    if str(call.from_user. id) != ADMIN_ID:
        bot.answer_callback_query(call.id, "❌ Bu buyruq siz uchun emas.")
        return
    
    try:
        # O'chirilayotgan kanal indexini olish
        channel_idx = int(call.data.split("_")[2])
        channels = list(channels_collection.find({}, {"_id": 0, "link": 1, "id": 1}))
        
        if channel_idx >= len(channels):
            bot.answer_callback_query(call. id, "❌ Kanal topilmadi.")
            return
        
        # Kanal linkini olish
        channel_link = channels[channel_idx]["link"]
        
        # MongoDB'dan o'chirish
        channels_collection.delete_one({"link":  channel_link})
        
        bot.answer_callback_query(call.id, f"✅ Kanal o'chirildi: {channel_link}")
        bot.edit_message_text(
            f"✅ '{channel_link}' kanali o'chirildi.",
            call.message. chat.id,
            call.message.message_id
        )
    except Exception as e:
        print(f"Xatolik:  {e}")
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi.")



# Xabarni o'chirish callback handler
@bot.callback_query_handler(func=lambda call: call.data == "delete_stats")
def delete_stats_message(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Xabar o'chirildi!")
    except Exception as e:
        print(f"Xatolik:  {e}")
        bot.answer_callback_query(call.id, "❌ Xabar o'chirilmadi.")






@bot.callback_query_handler(func=lambda call: call.data == "upload_back")
def upload_back(call):
    """Ortga tugmasi"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    admin_panel()



# ====================== START ================================
@bot.message_handler(commands=['start'])
def start(msg):
    """Start komandasi"""
    user = msg.from_user.id
    
    kino_kodi = None
    if ' ' in msg.text:
        start_parts = msg.text.split(' ', 1)
        kino_kodi = start_parts[1]. strip()
    
    save_user(user)
    
    print(f"🔍 /start tekshirilmoqda: user_id={user}, kino_kodi={kino_kodi}")

    if not check_sub(user):
        print(f"❌ Foydalanuvchi {user} obuna emas")
        upload_mdb(msg)
        return
    
    print(f"✅ Foydalanuvchi {user} obuna")
    
    if kino_kodi:
        print(f"🎬 Kino yuborilmoqda: {kino_kodi}")
        
        # Kino bormi?
        movie = movies.find_one({"code": kino_kodi})
        if movie:
            send_movie_info(msg. chat.id, kino_kodi)
            return
        
        # Serial bormi?
        serial = serials.find_one({"code": kino_kodi})
        if serial:
            show_serial_for_user(msg.chat.id, kino_kodi)
            return
        
        bot.send_message(msg.chat.id, "❌ Bunday kod topilmadi!")
        return
    #==== Admin va user panel ochish ===
    
    if (str(user) == ADMIN_ID or is_admin(user)):
        markup = admin_panel()
        text = "🔐 *Admin paneli*"
    else:
        markup=user_panel()
        text = "🆔 *Kino kodini kiriting*:\n\t(🔍 Yoki kino nomini: )"

    bot.send_message(
        msg.chat.id, 
        text, 
        parse_mode="Markdown",
        reply_markup=markup
        )
    


    
 

# ====================== ADMIN PANEL ===========================
# @bot.message_handler(commands=['panel'])
# def panel(msg):
#     user = msg.from_user.id
#     if not check_sub(user):
#         upload_mdb(msg)
#         return
    
#     if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
#         admin_panel(msg.chat.id)
#     else:
#         bot.send_message(msg.chat.id, "❌ Diqqat! Bu faqat admin uchun.")
        
# @bot.message_handler(commands=['kodlar'])
# def kodlar(msg):
#     user = msg.from_user.id
#     if not check_sub(user):
#         upload_mdb(msg)
#         return
#     if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
#         bot.send_message(msg.chat.id, "❗ Bu komanda admin uchun emas.")
#         return
    
#     user_panel(msg.chat.id)
 



# HDKinolarBot.py da qo'shish:

# =================== FILM YUKLASH MENYU ===================

@bot.message_handler(func=lambda msg: msg.text == "🎬 Film yuklash")
def upload_content_menu(msg):
    """Film yuklash menyu (kino/serial tanlash) - ✅ YANGI"""
    user_id = msg.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    buttons = [
        {"text": "🎥 Kino", "callback":  "upload_type_kino"},
        {"text": "🎞 Serial", "callback": "upload_type_serial"},
        {"text": "🔙 Ortga", "callback": "upload_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        "📺 *Film Yuklash - Turini Tanlang*\n\n🎥 Kino yoki 🎞 Serial?  ",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call. data == "upload_type_kino")
def upload_type_kino(call):
    """Kino yuklash bosilsa - eski logika"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    bot.send_message(call.message.chat.id,
                     "🎬 *Video yuboring (video fayl ko'rinishida).*")
    state[str(call.from_user.id)] = ["waiting_for_video"]
    

@bot.callback_query_handler(func=lambda call: call.data == "upload_type_serial")
def upload_type_serial(call):
    """Serial yuklash bosilsa - ✅ TUZATILGAN"""
    user_id = call.from_user.id
    
    # ✅ Admin tekshiruvini bu yerda qilish
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Siz admin emassiz!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # ✅ TO'G'RIDAN-TO'G'RI MENYU KO'RSATISH
    buttons = [
        {"text": "➕ Yangi Serial", "callback": "serial_add_new"},
        {"text": "📺 Mavjud Seriallar", "callback": "serial_show_existing"},
        {"text": "🔙 Ortga", "callback": "upload_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        call.message.chat.id,
        "🎞️ *Serial Yuklash Menyu*\n\nNima qilmoqchisiz?",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    

@bot.callback_query_handler(func=lambda call: call.data == "upload_back_to_admin")
def upload_back_to_admin(call):
    """Ortga tugmasi"""
    bot.delete_message(call.message.chat. id, call.message.message_id)
    admin_panel()

    
    
    
#===========================================**********************========================

# ============================================
# SERIAL HANDLERS - HDKinolarBot.py ga QO'SHISH
# ============================================

# =================== SERIAL YUKLASH MENYU ===================

@bot.message_handler(func=lambda msg: msg.text == "🎞 Serial yuklash")
def upload_serial_menu(msg):
    """Serial yuklash asosiy menyu"""
    user_id = msg.from_user.id
    
    # Admin tekshiruvi
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    buttons = [
        {"text": "➕ Yangi Serial", "callback": "serial_add_new"},
        {"text": "📺 Mavjud Seriallar", "callback": "serial_show_existing"},
        {"text": "🔙 Ortga", "callback": "serial_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        "🎞️ *Serial Yuklash Menyu*\n\nNima qilmoqchisiz?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== MAVJUD SERIALLAR ===================

@bot.callback_query_handler(func=lambda call: call.data == "serial_show_existing")
def show_serials_or_add(call):
    """Mavjud seriallarni ko'rsatish"""
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    serials_list = list(serials.find({}, {"_id": 0, "code": 1, "name": 1}))
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    # Mavjud seriallar
    for serial in serials_list:
        markup.add(types.InlineKeyboardButton(
            f"📺 {serial['name']}",
            callback_data=f"serial_select_{serial['code']}"
        ))
    
    # Yangi serial tugmasi
    markup.add(types.InlineKeyboardButton("➕ Yangi Serial", callback_data="serial_create_new"))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_back_to_admin"))
    
    if serials_list:
        bot.send_message(
            call.message.chat.id,
            "📚 *Mavjud Seriallar*\n\nSerialni tanlang:",
            reply_markup=markup,
            parse_mode="Markdown"
        )
    else:
        bot.send_message(
            call.message.chat.id,
            "📺 Hech qanday serial yo'q.\n\n➕ Yangi serial qo'shish uchun tugmani bosing.",
            reply_markup=markup,
            parse_mode="Markdown"
        )

# =================== YANGI SERIAL YARATISH - ✅ TUZATILGAN ===================

@bot.callback_query_handler(func=lambda call: call.data == "serial_add_new")
def add_new_serial_start(call):
    """Yangi serial yaratishni boshlash"""
    user_id = str(call.from_user.id)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        bot.send_message(
            call.message.chat.id,
            "🆔 *Serial kodini kiriting:*\n\n(Masalan: SER001 yoki Breaking\\_Bad)",
            parse_mode="Markdown"
        )
    except Exception as e:
        print("SEND MESSAGE ERROR:", e)
    
    # ✅ TO'G'RI STATE
    state[user_id] = ["serial_waiting_code"]

@bot.callback_query_handler(func=lambda call: call.data == "serial_create_new")
def create_new_serial_from_list(call):
    """Mavjud seriallar ro'yxatidan yangi serial yaratish"""
    user_id = str(call.from_user.id)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        bot.send_message(
            call.message.chat.id,
            "🆔 *Serial kodini kiriting:*\n\n(Masalan: SER001 yoki Breaking\\_Bad)",
            parse_mode="Markdown"
        )
    except Exception as e:
        print("SEND MESSAGE ERROR:", e)
    
    state[user_id] = ["serial_waiting_code"]

# =================== SERIAL KODI QABUL QILISH ===================

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "serial_waiting_code")
def save_serial_code(msg):
    """Serial kodini saqlash"""
    user_id = str(msg.from_user.id)
    serial_code = msg.text.strip()
    
    # Kod allaqachon borligini tekshirish
    if serials.find_one({"code": serial_code}):
        bot.send_message(
            msg.chat.id,
            f"⚠️ *Bu kod allaqachon mavjud!*\n\n🆔 Kod: `{serial_code}`\n\nBoshqa kod kiriting:",
            parse_mode="Markdown"
        )
        return
    
    # Serial nomini so'rash
    bot.send_message(msg.chat.id, "📺 *Serial nomini kiriting:*", parse_mode="Markdown")
    state[user_id] = ["serial_waiting_name", serial_code]

# ============================================
# SERIAL YARATISH (RASM BILAN) - TUZATILGAN
# HDKinolarBot.py da mavjud kodlarni ALMASHTIRING
# ============================================

# =================== SERIAL NOMI QABUL QILISH ===================

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "serial_waiting_name")
def save_serial_name(msg):
    """Serial nomini saqlash va RASM SO'RASH"""
    user_id = str(msg.from_user.id)
    serial_name = msg.text.strip()
    serial_code = state[user_id][1]
    
    # ✅ RASM SO'RASH
    bot.send_message(
        msg.chat.id,
        "🖼 *Serial rasmini yuboring*\n\n(Rasm yoki foto ko'rinishida)",
        parse_mode="Markdown"
    )
    
    # ✅ STATE YANGILASH - rasm kutish
    state[user_id] = ["serial_waiting_image", serial_code, serial_name]

# =================== SERIAL RASMI QABUL QILISH ===================

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "serial_waiting_image",
                     content_types=['photo'])
def save_serial_image(msg):
    """Serial rasmini saqlash va bazaga QO'SHISH"""
    user_id = str(msg.from_user.id)
    serial_code = state[user_id][1]
    serial_name = state[user_id][2]
    image_file_id = msg.photo[-1].file_id
    
    # ✅ SERIALNI BAZAGA QO'SHISH (RASM BILAN)
    serials.insert_one({
        "code": serial_code,
        "name": serial_name,
        "image": image_file_id,  # ← RASM QO'SHILDI
        "seasons": []
    })
    
    bot.send_message(
        msg.chat.id,
        f"✅ *Serial yaratildi!*\n\n"
        f"📺 Nomi: {serial_name}\n"
        f"🆔 Kod: `{serial_code}`\n\n"
        f"Endi bu serialga mavsum va qismlar qo'shishingiz mumkin.\n\n"
        f"Menyu: /panel → 🎞 Serial yuklash → 📺 Mavjud Seriallar",
        parse_mode="Markdown"
    )
    
    # ✅ STATE TOZALASH
    del state[user_id]
    
    

# =================== SERIALNI TANLASH (Qism qo'shish) ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("serial_select_"))
def select_serial_menu(call):
    """Serialni tanlagandan keyin menyu"""
    serial_code = call.data.replace("serial_select_", "")
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Mavsum statistikasi
    season_count = len(serial.get('seasons', []))
    total_episodes = sum(len(s.get('episodes', [])) for s in serial.get('seasons', []))
    
    markup = types.InlineKeyboardMarkup()
    
    # Mavjud mavsumlarga qism qo'shish
    for season in serial.get('seasons', []):
        season_num = season['season_number']
        episode_count = len(season.get('episodes', []))
        markup.add(types.InlineKeyboardButton(
            f"🎬 {season_num}-Mavsum ({episode_count} qism)",
            callback_data=f"add_episode_{serial_code}_{season_num}"
        ))
    
    # Yangi mavsum qo'shish
    markup.add(types.InlineKeyboardButton(
        "➕ Yangi Mavsum",
        callback_data=f"new_season_{serial_code}"
    ))
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="serial_show_existing"))
    
    bot.send_message(
        call.message.chat.id,
        f"📺 *{serial['name']}*\n\n"
        f"📊 Jami: {season_count} mavsum, {total_episodes} qism\n\n"
        f"Mavsumni tanlang yoki yangi mavsum qo'shing:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== YANGI MAVSUM QO'SHISH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("new_season_"))
def ask_new_season_number(call):
    """Yangi mavsum raqamini so'rash"""
    serial_code = call.data.replace("new_season_", "")
    user_id = str(call.from_user.id)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(
        call.message.chat.id,
        "🔢 *Mavsum raqamini kiriting*\n\n(Masalan: 1, 2, 3...)",
        parse_mode="Markdown"
    )
    
    state[user_id] = ["waiting_season_number", serial_code]

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_season_number")
def save_new_season(msg):
    """Yangi mavsumni saqlash"""
    user_id = str(msg.from_user.id)
    serial_code = state[user_id][1]
    
    try:
        season_num = int(msg.text.strip())
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Faqat raqam kiriting (masalan: 1)")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    # Mavsum allaqachon bormi?
    existing_seasons = serial.get('seasons', [])
    if any(s['season_number'] == season_num for s in existing_seasons):
        bot.send_message(
            msg.chat.id,
            f"⚠️ *{season_num}-Mavsum allaqachon mavjud!*\n\nBoshqa raqam kiriting:",
            parse_mode="Markdown"
        )
        return
    
    # Yangi mavsum qo'shish
    serials.update_one(
        {"code": serial_code},
        {"$push": {"seasons": {
            "season_number": season_num,
            "episodes": []
        }}}
    )
    
    bot.send_message(
        msg.chat.id,
        f"✅ *{season_num}-Mavsum qo'shildi!*\n\n"
        f"📺 Serial: {serial['name']}\n\n"
        f"Endi bu mavsumga qismlar qo'shishingiz mumkin.\n"
        f"/panel → 🎞 Serial yuklash → 📺 Mavjud Seriallar",
        parse_mode="Markdown"
    )
    
    del state[user_id]

# =================== QISM QO'SHISH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_episode_"))
def ask_episode_video(call):
    """Qism videosini so'rash"""
    parts = call.data.split("_")
    serial_code = parts[2]
    season_num = int(parts[3])
    user_id = str(call.from_user.id)
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = InlineKeyboardMarkup()
    markup.add(
    InlineKeyboardButton("⛔️ Exit", callback_data="exit_upload")
    )

    bot.send_message(
        call.message.chat.id,
        "🎬 *Qism videosini yuboring*\n\n"
        "⛔️ Tugatish uchun `stop` yozing yoki Exit tugmasini bosing",
        parse_mode="Markdown",
        reply_markup=markup
    )

    state[user_id] = ["waiting_episode_video", serial_code, season_num]


#==========*** Jarayonni to'xtatish uchun ***====
@bot.message_handler(func=lambda msg:
    str(msg.from_user.id) in state
    and state[str(msg.from_user.id)][0] == "waiting_episode_video"
    and msg.text
    and msg.text.lower() in ["stop", "exit", "bekor"]
)
def exit_by_text(msg):
    user_id = str(msg.from_user.id)

    del state[user_id]

    bot.send_message(
        msg.chat.id,
        "✅ Jarayon bekor qilindi",
        parse_mode="Markdown"
    )



@bot.callback_query_handler(func=lambda call: call.data == "exit_upload")
def exit_by_button(call):
    user_id = str(call.from_user.id)

    if user_id in state:
        del state[user_id]

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        "✅ Jarayon bekor qilindi",
        parse_mode="Markdown"
    )
#=====***********================



@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_episode_video",
                     content_types=['video'])
def save_episode_video(msg):
    """Qism videosini saqlash"""
    user_id = str(msg.from_user.id)
    serial_code = state[user_id][1]
    season_num = state[user_id][2]
    file_id = msg.video.file_id
    
    bot.send_message(
        msg.chat.id,
        "🔢 *Qism raqamini kiriting*\n\n(Masalan: 1, 2, 3...)",
        parse_mode="Markdown"
    )
    state[user_id] = ["waiting_episode_number", serial_code, season_num, file_id]

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_episode_number")
def save_episode_number(msg):
    """Qism raqamini saqlash va bazaga qo'shish"""
    user_id = str(msg.from_user.id)
    serial_code = state[user_id][1]
    season_num = state[user_id][2]
    file_id = state[user_id][3]
    
    try:
        episode_num = int(msg.text.strip())
    except ValueError:
        bot.send_message(msg.chat.id, "❌ Faqat raqam kiriting (masalan: 1)")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    # Mavsumni topish
    season = next((s for s in serial.get('seasons', []) if s['season_number'] == season_num), None)
    
    if not season:
        bot.send_message(msg.chat.id, "❌ Mavsum topilmadi!")
        del state[user_id]
        return
    
    # Qism allaqachon bormi?
    if any(e['episode_number'] == episode_num for e in season.get('episodes', [])):
        bot.send_message(
            msg.chat.id,
            f"⚠️ *{episode_num}-qism allaqachon mavjud!*\n\nBoshqa raqam kiriting:",
            parse_mode="Markdown"
        )
        return
    
    # Qismni qo'shish
    serials.update_one(
        {"code": serial_code, "seasons.season_number": season_num},
        {"$push": {"seasons.$.episodes": {
            "episode_number": episode_num,
            "file_id": file_id
        }}}
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(
    InlineKeyboardButton("⛔️ Exit", callback_data="exit_upload")
    )
    bot.send_message(
        msg.chat.id,
        f"✅ *{episode_num}-qism qo'shildi!*\n\n"
        "🎬 Yana video yuborishingiz mumkin\n"
        "⛔️ Tugatish uchun `stop` yozing yoki Exit tugmasini bosing",
        parse_mode="Markdown", 
        reply_markup=markup
    )
    
    state[user_id] = ["waiting_episode_video", serial_code, season_num]


# =================== ORTGA TUGMALARI ===================

@bot.callback_query_handler(func=lambda call: call.data == "serial_back_to_admin")
def serial_back_to_admin(call):
    """Admin panelga qaytish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    admin_panel()



# ===============*****************************************************************======================================
    
@bot.message_handler(func=lambda msg: msg.text == "🔙 Ortga")
def back(msg):
    if str(msg.from_user. id) != ADMIN_ID:
        return
    
    state.pop(str(msg.from_user.id), None)  # Holatni tozalash
    
    # Super Admin panelidan kelgan bo'lsa → Admin panelga qaytarish
    admin_panel()

@bot.message_handler(func=lambda msg: msg.text == "💼 Super Admin")
def open_super_admin_panel(msg):
    # Faqat Super Admin uchun
    if str(msg.from_user.id) != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Bu buyruq siz uchun emas.")
        return
    
    # Super Admin Panel ochiladi
    super_admin_panel(msg.chat.id)
    
 #=======****=====
@bot.message_handler(func=lambda msg: msg.text == "📺 Kanal qo'shish")
def add_channel(msg):
    if str(msg.from_user.id) != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Bu buyruq siz uchun emas.")
        return
    
    bot.send_message(msg.chat.id, "📺 Kanal linkini kiriting (masalan: https://t.me/channel_name yoki @channel_name):\n\n⚠️ Bot kanalga admin bo'lishi shart.")
    state[str(msg.from_user.id)] = ["waiting_for_channel_link"]

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_for_channel_link")
def save_channel_link(msg):
    channel_link = msg.text. strip()
    
    # Kanal linki to'g'ri formatda ekanligini tekshirish
    if not (channel_link.startswith("https://t.me/") or channel_link.startswith("@")):
        bot.send_message(msg.chat.id, "❌ Kanal linki noto'g'ri.  Masalan: https://t.me/channel_name yoki @channel_name")
        return
    
    # Kanal linki allaqachon mavjud ekanligini tekshirish
    if channels_collection.find_one({"link": channel_link}):
        bot.send_message(msg.chat.id, "⚠️ Bu kanal allaqachon qo'shilgan.")
        del state[str(msg.from_user.id)]
        return
    
    # Kanal ID'sini so'rash
    bot.send_message(msg.chat.id, "🆔 Kanal ID'sini kiriting (masalan: -1001234567890):\n\n💡 Kanal ID'sini qanday topish:\n1. @username_to_id_bot ga /start yuboring\n2. Kanal nomini kiriting\n3. Bot kanal ID'sini beradi")
    state[str(msg. from_user.id)] = ["waiting_for_channel_id", channel_link]

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg. from_user.id)][0] == "waiting_for_channel_id")
def save_channel_id(msg):
    channel_id_text = msg.  text.strip()
    channel_link = state[str(msg.from_user.id)][1]
    
    # Kanal ID'sini tekshirish
    try:
        channel_id = int(channel_id_text)
    except ValueError:
        bot. send_message(msg.chat. id, "❌ Kanal ID raqam bo'lishi kerak. Masalan: -1001234567890")
        return
    
    # MongoDB'ga kanal linkini va ID'sini saqlash
    channels_collection.insert_one({
        "link": channel_link,
        "id": channel_id,  # ⭐ MUHIM:  Kanal ID'sini saqlash
        "added_date": time.time()
    })
    
    print(f"✅ Kanal qo'shildi: link={channel_link}, id={channel_id}")  # Debug
    
    bot.send_message(
        msg.chat.id, 
        f"✅ Kanal qo'shildi:\n📺 Link: {channel_link}\n🆔 ID: {channel_id}"
    )
    del state[str(msg.from_user.id)]


@bot.message_handler(func=lambda msg: msg.text == "❌ Kanal o'chirish")
def delete_channel_menu(msg):
    if str(msg.from_user.id) != ADMIN_ID:
        bot.send_message(msg. chat.id, "❌ Bu buyruq siz uchun emas.")
        return
    
    # Barcha kanallarni olish
    channels = list(channels_collection.find({}, {"_id": 0, "link": 1, "id": 1}))
    
    if not channels:
        bot.send_message(msg.chat.id, "📺 Hech qanday kanal qo'shilmagan.")
        return
    
    # Inline tugmalar bilan kanallar ro'yxatini chiqarish
    markup = types.InlineKeyboardMarkup()
    for idx, channel in enumerate(channels):
        btn_text = f"❌ {channel['link']}"
        markup.add(types.InlineKeyboardButton(btn_text, callback_data=f"delete_channel_{idx}"))
    markup.add(types.InlineKeyboardButton("❌", callback_data = "delete_stats"))
    bot.send_message(msg.chat.id, "📺 O'chirmoqchi bo'lgan kanalni tanlang:", reply_markup=markup)



        
        

@bot.message_handler(func=lambda msg: msg.text == "📋 Kanallar ro'yxati")
def show_channels(msg):
    if str(msg.from_user. id) != ADMIN_ID:
        bot.send_message(msg.chat.id, "❌ Bu buyruq siz uchun emas.")
        return
    
    channels = list(channels_collection.find({}, {"_id": 0, "link": 1, "id": 1}))
    
    if not channels: 
        bot.send_message(msg.chat.id, "📺 Hech qanday kanal qo'shilmagan.")
        return
    markup = types.InlineKeyboardMarkup()
    text = "📺 *Qo'shilgan Kanallar: *\n\n"
    for idx, channel in enumerate(channels, 1):
        text += f"{idx}. {channel['link']}\n"
    
    
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


@bot.message_handler(func=lambda msg: msg.text == "🏷 Admin tayinlash")
def add_admin(msg):
    if str(msg.from_user.id) != ADMIN_ID:  # Faqat superadmin kirishi mumkin
        bot.send_message(msg.chat.id, "❌ Siz superadmin emassiz.")
        return

    # Yangi admin "user_id"ni kiritishni so'raymiz
    bot.send_message(msg.chat.id, "👤 Admin tayinlash uchun foydalanuvchining ID sini yuboring.")
    state[str(msg.from_user.id)] = ["waiting_for_admin_id"]  # Holatni saqlash
    

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_for_admin_id")
def save_admin_id(msg):
    admin_id = msg.text.strip()

    if not admin_id.isdigit():  # Faqat raqamlarni qabul qilish
        bot.send_message(msg.chat.id, "❌ Admin ID faqat raqamlardan iborat bo'lishi kerak.")
        return

    # Admin ID saqlanadi va nomni kiritish so'raladi
    state[str(msg.from_user.id)] = ["waiting_for_admin_name", admin_id]
    bot.send_message(msg.chat.id, f"✅ Admin ID ({admin_id}) qabul qilindi. Endi uning nomini kiriting.")
    

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_for_admin_name")
def save_admin_name(msg):
    admin_name = msg.text.strip()
    admin_id = state[str(msg.from_user.id)][1]  # Oldindan kiritilgan ID'ni olish

    # Adminni MongoDB kolleksiyasiga qo‘shish
    if admins_collection.find_one({"user_id": int(admin_id)}):
        bot.send_message(msg.chat.id, "❗ Bu foydalanuvchi allaqachon admin.")
    else:
        admins_collection.insert_one({
            "user_id": int(admin_id),
            "name": admin_name
        })
        bot.send_message(msg.chat.id, f"✅ Yangi admin qo'shildi:\n🆔 ID: {admin_id}\n👤 Ismi: {admin_name}")

    del state[str(msg.from_user.id)]  # Holatni tozalash
    
  #===== Adminni o'chirish=====

@bot.message_handler(func=lambda msg: msg.text == "🚫 Adminni olish")
def remove_admin(msg):
    if str(msg.from_user.id) != ADMIN_ID:  # Faqat superadmin kirishi mumkin
        bot.send_message(msg.chat.id, "❌ Siz superadmin emassiz.")
        return

    # Adminni bekor qilish uchun ID kiritishni so'rash
    bot.send_message(msg.chat.id, "👤 Adminlikni olib tashlash uchun foydalanuvchining ID sini yuboring.")
    state[str(msg.from_user.id)] = ["waiting_for_remove_admin"]  # Holatni saqlash
    

@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                     and state[str(msg.from_user.id)][0] == "waiting_for_remove_admin")
def delete_admin(msg):
    admin_id = msg.text.strip()  # O'chiriladigan admin ID sini olish

    if not admin_id.isdigit():
        bot.send_message(msg.chat.id, "❌ Foydalanuvchi ID faqat raqamlardan iborat bo'lishi kerak.")
        return

    # Admin bazadan o'chiriladi
    result = admins_collection.delete_one({"user_id": int(admin_id)})
    if result.deleted_count > 0:
        bot.send_message(msg.chat.id, f"✅ Foydalanuvchi {admin_id} adminlikdan o'chirildi.")
    else:
        bot.send_message(msg.chat.id, "❌ Bu foydalanuvchi admin emas.")

    # Holatni tozalash
    del state[str(msg.from_user.id)]



# ====================== PANELNI YOPISH =========================
@bot.message_handler(func=lambda msg: msg.text == "⛔ STOP")
def back_panel(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    state.pop(str(msg.from_user.id), None)
    #== Admin panel qayta ochiladi===
    markup = admin_panel()
    text = "🚫 Jarayon to'xtatildi!"
    
    bot.send_message(
        msg.chat.id, 
        text, 
        parse_mode="Markdown",
        reply_markup=markup
        )
    
    
# --- USER uchun ORTGA tugmasi (ADMIN bo'lmaganlar uchun) ---
# @bot.message_handler(func=lambda m: m.text == "🔙")
# def back_user(msg):
#     if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
#         return
    
#     state.pop(str(msg.from_user.id), None)
#     bot.send_message(
#         msg.chat.id,
#         "🆔 Kino kodini kiriting:\n\t(🔍 Yoki kino nomini:)",
#         reply_markup=types.ReplyKeyboardRemove()
#     )


    




#============ADMIN XABARI===========
@bot.message_handler(func=lambda msg: msg.text == "📢 Xabar yuborish")
def ask_broadcast(msg):
    if not str(msg.from_user.id) == ADMIN_ID:
        bot.send_message(msg.chat.id, "⚠️ Sizga xabar yuborish uchun ruxsat berilmagan!!!")
        return
    bot.send_message(msg.chat.id, "📝 Yuboriladigan xabarni kiriting:")
    state[str(msg.from_user.id)] = ["waiting_for_broadcast"]

#XabarBoshlandi:
 
@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state 
                      and state[str(msg.from_user.id)][0] == "waiting_for_broadcast",
                      content_types=['text', 'photo', 'video', 'audio', 'voice', 'document', 'animation', 'sticker'])
def do_broadcast(msg):

    # MEDIA GROUP (ALBOM) BO'LSA
    if msg.media_group_id:
        group_id = msg.media_group_id
    
        # --- Agar bu albom allaqachon yuborilayotgan bo'lsa, qaytamiz ---
        if album_sending.get(group_id) == "sending":
            return
    
        # Buferga saqlaymiz
        if group_id not in album_buffer:
            album_buffer[group_id] = []
        album_buffer[group_id].append(msg)
    
        # 0.5s kutamiz – albom tugashini kutish uchun
        time.sleep(0.5)
    
        # Albom hali tugamagan bo‘lsa — chiqamiz
        if album_buffer[group_id][-1].message_id != msg.message_id:
            return
    
        # Bu joyga kelgan bo'lsa — albom tugadi
        album_sending[group_id] = "sending"   # <—— LOCK qo‘yildi
    
        # Endi ALBOMNI YUBORAMIZ
        
        users_cursor = users_collection.find({}, {"_id": 0, "user_id": 1})
        users_list = [u["user_id"] for u in users_cursor]

    
        bot.send_message(msg.chat.id, "📤 Albom yuborilmoqda...")
    
        sent = 0
        media_group = []
    
        for m in album_buffer[group_id]:
            if m.content_type == "photo":
                media_group.append(
                    telebot.types.InputMediaPhoto(
                        media=m.photo[-1].file_id,
                        caption=m.caption if m.caption else None
                    )
                )
            elif m.content_type == "video":
                media_group.append(
                    telebot.types.InputMediaVideo(
                        media=m.video.file_id,
                        caption=m.caption if m.caption else None
                    )
                )
    
        for uid in users_list:
            try:
                bot.send_media_group(int(uid), media_group)
                sent += 1
                time.sleep(0.05)
            except Exception as e:
                print(e)
                continue

    
        bot.send_message(msg.chat.id, f"✅ Albom {sent} ta foydalanuvchiga yuborildi!")
    
        # Tozalaymiz
        del album_buffer[group_id]
        del album_sending[group_id]     # <—— LOCK bo‘shatildi
        del state[str(msg.from_user.id)]
    
        return



    # ——————————————————————
    # AGAR ODDIY XABAR BO'LSA
    # ——————————————————————
    
    users_cursor = users_collection.find({}, {"_id": 0, "user_id": 1})
    users_list = [u["user_id"] for u in users_cursor]  # agar bo‘sh bo‘lsa → users_list bo‘sh ro‘yxat


    bot.send_message(msg.chat.id, "⏳ Xabar yuborilmoqda, kuting...")

    sent = 0
    for uid in users_list:
        try:
            bot.copy_message(int(uid), msg.chat.id, msg.message_id)
            sent += 1
            time.sleep(0.02)
        except Exception as e:
            print(e)
            continue

    bot.send_message(msg.chat.id, f"✅ Xabar {sent} ta foydalanuvchiga yuborildi!")
    del state[str(msg.from_user.id)]




# =================== FILM O'CHIRISH MENYU ===================

@bot.message_handler(func=lambda msg: msg. text == "❌ Film o'chirish")
def delete_content_menu(msg):
    """Film o'chirish menyu (kino/serial tanlash) - ✅ YANGI"""
    user_id = msg.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    buttons = [
        {"text": "🎥 Kino", "callback":  "delete_type_kino"},
        {"text": "🎞 Serial", "callback": "delete_type_serial"},
        {"text": "🔙 Ortga", "callback": "delete_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        "🗑️ *Film O'chirish - Turini Tanlang*\n\n🎥 Kino yoki 🎞 Serial? ",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "delete_type_kino")
def delete_type_kino(call):
    """Kino o'chirish - eski logika"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "❌ O'chirilgan kinoning kodini kiriting.")
    state[str(call.from_user.id)] = ["waiting_for_delete_kino"]


@bot.callback_query_handler(func=lambda call: call.data == "delete_back_to_admin")
def delete_back_to_admin(call):
    """Ortga tugmasi"""
    bot.delete_message(call. message.chat.id, call. message.message_id)
    admin_panel()
    


# ============================================
# SERIAL O'CHIRISH - TO'LIQ TUZATILGAN
# HDKinolarBot.py da Line 1550 atrofidagi MAVJUD kodlarni ALMASHTIRING
# ============================================

@bot.callback_query_handler(func=lambda call: call.data == "delete_type_serial")
def delete_type_serial(call):
    """Serial o'chirish menyu - ✅ TUZATILGAN"""
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    # ✅ SERIALLAR RO'YXATINI OLISH
    serials_list = list(serials.find({}, {"_id": 0, "code": 1, "name": 1}))
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    if not serials_list:
        bot.send_message(
            call.message.chat.id,
            "📺 Hech qanday serial yo'q.",
            parse_mode="Markdown"
        )
        return
    
    # ✅ SERIALLAR TUGMALARI
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:
        markup.add(types.InlineKeyboardButton(
            f"🎞 {serial['name']}",
            callback_data=f"delete_serial_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_back_to_admin"))
    
    bot.send_message(
        call.message.chat.id,
        "🗑️ *Qaysi serialni o'chirish?*\n\nSerialni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== SERIAL O'CHIRISH CALLBACK ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_serial_"))
def delete_serial_selected(call):
    """Serial o'chirish uchun tanlandi"""
    # "delete_serial_confirm_" dan ajratish kerak
    if call.data.startswith("delete_serial_confirm_"):
        return  # Bu boshqa handler uchun
    
    serial_code = call.data.replace("delete_serial_", "")
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # Mavsum statistikasi
    season_count = len(serial.get('seasons', []))
    total_episodes = sum(len(s.get('episodes', [])) for s in serial.get('seasons', []))
    
    markup = types.InlineKeyboardMarkup()
    
    # Fasllarni boshqarish
    if season_count > 0:
        markup.add(types.InlineKeyboardButton(
            f"📺 Fasllarni boshqarish ({season_count} mavsum)",
            callback_data=f"delete_serial_seasons_{serial_code}"
        ))
    
    # Butunlay o'chirish
    markup.add(types.InlineKeyboardButton(
        "❌ Butun serialni o'chirish",
        callback_data=f"delete_serial_confirm_{serial_code}"
    ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_type_serial"))
    
    bot.send_message(
        call.message.chat.id,
        f"🎞 *{serial['name']}*\n\n"
        f"📊 Jami: {season_count} mavsum, {total_episodes} qism\n\n"
        f"Nima qilmoqchisiz?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== BUTUN SERIALNI O'CHIRISH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_serial_confirm_"))
def delete_serial_all(call):
    """Butun serialni o'chirish tasdiqlash"""
    serial_code = call.data.replace("delete_serial_confirm_", "")
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    # MongoDB dan o'chirish
    result = serials.delete_one({"code": serial_code})
    
    if result.deleted_count > 0:
        bot.answer_callback_query(call.id, "✅ Serial o'chirildi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(
            call.message.chat.id,
            f"✅ *'{serial['name']}' seriali o'chirildi.*",
            parse_mode="Markdown"
        )
    else:
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!")

# =================== FASLLARNI KO'RSATISH (O'chirish uchun) ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_serial_seasons_"))
def delete_serial_seasons(call):
    """Serialning fasllarini ko'rsatish - o'chirish uchun"""
    serial_code = call.data.replace("delete_serial_seasons_", "")
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup()
    
    seasons = serial.get("seasons", [])
    
    if not seasons:
        markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_{serial_code}"))
        bot.send_message(
            call.message.chat.id,
            f"🎞 *{serial['name']}*\n\n❌ Hech qanday mavsum yo'q.",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return
    
    for season in seasons:
        season_num = season["season_number"]
        episodes_count = len(season.get("episodes", []))
        
        markup.add(types.InlineKeyboardButton(
            f"📺 {season_num}-Mavsum ({episodes_count} qism)",
            callback_data=f"delete_season_select_{serial_code}_{season_num}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_{serial_code}"))
    
    bot.send_message(
        call.message.chat.id,
        f"🎞 *{serial['name']}*\n\n📺 Mavsumni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== MAVSUM TANLANDI - QISMLAR YOKI BUTUN MAVSUM ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_season_select_"))
def delete_season_or_episode(call):
    """Mavsum tanlandi - qismlarini ko'rsatish yoki butun mavsumni o'chirish"""
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    serial = serials.find_one({"code": serial_code})
    
    if not serial:
        bot.answer_callback_query(call.id, "❌ Serial topilmadi!")
        return
    
    # Mavsumni topish
    season = next((s for s in serial.get('seasons', []) if s['season_number'] == season_number), None)
    
    if not season:
        bot.answer_callback_query(call.id, "❌ Mavsum topilmadi!")
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
    
    # Butun mavsumni o'chirish
    markup.add(types.InlineKeyboardButton(
        f"❌ Butun {season_number}-Mavsumni o'chirish",
        callback_data=f"delete_season_confirm_{serial_code}_{season_number}"
    ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_seasons_{serial_code}"))
    
    ep_count = len(episodes)
    
    text = f"📺 *{serial['name']}*\n"
    text += f"🎬 {season_number}-Mavsum\n\n"
    
    if ep_count > 0:
        text += f"Qismlar: {ep_count} ta\n\nQismni tanlang yoki butun mavsumni o'chiring:"
    else:
        text += "❌ Hech qanday qism yo'q\n\nMavsumni o'chirish:"
    
    bot.send_message(
        call.message.chat.id,
        text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

# =================== BUTUN MAVSUMNI O'CHIRISH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_season_confirm_"))
def delete_season_all(call):
    """Butun mavsumni o'chirish"""
    parts = call.data.split("_")
    serial_code = parts[3]
    season_number = int(parts[4])
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    # Mavsumni o'chirish
    result = serials.update_one(
        {"code": serial_code},
        {"$pull": {"seasons": {"season_number": season_number}}}
    )
    
    if result.modified_count > 0:
        bot.answer_callback_query(call.id, f"✅ {season_number}-Mavsum o'chirildi!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Qayta fasllar ro'yxatini ko'rsatish
        serial = serials.find_one({"code": serial_code})
        
        if serial and serial.get('seasons'):
            # Hali fasllar bor
            markup = types.InlineKeyboardMarkup()
            
            for season in serial['seasons']:
                season_num = season["season_number"]
                episodes_count = len(season.get("episodes", []))
                
                markup.add(types.InlineKeyboardButton(
                    f"📺 {season_num}-Mavsum ({episodes_count} qism)",
                    callback_data=f"delete_season_select_{serial_code}_{season_num}"
                ))
            
            markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_{serial_code}"))
            
            bot.send_message(
                call.message.chat.id,
                f"✅ {season_number}-Mavsum o'chirildi!\n\n🎞 *{serial['name']}*\n\n📺 Boshqa mavsum:",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            # Hech qanday fasl qolmadi
            bot.send_message(
                call.message.chat.id,
                f"✅ {season_number}-Mavsum o'chirildi!\n\n❌ Serialda boshqa mavsum yo'q.",
                parse_mode="Markdown"
            )
    else:
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!")

# =================== QISMNI O'CHIRISH ===================

@bot.callback_query_handler(func=lambda call: call.data.startswith("delete_episode_"))
def delete_episode_confirm(call):
    """Qismni o'chirish"""
    parts = call.data.split("_")
    serial_code = parts[2]
    season_number = int(parts[3])
    episode_number = int(parts[4])
    user_id = call.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.answer_callback_query(call.id, "❌ Ruxsat yo'q!")
        return
    
    # Qismni o'chirish
    result = serials.update_one(
        {"code": serial_code, "seasons.season_number": season_number},
        {"$pull": {"seasons.$.episodes": {"episode_number": episode_number}}}
    )
    
    if result.modified_count > 0:
        bot.answer_callback_query(call.id, f"✅ {episode_number}-qism o'chirildi!")
        
        # Qayta qismlar ro'yxatini ko'rsatish
        serial = serials.find_one({"code": serial_code})
        season = next((s for s in serial.get('seasons', []) if s['season_number'] == season_number), None)
        
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        if season and season.get('episodes'):
            # Hali qismlar bor
            markup = types.InlineKeyboardMarkup()
            
            for episode in season['episodes']:
                ep_num = episode["episode_number"]
                markup.add(types.InlineKeyboardButton(
                    f"🎬 {ep_num}-qism",
                    callback_data=f"delete_episode_{serial_code}_{season_number}_{ep_num}"
                ))
            
            markup.add(types.InlineKeyboardButton(
                f"❌ Butun {season_number}-Mavsumni o'chirish",
                callback_data=f"delete_season_confirm_{serial_code}_{season_number}"
            ))
            
            markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=f"delete_serial_seasons_{serial_code}"))
            
            bot.send_message(
                call.message.chat.id,
                f"✅ {episode_number}-qism o'chirildi!\n\n"
                f"📺 *{serial['name']}*\n"
                f"🎬 {season_number}-Mavsum\n\n"
                f"Boshqa qismlar:",
                reply_markup=markup,
                parse_mode="Markdown"
            )
        else:
            # Hech qanday qism qolmadi
            bot.send_message(
                call.message.chat.id,
                f"✅ {episode_number}-qism o'chirildi!\n\n"
                f"❌ {season_number}-Mavsumda boshqa qism yo'q.",
                parse_mode="Markdown"
            )
    else:
        bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi!")









# =================== BACK BUTTON HANDLERLARI ===================

# @bot.callback_query_handler(func=lambda call: call.data == "serial_back_to_admin")
# def serial_back_menu(call):
#     """Asosiy serial menuyga qaytish"""
#     bot.  delete_message(call.message.  chat. id, call.message.  message_id)
#     upload_serial_menu(call.message)

@bot.callback_query_handler(func=lambda call: call.data == "delete_back_to_admin")
def delete_back_menu(call):
    """Admin paneliga qaytish - ✅ TUZATILGAN"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    admin_panel()

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
    
    
    
    
    
    


# =================== FILM KODLARI (Admin uchun) ===================

@bot.message_handler(func=lambda msg: msg.text == "📂 Kinolar")
def movie_list(msg):
    """Film kodlari ro'yxati (Admin uchun)"""
    user = msg.from_user.id
    
    if not check_sub(user):
        upload_mdb(msg)
        return
    
    if movies.count_documents({}) == 0:
        bot.send_message(msg.chat.id, "📂 Bazada kino yo'q.")
        return
    
    all_movies = list(movies.find({}, {"_id": 0}))
    total = len(all_movies)
    
    markup = types.InlineKeyboardMarkup()
    if total > 5:
        markup.add(types.InlineKeyboardButton("➡️ keyingi", callback_data="page_2"))
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
    
    text = "*🎬 Kinolar ro'yxati*\n\n"
    text += f"📊 Topildi: {total} ta kino | Sahifa: 1/{(total-1)//5+1}\n\n"
    
    c = 1
    for m in all_movies[: 5]:
        code = m['code']
        text += f"{c}.   {m['name']}\n"
        text += f"🆔 Kod: `{code}`\n"
        text += f"[▶️ Kinoni yuklash](https://t.me/DubKinoBot?start={code})\n"
        text += f"*{'─' * 10}*\n"
        c += 1
    
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)



# HDKinolarBot.py da qo'shish: 
    
    
    
    
    
    

    
    

# =================== SERIALLAR (User uchun) - ✅ YANGI ===================

@bot.message_handler(func=lambda msg: msg.text == "📥 Seriallar")
def show_user_serials(msg):
    """Foydalanuvchi uchun seriallar ro'yxati"""
    user = msg. from_user.id
    
    if not check_sub(user):
        upload_mdb(msg)
        return
    
    serials_list = list(serials.find({}, {"_id": 0, "code": 1, "name": 1, "image": 1}))
    
    if not serials_list: 
        bot.send_message(msg.chat.id, "📺 Hech qanday serial qo'shilmagan.")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:
        markup.add(types.InlineKeyboardButton(
            f"🎞 {serial['name']}",
            callback_data=f"user_view_serial_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙", callback_data="user_back_from_serials"))
    
    bot.send_message(
        msg.chat.id,
        "📺 *Barcha Seriallar*\n\nSerialni tanlang:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data. startswith("user_view_serial_"))
def user_view_serial(call):
    """Foydalanuvchi serialni tanlaganda"""
    serial_code = call.data.replace("user_view_serial_", "")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    show_serial_for_user(call.message.chat.id, serial_code)

@bot.callback_query_handler(func=lambda call: call.data == "user_back_from_serials")
def user_back_from_serials(call):
    """Seriallardan ortga"""
    bot.delete_message(call.message.chat. id, call.message.message_id)
    user_panel(call.message.chat.id)






# Statistika ko'rsatuvchi tugma ("♻️ Statistika")
@bot.message_handler(func=lambda msg: msg.text == "♻️ Statistika")
def show_statistics(msg):
    # Faqat admin kirishi mumkin
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz.")
        return
    
    # MongoDB Atlas bazasidan foydalanuvchilar va kinolar sonini olib kelish
    user_count = users_collection.count_documents({})  # Foydalanuvchilar soni
    movie_count = movies.count_documents({})  # Kinolar soni
    # Adminlar soni va nomlarini olish
    admins = list(admins_collection.find({}, {"_id": 0, "user_id": 1, "name": 1}))  # Tayinlangan adminlar
    admin_count = len(admins)
    
    # Javob statistika xabari
    stats_text = (
        f"📊 *Statistika:*\n\n"
        f"👤 Foydalanuvchilar soni: *{user_count}*\n"
        f"🎬 Kinolar soni: *{movie_count}*\n"
    )
    markup = types.InlineKeyboardMarkup()
    # Super Admin uchun tayinlangan adminlar sonini ko‘rsatish
    if str(msg.from_user.id) == ADMIN_ID:  # Foydalanuvchi Super Admin bo'lsa
        stats_text += f"🏷 Tayinlangan adminlar soni: *{admin_count}*\n"
        if admins:
            stats_text += "📋 Adminlar ro'yxati:\n"
            for admin in admins:
                admin_id = admin['user_id']
                stats_text += f"  - 🆔 `{admin_id}`, 👤 {admin['name']}\n"

                
    # Xabarni o'chirish tugmasi qo'shish
    
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_stats"))
    
    bot.send_message(msg.chat.id, stats_text, parse_mode="Markdown", reply_markup=markup)

        

                

# ====================== UMUMIY HANDLER ========================
# =================== UNIVERSAL HANDLER - ✅ YANGILANGAN VA TUZATILGAN ===================

@bot.message_handler(func=lambda msg:   True)
def universal_handler(msg):
    """Umumiy handler - kino/serial qidirish VA admin kino o'chirish"""
    user = str(msg.  from_user. id)
    text = msg.text.  strip()
    
    # 1️⃣ ADMIN KINO O'CHIRAYAPTI
    if user in state and state[user][0] == "waiting_for_delete_kino":
        result = movies.delete_one({"code": text})
        
        if result.  deleted_count > 0:
            bot.send_message(msg.chat.id, f"✔ Kino o'chirildi!\nKino kodi: {text}")
        else:
            bot.send_message(msg.chat.id, "❌ Bunday kod mavjud emas.")
        
        del state[user]
        return
    
    # 2️⃣ OBUNANI TEKSHIRISH
    if not check_sub(int(user)):
        upload_mdb(msg)
        return
    
    # 3️⃣ QIDIRISH
    if not text:
        bot.send_message(msg.chat.id, "❌ Kino kodi yoki nomini kiriting!")
        return
    
    result = search_content_by_code_or_name(text)
    
    # KINO - KOD TOPILDI
    if result[0] == "movie_code_found":  
        movie = result[1][0]
        send_movie_info(msg. chat.id, movie['code'])
        return
    
    # SERIAL - KOD TOPILDI - ✅ YANGI
    if result[0] == "serial_code_found":
        serial = result[1][0]
        show_serial_for_user(msg.chat.id, serial['code'])
        return
    
    # NOTASI - JUDA QO'LIK
    if result[0] == "too_short":
        bot.send_message(
            msg.chat.id,
            "❌ Kamina 3 ta belgi kiriting!\n\t(🔍 Kino nomini bot topishi kerak. )"
        )
        return
    
    # TOPILDI - KINO VA SERIALLAR - ✅ YANGILANGAN
    if result[0] == "found": 
        filtered_items = result[1]
        pages = result[2]
        total = result[3]
        
        user_int = int(user)
        search_cache[user_int] = {
            "query": text,
            "items":    filtered_items,
            "total":  total,
            "pages":   pages
        }
        
        # Birinchi sahifa
        page = 1
        boshlash = 0
        end = 5
        page_items = filtered_items[boshlash:end]
        
        text_result = f"🎬 **Qidirush natijalari:   '{text}'**\n\n"
        text_result += f"📊 Topildi: {total} ta | Sahifa: {page}/{pages}\n\n"
        
        c = 1
        for item in page_items:
            if "seasons" in item:  # Serial
                text_result += f"{c}.  🎞 {item['name']}\n"
                text_result += f"🆔 Kod: `{item['code']}`\n"
                text_result += f"[▶️ Serial](https://t.me/DubKinoBot?start={item['code']})\n"
            else:  # Kino
                text_result += f"{c}. 🎬 {item['name']}\n"
                text_result += f"🆔 Kod: `{item['code']}`\n"
                text_result += f"[▶️ Yuklab olish](https://t.me/DubKinoBot?start={item['code']})\n"
            
            text_result += f"*{'─' * 30}*\n"
            c += 1
        
        # Tugmalar
        markup = types.InlineKeyboardMarkup()
        btns = []
        
        if pages > 1:
            btns.append(types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"search_{user_int}_page_2"))
        
        btns.append(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
        
        if btns:
            markup.row(*btns)
        
        bot. send_message(msg.chat.id, text_result, parse_mode="Markdown", reply_markup=markup)
        return
    
    # TOPILMADI
    bot.send_message(
        msg.chat.id,
        f"❌ '{text}' bo'yicha hech qanday kino yoki serial topilmadi.\n\n"
        f"💡 Maslahat: To'liq nomi yoki kodni kiriting."
    )
        
    
    


@app.route('/' + TOKEN, methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "ok", 200

# Just to test server
@app.route('/')
def index():
    return "Bot is running"

if __name__ == "__main__":

    PORT = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=PORT)

# ==============================================================#
    