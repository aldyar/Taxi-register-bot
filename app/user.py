from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
import app.keyboards as kb
from aiogram.fsm.context import FSMContext
from app.state import Driver
from aiogram.types import InputFile
from aiogram.types.input_file import FSInputFile
import os
from aiogram.types import FSInputFile
from app.database.user_service import save_driver_data,delete_user_files, get_driver_by_tg_id, check_uniqueness,check_tg_id_exists
user = Router()



@user.message(CommandStart())
async def cmd_start(message: Message,state: FSMContext):
    await state.clear()
    exist = await check_tg_id_exists(message.from_user.id)
    if exist == True:
        await message.answer('Вы можете посмотреть ваши данные по кнопке ниже⬇️',reply_markup=kb.user_profile)
    else:
        await message.answer("Добро пожаловать! 👋\n\nДля начала регистрации нажмите на кнопку ниже",reply_markup=kb.register)


@user.message(F.text=='🖊Внести изменения в анкету')
async def exit_button(message: Message,state: FSMContext):
    await state.clear()
    await delete_user_files(message.from_user.id)
    await message.answer("Добро пожаловать! 👋\n\nДля начала регистрации нажмите на кнопку ниже",reply_markup=kb.register)


@user.message(F.text=='Регистрация')
async def registration(message: Message, state: FSMContext):
    await message.answer("Введите вашу фамилию:",reply_markup=kb.exit)
    await state.set_state(Driver.last_name)


@user.message(Driver.last_name)
async def process_last_name(message: Message, state: FSMContext):
    last_name = message.text.strip()
    if not last_name.isalpha():  # Проверка: фамилия должна состоять только из букв
        await message.answer("Фамилия должна содержать только буквы. Попробуйте ещё раз.")
        return
    await state.update_data(last_name=last_name)
    await message.answer("Теперь введите ваше имя:")
    await state.set_state(Driver.first_name)


@user.message(Driver.first_name)
async def process_first_name(message: Message, state: FSMContext):
    first_name = message.text.strip()
    if not first_name.isalpha():  # Проверка: имя должно быть только буквенным
        await message.answer("Имя должно содержать только буквы. Попробуйте ещё раз.")
        return
    await state.update_data(first_name=first_name)
    await message.answer("Введите ваше отчество (или напишите `Нет`, если отчество отсутствует):",parse_mode='Markdown')
    await state.set_state(Driver.middle_name)


@user.message(Driver.middle_name)
async def process_middle_name(message: Message, state: FSMContext):
    middle_name = message.text.strip()
    if not middle_name.isalpha() and middle_name.lower() != "нет":  # Отчество или 'Нет'
        await message.answer("Отчество должно содержать только буквы. Попробуйте ещё раз.")
        return
    await state.update_data(middle_name=middle_name if middle_name.lower() != "нет" else None)
    await message.answer("Теперь отправьте ваш рабочий номер телефона.")
    await state.set_state(Driver.phone)


