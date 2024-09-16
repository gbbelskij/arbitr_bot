from aiogram import Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import logging
from bot.util.db import get_db_connection, return_db_connection
from aiogram import Bot
import config

# Инициализация логирования
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)

# Создание роутера для этого контроллера
router = Router()

class OfferCallback(CallbackData, prefix="offer"):
    action: str
    offer_id: str

class ButtonCallback(CallbackData, prefix="accept"):
    action: str

class ButtonsState(StatesGroup):
    accept = State()

async def get_all_offers(message: Message, state: FSMContext):
    logging.info("Функция get_all_offers вызвана")

    # Подключаемся к базе данных
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Извлекаем все офферы из базы данных
            cursor.execute("""
                            SELECT *
                            FROM public.offers
                            WHERE blogger_id IS NULL
                            ORDER BY created_at DESC;
                        """)
            offers = cursor.fetchall()
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        offers = []
    finally:
        return_db_connection(connection)

    # Проверка на наличие офферов
    if not offers:
        await message.answer("Офферы не найдены.")
        return

    # Формируем текст для вывода офферов
    answer = ""
    count = 1
    for offer in offers:
        answer += f"{count}. {offer[3]}\n\n"
        count += 1

    # Создаем клавиатуру с офферами
    buttons = []
    count = 1
    for offer in offers:
        button = InlineKeyboardButton(
            text=str(count),  # Преобразуем число в строку
            callback_data=OfferCallback(action="select", offer_id=offer[0]).pack()  # Используем ID оффера из БД
        )
        count += 1
        buttons.append([button])  # Каждая кнопка в отдельном списке

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await message.answer(answer, reply_markup=keyboard)


accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Подтвердить", callback_data=ButtonCallback(action="accept").pack())]
])

seller_accept_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Принять", callback_data=ButtonCallback(action="agree").pack()),
     InlineKeyboardButton(text="Отклонить", callback_data=ButtonCallback(action="decline").pack())]
])


# Используем метод filter() без аргументов и выполняем проверку внутри lambda-функции
@router.callback_query(OfferCallback.filter())
async def handle_offer_selection(callback_query: CallbackQuery, callback_data: OfferCallback, state: FSMContext):
    # Проверяем, что действие совпадает с "select"
    if callback_data.action == "select":
        offer_id = callback_data.offer_id
        blogger_chat_id = callback_query.from_user.id
        await state.update_data(selected_offer=offer_id, blogger_chat_id=blogger_chat_id)

        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                # Извлекаем информацию о продавце оффера по его ID
                cursor.execute("""
                    SELECT description
                    FROM public.offers
                    WHERE id = %s;
                """, (offer_id,))
                seller_info = cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении информации о продавце: {e}")
            await callback_query.message.answer("Произошла ошибка при получении информации о продавце.")
            return
        finally:
            return_db_connection(connection)

        description = seller_info[0]
        await callback_query.message.edit_text(f"Вы выбрали оффер с ID: {offer_id}\nОписание:\n{description}", reply_markup=accept_keyboard)

        # Устанавливаем начальное состояние после выбора оффера
        await state.set_state(ButtonsState.accept)




@router.callback_query(ButtonCallback.filter())
async def button_handler(callback_query: CallbackQuery, callback_data: ButtonCallback, state: FSMContext):
    action = callback_data.action

    # Получаем текущее состояние данных
    state_data = await state.get_data()

    if action == "accept":
        offer_id = state_data.get("selected_offer")
        logging.info(f"offer_id:1::::{offer_id}")

        if offer_id is None:
            await callback_query.message.answer("Ошибка: ID оффера не найден.")
            return

        # Подключаемся к базе данных
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT seller_id, offer_name
                    FROM public.offers
                    WHERE id = %s;
                """, (offer_id,))
                seller_info = cursor.fetchone()
        except Exception as e:
            logging.error(f"Ошибка при получении информации о продавце: {e}")
            await callback_query.message.answer("Произошла ошибка при получении информации о продавце.")
            return
        finally:
            return_db_connection(connection)

        if not seller_info:
            await callback_query.message.answer("Продавец для выбранного оффера не найден.")
            return

        seller_telegram_id = seller_info[0]
        offer_name = seller_info[1]
        # Обновляем состояние FSM с offer_id
        await state.update_data(offer_name=offer_name, offer_id=offer_id)

        try:
            await state.update_data(offer_name=offer_name, offer_id=offer_id)
            logging.info(f"state в обработчике accept: {await state.get_data()}")

            # Используем bot.send_message для отправки кнопок следующего действия
            # await bot.send_message(
            #     chat_id=seller_telegram_id,
            #     text=f"Ваш оффер {offer_name} был выбран покупателем!",
            #     reply_markup=seller_accept_keyboard
            # )
            await callback_query.message.answer("Сообщение продавцу отправлено.")

            from bot.handlers.blogger_seller import seller_accept_button
            await seller_accept_button(callback_query, callback_data, state, seller_telegram_id)
        except Exception as e:
            logging.error(f"Ошибка при отправке сообщения продавцу: {e}")
            await callback_query.message.answer("Не удалось отправить сообщение продавцу.")


    elif action == "agree":
        # Проверяем данные состояния и устанавливаем состояние accept
        state_data = await state.get_data()
        offer_id = state_data.get("selected_offer")
        logging.info(f"state в обработчике agree: {state_data}")
        logging.info(f"offer_id:2::::{offer_id}")
        blogger_chat_id = state_data.get("blogger_chat_id")

        if offer_id is None:
            await callback_query.message.answer("Ошибка: ID оффера не найден.")
            return

        # Подключаемся к базе данных
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE public.offers
                    SET blogger_id = %s
                    WHERE id = %s;
                """, (blogger_chat_id, offer_id))
                connection.commit()
                await callback_query.message.answer("Вы подтвердили оффер. Оффер был назначен вам.")
        except Exception as e:
            logging.error(f"Ошибка при обновлении данных: {e}")
            await callback_query.message.answer("Произошла ошибка при обновлении данных.")
        finally:
            return_db_connection(connection)
        await state.set_state(ButtonsState.accept)

    elif action == "decline":
        # Заглушка для кнопки "Отклонить"
        await callback_query.message.answer("Вы отклонили оффер.")
        logging.info("Оффер был отклонен.")
        await state.set_state(ButtonsState.accept)
