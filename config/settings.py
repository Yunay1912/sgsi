import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:yunaykelastuadev@localhost:5432/asamblea_db")

APP_ENV = os.getenv("APP_ENV", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
