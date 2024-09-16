from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

# Создание роутера для этого контроллера
router = Router()

# Создаем CallbackData для обработки данных кнопки "Назад"
class BackCallback(CallbackData, prefix="back"):
    action: str

# Клавиатура с кнопкой "Назад"

# Обработчик информации о проекте
async def handle_project_info(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Приветствую тебя мой верный друг, Продавец это тот кто выставляет в объявление товар который можно будет купить, Блогер этот тот который начал или хочет начать зарабатывать на покупках товара рекламу которого крутит в рилсах.",
        reply_markup=back_keyboard  # Кнопка "Назад"
    )

back_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Назад", callback_data=BackCallback(action="back").pack())]
])

# Обработчик callback для кнопки "Назад"
@router.callback_query(BackCallback.filter())
async def callback_back_handler(callback_query: CallbackQuery, callback_data: BackCallback):
    if callback_data.action == "back":
        # Возврат в стартовый контроллер
        from bot.handlers.start import inline_keyboard
        await callback_query.message.edit_text(
            "Привет!\nДля начала работы с арбитражем маркетплейсов выберите роль и зарегистрируйтесь.",
            reply_markup=inline_keyboard
        )

    await callback_query.answer()
