import telebot
from telebot import types
import json
import time
import requests
from flask import Flask, request
import os

TOKEN = '8355160126:AAEl-Ul_QLI1I7AwkHPfE1_r4a2MUC0MISU'
ADMIN_ID = "8213048876" #A
CHANNEL_ID = [-1001574709061,  -1003359940811]#Usavyb

bot = telebot.TeleBot(TOKEN)

kanal_link="https://t.me/DubHDkinolar"

app = Flask(__name__)

# ====================== DB YUKLASH ============================
try:
    with open("db.json", "r", encoding="utf-8") as f:
        db = json.load(f)
except:
    db = {}
    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4)

# =================== STATE (HOLAT) ============================
state = {}  
# state[user_id] = ["waiting_for_video"]
# state[user_id] = ["waiting_for_code", file_id]
# state[user_id] = ["waiting_for_delete"]

album_buffer = {}
album_sending = {}
# album_sending[user_id] = time.time()

movie_pages = {}


def get_movie_page(page=1, per_page=10):
    movies = list(db.items())  # db — sening bazang
    total = len(movies)
    pages = (total - 1) // per_page + 1

    start = (page - 1) * per_page
    end = start + per_page
    page_movies = movies[start:end]

    text = ""
    c = start + 1
    for code, info in page_movies:
        text += f"{c}) {info['name']}------------#-{code}\n"
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
    btn.add("❌ Film o'chirish", "🔙 Ortga")
    btn.add("📢 Xabar yuborish")
    bot.send_message(chat_id, "🔐 Admin Paneli", reply_markup=btn)
    
def user_panel(chat_id):
    btn = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn.add("📂 Film kodlari", "🔙")
    bot.send_message(chat_id, "🔐 Kino kodlarini olish", reply_markup=btn)
    
# ====================== SAVE USER ================================
def save_user(user_id):
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []

    if user_id not in users:
        users.append(user_id)
        with open("users.json", "w") as f:
            json.dump(users, f, indent=4)



# ====================== START ================================
@bot.message_handler(commands=['start'])
def start(msg):
    user = msg.from_user.id
    
    save_user(msg.from_user.id)


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


    bot.send_message(msg.chat.id, "🎬 Kino kodini kiriting:")

@bot.callback_query_handler(func=lambda call: call.data == "check")
def check(call):
    if check_sub(call.from_user.id):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✔ Obuna tasdiqlandi!\n\nKino kodini yuboring:")
    else:
        bot.answer_callback_query(call.id, "❗ Hali obuna bo‘lmagansiz!")
        

@bot.callback_query_handler(func=lambda c: c.data.startswith("page_"))
def page_switch(call):
    page = int(call.data.split("_")[1])

    text, pages = get_movie_page(page)

    markup = types.InlineKeyboardMarkup()
    btns = []

    if page > 1:
        btns.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page_{page-1}"))
    if page < pages:
        btns.append(types.InlineKeyboardButton("➡️ Keyingi", callback_data=f"page_{page+1}"))

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


# ====================== ADMIN PANEL ===========================
@bot.message_handler(commands=['panel'])
def panel(msg):
    if str(msg.from_user.id) == ADMIN_ID:
        admin_panel(msg.chat.id)
    else:
        bot.send_message(msg.chat.id, "❌ Siz admin emassiz.")
        
@bot.message_handler(commands=['kodlar'])
def kodlar(msg):
    if str(msg.from_user.id) == ADMIN_ID:
        bot.send_message(msg.chat.id, "❗ Bu komanda admin uchun emas.")
        return
    
    user_panel(msg.chat.id)
    

# ====================== ORTGA QAYTISH =========================
@bot.message_handler(func=lambda msg: msg.text == "🔙 Ortga")
def back(msg):
    if str(msg.from_user.id) != ADMIN_ID:
        return
    
    state.pop(str(msg.from_user.id), None)
    bot.send_message(msg.chat.id, "🎬 Kino kodini kiriting:", reply_markup=types.ReplyKeyboardRemove())
    
