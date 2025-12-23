# serial/serial_states.py
"""
🎯 SERIAL STATES
Serial state management
"""

from utils.db_config import state

def is_serial_uploading(user_id):
    """Serial yuklanayotganmi tekshirish"""
    return str(user_id) in state and state[str(user_id)][0]. startswith("serial_")

def clear_serial_state(user_id):
    """State tozalash"""
    if str(user_id) in state:
        del state[str(user_id)]