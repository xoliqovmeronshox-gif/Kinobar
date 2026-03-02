import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
CHANNEL_ID = os.getenv('CHANNEL_ID', '')

# Bot sozlamalari
DATABASE_PATH = 'bot_database.db'
DATABASE_URL = os.getenv('DATABASE_URL')  # PostgreSQL uchun
MOVIES_PER_PAGE = 10
