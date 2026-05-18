import os

from dotenv import load_dotenv

if not load_dotenv():
    exit("Файл .env не создан или не был найден!")

TOKEN = os.getenv("TOKEN")
AI_TOKEN = os.getenv("AI_TOKEN")
