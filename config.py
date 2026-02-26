import os

class Config:
    # Kinukuha ang details mula sa iyong existing config
    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = '3306'  # Siguraduhing tugma sa XAMPP port mo
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = ''
    MYSQL_DB = 'cateringinventory'

    # Ito ang gagamitin ng Flask-SQLAlchemy para kumonekta
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Importante para sa form security at sessions
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'janet_catering_secret_key_123'
