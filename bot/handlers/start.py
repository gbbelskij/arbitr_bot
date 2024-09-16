from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from bot.util.db import get_db_connection, return_db_connection

# Создание роутера для этого контроллера
router = Router()

# Создаем CallbackData для обработки данных кнопок
class ButtonCallback(CallbackData, prefix="button"):
    action: str

class RegisterBlogger(StatesGroup):
    waiting_for_name = State()
    waiting_for_email = State()

# Создание инлайн-клавиатуры с кнопками
inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продавец", callback_data=ButtonCallback(action="seller").pack())],
    [InlineKeyboardButton(text="Блоггер", callback_data=ButtonCallback(action="blogger").pack())],
    [InlineKeyboardButton(text="Информация о проекте", callback_data=ButtonCallback(action="project_info").pack())]
])

# Обработчик команды /start
@router.message(CommandStart())
async def send_welcome(message: Message, state: FSMContext):
    chat_id = message.chat.id
    await state.update_data(chat_id=chat_id)
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tg_id, role FROM public.users WHERE tg_id = %s", (str(message.chat.id),))

            # Получаем результат
            user_data = cursor.fetchone()

            if user_data:
                tg_id, role = user_data  # Распаковываем данные

                if role == "blogger":
                    from bot.handlers.menu_blogger import stop
                    await stop(message, state)
                else:
                    from bot.handlers.menu_seller import stop1
                    await stop1(message, state)
            else:
                await message.answer(
                    "Привет!\nДля начала работы с арбитражем маркетплейсов выберите роль и зарегистрируйтесь.",
                    reply_markup=inline_keyboard  # Передаем инлайн-клавиатуру с кнопками
                )

    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
    finally:
        # Возвращаем подключение в пул
        return_db_connection(connection)

# Обработчик callback для кнопок
@router.callback_query(ButtonCallback.filter())
async def callback_button_handler(callback_query: CallbackQuery, callback_data: ButtonCallback, state: FSMContext):
    if callback_data.action == "seller":
        await callback_query.message.edit_text("Информация для продавцов.", reply_markup=None)
        from bot.handlers.seller import handle_seller
        await handle_seller(callback_query, state)

    elif callback_data.action == "blogger":
        await callback_query.message.edit_text("Информация для блоггеров.", reply_markup=None)
        from bot.handlers.blogger import handle_blogger
        await handle_blogger(callback_query, state)

    elif callback_data.action == "project_info":
        from bot.handlers.project_info import handle_project_info
        await handle_project_info(callback_query)  # Вызов обработчика для информации о проекте

    await callback_query.answer()
