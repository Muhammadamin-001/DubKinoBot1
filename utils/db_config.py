# utils/db_config.py
"""
🛢️ DATABASE CONFIGURATION
MongoDB, Bot instance va global o'zgaruvchilar
"""

import telebot
from pymongo import MongoClient
from config.settings import TOKEN, MONGO_URI

# ⭐ BOT INSTANCE (GLOBAL)
bot = telebot.TeleBot(TOKEN)

# 🔌 MONGODB CONNECTION
client = MongoClient(MONGO_URI)
db = client["TelegramBot"]

# 📚 COLLECTIONS
users_collection = db["users"]
movies = db["movies"]
serials = db["serials"]
admins_collection = db["admins"]
channels_collection = db["channels"]

# 🌍 GLOBAL STATE
state = {}
user_clicks = {}
album_buffer = {}
album_sending = {}
search_cache = {}
user_pages = {}
movie_pages = {}