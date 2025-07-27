# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Get the directory where config.py is located
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, "hotel.db")

print(f"🔹 Base directory: {BASE_DIR}")
print(f"🔹 Database path: {DATABASE_PATH}")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-me"
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True