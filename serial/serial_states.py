# serial/serial_states.py
from utils. db_config import state

def is_serial_uploading(user_id):
    """Serialni yuklanish jarayoni davommi? """
    return str(user_id) in state and state[str(user_id)][0]. startswith("serial_")

def clear_serial_state(user_id):
    """Serial stateini tozalash"""
    user_id = str(user_id)
    if user_id in state:
        del state[user_id]

def get_serial_state(user_id):
    """Serial stateni olish"""
    return state.get(str(user_id))

# ... qolgan state helperlar ...