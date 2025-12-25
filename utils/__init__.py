# utils/__init__.py
"""
🛠️ UMUMIY YORDAMCHI MODULLAR
Admin panellar, menu tayyorlash, database konfiguratsiya va misc funksiyalar
"""
from .db_config import (
    bot,
    db,
    client,
    users_collection,
    movies,
    serials,
    admins_collection,
    channels_collection,
    state,
    user_clicks,
    album_buffer,
    album_sending,
    search_cache,
)

from .admin_utils import (
    admin_panel,
    super_admin_panel,
    user_panel,
    check_sub,
    upload_mdb,
    is_admin,
    save_user
)

from .menu_builder import (
    create_inline_buttons,
    create_back_button
)

__all__ = [
    # Database
    'bot',
    'db',
    'client',
    'users_collection',
    'movies',
    'serials',
    'admins_collection',
    'channels_collection',
    'state',
    'user_clicks',
    'album_buffer',
    'album_sending',
    'search_cache',
    
    # Admin Utils
    'admin_panel',
    'super_admin_panel',
    'user_panel',
    'check_sub',
    'upload_mdb',
    'is_admin',
    'save_user',
    
    # Menu
    'create_inline_buttons',
    'create_back_button',
]