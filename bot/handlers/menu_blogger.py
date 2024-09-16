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
    [InlineKeyboardButton(text="Получить список офферов", callback_data=MenuCallback(action="button1").pack())],
    [InlineKeyboardButton(text="Мои офферы", callback_data=MenuCallback(action="button2").pack())],
    [InlineKeyboardButton(text="Счёт", callback_data=MenuCallback(action="button3").pack())],
    [InlineKeyboardButton(text="Рейтинг", callback_data=MenuCallback(action="button4").pack())]
])

async def stop(message: Message, state: FSMContext):
    logging.info("Функция 'stop' вызвана.")  # Логирование
    await message.answer(
        "Выберите действие:",
        reply_markup=menu_keyboard
    )
    await state.set_state(MainMenu.main_menu)  # Устанавливаем состояние в главное меню

@router.callback_query(MenuCallback.filter())
async def menu_callback_handler(callback_query: CallbackQuery, callback_data: MenuCallback, state: FSMContext):
    logging.info(f"Обработчик кнопки меню вызван: {callback_data.action}")  # Логирование

    if callback_data.action == "button1":
        from bot.handlers.offer_blogger import get_all_offers
        await get_all_offers(callback_query.message, state)
    elif callback_data.action == "button2":
        from bot.handlers.offer_blogger2 import get_my_offers
        await get_my_offers(callback_query, callback_data, state)
    elif callback_data.action == "button3":
        await callback_query.message.edit_text("Вы выбрали Кнопку 3")
    elif callback_data.action == "button4":
        await callback_query.message.edit_text("Вы выбрали Кнопку 4")
    elif callback_data.action == "button11":
        from bot.handlers.offer_seller import start_create_offer  # Импорт функции создания оффера
        await start_create_offer(callback_query.message, state)

    elif callback_data.action == "button22":
        username = callback_query.from_user.username
        chat_id = callback_query.message.chat.id
        await state.update_data(chat_id=chat_id)
        from bot.handlers.offer_seller import offers_by_seller
        await offers_by_seller(callback_query.message, state)
    elif callback_data.action == "button33":
        await callback_query.message.edit_text("Вы выбрали Кнопку 3")

    await callback_query.answer()
