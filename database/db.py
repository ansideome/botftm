import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASS'),
    'db': os.getenv('DB_NAME'),
    'cursorclass': pymysql.cursors.DictCursor
}

def get_connection_database():
    return pymysql.connect(**CONFIG)