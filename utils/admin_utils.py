# utils/admin_utils.py
from telebot import types
from utils.db_config import bot

def admin_panel(chat_id):
    """Admin Panel (Kino va Serial boshqarish)"""
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("🎬 Kino yuklash", "🎞 Serial yuklash")  # 🆕
    btn.add("📂 Film kodlari", "📥 Seriallar")  # 🆕
    btn.add("❌ Film o'chirish", "♻️ Statistika")
    btn.add("💼 Super Admin", "⏻ Exit")
    bot.send_message(chat_id, "🔐 Admin Paneli", reply_markup=btn)

def super_admin_panel(chat_id):
    """Super Admin Panel"""
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📢 Xabar yuborish", "🏷 Admin tayinlash")
    btn.add("🚫 Adminni olish", "📺 Kanal qo'shish")
    btn.add("❌ Kanal o'chirish", "📋 Kanallar ro'yxati")
    btn.add("🔙 Ortga")
    bot.send_message(chat_id, "👑 Super Admin Paneli", reply_markup=btn)

def user_panel(chat_id):
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📂 Film kodlari", "🎞 Seriallar")  # 🆕
    btn.add("🎁 Donat", "📊 Top 10")
    btn.add("🔙")
    bot.send_message(chat_id, "🔐 Kino kodlarini olish", reply_markup=btn)