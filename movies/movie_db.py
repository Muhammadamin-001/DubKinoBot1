# movies/movie_db.py
from utils. db_config import movies

def create_movie(code, name, file_id, genre, formati):
    """Kino yaratish"""
    movies.update_one(
        {"code":  code},
        {"$set": {
            "file_id": file_id,
            "name": name,
            "genre":  genre,
            "formati":  formati,
            "url": "@DubHDkinolar",
            "urlbot": "@DubKinoBot"
        }},
        upsert=True
    )

def delete_movie(code):
    """Kino o'chirish"""
    movies.delete_one({"code": code})

def get_movie(code):
    """Kino olish"""
    return movies.find_one({"code": code})

# ... qolgan kino CRUD ... 