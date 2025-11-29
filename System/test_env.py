import os
from pathlib import Path
from dotenv import load_dotenv

# Mimic settings.py
BASE_DIR = Path(__file__).resolve().parent
env_path = os.path.join(BASE_DIR.parent, '.env')

print(f"BASE_DIR: {BASE_DIR}")
print(f".env path: {env_path}")
print(f".env exists: {os.path.exists(env_path)}")

# Load .env
load_dotenv(env_path)

# Check environment variables
print(f"\nDB_ENGINE from os.getenv: {os.getenv('DB_ENGINE')}")
print(f"DB_NAME from os.getenv: {os.getenv('DB_NAME')}")
print(f"DB_USER from os.getenv: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD from os.getenv: {os.getenv('DB_PASSWORD')}")
print(f"DB_HOST from os.getenv: {os.getenv('DB_HOST')}")
print(f"DB_PORT from os.getenv: {os.getenv('DB_PORT')}")
