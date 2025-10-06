import os
from dotenv import load_dotenv

load_dotenv()

# DB_URL = os.getenv("DB_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
ORS_API_KEY = os.getenv("ORS_API_KEY")
# DB_URL = "postgresql://postgres:Hana%402407@10.10.1.61:5432/AI TP"
from urllib.parse import quote_plus

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))  # Encodes @
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
