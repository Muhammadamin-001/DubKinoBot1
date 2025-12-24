# ============================================
# HDKinolarBot.py - ASOSIY BOT FAYLI
# ============================================

# 📦 Standart kutubxonalar
import os
import time
from flask import Flask, request
import telebot
from telebot import types
#from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ⚙️ Konfiguratsiya
from config. settings import TOKEN, ADMIN_ID #, WEBHOOK_URL, MONGO_URI

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
# ✅ TUZATILDI:  FAQAT MAVJUD FUNKSIYALARNI IMPORT QIL
from serial.serial_handler import (
    upload_serial_menu,
    delete_serial_menu,
    show_serial_menu_after_upload  # ✅ QOSHILDI
)
from serial.serial_user import show_serial_for_user
from movies.movie_handler import send_movie_info#, upload_movie #, catch_video, movie_code, movie_name, movie_genre, movie_url
#from movies.movie_db import get_movie, get_all_movies

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



# def send_movie_info(chat_id, kino_kodi):
#     movie = movies.find_one({"code": kino_kodi})  # Kino kodi bo'yicha ma'lumot
#     if movie:
#         file_id = movie["file_id"]
#         code = movie["code"]
#         markup = types.InlineKeyboardMarkup()
#         markup.add(types.InlineKeyboardButton("🎬 Kanalimiz", url = kanal_link))  # Kanal linki
#         markup.add(types.InlineKeyboardButton("❌", callback_data="delete_movie"))
#         # Kino haqida ma'lumot yuboriladi
#         caption_text = (
#                 f"🎬 {movie['name']} \n"
#                 f"{'─' * 15}\n"
#                 f"💽 Formati: {movie['formati']}\n"
#                 f"🎞 Janri: {movie['genre']}\n"
#                 f"🆔 Kod: {code}\n\n"
#                 f"🤖 Botimiz: {movie['urlbot']}"
#         )
#         bot.send_video(
#             chat_id,
#             file_id,
#             caption = caption_text,
#             reply_markup=markup
#         )
        
#     else:
#         bot.send_message(chat_id, "❌ Bunday kod bo‘yicha kino topilmadi.")
        





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
# @bot.callback_query_handler(func=lambda call: call.data == "delete_movie")
# def delete_movie_warning(call):
#     markup = InlineKeyboardMarkup()
#     markup.add(
#         InlineKeyboardButton("❌ O'chirish", callback_data="delete_movie_confirm")
#     )

#     bot.answer_callback_query(
#         call.id,
#         "⚠️ Rostdan ham kinoni o‘chirmoqchimisiz?\n\nYana bir marta bosing ...❌",
#         show_alert=True
#     )

#     # ❗ XABAR O‘CHMAYDI
#     # faqat tugma o‘zgaradi
#     bot.edit_message_reply_markup(
#         call.message.chat.id,
#         call.message.message_id,
#         reply_markup=markup
#     )
    
# @bot.callback_query_handler(func=lambda call: call.data == "delete_movie_confirm")
# def delete_movie_confirm(call):
#     try:
#         bot.delete_message(call.message.chat.id, call.message.message_id)
#         bot.answer_callback_query(call.id, "✅ Kino o‘chirildi")
#     except Exception as e:
#         print(e)
#         bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi")

    
    
        

# @bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
# def page_switch(call):
#     page = int(call.data.split("_")[1])
#     all_movies = list(movies.find({}, {"_id": 0}))
#     total = len(all_movies)
#     text, pages = get_movie_page(page)
    
#     text += f" \t📚| Sahifa: {page}/{pages}\n\n"
#     markup = types.InlineKeyboardMarkup()
#     btns = []

#     if page > 1:
#         btns.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"page_{page-1}"))
        
        
#     if page > 1 and page < pages:
#         btns.append(types.InlineKeyboardButton("📌 Last", callback_data=f"page_{pages}"))
        
#     if page < pages:
#         btns.append(types.InlineKeyboardButton("➡️ Next", callback_data=f"page_{page+1}"))
        
#     # O'chirish tugmasi qo'shish
#     btns.append(types.InlineKeyboardButton("❌", callback_data="delete_msg_list"))
       
#     if btns:
#         markup.row(*btns)

#     try:
#         bot.edit_message_text(
#             f"🎬 *Kino ro‘yxati:*\n\n📊 Topildi: {total} ta kino |\n\n" + text,
#             chat_id=call.message.chat.id,
#             message_id=call.message.message_id,
#             parse_mode="Markdown",
#             reply_markup=markup
#             )
#     except:
#         pass




# =================== PAGE HANDLER - ✅ QOSHILDI ===================

@bot.callback_query_handler(func=lambda call: call.  data.  startswith("page_"))
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

