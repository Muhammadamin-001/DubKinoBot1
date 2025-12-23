# serial/serial_db. py
"""
💾 SERIAL DATABASE
Serial MongoDB operatsiyalari
"""

from utils. db_config import serials
import time

def create_serial(code, name, image_file_id):
    """Serial yaratish"""
    serials.insert_one({
        "code": code,
        "name": name,
        "image":  image_file_id,
        "seasons": [],
        "created_date": time.time()
    })

def add_season(serial_code, season_number):
    """Fasl qo'shish"""
    serials.update_one(
        {"code": serial_code},
        {"$push": {"seasons": {
            "season_number": season_number,
            "episodes":  [],
            "full_files": []
        }}}
    )