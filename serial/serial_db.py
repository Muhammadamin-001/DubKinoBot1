# serial/serial_db.py
"""
💾 SERIAL DATABASE
MongoDB CRUD operatsiyalari
"""

from utils.db_config import serials
import time

# =================== CREATE OPERATIONS ===================

def create_serial(code, name, image_file_id):
    """Serial yaratish"""
    try:
        serials.insert_one({
            "code": code,
            "name": name,
            "image":  image_file_id,
            "seasons": [],
            "created_date": time.time()
        })
        return True
    except Exception as e:
        print(f"❌ Serial yaratish xatosi: {e}")
        return False

def add_season(serial_code, season_number):
    """Fasl qo'shish"""
    try:
        serials.update_one(
            {"code": serial_code},
            {
                "$push": {
                    "seasons":  {
                        "season_number": season_number,
                        "episodes": [],
                        "full_files":  []
                    }
                }
            }
        )
        return True
    except Exception as e:
        print(f"❌ Fasl qo'shish xatosi: {e}")
        return False

def add_episode(serial_code, season_number, episode_number, file_id):
    """Qism qo'shish"""
    try:
        serials. update_one(
            {
                "code": serial_code,
                "seasons.season_number": season_number
            },
            {
                "$push": {
                    "seasons.$.episodes": {
                        "episode_number": episode_number,
                        "file_id": file_id
                    }
                }
            }
        )
        return True
    except Exception as e: 
        print(f"❌ Qism qo'shish xatosi: {e}")
        return False

def add_full_files(serial_code, season_number, file_ids):
    """To'liq fasl videolari qo'shish"""
    try:
        serials.update_one(
            {
                "code": serial_code,
                "seasons.season_number": season_number
            },
            {
                "$set": {
                    "seasons. $.full_files": file_ids
                }
            }
        )
        return True
    except Exception as e:
        print(f"❌ To'liq fasl saqlash xatosi: {e}")
        return False

# =================== READ OPERATIONS ===================

def get_serial(serial_code):
    """Serial olish"""
    try:
        return serials.find_one({"code": serial_code})
    except Exception as e:
        print(f"❌ Serial olish xatosi: {e}")
        return None

def get_all_serials():
    """Barcha seriallar"""
    try:
        return list(serials.find({}, {"_id": 0}))
    except Exception as e:
        print(f"❌ Seriallar olish xatosi: {e}")
        return []

def get_season(serial_code, season_number):
    """Faslni olish"""
    try:
        serial = serials.find_one({"code": serial_code})
        if serial:
            for season in serial.get("seasons", []):
                if season["season_number"] == season_number:
                    return season
        return None
    except Exception as e:
        print(f"❌ Fasl olish xatosi: {e}")
        return None

def get_episode(serial_code, season_number, episode_number):
    """Qismni olish"""
    try:
        season = get_season(serial_code, season_number)
        if season:
            for episode in season.get("episodes", []):
                if episode["episode_number"] == episode_number:
                    return episode
        return None
    except Exception as e:
        print(f"❌ Qism olish xatosi: {e}")
        return None

def check_serial_code_exists(serial_code):
    """Serial kodi bormi tekshirish"""
    return serials.find_one({"code": serial_code}) is not None

def check_episode_exists(serial_code, season_number, episode_number):
    """Qism bormi tekshirish"""
    episode = get_episode(serial_code, season_number, episode_number)
    return episode is not None

# =================== DELETE OPERATIONS ===================

def delete_serial(serial_code):
    """Butun serialni o'chirish"""
    try:
        result = serials.delete_one({"code": serial_code})
        return result.deleted_count > 0
    except Exception as e:
        print(f"❌ Serial o'chirish xatosi:  {e}")
        return False

def delete_season(serial_code, season_number):
    """Faslni o'chirish"""
    try:
        result = serials.update_one(
            {"code":  serial_code},
            {
                "$pull": {
                    "seasons":  {"season_number": season_number}
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Fasl o'chirish xatosi:  {e}")
        return False

def delete_episode(serial_code, season_number, episode_number):
    """Qismni o'chirish"""
    try:
        result = serials. update_one(
            {
                "code": serial_code,
                "seasons.season_number": season_number
            },
            {
                "$pull":  {
                    "seasons.$. episodes": {"episode_number": episode_number}
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Qism o'chirish xatosi: {e}")
        return False