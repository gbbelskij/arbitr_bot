from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
from bot.util.db import get_db_connection, return_db_connection
from bot.handlers.offer_blogger import bot, router
import config



class ButtonCallback2(CallbackData, prefix="agree"):
    action: str
    offer_id: str
    blogger_chat_id: str

def create_seller_accept_keyboard(offer_id: str, blogger_chat_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Принять", callback_data=ButtonCallback2(action="agree", offer_id=offer_id, blogger_chat_id=blogger_chat_id).pack())],
        [InlineKeyboardButton(text="Отклонить", callback_data=ButtonCallback2(action="decline", offer_id=offer_id, blogger_chat_id=blogger_chat_id).pack())]
    ])

async def seller_accept_button(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext, seller_id: str):
    # Извлекаем данные из состояния
    state_data = await state.get_data()
    offer_name = state_data.get("offer_name")
    logging.info(f"state_data = {state_data}")
    # Отправляем сообщение продавцу

    seller_accept_keyboard = create_seller_accept_keyboard(offer_id=state_data.get("offer_id"), blogger_chat_id=str(state_data.get("blogger_chat_id")))
    await bot.send_message(
        chat_id=seller_id,
        text=f"Ваш оффер {offer_name} был выбран покупателем!",
        reply_markup=seller_accept_keyboard
    )


# Обработчик для кнопок принятия и отклонения
@router.callback_query(ButtonCallback2.filter())
async def seller_accept_button_handler(callback_query: CallbackQuery, callback_data: ButtonCallback2, state: FSMContext):
    action = callback_data.action
    offer_id = callback_data.offer_id
    blogger_chat_id = callback_data.blogger_chat_id

    logging.info(f"offer_id:2:::: {offer_id}")
    if action == "agree":

        # Обновляем данные в базе
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE public.offers
                    SET blogger_id = %s
                    WHERE id = %s;
                """, (blogger_chat_id, offer_id,))

                connection.commit()
                await callback_query.message.answer("Вы подтвердили оффер. Сообщение блоггеру отправлено!")
                cursor.execute("""
                    SELECT offer_name
                    FROM public.offers
                    WHERE id = %s;
                """, (str(offer_id),))

                offer_name = cursor.fetchone()[0]
                await bot.send_message(chat_id=blogger_chat_id, text=f"Продавец подтвердил оффер {offer_name}. Приступайте к работе!")
        except Exception as e:
            logging.error(f"Ошибка при обновлении данных: {e}")
            await callback_query.message.answer("Произошла ошибка при обновлении данных.")
        finally:
            return_db_connection(connection)

    elif action == "decline":
        await callback_query.message.answer("Вы отклонили оффер.")
        logging.info("Оффер был отклонен.")
