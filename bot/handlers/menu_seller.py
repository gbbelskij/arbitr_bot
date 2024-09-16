from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

# Создание роутера для этого контроллера
router = Router()

# Создаем CallbackData для обработки данных кнопок
class MenuCallback(CallbackData, prefix="menu"):
    action: str

class MainMenu(StatesGroup):
    main_menu = State()

# Создание инлайн-клавиатуры с кнопками меню
menu_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Добавить оффер", callback_data=MenuCallback(action="button11").pack())],
    [InlineKeyboardButton(text="Список моих офферов", callback_data=MenuCallback(action="button22").pack())],
    [InlineKeyboardButton(text="Подписка✅", callback_data=MenuCallback(action="button33").pack())],
])

async def stop1(message: Message, state: FSMContext):
    logging.info("Функция 'stop1' вызвана.")  # Логирование
    await message.answer(
        "Выберите действие:",
        reply_markup=menu_keyboard
    )
    await state.set_state(MainMenu.main_menu)  # Устанавливаем состояние в главное меню

# @router.callback_query(MenuCallback.filter())
# async def menu_callback_handler(callback_query: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
#     logging.info(f"Обработчик кнопки меню вызван: {callback_data.action}")  # Логирование

#     if callback_data.action == "button11":
#         logging.info("11111111111111111111")
#         from bot.handlers.offer_seller import start_create_offer  # Импорт функции создания оффера
#         await start_create_offer(callback_query.message, state)  # Используем await для вызова асинхронной функции
#     elif callback_data.action == "button22":
#         await callback_query.message.edit_text("Вы выбрали Кнопку 2")
#     elif callback_data.action == "button33":
#         await callback_query.message.edit_text("Вы выбрали Кнопку 3")

#     await callback_query.answer()