@bot.callback_query_handler(func=lambda c: c.data.  startswith("search_"))
def search_page_switch(call):
    """Qidirush natijalari sahifalarini chiqarish - ✅ YANGILANGAN"""
    try:
        parts = call.data.split("_page_")
        user_id = int(parts[0]. replace("search_", ""))
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
        
        bot. edit_message_text(
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
    admin_panel(call.message.chat.id)



# ====================== START ================================
@bot.message_handler(commands=['start'])
def start(msg):
    """Start komandasi"""
    user = msg. from_user.id
    
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

    bot.send_message(msg.chat.id, "🆔 Film kodini kiriting:\n\t(🔍 Yoki film nomini: )")



    
 

# ====================== ADMIN PANEL ===========================
@bot.message_handler(commands=['panel'])
def panel(msg):
    user = msg.from_user.id
    if not check_sub(user):
        upload_mdb(msg)
        return
    
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        admin_panel(msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "❌ Diqqat! Bu faqat admin uchun.")
        
@bot.message_handler(commands=['kodlar'])
def kodlar(msg):
    user = msg.from_user.id
    if not check_sub(user):
        upload_mdb(msg)
        return
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        bot.send_message(msg.chat.id, "❗ Bu komanda admin uchun emas.")
        return
    
    user_panel(msg.chat.id)
 



# HDKinolarBot.py da qo'shish:

# =================== FILM YUKLASH MENYU ===================

@bot. message_handler(func=lambda msg: msg.text == "🎬 Film yuklash")
def upload_content_menu(msg):
    """Film yuklash menyu (kino/serial tanlash) - ✅ YANGI"""
    user_id = msg.from_user.id
    
    if not (str(user_id) == ADMIN_ID or is_admin(user_id)):
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz!")
        return
    
    buttons = [
        {"text": "🎥 Kino", "callback": "upload_type_kino"},
        {"text": "🎞 Serial", "callback": "upload_type_serial"},
        {"text": "🔙 Ortga", "callback":  "upload_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        msg.chat.id,
        "📺 *Film Yuklash - Turini Tanlang*\n\n🎥 Kino yoki 🎞 Serial? ",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "upload_type_kino")
def upload_type_kino(call):
    """Kino yuklash bosilsa"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "🎬 Video yuboring (video fayl ko'rinishida).")
    state[str(call.from_user.id)] = ["waiting_for_video"]


# ✅ TUZATILDI:   CALLBACK dan SERIAL MENYU
@bot.callback_query_handler(func=lambda call: call.data == "upload_type_serial")
def upload_type_serial(call):
    """Serial yuklash bosilsa"""
    bot.delete_message(call.message.chat. id, call.message.message_id)
    
    # Serial menyu chiqarish
    buttons = [
        {"text": "➕ Yangi Serial", "callback": "serial_add_new"},
        {"text": "📺 Mavjud Seriallar", "callback": "serial_show_existing"},
        {"text": "🔙 Ortga", "callback": "upload_back_to_admin"}
    ]
    markup = create_inline_buttons(buttons)
    
    bot.send_message(
        call.message.chat.id,
        "🎞️ *Serial Yuklash Menyu*\n\nNima qilish? ",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "upload_back_to_admin")
def upload_back_to_admin(call):
    """Ortga tugmasi"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    admin_panel(call.message.chat.id)


# =================== FILM O'CHIRISH MENYU ===================

@bot. message_handler(func=lambda msg: msg.text == "❌ Film o'chirish")
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
        "🗑️ *Film O'chirish - Turini Tanlang*\n\n🎥 Kino yoki 🎞 Serial?",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "delete_type_kino")
def delete_type_kino(call):
    """Kino o'chirish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "❌ O'chirilgan kinoning kodini kiriting.")
    state[str(call.from_user.id)] = ["waiting_for_delete_kino"]


# ✅ TUZATILDI:  CALLBACK dan SERIAL O'CHIRISH MENYU
@bot.callback_query_handler(func=lambda call: call.data == "delete_type_serial")
def delete_type_serial(call):
    """Serial o'chirish menyu"""
    bot.delete_message(call.message.chat. id, call.message.message_id)
    
    from serial.serial_db import get_all_serials
    from telebot import types
    
    serials_list = get_all_serials()
    
    if not serials_list:
        bot.answer_callback_query(call.id, "📺 Hech qanday serial qo'shilmagan.")
        return
    
    markup = types.InlineKeyboardMarkup()
    
    for serial in serials_list:
        markup.add(types.InlineKeyboardButton(
            f"🎞 {serial['name']}",
            callback_data=f"delete_serial_{serial['code']}"
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data="delete_back_to_admin"))
    
    bot.send_message(
        call.message.chat.id,
        "🗑️ *Qaysi serialni o'chirish?*",
        reply_markup=markup,
        parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data == "delete_back_to_admin")
def delete_back_to_admin(call):
    """Ortga tugmasi"""
    bot.delete_message(call. message.chat.id, call. message.message_id)
    admin_panel(call.message. chat.id)




#---------------------------------------------------------------------------------------------
    
@bot.message_handler(func=lambda msg: msg.text == "🔙 Ortga")
def back(msg):
    if str(msg.from_user. id) != ADMIN_ID:
        return
    
    state. pop(str(msg.from_user.id), None)  # Holatni tozalash
    
    # Super Admin panelidan kelgan bo'lsa → Admin panelga qaytarish
    admin_panel(msg.chat.id)

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
@bot.message_handler(func=lambda msg: msg.text == "⏻ Exit")
def back_panel(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    state.pop(str(msg.from_user.id), None)
    bot.send_message(msg.chat.id, "🆔 Kino kodini kiriting:\n\t(🔍 Yoki kino nomini:)", reply_markup=types.ReplyKeyboardRemove())
    
# --- USER uchun ORTGA tugmasi (ADMIN bo'lmaganlar uchun) ---
@bot.message_handler(func=lambda m: m.text == "🔙")
def back_user(msg):
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    state.pop(str(msg.from_user.id), None)
    bot.send_message(
        msg.chat.id,
        "🆔 Film kodini kiriting:\n\t(🔍 Yoki film nomini:)",
        reply_markup=types.ReplyKeyboardRemove()
    )






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





    

# =================== FILM KODLARI (Admin uchun) ===================

@bot.message_handler(func=lambda msg: msg.text == "📂 Film kodlari")
def movie_list(msg):
    """Film kodlari ro'yxati (Admin uchun)"""
    user = msg.from_user. id
    
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
    user = msg.from_user.id
    
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
    