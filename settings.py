import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BANNED_DIR = os.path.join(BASE_DIR, "BANNED_FILES")


load_dotenv(os.path.join(BANNED_DIR, ".env"))
load_dotenv(os.path.join(BASE_DIR, ".env"))

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
REDIS_DB = int(os.environ.get("NUMBER_BD", os.environ.get("REDIS_DB", "0")))


DATA_FILE = os.environ.get("DATA_FILE") or os.path.join(BANNED_DIR, "url_storage.json")

PUBLIC_BASE_URL = (os.environ.get("PUBLIC_BASE_URL") or "").rstrip("/")
REDIRECT_DELAY = max(0, int(os.environ.get("REDIRECT_DELAY", "5")))
BACKUP_EVERY = int(os.environ.get("BACKUP_EVERY", "60"))
