from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.admin_service import search_driver, update_driver, block_driver,get_all_drivers
from app.state import SearchState, RassylkaStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot

admin1 = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    

@admin1.message(Admin(), F.text == '📢Рассылка')
async def rassylka(message: Message, bot: Bot, state: FSMContext):
    # Запрос на выбор рассылки
    await message.answer("Выберите тип рассылки:\n1. Всем пользователям\n2. По городам", reply_markup=kb.city_keyboard)
    await state.set_state(RassylkaStates.choosing_rassylka_type)


@admin1.message(Admin(), F.text == "Всем пользователям")
async def send_to_all_users(message: Message, bot: Bot, state: FSMContext):
    # Запрашиваем текст рассылки
    await message.answer("Введите текст рассылки:")
    await state.set_state(RassylkaStates.awaiting_rassylka_text)
    await state.update_data(rassylka_type="all")


@admin1.message(Admin(), F.text == "По городам")
async def send_by_city(message: Message, bot: Bot, state: FSMContext):
    # Запрашиваем город
    await message.answer("Введите название города:")
    await state.set_state(RassylkaStates.awaiting_city_name)


@admin1.message(Admin(), RassylkaStates.awaiting_rassylka_text)
async def handle_rassylka_text(message: Message, bot: Bot, state: FSMContext):
    # Получаем текст рассылки
    text = message.text
    data = await state.get_data()

    # Выбираем рассылку по типу
    if data.get("rassylka_type") == "all":
        drivers = await get_all_drivers()
        for driver in drivers:
            try:
                await bot.send_message(driver.tg_id, text)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {driver.tg_id}: {e}")

    await message.answer("Рассылка завершена!",reply_markup=kb.admin_main)
    await state.clear()


@admin1.message(Admin(), RassylkaStates.awaiting_city_name)
async def handle_city_name(message: Message, bot: Bot, state: FSMContext):
    # Получаем название города
    city = message.text
    await state.update_data(city_name=city)

    # Запрашиваем текст рассылки
    await message.answer("Введите текст рассылки:")
    await state.set_state(RassylkaStates.awaiting_rassylka_text_city)


@admin1.message(Admin(), RassylkaStates.awaiting_rassylka_text_city)
async def handle_rassylka_text_by_city(message: Message, bot: Bot, state: FSMContext):
    # Получаем текст рассылки
    text = message.text
    data = await state.get_data()
    city_name = data.get("city_name")

    # Ищем водителей по городу
    drivers = await search_driver("city", city_name)
    if not drivers:
        await message.answer(f"Нет водителей в городе {city_name}.")
    else:
        for driver in drivers:
            try:
                await bot.send_message(driver.tg_id, text)
            except Exception as e:
                print(f"Не удалось отправить сообщение пользователю {driver.tg_id}: {e}")

    await message.answer(f"Рассылка по городу {city_name} завершена!",reply_markup=kb.admin_main)
    await state.clear()