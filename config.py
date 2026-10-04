import os
import sys

from dotenv import load_dotenv

from app.get_loggers import get_logger

logger = get_logger(__name__)

if not load_dotenv():
    logger.error("Файл .env не создан или не был найден!")
    sys.exit()

TOKEN = os.getenv("TOKEN")
AI_TOKEN = os.getenv("AI_TOKEN")
ADMIN_IDS = {int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()}
