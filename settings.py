import os

from dotenv import load_dotenv

load_dotenv()


DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB = os.getenv("DB")
NEWSAPI_TABLE = os.getenv("NEWSAPI_TABLE")
