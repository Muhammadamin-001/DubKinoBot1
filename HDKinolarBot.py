import telebot
from telebot import types
import time
from flask import Flask, request
from pymongo import MongoClient
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MONGO_URI =os.getenv("MONGO_URI")

CHANNEL_ID = [-1001574709061,  -1003359940811]#Usavyb

bot = telebot.TeleBot(TOKEN)

kanal_link="https://t.me/DubHDkinolar"

app = Flask(__name__)


for varname in ["TOKEN", "ADMIN_ID", "WEBHOOK_URL", "MONGO_URI"]:
    if globals()[varname] is None:
        print(f"ERROR: {varname} is not set!")


client = MongoClient(MONGO_URI)
db = client["TelegramBot"]   # baza nomi
users_collection = db["users"]       # userlar collection
movies = db["movies"]     # kinolar collection
admins_collection = db["admins"]  # Adminlarni saqlash kolleksiyasi



# =================== STATE (HOLAT) ============================
state = {}  


album_buffer = {}
album_sending = {}

movie_pages = {}


# === is_admin funksiyasi ===
def is_admin(user_id):
    # Foydalanuvchi admin bo'lsa, True qaytaradi
    return admins_collection.find_one({"user_id": int(user_id)}) is not None

def get_movie_page(page=1, per_page=10):
    # Barcha kinolarni bazadan o'qish
    all_movies = list(movies.find({}, {"_id": 0}))  # movies = db["movies"]
    
    total = len(all_movies)
    pages = (total - 1) // per_page + 1

    boshlash = (page - 1) * per_page
    end = boshlash + per_page
    page_movies = all_movies[boshlash:end]

    text = ""
    c = boshlash + 1
    for m in page_movies:
        # m['code'] va m['name'] MongoDB document ichida bo'lishi kerak
        text += f"• {c}) {m['name']} ----------------------------- #--Kodi: {m['code']}\n\n"
        c += 1

    return text, pages



# =================== OBUNA TEKSHIRISH =========================
def check_sub(user_id):
    for channel in CHANNEL_ID: 
    
        try:
            member = bot.get_chat_member(channel, user_id)
            if member.status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

# =================== ADMIN PANEL =============================
def admin_panel(chat_id):
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("🎬 Kino yuklash", "📂 Film kodlari")
    btn.add("❌ Film o'chirish", "♻️ Statistika")
    btn.add("📢 Xabar yuborish", "🔙 Ortga")
    btn.add("🏷 Admin tayinlash", "🚫 Adminni olish")  # Yangi tugmalar
    bot.send_message(chat_id, "🔐 Admin Paneli", reply_markup=btn)
    
def user_panel(chat_id):
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📂 Film kodlari", "🔙")
    bot.send_message(chat_id, "🔐 Kino kodlarini olish", reply_markup=btn)
    
# ====================== SAVE USER ================================
def save_user(user_id):
    # Agar user bazada mavjud bo'lmasa qo'shadi
    if not users_collection.find_one({"user_id": user_id}):
        users_collection.insert_one({"user_id": user_id})

def send_movie_info(chat_id, kino_kodi):
    movie = movies.find_one({"code": kino_kodi})  # Kino kodi bo'yicha ma'lumot
    if movie:
        file_id = movie["file_id"]
        code = movie["code"]
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌", callback_data="delete_stats"))
        # Kino haqida ma'lumot yuboriladi
        bot.send_video(
            chat_id,
            file_id,
            caption=f"🎬 {movie['name']} \n"
                    f"💽 Formati: {movie['formati']}\n"
                    f"🎞 Janri: {movie['genre']}\n"
                    f"🆔 Kod: #{code}\n"
                    f"\n📹 Kanalimiz: {movie['url']}\n"
                    f"🤖 Botimiz: {movie['urlbot']}"
        )
    
    else:
        bot.send_message(chat_id, "❌ Bunday kod bo‘yicha kino topilmadi.")



