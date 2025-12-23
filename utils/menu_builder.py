# utils/menu_builder.py
from telebot import types

def create_inline_buttons(buttons_data):
    """
    buttons_data = [
        {"text": "Kino", "callback":  "upload_kino"},
        {"text": "Serial", "callback": "upload_serial"}
    ]
    """
    markup = types.InlineKeyboardMarkup()
    for btn_data in buttons_data:
        markup.add(types.InlineKeyboardButton(btn_data["text"], callback_data=btn_data["callback"]))
    return markup

def create_back_button(callback_data="back"):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=callback_data))
    return markup