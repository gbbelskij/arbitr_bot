import os
import psycopg2
from psycopg2 import pool
import logging
import config

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Получение переменных окружения для подключения к базе данных
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASSWORD = config.DB_PASSWORD

# Создание пула подключений
try:
    connection_pool = psycopg2.pool.SimpleConnectionPool(
        1,  # Минимальное количество подключений в пуле
        10,  # Максимальное количество подключений в пуле
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    if connection_pool:
        logging.info("Пул подключений к базе данных успешно создан.")
except Exception as e:
    logging.error("Ошибка при создании пула подключений: %s", e)
    raise

# Функция для получения подключения из пула
def get_db_connection():
    try:
        connection = connection_pool.getconn()
        logging.info("Подключение к базе данных установлено.")
        return connection
    except Exception as e:
        logging.error("Ошибка при получении подключения: %s", e)
        raise

# Функция для возврата подключения в пул
def return_db_connection(connection):
    try:
        if connection:
            connection_pool.putconn(connection)
            logging.info("Подключение возвращено в пул.")
    except Exception as e:
        logging.error("Ошибка при возврате подключения: %s", e)
        raise
