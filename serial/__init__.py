"""
🎞️ SERIAL MODULI
Seriallarni yuklash, fasllarni boshqarish, qismlarni o'chirish va boshqalar
"""

from .serial_handler import (
    upload_serial_menu,
    add_new_serial_start,
    save_serial_code,
    save_serial_name,
    save_serial_image,
    select_serial,
    add_season_start,
    save_season_number,
    season_type_full,
    upload_season_full_video,
    season_type_episodes,
    save_episode_number,
    save_episode_video,
    delete_serial_menu,
    delete_serial_start,
    delete_serial_selected,
    delete_serial_all,
    delete_serial_seasons,
    delete_season_or_episode,
    delete_episode,
    delete_season_all
)

from .serial_db import (
    create_serial,
    add_season,
    add_episode,
    delete_serial as db_delete_serial,
    delete_season as db_delete_season,
    delete_episode as db_delete_episode,
    get_serial,
    get_all_serials,
    search_serial_by_code_or_name
)

from .serial_states import (
    is_serial_uploading,
    clear_serial_state,
    get_serial_state,
    set_serial_state
)

from .serial_user import (
    show_serial_for_user,
    show_episodes_for_user,
    send_episode_to_user,
    search_serial_results
)

__all__ = [
    # Handlers
    'upload_serial_menu',
    'add_new_serial_start',
    'save_serial_code',
    'save_serial_name',
    'save_serial_image',
    'select_serial',
    'add_season_start',
    'save_season_number',
    'season_type_full',
    'upload_season_full_video',
    'season_type_episodes',
    'save_episode_number',
    'save_episode_video',
    'delete_serial_menu',
    'delete_serial_start',
    'delete_serial_selected',
    'delete_serial_all',
    'delete_serial_seasons',
    'delete_season_or_episode',
    'delete_episode',
    'delete_season_all',
    
    # Database
    'create_serial',
    'add_season',
    'add_episode',
    'db_delete_serial',
    'db_delete_season',
    'db_delete_episode',
    'get_serial',
    'get_all_serials',
    'search_serial_by_code_or_name',
    
    # States
    'is_serial_uploading',
    'clear_serial_state',
    'get_serial_state',
    'set_serial_state',
    
    # User
    'show_serial_for_user',
    'show_episodes_for_user',
    'send_episode_to_user',
    'search_serial_results',
]