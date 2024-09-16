from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
from bot.util.db import get_db_connection, return_db_connection
import config

router = Router()

async def get_my_offers(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):

    blogger_chat_id = callback_query.from_user.id
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Извлекаем все офферы из базы данных
            cursor.execute("""
                            SELECT *
                            FROM public.offers
                            WHERE blogger_id = %s
                        """, (str(blogger_chat_id)))
            offers = cursor.fetchall()
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        offers = []
    finally:
        return_db_connection(connection)