@user.message(Driver.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    # Простая валидация номера телефона
    if not phone.isdigit() or len(phone) < 10:
        await message.answer("Пожалуйста, введите корректный номер телефона (только цифры, минимум 10 символов).")
        return
    is_unique = await check_uniqueness('phone', phone)
    if not is_unique:
        await message.answer("Этот номер телефона уже зарегистрирован. Пожалуйста, введите другой номер.")
        return
    await state.update_data(phone=phone)
    await message.answer("Пожалуйста, укажите ваш город проживания с большой буквы. Если в названии города есть тире, напишите его с тире (например, `Санкт-Петербург`).",parse_mode='Markdown')
    await state.set_state(Driver.city)


@user.message(Driver.city)
async def process_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if not city.isalpha():  # Проверка: название города должно содержать только буквы
        await message.answer("Название города должно содержать только буквы. Попробуйте ещё раз.")
        return
    await state.update_data(city=city)
    await message.answer("Укажите марку вашего автомобиля:")
    await state.set_state(Driver.car_make)


@user.message(Driver.car_make)
async def process_car_make(message: Message, state: FSMContext):
    car_make = message.text.strip()
    if len(car_make) < 2:  # Проверка: марка автомобиля должна быть адекватной длины
        await message.answer("Название марки автомобиля должно быть не короче 2 символов. Попробуйте ещё раз.")
        return
    await state.update_data(car_make=car_make)
    await message.answer("Введите государственный номер вашего автомобиля (например `A123BC77`):",parse_mode='Markdown')
    await state.set_state(Driver.car_plate)


@user.message(Driver.car_plate)
async def process_car_plate(message: Message, state: FSMContext):
    car_plate = message.text.strip().upper()
    # Проверка на корректность формата гос. номера (российский пример: буква-цифра-буква)
    if not car_plate.isupper():  # Проверяем, что все символы в верхнем регистре
        await message.answer("Введите номер автомобиля только в верхнем регистре (например, A123BC).")
        return
    is_unique = await check_uniqueness('car_plate', car_plate)
    if not is_unique:
        await message.answer("Этот государственный номер уже зарегистрирован. Пожалуйста, введите другой номер.")
        return
    await state.update_data(car_plate=car_plate)
    await message.answer("Введите номер ваших водительских прав:")
    await state.set_state(Driver.license_number)


@user.message(Driver.license_number)
async def process_license_number(message: Message, state: FSMContext):
    license_number = message.text.strip()
    if not license_number.isdigit() or len(license_number) < 10:
        await message.answer("Номер прав должен состоять только из цифр и быть не короче 10 символов. Попробуйте ещё раз.")
        return
    is_unique = await check_uniqueness('license_number', license_number)
    if not is_unique:
        await message.answer("Этот номер водительских прав уже зарегистрирован. Пожалуйста, введите другой номер.")
        return
    await state.update_data(license_number=license_number)
    await message.answer("Пожалуйста, отправьте фотографию передней стороны ваших водительских прав:")
    await state.set_state(Driver.license_front)
    

@user.message(Driver.license_front)
async def process_license_front(message: Message, state: FSMContext):
    photo = message.photo[-1]  # Получаем максимальное разрешение фотографии
    file = await message.bot.get_file(photo.file_id)  # Получаем объект File
    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)  # Создаем папку, если ее нет
    # Сохраняем файл на диск
    save_path = os.path.join(save_dir, f"license_front_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)
    # Сохраняем путь к файлу в состоянии
    await state.update_data(license_front=save_path)
    await message.answer("Теперь отправьте фотографию задней стороны ваших водительских прав:")
    await state.set_state(Driver.license_back)


@user.message(Driver.license_back)
async def process_license_back(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"license_back_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)

    await state.update_data(license_back=save_path)
    await message.answer("Теперь отправьте фото автомобиля (вид спереди):")
    await state.set_state(Driver.car_photo_1)


@user.message(Driver.car_photo_1)
async def process_car_photo_1(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"car_photo_1_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)

    await state.update_data(car_photo_1=save_path)
    await message.answer("Теперь отправьте фото автомобиля (вид сзади):")
    await state.set_state(Driver.car_photo_2)


@user.message(Driver.car_photo_2)
async def process_car_photo_2(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"car_photo_2_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)

    await state.update_data(car_photo_2=save_path)
    await message.answer("Теперь отправьте фото автомобиля (вид сбоку):")
    await state.set_state(Driver.car_photo_3)


@user.message(Driver.car_photo_3)
async def process_car_photo_3(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file = await message.bot.get_file(photo.file_id)

    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, f"car_photo_3_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)

    await state.update_data(car_photo_3=save_path)
    await message.answer("Теперь отправьте селфи с автомобилем и водительскими правами:")
    await state.set_state(Driver.selfie_with_car)


@user.message(Driver.selfie_with_car)
async def process_selfie_with_car(message: Message, state: FSMContext):
    photo = message.photo[-1]  # Получаем фото в максимальном разрешении
    file = await message.bot.get_file(photo.file_id)  # Получаем объект файла

    # Определяем директорию для сохранения
    save_dir = os.path.join(os.getcwd(), "app", "image")
    os.makedirs(save_dir, exist_ok=True)  # Создаем папку, если ее нет

    # Сохраняем файл на диск
    save_path = os.path.join(save_dir, f"selfie_with_car_{message.from_user.id}.jpg")
    await message.bot.download_file(file.file_path, save_path)

    # Сохраняем путь к файлу в состоянии
    await state.update_data(selfie_with_car=save_path)

    # Получаем все данные из состояния
    user_data = await state.get_data()
    
    # Формируем текст для вывода данных
    registration_info = (
        f"📛Фамилия: {user_data.get('last_name')}\n"
        f"📛Имя: {user_data.get('first_name')}\n"
        f"📛Отчество: {user_data.get('middle_name', 'Нет')}\n"
        f"📞Телефон: {user_data.get('phone')}\n"
        f"🏙️Город: {user_data.get('city')}\n"
        f"🚗Марка автомобиля: {user_data.get('car_make')}\n"
        f"🔢Гос. номер автомобиля: {user_data.get('car_plate')}\n"
        f"📜Номер водительских прав: {user_data.get('license_number')}\n"
    )

    # Отправляем текстовые данные пользователю
    await message.answer("Ваши данные:\n\n" + registration_info,reply_markup=kb.exit_save)

    # Отправляем фотографии пользователю
    photo_descriptions = {
        'license_front': "Лицевая сторона водительских прав",
        'license_back': "Задняя сторона водительских прав",
        'car_photo_1': "Фото автомобиля (вид спереди)",
        'car_photo_2': "Фото автомобиля (вид сзади)",
        'car_photo_3': "Фото автомобиля (вид сбоку)",
        'selfie_with_car': "Селфи с автомобилем"
    }


    for key, description in photo_descriptions.items():
        file_path = user_data.get(key)
        if file_path and os.path.exists(file_path):
            photo_input = FSInputFile(file_path)
            await message.answer_photo(photo_input, caption=description)
            #os.remove(file_path)  # Удаляем файл после отправки

    await state.set_state(Driver.save)

@user.message(Driver.save)
async def save_driver_state(message: Message, state: FSMContext):
    user_data = await state.get_data()
    await save_driver_data(user_data,message.from_user.id)
    await message.answer("✅Данные успешно сохранены.",reply_markup=kb.user_profile)
    await state.clear()


@user.message(F.text == '⏳Отправить на проверку')
async def save_driver(message: Message, state: FSMContext):
    await state.set_state(Driver.save)

    
@user.message(F.text == 'Профиль')
async def user_profile(message: Message):
    driver = await get_driver_by_tg_id(message.from_user.id)
    if not driver:
        await message.answer("Профиль не найден. Пожалуйста, зарегистрируйтесь.")
        return
    profile_info = (
        f"👤 Профиль водителя:\n"
        f"🆔 Telegram ID: {driver.tg_id}\n"
        f"📛 Полное имя: {driver.full_name}\n"
        f"📞 Телефон: {driver.phone}\n"
        f"🏙️ Город: {driver.city}\n"
        f"🚗 Марка машины: {driver.car_make}\n"
        f"🔢 Гос. номер: {driver.car_plate}\n"
        f"📜 Номер лицензии: {driver.license_number}\n"
        f"📅 Дата регистрации: {driver.registration_date.strftime('%d.%m.%Y')}\n\n"
    )
    if driver.verification:
        profile_info += "✅ Статус: Верификация пройдена.\n"
    else:
        profile_info += "⏳ Статус: Ожидание проверки администратора.\n"
    await message.answer(profile_info)

    if driver.is_blocked:
        blocked_message = (
            f"🚫 Внимание! Вы заблокированы.\n"
            f"❗ Комментарий: {driver.comments if driver.comments else 'Не указана'}"
        )
        await message.answer(blocked_message)