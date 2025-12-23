
# config/settings.py
import os

TOKEN = os.getenv("TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
MONGO_URI = os.getenv("MONGO_URI")

# Tekshirish
for varname in ["TOKEN", "ADMIN_ID", "WEBHOOK_URL", "MONGO_URI"]: 
    if globals()[varname] is None:
        print(f"ERROR: {varname} is not set!")
