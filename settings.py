import os
from dotenv import load_dotenv

load_dotenv()

os.environ['token'] = '6520753056:AAHudF5McGzw-_LjUriotWTaYvPOjpD77iM'
os.environ['db_user'] = 'wolfychan'
os.environ['db_name'] = 'megahelp'

BOT_TOKEN = os.environ.get('token')
DB_NAME = os.environ.get('db_name')
DB_USER = os.environ.get('db_user')
#DB_PASS = os.environ.get('DB_PASS')

DB_CONNECTION_STRING = f'postgresql+asyncpg://{DB_USER}@127.0.0.1:5432/{DB_NAME}'
