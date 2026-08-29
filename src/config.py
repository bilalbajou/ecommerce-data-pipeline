import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

class Config:
    # API & Paths
    API_URL = os.getenv("API_URL", "https://dummyjson.com/products")
    DATA_DIR = os.getenv("DATA_DIR", "data")
    RAW_DATA_PATH = os.path.join(DATA_DIR, "raw_products.json")
    PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed_products.csv")

    # Database
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "ecommerce_db")

    @classmethod
    def get_db_url(cls, db_name=None):
        """Constructs the SQLAlchemy connection URL."""
        db = db_name or cls.DB_NAME
        return f"postgresql+psycopg2://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{db}"
