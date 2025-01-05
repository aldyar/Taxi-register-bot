from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command, CommandStart
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.database.admin_service import search_driver, update_driver, block_driver,get_all_drivers,unblock_driver
from app.state import SearchState, RassylkaStates
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import Bot

admin = Router()

class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in [1075213318]
    

@admin.message(F.text=='В главное меню')
@admin.message(Admin(), CommandStart())
async def start_admin(message: Message,state: FSMContext):
    await state.clear()
    await message.answer('Hello ADMIN',reply_markup=kb.admin_main)


@admin.message(Admin(), F.text == '🔍Поиск пользователя')
async def search_user(message: Message):
    text = (
        "🔍 *Поиск пользователя*\n\n"
        "Пожалуйста, выберите критерий, по которому вы хотите найти пользователя:\n\n"
        "📌 *Возможные варианты:*\n"
        "• По Telegram ID\n"
        "• По имени\n"
        "• По номеру телефона\n"
        "• По городу\n"
        "• По гос. номеру автомобиля\n"
        "• По номеру лицензии\n\n"
        "⬇️ Нажмите на кнопку ниже, чтобы выбрать критерий."
    )
    await message.answer(text, reply_markup=kb.inline_search, parse_mode="Markdown")

"""
@admin.callback_query(Admin(), F.data == 'search_by_tg_id')
async def search_by_tg_id(message: Message, callback: CallbackQuery):"""

# Хэндлер для выбора критерия поиска
@admin.callback_query(Admin(), F.data.in_([
    'search_by_tg_id', 
    'search_by_name', 
    'search_by_phone', 
    'search_by_city', 
    'search_by_car_make', 
    'search_by_car_plate', 
    'search_by_license'
]))
async def select_search_criteria(callback: CallbackQuery, state: FSMContext):
    criteria_map = {
        'search_by_tg_id': 'tg_id',
        'search_by_name': 'full_name',
        'search_by_phone': 'phone',
        'search_by_city': 'city',
        'search_by_car_make': 'car_make',
        'search_by_car_plate': 'car_plate',
        'search_by_license': 'license_number'
    }
    field = criteria_map[callback.data]
    await state.update_data(search_field=field)  # Сохраняем критерий поиска в state
    await callback.message.answer(f"Введите значение для поиска по критерию '{field}':")
    await state.set_state(SearchState.waiting_for_field_value)


# Хэндлер для ввода значения поиска
@admin.message(Admin(), SearchState.waiting_for_field_value)
async def process_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data['search_field']
    value = message.text.strip()  # Убираем лишние пробелы

    # Выполняем поиск
    users = await search_driver(field, value)
    if not users:
        await message.answer("❌ Пользователи не найдены. Попробуйте снова.")
        await state.clear()
        return

    if len(users) == 1:
        user = users[0]
        await state.update_data(selected_user=user)  # Сохраняем найденного пользователя в state
        await message.answer(
            f"✅ Найден пользователь:\n\n"
            f"ID: {user.tg_id}\n"
            f"Имя: {user.full_name}\n"
            f"Телефон: {user.phone}\n"
            f"Город: {user.city}\n"
            f"Марка автомобиля: {user.car_make}\n"
            f"Гос. номер: {user.car_plate}\n"
            f"Лицензия: {user.license_number}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='✏️ Редактировать', callback_data='edit_user')],
                [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel')]
            ])
        )
        await state.set_state(SearchState.selected_user)
    else:
        # Создаем клавиатуру с помощью InlineKeyboardBuilder
        keyboard_builder = InlineKeyboardBuilder()

        for user in users:
            # Добавляем каждую кнопку в новый ряд
            keyboard_builder.row(
                InlineKeyboardButton(
                    text=f"{user.full_name} ({user.tg_id})",
                    callback_data=f"select_user_{user.tg_id}"
                )
            )

        # Генерируем InlineKeyboardMarkup
        keyboard = keyboard_builder.as_markup()

        # Отправляем сообщение с клавиатурой
        await message.answer(
            "🔍 Найдено несколько пользователей. Выберите одного из них:",
            reply_markup=keyboard
        )


# Хэндлер для выбора пользователя из списка
@admin.callback_query(Admin(), F.data.startswith("select_user_"))
async def select_user(callback: CallbackQuery, state: FSMContext):
    tg_id = int(callback.data.split("_")[-1])
    user = await search_driver('tg_id', tg_id)
    if user:
        user = user[0]
        await state.update_data(selected_user=user)
        await callback.message.answer(
            f"✅ Вы выбрали пользователя:\n\n"
            f"ID: {user.tg_id}\n"
            f"Имя: {user.full_name}\n"
            f"Телефон: {user.phone}\n"
            f"Город: {user.city}\n"
            f"Марка автомобиля: {user.car_make}\n"
            f"Гос. номер: {user.car_plate}\n"
            f"Лицензия: {user.license_number}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='✏️ Редактировать', callback_data='edit_user')],
                [InlineKeyboardButton(text='❌ Отменить', callback_data='cancel')]
            ])
        )
        await state.set_state(SearchState.selected_user)

# Хэндлер для отмены
@admin.callback_query(Admin(), F.data == 'cancel')
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Действие отменено.")
    await callback.answer()
    await state.clear()


