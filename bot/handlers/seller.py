from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
import uuid
from bot.util.db import get_db_connection, return_db_connection

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Создание роутера для этого контроллера
router = Router()

# Создаем CallbackData для обработки данных кнопок
class ButtonCallback(CallbackData, prefix="button"):
    action: str

class RegisterSeller(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()
    waiting_for_inst = State()
    end = State()

# Создание инлайн-клавиатуры с кнопками
next_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Далее", callback_data=ButtonCallback(action="next").pack())]
])

async def handle_seller(callback_query: CallbackQuery, state: FSMContext):
    logging.info("Обработчик 'handle_seller' вызван.")  # Логирование
    await callback_query.message.edit_text(
        "Вы выбрали работать продавцом! Для регистрации\nВведите ваше ФИО:"
    )
    await state.set_state(RegisterSeller.waiting_for_name)

@router.message(StateFilter(RegisterSeller.waiting_for_name))
async def process_name_input(message: Message, state: FSMContext):
    logging.info(f"Получено ФИО: {message.text}")  # Логирование
    full_name = message.text
    await state.update_data(full_name=full_name)
    await message.answer(
        "Введите вашу почту:",
    )
    await state.set_state(RegisterSeller.waiting_for_email)

@router.message(StateFilter(RegisterSeller.waiting_for_email))
async def process_email_input(message: Message, state: FSMContext):
    logging.info(f"Получен email: {message.text}")  # Логирование
    email = message.text
    await state.update_data(email=email)

    await message.answer("Введите ваш инстаграм:")
    await state.set_state(RegisterSeller.waiting_for_inst)

@router.message(StateFilter(RegisterSeller.waiting_for_inst))
async def process_inst_input(message: Message, state: FSMContext):
    inst = message.text
    await state.update_data(inst=inst)
    await state.update_data(role="seller")
    user_data = await state.get_data()
    full_name = user_data["full_name"]
    email = user_data["email"]
    role = user_data["role"]

    await message.answer(
        f"Регистрация завершена!\nВаше ФИО: {full_name}\nВаша почта: {email}\nВаш инстаграм: {inst}"
    )

    username = message.from_user.username
    chat_id = message.chat.id
    name_based_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, username)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"""
                            INSERT INTO public.users (id, tg_id, role)
                            VALUES ('{name_based_uuid}', '{chat_id}', '{role}');
                        """)
            connection.commit()

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
    finally:
        # Возвращаем подключение в пул
        return_db_connection(connection)

    await state.clear()  # Устанавливаем состояние end
    from bot.handlers import menu_seller
    await menu_seller.stop1(message, state)
