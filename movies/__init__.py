# movies/__init__.py
"""
🎬 KINO MODULI
Kinolarni yuklash, o'chirish va boshqarish uchun barcha funksiyalar
"""

# from movies.movie_handler import send_movie_info, upload_movie, catch_video, movie_code, movie_name, movie_genre, movie_url
# from movies.movie_db import get_movie, get_all_movies

# __all__ = [
#     # movie_handler. py dan
#     'upload_movie',
#     'catch_video',
#     'movie_code',
#     'movie_name',
#     'movie_genre',
#     'movie_url',
#     'delete_movie',
#     'movie_list',
#     'send_movie_info',
    
#     # movie_db.py dan
#     'create_movie',
#     'delete_movie_db',
#     'get_movie',
#     'get_all_movies',
# ]

# movies/__init__.py
"""
🎬 KINO MODULI
Kinolarni yuklash, o'chirish va boshqarish
"""

# ✅ ANIQ IMPORT (Star o'rniga)
from .movie_handler import (
    upload_movie,
    catch_video,
    movie_code,
    movie_name,
    movie_genre,
    movie_url,
    delete_movie_warning,
    delete_movie_confirm,
    send_movie_info,
)

from .movie_db import (
    create_movie,
    delete_movie_db,
    get_movie,
    get_all_movies,
    check_movie_code_exists,
)

__all__ = [
    # movie_handler.py
    'upload_movie',
    'catch_video',
    'movie_code',
    'movie_name',
    'movie_genre',
    'movie_url',
    'delete_movie_warning',
    'delete_movie_confirm',
    'send_movie_info',
    
    # movie_db.py
    'create_movie',
    'delete_movie_db',
    'get_movie',
    'get_all_movies',
    'check_movie_code_exists',
]