#======== Foydalanuvchi kinoni O'chirib yuborsa======
@bot.callback_query_handler(func=lambda call: call.data == "delete_movie")
def delete_movie_message(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Video o'chirildi!")
    except Exception as e:
        print(f"Xatolik: {e}")
        bot.answer_callback_query(call.id, "❌ Video o'chirilmadi.")   
        

@bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
def page_switch(call):
    page = int(call.data.split("_")[1])

    text, pages = get_movie_page(page)

    markup = types.InlineKeyboardMarkup()
    btns = []

    if page > 1:
        btns.append(types.InlineKeyboardButton("⬅️ Back", callback_data=f"page_{page-1}"))
        
    if page < pages:
        btns.append(types.InlineKeyboardButton("➡️ Next", callback_data=f"page_{page+1}"))
        
    if page > 1 and page < pages:
        btns.append(types.InlineKeyboardButton("📌 Oxirgi", callback_data=f"page_{pages}"))
     
    # O'chirish tugmasi qo'shish
    btns.append(types.InlineKeyboardButton("❌", callback_data="delete_movies_list"))
       
    if btns:
        markup.row(*btns)

    try:
        bot.edit_message_text(
            "🎬 *Kino ro‘yxati:*\n\n" + text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except:
        pass

# O'chirish tugmasi uchun callback handler
@bot.callback_query_handler(func=lambda call: call.data == "delete_movies_list")
def delete_movies_list(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Ro'yxat o'chirildi!")
    except Exception as e:
        print(f"Xatolik:  {e}")
        bot.answer_callback_query(call.id, "❌ Ro'yxat o'chirilmadi.")
        

# ====================== START ================================
@bot.message_handler(commands=['start'])
def start(msg):
    user = msg.from_user.id
    
    # "start=kino_kodi" formatida yuborilgan parametrni olish
    kino_kodi = None  # Boshlang'ich qiymat
    if ' ' in msg.text:  # Agar `/start kino_kod` xabar formatida bo'lsa
        start_parts = msg.text.split(' ', 1)  # Bo'shliqdan ajratamiz
        kino_kodi = start_parts[1].strip()  # Kino kodini ajratamiz
        
    save_user(user)

    if not check_sub(user):
        btn = types.InlineKeyboardMarkup()
        btn.add(types.InlineKeyboardButton("📌 Kanalga obuna bo'lish", url="https://t.me/USAVYBE"))
        btn.add(types.InlineKeyboardButton("📌 Kanalga obuna bo'lish", url=kanal_link))
        btn.add(types.InlineKeyboardButton("♻️ Tekshirish", callback_data="check"))
        
        bot.send_message(
            msg.chat.id,
            "❗ Botdan foydalanish uchun kanalga obuna bo'ling!",
            reply_markup=btn
        )
        return
    
    if kino_kodi:
        send_movie_info(msg.chat.id, kino_kodi)  # Kino haqida ma'lumotni yuborish uchun funksiya chaqiriladi
        return


    bot.send_message(msg.chat.id, "🎬 Kino kodini kiriting:")

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    if check_sub(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✔ Obuna tasdiqlandi!\n\nKino kodini yuboring:")
    else:
        bot.answer_callback_query(call.id, "❗ Hali obuna bo‘lmagansiz!")
        


    


        

# ====================== ADMIN PANEL ===========================
@bot.message_handler(commands=['panel'])
def panel(msg):
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        admin_panel(msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz.")
        
@bot.message_handler(commands=['kodlar'])
def kodlar(msg):
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        bot.send_message(msg.chat.id, "❗ Bu komanda admin uchun emas.")
        return
    
    user_panel(msg.chat.id)
    


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



# ====================== ORTGA QAYTISH =========================
@bot.message_handler(func=lambda msg: msg.text == "🔙 Ortga")
def back(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    state.pop(str(msg.from_user.id), None)
    bot.send_message(msg.chat.id, "🎬 Kino kodini kiriting:", reply_markup=types.ReplyKeyboardRemove())
    
# --- USER uchun ORTGA tugmasi (ADMIN bo'lmaganlar uchun) ---
@bot.message_handler(func=lambda m: m.text == "🔙")
def back_user(msg):
    if (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    state.pop(str(msg.from_user.id), None)
    bot.send_message(
        msg.chat.id,
        "🎬 Kino kodini kiriting:",
        reply_markup=types.ReplyKeyboardRemove()
    )


    
# ====================== KINO YUKLASH ==========================
@bot.message_handler(func=lambda msg: msg.text == "🎬 Kino yuklash")
def upload_movie(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return

    bot.send_message(msg.chat.id, "🎬 Video yuboring (video fayl ko‘rinishida).")
    state[str(msg.from_user.id)] = ["waiting_for_video"]

# ======== KINO KODINI QABUL QILISH ========
@bot.message_handler(func=lambda m: str(m.from_user.id) in state 
                     and state[str(m.from_user.id)][0] == "waiting_for_video",
                     content_types=['video'])
def catch_video(msg):
    user = str(msg.from_user.id)
    file_id = msg.video.file_id
    state[user] = ["waiting_for_code", file_id]
    bot.send_message(msg.chat.id, "📌 Kino uchun kod kiriting:")
    
# ======== KINO NOMI ========
@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user.id)][0] == "waiting_for_code")
def movie_code(msg):
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = msg.text.strip()
    
    # === 1) KOD BORLIGINI TEKSHIRAMIZ ===
    if movies.find_one({"code": code}):
        bot.send_message(
            msg.chat.id,
            f"⚠️ *Bu kod allaqachon mavjud!* #-({code})\nBoshqa kod kiriting:",
            parse_mode="Markdown"
        )
        return   # state o'zgarmaydi → admin qayta kod kiritadi

   # === 2) KOD YANGI BO'LSA DAVOM ETADI ===

    state[user] = ["waiting_for_name", file_id, code]
    bot.send_message(msg.chat.id, "🎬 Kino nomini kiriting:")

# ======== KINO JANRI ========
@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user.id)][0] == "waiting_for_name")
def movie_name(msg):
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = msg.text.strip()

    state[user] = ["waiting_for_genre", file_id, code, name]
    bot.send_message(msg.chat.id, "📚 Kino janrini kiriting:")


@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user.id)][0] == "waiting_for_genre")
def movie_genre(msg):
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = state[user][3]
    genre = msg.text.strip()

    state[user] = ["waiting_for_url", file_id, code, name, genre]
    bot.send_message(msg.chat.id, "💽Formati:")


