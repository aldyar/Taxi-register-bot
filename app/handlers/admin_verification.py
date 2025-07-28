from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.admin_service import search_driver_ver, update_driver, block_driver,get_all_drivers, update_driver_verification
from app.state import SearchState, RassylkaStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, FSInputFile
import os

admin2 = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    
@admin2.message(Admin(), F.text == '⏳Список ожидания')
async def list_wait(message: Message, bot: Bot, state: FSMContext):
    # Ищем водителей с верификацией False
    drivers = await search_driver_ver("verification", False)
    
    if not drivers:
        await message.answer("Нет водителей на верификации.")
        return
    
    # Выводим информацию о каждом водителе с кнопкой выбора
    for driver in drivers:
        driver_info = (
        f"👤 Профиль водителя:\n"
        f"🆔 Telegram ID: {driver.tg_id}\n"
        f"📛 Полное имя: {driver.full_name}\n"
        f"📞 Телефон: {driver.phone}\n"
        f"🏙️ Город: {driver.city}\n"
        f"🚗 Марка машины: {driver.car_make}\n"
        f"🔢 Гос. номер: {driver.car_plate}\n"
        f"📜 Номер лицензии: {driver.license_number}\n"
        f"🕒 Статус: В ожидании\n"
    )
        
        # Создаем кнопку для выбора водителя
       # button = InlineKeyboardButton("Выбрать", callback_data=f"select_driver_{driver.tg_id}")
        #markup = InlineKeyboardMarkup().add(button)
        
        await message.answer(driver_info,reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Выбрать', callback_data=f"select_driver_{driver.tg_id}")]
            ]))

@admin2.callback_query(Admin(), F.data.startswith("select_driver_"))
async def select_driver(callback_query: CallbackQuery, bot: Bot, state: FSMContext):
    tg_id = int(callback_query.data.split("_")[2])
    
    # Ищем водителя по tg_id
    driver = await search_driver_ver("tg_id", tg_id)
    if driver:
        driver = driver[0]
        await state.update_data(selected_driver_id=tg_id)
        # Собираем данные водителя
        driver_details = (
        f"👤 Профиль водителя:\n"
        f"🆔 Telegram ID: {driver.tg_id}\n"
        f"📛 Полное имя: {driver.full_name}\n"
        f"📞 Телефон: {driver.phone}\n"
        f"🏙️ Город: {driver.city}\n"
        f"🚗 Марка машины: {driver.car_make}\n"
        f"🔢 Гос. номер: {driver.car_plate}\n"
        f"📜 Номер лицензии: {driver.license_number}\n"
        f"🕒 Статус: В ожидании\n"
    )
        
         # Отправляем данные водителя
        await bot.send_message(callback_query.from_user.id, driver_details, reply_markup=kb.approve_button)
        
        # Путь к папке с изображениями
        base_path = "C:\\Users\\PC\\Desktop\\Taxi registor bot\\app\\image"
        
        # Список фотографий
        photos = {
            "Лицевая сторона лицензии": driver.license_front_url,
            "Обратная сторона лицензии": driver.license_back_url,
            "Фото автомобиля (вид 1)": driver.car_photo_1,
            "Фото автомобиля (вид 2)": driver.car_photo_2,
            "Фото автомобиля (вид 3)": driver.car_photo_3,
            "Фото водителя с автомобилем": driver.selfie_with_car,
        }
        
        # Отправляем каждое фото, если оно существует
        for caption, file_name in photos.items():
            file_path = os.path.join(base_path, file_name)
            if os.path.exists(file_path):
                photo = FSInputFile(file_path)
                await bot.send_photo(callback_query.from_user.id, photo, caption=caption)
            else:
                await bot.send_message(callback_query.from_user.id, f"{caption}: файл не найден.")
        
        await callback_query.answer(f"Вы выбрали водителя: {driver.full_name}")
    else:
        await callback_query.answer("Водитель не найден.")


@admin2.message(Admin(), F.text == "Одобрить")
async def approve_driver(message: Message, state: FSMContext, bot: Bot):
    # Получаем ID выбранного водителя из state
    data = await state.get_data()
    tg_id = data.get("selected_driver_id")
    
    if tg_id is None:
        await message.answer("Ошибка: выберите водителя для одобрения.")
        return
    
    # Обновляем статус верификации водителя
    success = await update_driver_verification(tg_id, True)
    
    if success:
        await message.answer(f"✅ Водитель с Telegram ID {tg_id} был одобрен!")
        try:
            await bot.send_message(
                chat_id=tg_id,
                text="🎉 Поздравляем! Вы успешно прошли верификацию. Теперь вы можете использовать платформу.\n\n [Присоединяйтесь к группе](https://t.me/+evPOe_ZA2GUxOTVi)",
                parse_mode="Markdown",
                disable_web_page_preview=True
            )

        except Exception as e:
            await message.answer(f"⚠️ Сообщение водителю отправить не удалось. Ошибка: {e}")
    else:
        await message.answer("❌ Не удалось обновить статус водителя. Попробуйте снова.")
    
    # Сбрасываем state
    await state.clear()