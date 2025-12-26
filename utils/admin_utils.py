# utils/admin_utils.py
"""
👥 ADMIN UTILITIES
Admin panellar, obuna tekshiruvi, user saqlash
"""

from telebot import types
from .db_config import bot, admins_collection, channels_collection, users_collection #, state
#from config.settings import ADMIN_ID

# === Admin Panel - ✅ YANGILANGAN ===
def admin_panel(chat_id):
    """Admin Panel"""
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("🎬 Film yuklash", "📂 Kinolar")
    btn.add("❌ Film o'chirish", "📥 Seriallar")
    btn.add("💼 Super Admin", "♻️ Statistika")
    btn.add("⛔ STOP")
    bot.send_message(chat_id, "🔐 Admin paneli", reply_markup=btn)

def super_admin_panel(chat_id):
    """Super Admin Panel"""
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📢 Xabar yuborish", "🏷 Admin tayinlash")
    btn.add("🚫 Adminni olish", "📺 Kanal qo'shish")
    btn.add("❌ Kanal o'chirish", "📋 Kanallar ro'yxati")
    btn.add("🔙 Ortga")
    bot.send_message(chat_id, "👑 Super Admin Paneli", reply_markup=btn)

def user_panel(chat_id):
    """User Panel - ✅ YANGILANGAN"""
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📂 Kinolar", "📥 Seriallar")
    btn.add("🎁 Donat", "📊 Top 10")
    bot.send_message(chat_id, "🆔 Kino kodini kiriting:\n\t(🔍 Yoki kino nomini: )", reply_markup=btn)

# === Obuna Tekshirish ===
def check_sub(user_id):
    """Obunani tekshirish"""
    try:
        channels = list(channels_collection.find({}, {"_id": 0, "id": 1, "link": 1}))
        
        if not channels:
            return True
        
        channels_to_check = [ch["id"] for ch in channels if "id" in ch and ch["id"] is not None]
        
        if not channels_to_check:
            return True
        
        for channel in channels_to_check:
            try:
                member = bot.get_chat_member(channel, user_id)
                if member.status not in ["member", "administrator", "creator"]:
                    return False
            except Exception as e:
                print(f"❌ Kanal tekshirish xatosi ({channel}): {e}")
                return False
        
        return True
    
    except Exception as e: 
        print(f"❌ check_sub xatosi: {e}")
        return False

def upload_mdb(msg):
    """Obuna so'rash xabari"""
    channels = list(channels_collection.find({}, {"_id": 0, "link": 1}))
    
    if not channels:
        return
    
    btn = types.InlineKeyboardMarkup()
    for channel in channels:
        btn. add(types.InlineKeyboardButton("📌 Kanalga obuna bo'lish", url=channel["link"]))
    
    btn.add(types.InlineKeyboardButton("♻️ Tekshirish", callback_data="check"))
    
    bot.send_message(
        msg.chat.id,
        "❗ Botdan foydalanish uchun kanalga obuna bo'ling! ",
        reply_markup=btn
    )

def is_admin(user_id):
    """Admin tekshiruvi"""
    return admins_collection.find_one({"user_id": int(user_id)}) is not None

def save_user(user_id):
    """Userni bazaga saqlash"""
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})