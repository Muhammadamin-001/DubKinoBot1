# serial/serial_states.py
"""
🎯 SERIAL STATE MANAGEMENT
State checking va helpers
"""

from utils.db_config import state

# =================== STATE CHECKERS ===================

def is_serial_uploading(user_id):
    """Serial yuklanmoqda tekshirish"""
    user_id = str(user_id)
    return user_id in state and state[user_id][0]. startswith("serial_")

def is_waiting_for(user_id, state_name):
    """Muayyan state kutmoqda tekshirish"""
    user_id = str(user_id)
    return user_id in state and state[user_id][0] == state_name

def get_state_step(user_id):
    """State qadamini olish"""
    user_id = str(user_id)
    if user_id in state:
        return state[user_id][0]
    return None

def get_serial_state(user_id):
    """Butun state olish"""
    user_id = str(user_id)
    return state. get(user_id)

def set_serial_state(user_id, state_list):
    """State o'rnatish"""
    state[str(user_id)] = state_list

def clear_serial_state(user_id):
    """State tozalash"""
    user_id = str(user_id)
    if user_id in state: 
        del state[user_id]

def get_serial_code_from_state(user_id):
    """State ichidan serial kodi olish"""
    user_id = str(user_id)
    if user_id in state and len(state[user_id]) > 1:
        return state[user_id][1]
    return None

def get_season_number_from_state(user_id):
    """State ichidan fasl raqami olish"""
    user_id = str(user_id)
    if user_id in state and len(state[user_id]) > 2:
        return state[user_id][2]
    return None

def get_episode_number_from_state(user_id):
    """State ichidan qism raqami olish"""
    user_id = str(user_id)
    if user_id in state and len(state[user_id]) > 3:
        return state[user_id][3]
    return None

def get_videos_from_state(user_id):
    """State ichidan videolar ro'yxatini olish"""
    user_id = str(user_id)
    if user_id in state and len(state[user_id]) > 3:
        return state[user_id][3]
    return []