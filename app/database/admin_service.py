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
async def search_driver(session, field: str, value):
    # Проверяем, что поле существует в модели Driver
    if not hasattr(Driver, field):
        raise ValueError(f"Поле '{field}' не существует в модели Driver.")
    
    # Динамически строим запрос
    #query = select(Driver).where(getattr(Driver, field) == value)
    query = select(Driver).where(getattr(Driver, field).like(f"%{value}%"))
    # Выполняем запрос
    result = await session.scalars(query)
    return result.all()


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import sessionmaker

@connection
async def update_driver(session, user_id: int, field: str, new_value: str):
    # Проверяем, что поле существует в модели Driver
    if not hasattr(Driver, field):
        raise ValueError(f"Поле '{field}' не существует в модели Driver.")

    # Динамически обновляем поле
    query = select(Driver).where(Driver.tg_id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError(f"Пользователь с ID {user_id} не найден.")
    
    # Обновляем выбранное поле
    setattr(user, field, new_value)

    # Сохраняем изменения в базе данных
    await session.commit()

    return user  # Возвращаем обновленного пользователя


@connection
async def block_driver(session, tg_id: int, comment: str = None):
    # Асинхронный запрос для поиска водителя по tg_id
    result = await session.execute(select(Driver).filter(Driver.tg_id == tg_id))
    driver = result.scalar_one_or_none()

    if driver:
        # Обновляем статус блокировки
        driver.is_blocked = True

        # Если комментарий передан, обновляем комментарий
        if comment:
            driver.comments = comment

        # Сохраняем изменения в базе данных
        await session.commit()
        return True


@connection
async def get_all_drivers(session):
    result = await session.execute(select(Driver))  # Получаем всех водителей
    drivers = result.scalars().all()
    return drivers

@connection
async def search_driver_ver(session, field: str, value):
    # Проверяем, что поле существует в модели Driver
    if not hasattr(Driver, field):
        raise ValueError(f"Поле '{field}' не существует в модели Driver.")
    
    query = select(Driver).where(getattr(Driver, field) == value)  # Используем точное сравнение, а не LIKE
    result = await session.execute(query)
    return result.scalars().all()  # Возвращаем результат в виде списка объектов Driver

@connection
async def update_driver_verification(session, tg_id: int, status: bool):
    query = select(Driver).where(Driver.tg_id == tg_id)
    result = await session.execute(query)
    driver = result.scalar_one_or_none()
    
    if driver:
        driver.verification = status
        await session.commit()
        return True
    return False


@connection
async def unblock_driver(session, tg_id):
    # Асинхронный запрос для поиска водителя по tg_id
    result = await session.execute(select(Driver).filter(Driver.tg_id == tg_id))
    driver = result.scalar_one_or_none()

    if driver:
        # Обновляем статус блокировки
        driver.is_blocked = False

        # Сохраняем изменения в базе данных
        await session.commit()
        return True
    else:
        return False
        































"""@connection
async def search_driver(session, field: str, value: str):
    if not hasattr(Driver, field):
        raise ValueError(f"Поле '{field}' не существует в модели Driver.")

    value = value.strip().lower()

    # Применяем LOWER для сравнения с учетом регистра
    query = select(Driver).where(func.lower(getattr(Driver, field)).like(f"%{value}%"))

    print(f"SQL Query: {query}")  # Логирование запроса для отладки

    result = await session.scalars(query)
    return result.all()"""








"""    drivers = await search_driver('tg_id' ,1075213318)
    if drivers:  # Проверяем, что список не пустой
        response = "👤 Найдены пользователи:\n"
        for driver in drivers:  # Перебираем всех найденных пользователей
            response += (
                f"ID: {driver.tg_id}\n"
                f"Имя: {driver.full_name}\n"
                f"Город: {driver.city}\n\n"
            )
        await message.answer(response)
    else:
        await message.answer("❌ Пользователь не найден.")"""