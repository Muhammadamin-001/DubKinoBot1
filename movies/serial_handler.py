# serial/serial_handler.py
from telebot import types
from utils.db_config import bot, serials, state
from utils.menu_builder import create_inline_buttons

@bot.message_handler(func=lambda msg: msg.text == "🎞 Serial yuklash")
def upload_serial_menu(msg):
    """Serial yuklash menyusi"""
    if not (str(msg.from_user. id) == ADMIN_ID or is_admin(msg.from_user.id)):
        return
    
    buttons = [
        {"text": "➕ Yangi Serial", "callback": "serial_add_new"},
        {"text": "📝 Mavjud serialga fasl qo'shish", "callback": "serial_select_for_season"},
        {"text": "🔙 Ortga", "callback": "serial_back"}
    ]
    markup = create_inline_buttons(buttons)
    bot.send_message(msg.chat.id, "🎞 Serial yuklash:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "serial_add_new")
def add_new_serial(call):
    """Yangi serial yaratish"""
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "🆔 Serial kodini kiriting:")
    state[str(call.from_user.id)] = ["serial_waiting_code"]

# ... qolgan serial handler kodi ...