

# serial/serial_db.py
from utils.db_config import serials
import time

def create_serial(code, name, image_file_id):
    """Yangi serial yaratish"""
    serials.insert_one({
        "code": code,
        "name": name,
        "image":  image_file_id,
        "seasons": [],
        "created_date": time.time()
    })

def add_season(serial_code, season_number, episodes=None, full_files=None):
    """Fasl qo'shish"""
    season_data = {
        "season_number": season_number,
        "episodes": episodes or [],
        "full_files": full_files or []
    }
    serials. update_one(
        {"code": serial_code},
        {"$push": {"seasons": season_data}}
    )

def add_episode(serial_code, season_number, episode_number, file_id):
    """Qism qo'shish"""
    serials.update_one(
        {"code": serial_code, "seasons.season_number": season_number},
        {"$push": {"seasons. $.episodes": {
            "episode_number": episode_number,
            "file_id": file_id
        }}}
    )

def delete_serial(serial_code):
    """Serial o'chirish"""
    serials.delete_one({"code": serial_code})

def get_serial(serial_code):
    """Serial olish"""
    return serials. find_one({"code": serial_code})

def get_all_serials():
    """Barcha seriallar"""
    return list(serials.find({}, {"_id": 0}))

# ... qolgan CRUD operatsiyalari ... 