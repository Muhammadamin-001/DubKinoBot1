# serial/__init__.py
"""
🎞️ SERIAL MODULI
Seriallarni yuklash, o'chirish va boshqarish uchun barcha funksiyalar
"""

# ✅ ANIQ IMPORT (Star o'rniga)
# from .serial_handler import (
#     # upload_serial_menu,
#     # show_serials_or_add,
#     # add_new_serial_start,
#     # save_serial_code,
#     # save_serial_name,
#     # save_serial_image,
#     # select_serial,
#     # add_season_start,
#     # save_season_number,
#     # season_type_full,
#     # season_type_episodes,
#     # upload_season_full_video,
#     # save_episode_number,
#     # save_episode_video,
#     # delete_serial_menu,
#     # delete_serial_selected,
#     # delete_serial_all,
#     # delete_serial_seasons,
#     # delete_season_or_episode,
#     # # ❌ 'delete_episode' O'CHIRILDI - serial_db.py da bor
#     # delete_season_all,
#     #serial_back_menu,
# )

from .serial_db import (
    create_serial,
    add_season,
    add_episode,
    add_full_files,
    delete_serial,
    delete_season,
    delete_episode,  # ✅ SHUDAN IMPORT QILINADI
    get_serial,
    get_all_serials,
    get_season,
    get_episode,
    check_episode_exists,
    check_serial_code_exists,
)

from .serial_states import (
    is_serial_uploading,
    clear_serial_state,
    get_serial_state,
    set_serial_state,
    get_state_step,
    is_waiting_for,
)

from .serial_user import (
    show_serial_for_user,
    show_episodes_for_user,
    send_episode_to_user,
)

__all__ = [
    # serial_handler.py
    #'upload_serial_menu',
    # 'show_serials_or_add',
    # 'add_new_serial_start',
    # 'save_serial_code',
    # 'save_serial_name',
    # 'save_serial_image',
    # 'select_serial',
    # 'add_season_start',
    # 'save_season_number',
    # 'season_type_full',
    # 'season_type_episodes',
    # 'upload_season_full_video',
    # 'save_episode_number',
    # 'save_episode_video',
    # 'delete_serial_menu',
    # 'delete_serial_selected',
    # 'delete_serial_all',
    # 'delete_serial_seasons',
    # 'delete_season_or_episode',
    # 'delete_season_all',
    #'serial_back_menu',
    
    #serial_db.py
    'create_serial',
    'add_season',
    'add_episode',
    'add_full_files',
    'delete_serial',
    'delete_season',
    'delete_episode',  # ✅ SHUDAN
    'get_serial',
    'get_all_serials',
    'get_season',
    'get_episode',
    'check_episode_exists',
    'check_serial_code_exists',
    
    # serial_states.py
    'is_serial_uploading',
    'clear_serial_state',
    'get_serial_state',
    'set_serial_state',
    'get_state_step',
    'is_waiting_for',
    
    # serial_user.py
    'show_serial_for_user',
    'show_episodes_for_user',
    'send_episode_to_user',
]