# Хэндлер для редактирования выбранного пользователя
@admin.callback_query(Admin(), F.data == 'edit_user')
async def edit_user(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user = data.get('selected_user')
    
    if not user:
        await callback.message.answer("❌ Не найден выбранный пользователь для редактирования.")
        return
    
    # Отправляем пользователю сообщение с предложением выбрать, что редактировать
    text = (
        f"📝 Редактирование пользователя {user.full_name}:\n\n"
        "Пожалуйста, выберите поле, которое вы хотите изменить:\n\n"
        "• ФИО\n"
        "• Город\n"
        "• Марка автомобиля\n"
        "• Гос. номер автомобиля\n"
        "• Номер лицензии\n"
    )
    await callback.message.answer(text, reply_markup=kb.inline_edit_criteria)
    await callback.message.answer('⬇️Если вы хотите заблокировать пользователя используйте кнопки ниже', reply_markup=kb.admin_block_user)
    await state.set_state(SearchState.waiting_for_edit_criteria)

# Хэндлер для выбора критерия редактирования
@admin.callback_query(Admin(), F.data.in_([
    'edit_full_name', 
    'edit_city', 
    'edit_car_make', 
    'edit_car_plate', 
    'edit_license_number'
]))
async def select_edit_criteria(callback: CallbackQuery, state: FSMContext):
    criteria_map = {
        'edit_full_name': 'full_name',
        'edit_city': 'city',
        'edit_car_make': 'car_make',
        'edit_car_plate': 'car_plate',
        'edit_license_number': 'license_number',
    }

    field = criteria_map[callback.data]
    await state.update_data(edit_field=field)  # Сохраняем критерий редактирования в state
    await callback.message.answer(f"Введите новое значение для поля '{field}':")
    await state.set_state(SearchState.waiting_for_edit_value)

# Хэндлер для ввода нового значения для редактируемого поля
@admin.message(Admin(), SearchState.waiting_for_edit_value)
async def process_edit_value(message: Message, state: FSMContext):
    data = await state.get_data()
    field = data['edit_field']
    new_value = message.text.strip()  # Убираем лишние пробелы

    # Получаем пользователя из state
    user = data.get('selected_user')
    if not user:
        await message.answer("❌ Пользователь не найден для редактирования.")
        await state.clear()
        return

    # Обновляем поле выбранного пользователя
    setattr(user, field, new_value)

    # Сохраняем изменения в базе данных
    await update_driver(user.tg_id, field, new_value)  # Предполагаем, что у вашего объекта есть метод save() для сохранения

    # Подтверждаем изменения
    await message.answer(
        f"✅ Значение для поля '{field}' обновлено:\n\n"
        f"{field.capitalize()}: {new_value}"
    )
    await state.set_state(SearchState.selected_user)


@admin.message(Admin(),F.text=='Заблокировать' )
async def process_block_button(message: Message,state: FSMContext):
    await message.answer('⚠️Введите комментарий который будет видеть пользователь',reply_markup=kb.admin_block_user_2)
    await state.set_state(SearchState.block_user)

@admin.message(Admin(), F.text == "Без комментария")
async def block_user_without_comment(message: Message, state: FSMContext,bot:Bot):
    # Получаем данные из состояния
    data = await state.get_data()

    # Извлекаем tg_id выбранного пользователя
    user = data.get('selected_user')
    if user:
        tg_id = user.tg_id  # Извлекаем tg_id
    else:
        await message.answer("❌ Не удалось найти выбранного пользователя.")
        return
    success = await block_driver( tg_id)
    if success:
        await message.answer(f"🔒 Водитель с TG ID {tg_id} был заблокирован без комментария.",reply_markup=kb.admin_back)
        try:
            await bot.send_message(
                chat_id=tg_id,
                text="❌Ваш аккаунт заблокировал администратор"
            )
        except Exception as e:
            await message.answer(f"⚠️ Сообщение водителю отправить не удалось. Ошибка: {e}",reply_markup=kb.admin_back)
    else:
        await message.answer(f"❌ Водитель с TG ID {tg_id} не найден.",reply_markup=kb.admin_back)
    await state.clear()  # Очищаем состояние после выполнения


@admin.message(Admin(), SearchState.block_user)
async def block_user(message: Message, state: FSMContext, bot: Bot):
    # Получаем данные из состояния
    data = await state.get_data()

    # Извлекаем tg_id выбранного пользователя
    user = data.get('selected_user')
    if user:
        tg_id = user.tg_id  # Извлекаем tg_id
    else:
        await message.answer("❌ Не удалось найти выбранного пользователя.")
        return

    # Получаем комментарий
    comment = message.text
    success = await block_driver(tg_id, comment)
    if success:
        await message.answer(f"🔒 Водитель с TG ID {tg_id} был заблокирован с комментарием: {comment}",reply_markup=kb.admin_back)
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=f"❌Ваш аккаунт заблокировал администратор.\n\nКомментарий: {comment}"
            )
        except Exception as e:
            await message.answer(f"⚠️ Сообщение водителю отправить не удалось. Ошибка: {e}",reply_markup=kb.admin_back)
    else:
        await message.answer(f"❌ Водитель с TG ID {tg_id} не найден.",reply_markup=kb.admin_back)
    await state.clear()  # Очищаем состояние после выполнения
    

@admin.message(Admin(), F.text == "Разблокировать")
async def unblock_user(message: Message, state: FSMContext,bot:Bot):
    data = await state.get_data()
    user = data.get('selected_user')
    if user:
        tg_id = user.tg_id  # Извлекаем tg_id
    unblock = await unblock_driver(tg_id)
    if unblock:
        await message.answer(f"✅ Пользователь с Telegram ID {tg_id} успешно разблокирован!",reply_markup=kb.admin_back)
        try:
            await bot.send_message(
                chat_id=tg_id,
                text=f"✅Ваш аккаунт разблокировал администратор."
            )
        except Exception as e:
            await message.answer(f"⚠️ Сообщение водителю отправить не удалось. Ошибка: {e}",reply_markup=kb.admin_back)
    await state.clear()