# ======== KINO URL / INFO ========
@bot.message_handler(func=lambda msg: str(msg.from_user.id) in state and state[str(msg.from_user.id)][0] == "waiting_for_url")
def movie_url(msg):
    user = str(msg.from_user.id)
    file_id = state[user][1]
    code = state[user][2]
    name = state[user][3]
    genre = state[user][4]
    formati= msg.text.strip()


    # MongoDB-da code kaliti bo'lib, qiymat dict shaklida saqlaymiz
    movies.update_one(
        {"code": code},  # filter
        {"$set": {
            "file_id": file_id,
            "name": name,       
            "formati": formati,    
            "genre": genre,      
            "url": "@DubHDkinolar",
            "urlbot": "@DubKinoBot"
        }},
        upsert=True     #agar code mavjud bo‘lmasa, yangi document yaratadi
    )
    
    
    bot.send_message(msg.chat.id, "✅ Kino muvaffaqiyatli qo‘shildi!")
    del state[user]



#============ADMIN XABARI===========
@bot.message_handler(func=lambda msg: msg.text == "📢 Xabar yuborish")
def ask_broadcast(msg):
    if not str(msg.from_user.id) == ADMIN_ID:
        bot.send_message(msg.chat.id, "📢 Sizga xabar yuborish uchun ruxsat berilmagan!!!")
        return
    bot.send_message(msg.chat.id, "📢 Yuboriladigan xabarni kiriting:")
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




