# config/__init__.py
"""
⚙️ KONFIGURATSIYA PACKAGE
Environment variables va global sozlamalar
"""

from .settings import (
    TOKEN,
    ADMIN_ID,
    WEBHOOK_URL,
    MONGO_URI
)

__all__ = [
    'TOKEN',
    'ADMIN_ID',
    'WEBHOOK_URL',
    'MONGO_URI',
]