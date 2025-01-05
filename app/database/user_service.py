from app.database.models import async_session
from app.database.models import Driver
from sqlalchemy import select, func
from datetime import datetime, date, timedelta
from aiogram import Bot
from aiogram.types import ChatMember
from sqlalchemy import update
import os

def connection(func):
    async def inner(*args, **kwargs):
        async with async_session() as session:
            return await func(session, *args, **kwargs)
    return inner

@connection
async def save_driver_data(session, user_data, tg_id):
    # Создаем объект Driver с переданными данными
    driver = Driver(
        tg_id=tg_id,
        last_name=user_data.get('last_name'),
        first_name=user_data.get('first_name'),
        middle_name=user_data.get('middle_name'),
        full_name=f"{user_data.get('last_name')} {user_data.get('first_name')} {user_data.get('middle_name', '')}",
        phone=user_data.get('phone'),
        city=user_data.get('city'),
        car_make=user_data.get('car_make'),
        car_plate=user_data.get('car_plate'),
        license_number=user_data.get('license_number'),
        license_front_url=user_data.get('license_front'),
        license_back_url=user_data.get('license_back'),
        car_photo_1=user_data.get('car_photo_1'),
        car_photo_2=user_data.get('car_photo_2'),
        car_photo_3=user_data.get('car_photo_3'),
        selfie_with_car=user_data.get('selfie_with_car'),
        registration_date=date.today(),
        is_blocked=False,
        comments=user_data.get('comments', ''),
        verification=False
    )

    # Добавляем данные в сессию и коммитим
    session.add(driver)
    await session.commit()


async def delete_user_files(tg_id):
    save_dir = os.path.join(os.getcwd(), "app", "image") 
    if not os.path.exists(save_dir):
        print("Папка с изображениями не существует.")
        return
    for file_name in os.listdir(save_dir):
        if str(tg_id) in file_name:
            file_path = os.path.join(save_dir, file_name)
            os.remove(file_path)
            print(f"Файл {file_name} успешно удалён.")


@connection
async def get_driver_by_tg_id(session,tg_id):
    driver = await session.scalar(select(Driver).where(Driver.tg_id == tg_id))
    return driver


@connection
async def check_uniqueness(session, field: str, value: str) -> bool:
    """
    Проверяет уникальность значения в указанном поле таблицы Driver.
    Возвращает True, если нет схожих записей, и False, если они есть.
    """
    # Проверяем, что поле существует в модели Driver
    if not hasattr(Driver, field):
        raise ValueError(f"Поле '{field}' не существует в модели Driver.")
    
    # Динамически строим запрос для проверки схожести
    query = select(Driver).where(getattr(Driver, field) == value)
    
    # Выполняем запрос
    result = await session.execute(query)
    driver = result.scalar()
    
    # Возвращаем True, если схожих записей нет, иначе False
    return driver is None

@connection
async def check_tg_id_exists(session, tg_id: str) -> bool:
    """
    Проверяет, существует ли водитель с указанным tg_id в базе данных.
    Возвращает True, если такой водитель найден, иначе False.
    """
    # Строим запрос для поиска водителя по tg_id
    query = select(Driver).where(Driver.tg_id == tg_id)
    
    # Выполняем запрос
    result = await session.execute(query)
    driver = result.scalar_one_or_none()  # Получаем первого водителя или None, если не найдено
    
    # Проверяем, найден ли водитель
    if driver is not None:
        return True  # Водитель найден, возвращаем True
    else:
        return False  # Водитель не найден, возвращаем False