# ====================== FILM O‘CHIRISH ========================
@bot.message_handler(func=lambda msg: msg.text == "❌ Film o'chirish")
def delete_movie(msg):
    if not (str(msg.from_user.id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    state[str(msg.from_user.id)] = ["waiting_for_delete"]
    bot.send_message(msg.chat.id, "❌ O‘chirmoqchi bo‘lgan kino kodini yuboring.")

# ====================== FILM RO‘YXATI =========================
@bot.message_handler(func=lambda msg: msg.text == "📂 Film kodlari")
def movie_list(msg):
    # if (str(msg.from_user.id) != ADMIN_ID or is_admin(msg.from_user.id)):   #Buni ochsak, ro'yxat faqat adminlarga ko'rinadi
    #     text = "🎬 *Kino topish uchun mos #Kodlarni shu kanaldan topasiz:*\n\n"
    #     text+="https://t.me/DubHDkinolar"
    #     bot.send_message(msg.chat.id, text, parse_mode="Markdown")
    #     return
    
    # Baza bo‘shligini tekshirish
    if movies.count_documents({}) == 0:
        bot.send_message(msg.chat.id, "📂 Bazada kino yo'q.")
        return
    
    # Kino ro‘yxati uchun sahifa
    
    text, pages = get_movie_page(page=1)
    markup = types.InlineKeyboardMarkup()
    if pages > 1:
        markup.add(types.InlineKeyboardButton("➡️ Keyingi", callback_data="page_2"))
        markup.add(types.InlineKeyboardButton("📌 Oxirgi", callback_data=f"page_{pages}"))
    # O'chirish tugmasi
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_movies_list")) 
    
    # Kino ro‘yxatini chiqarish
    text = "🎬 *Kino ro‘yxati:*\n\n"
    all_movies = list(movies.find({}, {"_id": 0}))
    c = 1
    texts=""
    for m in all_movies:
        text += f"• {c}) {m['name']} ----------------------------- #--Kodi: {m['code']}\n\n"
        
        if c == 10:
            texts=text[:]
        c += 1
    text=texts
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)


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
    # Super Admin uchun tayinlangan adminlar sonini ko‘rsatish
    if str(msg.from_user.id) == ADMIN_ID:  # Foydalanuvchi Super Admin bo'lsa
        stats_text += f"🏷 Tayinlangan adminlar soni: *{admin_count}*\n"
        if admins:
            stats_text += "📋 Adminlar ro'yxati:\n"
            for admin in admins:
                stats_text += f"  - 🆔 {admin['user_id']}, 👤 {admin['name']}\n"
                
    # Xabarni o'chirish tugmasi qo'shish
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌", callback_data="delete_stats"))
    
    bot.send_message(msg.chat.id, stats_text, parse_mode="Markdown", reply_markup=markup)

# Xabarni o'chirish callback handler
@bot.callback_query_handler(func=lambda call: call.data == "delete_stats")
def delete_stats_message(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.answer_callback_query(call.id, "✅ Xabar o'chirildi!")
    except Exception as e:
        print(f"Xatolik:  {e}")
        bot.answer_callback_query(call.id, "❌ Xabar o'chirilmadi.")
        

                

# ====================== UMUMIY HANDLER ========================
@bot.message_handler(func=lambda msg: True)
def universal_handler(msg):
    user = str(msg.from_user.id)
    text = msg.text.strip()

    # --- 1) Admin kino kodi kiritayapti ---
    if user in state and state[user][0] == "waiting_for_code":
        file_id = state[user][1]
        
        movies.update_one(
            {"code": text},      # filter: qaysi document-ni yangilash
            {"$set": {"file_id": file_id}},
            upsert=True           # agar document yo‘q bo‘lsa, yangi yaratadi
        )


        bot.send_message(msg.chat.id, f"✔ Kino saqlandi!\nKino kodi: {text}")
        del state[user]
        return


    # --- 2) Admin kino o‘chirayapti ---
    if user in state and state[user][0] == "waiting_for_delete":

        result = movies.delete_one({"code": text})
        
        if result.deleted_count > 0:
            bot.send_message(msg.chat.id, f"✔ Kino o‘chirildi. Kod: {text}")
        else:
            bot.send_message(msg.chat.id, "❌ Bunday kod mavjud emas.")
    
        del state[user]
        return


    # --- 3) Oddiy foydalanuvchi kino kodi so‘rayapti ---
    if not check_sub(int(user)):
        bot.send_message(msg.chat.id, "❗ Avval kanalga obuna bo‘ling.")
        return
    
    movie_code = msg.text.strip()
    send_movie_info(msg.chat.id, movie_code)
    

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
    
    
