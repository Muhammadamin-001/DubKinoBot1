# utils/db_config.py
import telebot
from pymongo import MongoClient
from config.settings import TOKEN, MONGO_URI

# Bot instance (global)
bot = telebot.TeleBot(TOKEN)

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client["TelegramBot"]

# Kolleksiyalar
users_collection = db["users"]
movies = db["movies"]
serials = db["serials"]  # 🆕 SERIAL KOLEKSIYASI
admins_collection = db["admins"]
channels_collection = db["channels"]

# Global state
state = {}
user_clicks = {}
album_buffer = {}
album_sending = {}
search_cache = {}