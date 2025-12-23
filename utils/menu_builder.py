# utils/menu_builder.py
"""
🎨 MENU BUILDER
Tugmalar va menyu generatsiyasi
"""

from telebot import types

def create_inline_buttons(buttons_data):
    """
    Inline tugmalar yaratish
    buttons_data = [
        {"text": "Kino", "callback":  "upload_kino"},
        {"text": "Serial", "callback": "upload_serial"}
    ]
    """
    markup = types.InlineKeyboardMarkup()
    for btn_data in buttons_data:
        markup.add(types.InlineKeyboardButton(
            btn_data["text"],
            callback_data=btn_data["callback"]
        ))
    return markup

def create_back_button(callback_data="back"):
    """Ortga tugmasi"""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 Ortga", callback_data=callback_data))
    return markup