# --- USER uchun ORTGA tugmasi (ADMIN bo'lmaganlar uchun) ---
@bot.message_handler(func=lambda m: m.text == "🔙")
def back_user(msg):
    if str(msg.from_user.id) == ADMIN_ID:
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
    if str(msg.from_user.id) != ADMIN_ID:
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
    if code in db:
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

    # JSON ga saqlash ko‘rinishi:
    db[code] = {
        "file_id": file_id,
        "name": name,
        "formati": formati,
        "genre": genre,
        "url": "@DubHDkinolar",
        "urlbot":"@DubKinoBot"
    }

    with open("db.json", "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

    bot.send_message(msg.chat.id, "✅ Kino muvaffaqiyatli qo‘shildi!")

    del state[user]


#============ADMIN XABARI===========
@bot.message_handler(func=lambda msg: msg.text == "📢 Xabar yuborish")
def ask_broadcast(msg):
    if str(msg.from_user.id) != ADMIN_ID:
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
        try:
            with open("users.json", "r") as f:
                users = json.load(f)
        except:
            users = []
    
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
    
        for uid in users:
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
    
    try:
        with open("users.json", "r") as f:
            users = json.load(f)
    except:
        users = []

    bot.send_message(msg.chat.id, "⏳ Xabar yuborilmoqda, kuting...")

    sent = 0
    for uid in users:
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
    if str(msg.from_user.id) != ADMIN_ID:
        return
    state[str(msg.from_user.id)] = ["waiting_for_delete"]
    bot.send_message(msg.chat.id, "❌ O‘chirmoqchi bo‘lgan kino kodini yuboring.")

# ====================== FILM RO‘YXATI =========================
@bot.message_handler(func=lambda msg: msg.text == "📂 Film kodlari")
def movie_list(msg):
    if str(msg.from_user.id) != ADMIN_ID:
        text = "🎬 *Kino topish uchun mos #Kodlarni shu kanaldan topasiz:*\n\n"
        text+="https://t.me/DubHDkinolar"
        bot.send_message(msg.chat.id, text, parse_mode="Markdown")
        return
    
    if not db:
        bot.send_message(msg.chat.id, "📂 Bazada kino yo'q.")
        return
    
    text, pages = get_movie_page(page=1)
    markup = types.InlineKeyboardMarkup()
    if pages > 1:
        markup.add(types.InlineKeyboardButton("➡️ Keyingi", callback_data="page_2"))

    
    text = "🎬 *Kino ro‘yxati:*\n\n"
    c=1
    for code, info in db.items():
        text += f"• {c}) {info['name']}-----------------------------#-{code}\n"
        c+=1
    bot.send_message(msg.chat.id, text, parse_mode="Markdown", reply_markup=markup)




# ====================== UMUMIY HANDLER ========================
@bot.message_handler(func=lambda msg: True)
def universal_handler(msg):
    user = str(msg.from_user.id)
    text = msg.text.strip()

    # --- 1) Admin kino kodi kiritayapti ---
    if user in state and state[user][0] == "waiting_for_code":
        file_id = state[user][1]
        db[text] = file_id

        with open("db.json", "w", encoding="utf-8") as f:
            json.dump(db, f, indent=4)

        bot.send_message(msg.chat.id, f"✔ Kino saqlandi!\nKino kodi: {text}")
        del state[user]
        return

    # --- 2) Admin kino o‘chirayapti ---
    if user in state and state[user][0] == "waiting_for_delete":
        if text in db:
            del db[text]
            with open("db.json", "w", encoding="utf-8") as f:
                json.dump(db, f, indent=4)
            bot.send_message(msg.chat.id, "✔ Kino o‘chirildi.")
        else:
            bot.send_message(msg.chat.id, "❌ Bunday kod mavjud emas.")
        del state[user]
        return

    # --- 3) Oddiy foydalanuvchi kino kodi so‘rayapti ---
    if not check_sub(user):
        bot.send_message(msg.chat.id, "❗ Avval kanalga obuna bo‘ling.")
        return

    if text in db:
        movie = db[text]       # DICT
        file_id = movie["file_id"]
        #code=text 
        keys = [k for k, v in db.items() if v == movie] # shu koddan foydalanib,
        key = keys[0] if keys else None                 # kalitni chiqardim.
        
        bot.send_video(
            msg.chat.id,
            file_id,
            caption=f"🎬 {movie['name']} \n\t\t-------------------------\n"
                    f"💽Formati: {movie['formati']}\n"
                    f"🎞Janri: {movie['genre']}\n"
                    f"🆔Kod: #{key}\n" #ishladi
                    f"\n📹Kanalimiz: {movie['url']}\n"
                    f"🤖Bizning bot: {movie['urlbot']}"
        )
    else:
        bot.send_message(msg.chat.id, "❌ Bunday kod bo‘yicha kino topilmadi.")




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

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url="https://YOUR-RENDER-APP-NAME.onrender.com/" + TOKEN)
    app.run(host="0.0.0.0", port=5000)
# ==============================================================#
    
    
