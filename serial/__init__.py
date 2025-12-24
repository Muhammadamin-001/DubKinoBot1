# serial/__init__.py
"""
🎞️ SERIAL MODULI
Seriallarni yuklash, o'chirish va boshqarish uchun barcha funksiyalar
"""

# ✅ FAQAT MAVJUD FUNKSIYALARNI IMPORT QIL
from serial.serial_handler import (
    upload_serial_menu,
    delete_serial_menu,
)

from .serial_db import (
    create_serial,
    add_season,
    add_episode,
    add_full_files,
    delete_serial,
    delete_season,
    delete_episode,
    get_serial,
    get_all_serials,
    get_season,
    get_episode,
    check_episode_exists,
    check_serial_code_exists,
)

from .serial_states import (
    is_waiting_for,
    set_serial_state,
    clear_serial_state,
    get_serial_state,
)

from .serial_user import (
    show_serial_for_user,
    show_episodes_for_user,
    send_episode_to_user,
)

__all__ = [
    # serial_handler. py - FAQAT MAVJUD
    'upload_serial_menu',
    'delete_serial_menu',
    
    # serial_db.py
    'create_serial',
    'add_season',
    'add_episode',
    'add_full_files',
    'delete_serial',
    'delete_season',
    'delete_episode',
    'get_serial',
    'get_all_serials',
    'get_season',
    'get_episode',
    'check_episode_exists',
    'check_serial_code_exists',
    
    # serial_states.py
    'is_waiting_for',
    'set_serial_state',
    'clear_serial_state',
    'get_serial_state',
    
    # serial_user.py
    'show_serial_for_user',
    'show_episodes_for_user',
    'send_episode_to_user',
]