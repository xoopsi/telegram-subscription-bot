# user should define BOT_TOKEN, ADMIN_IDS, etc.


import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Telegram
BOT_TOKEN = os.getenv("BOT_TOKEN", "XXXXXXXXXXXXXXXXXXXXXXX")

# Admins
ADMIN_IDS = [
    int(os.getenv("ADMIN_ID_1", "XXXXX")),
    int(os.getenv("ADMIN_ID_2", "XXXXX")),
    int(os.getenv("ADMIN_ID_3", "XXXXX"))
]

# Supergroup ID where bot is admin
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "-100XXXXXXXXX"))

# Payment card info (displayed to users)
BANK_NAME = os.getenv("BANK_NAME", "XXXXXXXX")
CARD_NUMBER = os.getenv("CARD_NUMBER", "XXXX-XXXX-XXXX-XXXX")
ACCOUNT_NAME = os.getenv("ACCOUNT_NAME", "XXXXXXXX")

# Uploads and logs
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR / 'data.db'}"

# Pricing & defaults
BASE_PRICE_6M = int(os.getenv("BASE_PRICE_6M", "2500000"))  # تومان
DEFAULT_DISCOUNT = int(os.getenv("DEFAULT_DISCOUNT", "10"))  # درصد

# Access code settings
ACCESS_CODE_EXPIRY_HOURS = int(os.getenv("ACCESS_CODE_EXPIRY_HOURS", "24"))
ONE_TIME_LINK_MAX_USES = int(os.getenv("ONE_TIME_LINK_MAX_USES", "1"))

# Scheduler
SCHEDULER_INTERVAL = int(os.getenv("SCHEDULER_INTERVAL", str(60 * 60 * 6)))

# Log retention (days)
LOG_RETENTION_DAYS = int(os.getenv("LOG_RETENTION_DAYS", "4"))


PROXY_URL = os.getenv("PROXY_URL", "")

MANAGERS_SHARE = {
    "Admin1" : 0.8,
    "Admin2" : 0.2
}
