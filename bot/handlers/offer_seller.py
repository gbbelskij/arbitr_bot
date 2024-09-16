from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
from bot.util.db import get_db_connection, return_db_connection
import uuid

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Создание роутера для этого контроллера
router = Router()

# Создаем CallbackData для обработки данных кнопок
class OfferCallback(CallbackData, prefix="offer"):
    action: str

class OfferStates(StatesGroup):
    creating_offer_name = State()  # Состояние для ввода названия оффера
    creating_offer_details = State()  # Состояние для ввода деталей оффера

class BackCallback1(CallbackData, prefix="back1"):
    action: str

async def start_create_offer(message: Message, state: FSMContext):
    logging.info("Функция 'start_create_offer' вызвана.")  # Логирование
    await message.answer("Введите название оффера:")
    await state.set_state(OfferStates.creating_offer_name)  # Устанавливаем состояние ввода названия оффера

@router.message(StateFilter(OfferStates.creating_offer_name))
async def process_offer_name(message: Message, state: FSMContext):
    # Сохраняем введенное пользователем название оффера
    offer_name = message.text
    await state.update_data(offer_name=offer_name)

    await message.answer(
        """Опишите инструкцию (ТЗ) для выкупа вашего товара.

        Пример ТЗ.

        1. Введите в строку поиска Валдбериз запрос "Футболка".

        2. Сделайте фильтр по бренду "Арко".

        3. Нужно/ не нужно оставлять отзыв на WB.

        Опишите условия оффера:

        Каждые 10000 просмотров с артикулом, обязуюсь выплачивать 1000 рублей хозяину видео.

        Прописанные условия в договоре:

        Ссылка на договор."""
    )
    await state.set_state(OfferStates.creating_offer_details)  # Устанавливаем состояние ввода деталей оффера

@router.message(StateFilter(OfferStates.creating_offer_details))
async def process_offer_details(message: Message, state: FSMContext):
    # Сохраняем введенные пользователем данные
    offer_details = message.text
    data = await state.get_data()
    offer_name = data.get('offer_name')

    offer_id = uuid.uuid5(uuid.NAMESPACE_DNS, offer_name)
    username = message.from_user.username
    chat_id = message.chat.id

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                            INSERT INTO public.offers (id, seller_id, offer_name, description, created_at, updated_at)
                            VALUES ('{offer_id}', '{chat_id}', '{offer_name}', '{offer_details}', NOW(), NOW());
                        """)
            connection.commit()

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
    finally:
        # Возвращаем подключение в пул
        return_db_connection(connection)

    logging.info(f"Детали оффера: {offer_details}")  # Логирование

    await message.answer("Ваше ТЗ сохранено. Спасибо!")
    from bot.handlers.menu_seller import stop1
    await stop1(message, state)
    await state.clear()  # Очищаем состояние или можно перевести в другое состояние


back_keyboard1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=BackCallback1(action="back1").pack())]
])

# Остальные функции остаются без изменений
